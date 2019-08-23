from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
from typing import Dict, List, Optional
from abstract_agent import Verbosity, NegSpace
from lin_rand_agent import LinRandAgent
from offer import Offer
from strategy import Strategy


class LinRandPyAgent(LinRandAgent):
    def __init__(self,
                 name: str,
                 neg_space: Dict[str, List[str]],
                 utilities: Dict[str, float],
                 reservation_value: float,
                 issue_weights: Optional[Dict[str, float]],
                 max_rounds: int = None,
                 max_generation_tries: int = 500,
                 verbose: Verbosity = Verbosity.none):

        super().__init__(name, neg_space, utilities, reservation_value, issue_weights,
                         verbose=Verbosity.none, max_rounds=max_rounds,
                         max_generation_tries=max_generation_tries)

    def calc_offer_utility(self, offer: Optional[Offer]) -> float:
        if not offer:
            return self.non_agreement_cost

        score = 0.0

        for issue in self.neg_space.keys():
            chosen_value = offer.get_chosen_value(issue)
            chosen_value_atom = Offer.atom_from_issue_value(
                issue,
                chosen_value
            )
            if chosen_value_atom in self.utilities.keys():
                score += self.utilities[chosen_value_atom] * \
                    self.issue_weights[issue]

        return score

    def calc_strategy_utility(self) -> float:
        total_expected_util = 0.0
        for issue in self.neg_space.keys():
            expected_util_per_issue = 0.0
            for value in self.neg_space[issue]:
                atom = Offer.atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    expected_util_per_issue += self.utilities[atom] * \
                        self.strategy[issue, value]

            total_expected_util += expected_util_per_issue

        return total_expected_util
