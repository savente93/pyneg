"""
This module devines the :class:`DTPGenerator` class,
which uses DTProbLog to generate optimal offers in
settings that include probabalistic knowledge bases.
"""

from copy import deepcopy
from re import search
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from numpy import isclose
from problog.program import PrologString
from problog.tasks.dtproblog import dtproblog

from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import AtomicDict, NegSpace
from pyneg.utils import (atom_dict_from_nested_dict, atom_from_issue_value,
                         nested_dict_from_atom_dict)

from .generator import Generator

# Help out MyPy a bit
if TYPE_CHECKING:
    from problog.logic import Term # pylint: disable=ungrouped-imports


class DTPGenerator(Generator):
    """
    This generator class uses DTProbLog to generate optimal offers.
    Since it uses DTProbLog it can reason about offers using utilities,
    both atomic and compound and also using arbitrary knowledge bases.
    It does mean that it is very slow and prone to memory leaks due to the
    python implementation of DTProbLog
    """

    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 acceptability_threshold: float,
                 knowledge_base: List[str]):
        super().__init__()
        self.utilities = utilities
        self.knowledge_base = knowledge_base
        self.neg_space = {issue: list(map(str, values))
                          for issue, values in neg_space.items()}
        self.non_agreement_cost = non_agreement_cost
        self.acceptability_threshold = acceptability_threshold
        self.reset_generator()

    def reset_generator(self):
        """
        Reset the internals of the generator so we can start anew for a new negotiaton.
        """
        self.generated_offers = {}
        self.offer_queue = []
        self.active = True

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        return True

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        return True

    def _compile_dtproblog_model(self) -> str:
        """
        Takes the internal knowledge of the agent and complies it into a string representing
        a valid DTProbLog model that it can use to generate the next offer.

        :return: A string representing a valid DTProbLog model
        :rtype: str
        """
        dtp_decision_vars = ""
        for issue in self.neg_space.keys():
            atom_list = []
            for value in self.neg_space[issue]:
                atom_list.append("?::{atom}".format(
                    atom=atom_from_issue_value(issue, value)))
            dtp_decision_vars += ";".join(
                atom_list) + ".\n"

        utility_string = ""
        for utility, reward in self.utilities.items():
            utility_string += "utility({},{}).\n".format(utility, reward)

        # we have to make sure we offset the utility of previously generated
        # offers so dtproblog won't generate them again
        offer_count = 0
        for sparse_offer, util in self.generated_offers.items():
            config_string = ",".join(
                list(map(
                    lambda x: atom_from_issue_value(x[0], x[1]),
                    sparse_offer)))  + "."
            utility_string += "offer{} :- {}\n".format(
                offer_count, config_string)
            utility_string += "utility(offer{},{}).\n".format(
                offer_count, -util + self.non_agreement_cost)
            offer_count += 1

        kb_string = "\n".join(self.knowledge_base) + "\n"
        return dtp_decision_vars + kb_string + utility_string

    def _extend_partial_offer(self, partial_offer: Dict[str, float]) -> Set[Offer]:
        """
        When some decision variables have no impact on the final utility DTProbLog will
        generate partial answers. This function will expand those final offers into all of their
        full options so we can propose them. e.g.

        >>> gen = DTPGenerator(
            neg_space = {"boolean":["True","False"], "dummy":["1","2"]},
            utilities = {"boolean_True":100},
            non_agreement_cost = -100,
            acceptability_threshold = 10,
            knowledge_base = []
        )
        >>> program = PrologString(gen._compile_dtproblog_model())
        >>> query_output, score, _ = dtproblog(program)
        >>> query_output
        {boolean_True: 1}
        >>> cleaned_query_output = gen.clean_query_output(query_output)
        >>> gen._extend_partial_offer(cleaned_query_output)
        {[boolean->True, dummy->1], [boolean->True, dummy->2]}


        :param partial_offer:
        :type partial_offer: [type]
        :raises valueerror: [description]
        :return: [description]
        :rtype: Set[Offer]
        """
        partial_offer_queue = []
        partial_offer_queue.append(partial_offer)
        full_offers = set()
        while partial_offer_queue:
            nested_partial_offer = nested_dict_from_atom_dict(
                partial_offer_queue.pop())
            # make sure we cover all of the issues
            for issue in self.neg_space.keys():
                if issue not in nested_partial_offer.keys():
                    nested_partial_offer[issue] = {
                        value: 0.0 for value in self.neg_space[issue]}

            # make sure the issues cover all values
            for issue in self.neg_space.keys():
                for value in self.neg_space[issue]:
                    if value not in nested_partial_offer[issue].keys():
                        nested_partial_offer[issue][value] = 0.0

            # if an issue didn't have any utilities we can use that
            # to make lateral moves for free.
            for issue in self.neg_space.keys():
                if isclose(sum(nested_partial_offer[issue].values()), 0):
                    for value in self.neg_space[issue]:
                        partial_offer_copy = deepcopy(nested_partial_offer)
                        partial_offer_copy[issue][value] = 1.0
                        partial_atom_dict = atom_dict_from_nested_dict(
                            partial_offer_copy)
                        partial_offer_queue.append(partial_atom_dict)

            try:
                # is the partial offer valid? (Offer will raise valueerror if not)
                full_offer = Offer(nested_partial_offer)
                full_offers.add(full_offer)
            except ValueError:
                continue

        return full_offers

    def _clean_query_output(self, query_output: Dict['Term', float]) -> Dict[str, float]:
        """
        sometimes dtproblog can return things such as "choice(0,0,boolean_true)" under certain
        circumstances so we need to filter these. This function also casts the keys from
        problog.logic.Term to str so we can manipulate them.

        :param query_output: the raw output dictionary from DTProbLog
        :type query_output: Dict[problog.logic.Term, float]
        :return: A dictionary containing the cleaned assignements of the optimal offer
        :rtype: Dict[str, float]
        """
        return_dict = {}
        for atom, prob in query_output.items():
            # sometimes dtproblog can return things
            # like "choice(0,0,boolean_true)" so we need to filter that out
            reg_search = search(r"(\'?[A-z0-9|\.]+\_[A-z0-9|\.]+\'?)", str(atom))
            if not reg_search:
                raise ValueError(f"Could not parse query output: {query_output}")

            clean_atom = reg_search.group(0)
            return_dict[clean_atom] = prob

        return return_dict

    def generate_offer(self) -> Offer:
        if not self.offer_queue:
            program = PrologString(self._compile_dtproblog_model())
            query_output, score, _ = dtproblog(program)

            # score of offers are now below acceptability threshold
            # so we should terminate
            if score < self.acceptability_threshold:
                self.active = False
                raise StopIteration()
            cleaned_query_output = self._clean_query_output(query_output)
            extended_offers = self._extend_partial_offer(cleaned_query_output)

            for offer in extended_offers:
                if offer not in self.generated_offers:
                    self.generated_offers[offer.get_sparse_repr()] = score
                    self.offer_queue.append(offer)

        if not self.offer_queue:
            raise RuntimeError()

        return self.offer_queue.pop()
