from pyneg.comms import Offer
from pyneg.utils import atom_from_issue_value
from pyneg.types import AtomicDict
from .engine import Evaluator
from typing import Dict
from .strategy import Strategy


class LinearEvaluator(Evaluator):
    def __init__(self, utilities: AtomicDict,
                 issue_weights: Dict[str, float],
                 non_agreement_cost: float):

        self.utilities = utilities
        self.issue_weights = issue_weights
        self.non_agreement_cost = non_agreement_cost

    def add_utilities(self, new_utils: AtomicDict) -> None:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def calc_offer_utility(self, offer: Offer) -> float:
        score = 0
        for issue in offer.get_issues():
            chosen_value = offer.get_chosen_value(issue)
            chosen_atom = atom_from_issue_value(issue, chosen_value)
            if chosen_atom in self.utilities.keys():
                score += self.issue_weights[issue] * \
                    self.utilities[chosen_atom]
            else:
                continue

        return score

    def calc_strat_utility(self, strat: Strategy) -> float:
        score = 0
        for issue in strat.get_issues():
            for value, prob in strat.get_value_dist(issue).items():
                atom = atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    score += self.issue_weights[issue] * \
                        self.utilities[atom] * prob

        return score
