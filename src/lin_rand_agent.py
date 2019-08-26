from message import Message
from numpy.random import choice
from typing import Tuple, Dict, List, Optional
from abstract_agent import Verbosity, NegSpace
from abstract_lin_agent import AbstractLinearAgent
from offer import Offer
from strategy import Strategy


class LinRandAgent(AbstractLinearAgent):
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
                         verbose=Verbosity.none, max_rounds=max_rounds)

        self.strat_name = "Random"
        self.total_offers_generated: int = 0
        self.strategy: Strategy = self.init_uniform_strategy()
        self.max_generation_tries: int = max_generation_tries
        self.max_utility_by_issue: Optional[Dict[str, float]] = None

    def setup_negotiation(self, neg_space: NegSpace) -> None:
        if self.verbose >= Verbosity.reasoning:
            print("{name} is setting negotiation".format(name=self.agent_name))
        self.init_uniform_strategy()
        self.index_max_utilities()

    def set_strat(self, strat: Strategy) -> None:
        self.strategy = strat

    def set_utilities(self, utilities: Dict[str, float]) -> None:
        self.utilities = utilities
        if self.verbose >= Verbosity.debug:
            print("{}'s utilities: {}".format(self.agent_name, self.utilities))

        self.index_max_utilities()

    def add_utilities(self, new_utils: Dict[str, float]) -> None:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        self.index_max_utilities()

    def init_uniform_strategy(self) -> None:
        strat_dict: Dict[str, Dict[str, float]] = {}
        for issue in self.neg_space.keys():
            if issue not in strat_dict.keys():
                strat_dict[issue] = {}
            for val in self.neg_space[issue]:
                strat_dict[issue][str(val)] = 1 / len(self.neg_space[issue])

        self.strategy = Strategy(strat_dict)

    def generate_offer(self) -> Optional[Offer]:
        for _ in range(self.max_generation_tries):
            self.total_offers_generated += 1
            offer: Dict[str, Dict[str, float]] = {}
            for issue in self.neg_space.keys():
                # convert to two lists so we can use numpy's choice
                values, probs = zip(
                    *self.strategy.get_value_dist(issue).items())
                chosen_value = choice(values, p=probs)

                offer[issue] = {
                    key: 0 for key in self.strategy.get_value_dist(issue).keys()}
                offer[issue][chosen_value] = 1
            possible_offer = Offer(offer)
            if self.accepts(possible_offer):
                return possible_offer

        # # we can't find a solution we can accept so just give up
        return None

    def index_max_utilities(self) -> None:
        if self.verbose >= Verbosity.debug:
            print("{} is indexing max utilities".format(self.agent_name))

        self.max_utility_by_issue = {}
        for issue in self.neg_space.keys():
            max_issue_util: float = -(2**31)
            for value in self.neg_space[issue]:
                atom = Offer.atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    util = self.utilities[atom] * self.issue_weights[issue]
                else:
                    util = 0

                if util > max_issue_util:
                    max_issue_util = util
                    self.max_utility_by_issue[issue] = max_issue_util

                if not issue in self.max_utility_by_issue.keys():
                    self.max_utility_by_issue[issue] = 0

        self.absolute_reservation_value = self.relative_reservation_value * self.get_max_utility()
