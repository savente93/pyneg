from re import search, sub
from message import Message
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from problog.program import PrologString
from problog import get_evaluatable
from typing import Dict, List, Optional
from abstract_agent import Verbosity, NegSpace
from lin_rand_agent import LinRandAgent
from offer import Offer
from strategy import Strategy


class LinRandProblogAgent(LinRandAgent):
    def __init__(self,
                 name: str,
                 neg_space: Dict[str, List[str]],
                 utilities: Dict[str, float],
                 reservation_value: float,
                 issue_weights: Optional[Dict[str, float]],
                 max_rounds: int = None,
                 max_generation_tries: int = 500,
                 verbose: Verbosity = Verbosity.none,
                 kb: List[str] = []):

        super().__init__(name, neg_space, utilities, reservation_value, issue_weights,
                         verbose=Verbosity.none, max_rounds=max_rounds)

        self.kb: List[str] = kb

    def compile_problog_model(self, offer: Offer) -> str:
        decision_facts_string = offer.get_problog_dists()
        query_string = self.format_query_string()
        kb_string = "\n".join(self.kb) + "\n"
        return decision_facts_string + kb_string + query_string

    def format_query_string(self):
        query_string = ""

        for util_atom in self.utilities.keys():
            # we shouldn't ask problog for facts that we currently have no rules for
            # like we might not have after new issues are set so we'll skip those
            if any([util_atom in rule for rule in self.kb]) or any(
                    [util_atom in atom for atom in self.strategy.get_atom_dict()]):
                query_string += "query({utilFact}).\n".format(utilFact=util_atom)

        return query_string

    def calc_offer_utility(self, offer: Optional[Offer]) -> float:
        if not offer:
            return self.non_agreement_cost

        score = 0

        problog_model = self.compile_problog_model(offer)
        probability_of_facts = get_evaluatable("sdd").create_from(
            PrologString(problog_model)).evaluate().copy()
        probability_of_facts = {
            str(atom): prob for atom, prob in probability_of_facts.items()}
        for fact, reward in self.utilities.items():
            if fact in probability_of_facts.keys():
                issue, _ = Offer.issue_value_tuple_from_atom(fact)
                score += reward * \
                    probability_of_facts[fact] * self.issue_weights[issue]
                score += reward * probability_of_facts[fact]

        if self.verbose >= Verbosity.reasoning:
            print("{}: offer is worth {}".format(self.agent_name, score))
        return score

    def calc_strat_utility(self, strat):
        problog_model = self.compile_problog_model(strat)
        probability_of_facts = get_evaluatable("sdd").create_from(
            PrologString(problog_model)).evaluate().copy()
        probability_of_facts = {
            str(atom): prob for atom, prob in probability_of_facts.items()}

        score = 0
        for fact, reward in self.utilities.items():
            issue, _ = Offer.issue_value_tuple_from_atom(fact)
            score += reward * \
                probability_of_facts[fact] * self.issue_weights[issue]

        return score

    # @staticmethod
    # def file_based_problog(model):
    #     # using the python implementation of problog causes memory leaks
    #     # so we use the commandline interface separately to avoid this as a temp fix
    #     model_path = abspath(
    #         join(dirname(__file__), 'models/temp_model_{}.pl'.format(getpid())))
    #     with open(model_path, "w") as temp_file:
    #         temp_file.write(model)

    #     process = sp.Popen(["problog", model_path], stdout=sp.PIPE)
    #     output, _ = process.communicate()

    #     ans = {}

    #     for string in output.decode("ascii").split("\n"):
    #         if string:
    #             key, prob = string.strip().split(":\t")
    #             ans[key] = float(prob)

    #     remove(model_path)

    #     return ans
