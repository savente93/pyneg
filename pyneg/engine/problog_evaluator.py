from pyneg.comms import Offer
from typing import Dict, Union, Optional, List
from pyneg.utils import atom_from_issue_value
from pyneg.types import AtomicDict
from .strategy import Strategy
from pyneg.types import NegSpace
from problog.program import PrologString
from problog import get_evaluatable
from .engine import Evaluator


class ProblogEvaluator(Evaluator):
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 kb: List[str]):

        self.utilities = utilities
        self.kb = kb
        self.neg_space = neg_space
        self.non_agreement_cost = non_agreement_cost

    def add_utilities(self, new_utils: AtomicDict) -> None:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def calc_probabilities_of_utilities(self, offer: Offer) -> Dict[str, float]:
        model = self.compile_problog_model(offer)
        probability_of_facts = {str(atom): util for atom, util in
                                get_evaluatable("sdd").create_from(
                                PrologString(model)).evaluate().items()}

        return probability_of_facts

    def compile_problog_model(self, offer: Offer) -> str:
        decision_facts_string = offer.get_problog_dists()

        query_string = ""
        for util_atom in self.utilities.keys():
                # we shouldn't ask problog for facts that we currently have no rules for
                # like we might not have after new issues are set so we'll skip those
            if any([util_atom in rule for rule in self.kb]) or any(
                    [util_atom in atom for atom in self.utilities.keys()]):
                query_string += "query({utilFact}).\n".format(utilFact=util_atom)

        kb_string = "\n".join(self.kb) + "\n"

        return decision_facts_string + kb_string + query_string

    def calc_offer_utility(self, offer: Offer) -> float:
        probability_of_utilities = self.calc_probabilities_of_utilities(offer)
        total_util = 0.0
        for atom, prob in probability_of_utilities.items():
            total_util += prob * self.utilities[atom]

        return total_util

    def calc_strat_utility(self, strat: Strategy) -> float:
        score = 0
        for issue in strat.get_issues():
            for value, prob in strat.get_value_dist(issue).items():
                atom = atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    score += self.utilities[atom] * prob

        return score
