from typing import List, Tuple, cast, Dict, Union, Set
from copy import deepcopy
from problog.program import PrologString
from problog import get_evaluatable
from problog.tasks.dtproblog import dtproblog
from pyneg.comms import Offer
from pyneg.types import NegSpace, NestedDict, AtomicDict
from pyneg.utils import nested_dict_from_atom_dict, atom_from_issue_value, atom_dict_from_nested_dict
from .evaluator import Evaluator
from .strategy import Strategy
from numpy.random import choice
from re import search
from queue import PriorityQueue
from numpy import isclose
from .generator import Generator


class DTPGenerator(Generator):

    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 acceptability_threshold: float,
                 kb: List[str]):

        self.utilities = utilities
        self.kb = kb
        self.neg_space = {issue: list(map(str, values))
                          for issue, values in neg_space.items()}
        self.non_agreement_cost = non_agreement_cost
        self.acceptability_threshold = acceptability_threshold
        self.reset_generator()

    def reset_generator(self):
        self.generated_offers = {}
        self.offer_queue = []

    def add_utilities(self, new_utils: AtomicDict) -> None:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def accepts(self, offer: Offer) -> bool:
        util = self.evaluator.calc_offer_utility(offer)
        return util >= self.acceptability_threshold

    def compile_dtproblog_model(self):
        dtp_decision_vars = ""
        for issue in self.neg_space.keys():
            atom_list = []
            for value in self.neg_space[issue]:
                atom_list.append("?::{atom}".format(
                    atom=atom_from_issue_value(issue, value)))
            dtp_decision_vars += ";".join(
                atom_list) + ".\n"

        utility_string = ""
        for u, r in self.utilities.items():
            utility_string += "utility({},{}).\n".format(u, r)

        # we have to make sure we offset the utility of previously generated
        # offers so dtproblog won't generate them again
        offer_count = 0
        for sparse_offer, util in self.generated_offers.items():
            config_string = ",".join(
                list(map(lambda x: atom_from_issue_value(x[0], x[1]), sparse_offer))) + "."
            utility_string += "offer{} :- {}\n".format(
                offer_count, config_string)
            utility_string += "utility(offer{},{}).\n".format(
                offer_count, -util + self.non_agreement_cost)
            offer_count += 1

        kb_string = "\n".join(self.kb) + "\n"
        return dtp_decision_vars + kb_string + utility_string

    def extend_partial_offer(self, partial_offer) -> Set[Offer]:
        partial_offer_queue = []
        partial_offer_queue.append(partial_offer)
        full_offers = set()
        while len(partial_offer_queue) > 0:
            partial_offer = nested_dict_from_atom_dict(
                partial_offer_queue.pop())
            # make sure we cover all of the issues
            for issue in self.neg_space.keys():
                if issue not in partial_offer.keys():
                    partial_offer[issue] = {
                        value: 0.0 for value in self.neg_space[issue]}

            # make sure the issues cover all values
            for issue in self.neg_space.keys():
                for value in self.neg_space[issue]:
                    if value not in partial_offer[issue].keys():
                        partial_offer[issue][value] = 0.0

            # if an issue didn't have any utilities we can use that
            # to make lateral moves for free.
            for issue in self.neg_space.keys():
                if isclose(sum(partial_offer[issue].values()), 0):
                    for value in self.neg_space[issue]:
                        partial_offer_copy = deepcopy(partial_offer)
                        partial_offer_copy[issue][value] = 1.0
                        partial_atom_dict = atom_dict_from_nested_dict(
                            partial_offer_copy)
                        partial_offer_queue.append(partial_atom_dict)

            try:
                # is the partial offer valid? (Offer will raise valueerror if not)
                full_offer = Offer(partial_offer)
                full_offers.add(full_offer)
            except ValueError:
                continue

        return full_offers

    def clean_query_output(self, query_output: Dict) -> Dict:
        return_dict = {}
        for atom, prob in query_output.items():
            # sometimes dtproblog can return things like "choice(0,0,boolean_true)" so we need to filter that out
            s = search(r"(\'?[A-z0-9|\.]+\_[A-z0-9|\.]+\'?)", str(atom))
            clean_atom = s.group(0)
            return_dict[clean_atom] = prob

        return return_dict

    def generate_offer(self) -> Offer:
        if len(self.offer_queue) == 0:
            program = PrologString(self.compile_dtproblog_model())
            query_output, score, _ = dtproblog(program)

            # score of offers are now below acceptability threshold
            # so we should terminate
            if score < self.acceptability_threshold:
                raise StopIteration()
            cleaned_query_output = self.clean_query_output(query_output)
            extended_offers = self.extend_partial_offer(cleaned_query_output)

            for offer in extended_offers:
                if offer not in self.generated_offers.keys():
                    self.generated_offers[offer.get_sparse_repr()] = score
                    self.offer_queue.append(offer)

        if len(self.offer_queue) == 0:
            raise RuntimeError()

        return self.offer_queue.pop()
