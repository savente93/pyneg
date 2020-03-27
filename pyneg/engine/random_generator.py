"""
Defines the :class:`RandomGenerator` class.
"""

from typing import Dict, List, Optional, Set

from numpy.random import choice

from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import AtomicDict, NegSpace

from .evaluator import Evaluator
from .generator import Generator
from .strategy import Strategy


class RandomGenerator(Generator):
    """
    This generator generates random offers without any reasoning.
    By default it uses uniform distriutions across all issues and values.

    :raises StopIteration: when maximum number of samples for one offer or \
        maximum total number offers generated is exceded
    """
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 non_agreement_cost: float,
                 knowledge_base: List[str],
                 acceptability_threshold: float,
                 max_rounds: int,
                 max_generation_tries: int = 1000):
        super().__init__()
        self.utilities = utilities
        self.knowledge_base = knowledge_base
        self.neg_space = {issue: list(map(str, values))
                          for issue, values in neg_space.items()}
        self.non_agreement_cost = non_agreement_cost
        self.evaluator = evaluator
        self.init_uniform_strategy(neg_space)
        self.max_rounds = max_rounds
        self.round_counter = 0
        self.active = True
        self.max_generation_tries = max_generation_tries
        self.acceptability_threshold = acceptability_threshold

    def init_uniform_strategy(self, neg_space: NegSpace) -> None:
        """
        Initialises a uniform distribution across all possible values for every issue.

        :param neg_space: The negotiation space that the strategy will be based on.
        :type neg_space: NegSpace
        """
        strat_dict: Dict[str, Dict[str, float]] = {}
        for issue in neg_space.keys():
            if issue not in strat_dict.keys():
                strat_dict[issue] = {}
            for val in neg_space[issue]:
                strat_dict[issue][str(val)] = 1 / len(neg_space[issue])

        self.strategy = Strategy(strat_dict)

    def generate_offer(self) -> Offer:
        """
        Generate an offer by sampling from the current strategy until the
        maximum amount of tries are reached or the maximum number of offers are
        generated. (this is to insure that it terminates even in impossible situations.)

        :raises StopIteration: [description]
        :raises StopIteration: [description]
        :return: [description]
        :rtype: Offer
        """

        if self.round_counter >= self.max_rounds:
            self.active = False
            raise StopIteration()

        return_offer = None
        for _ in range(self.max_generation_tries):
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
            util = self.evaluator.calc_offer_utility(possible_offer)
            if util >= self.acceptability_threshold:
                return_offer = possible_offer
                break

        if not return_offer:
            self.active = False
            raise StopIteration()

        self.round_counter += 1
        if self.round_counter >= self.max_rounds:
            self.active = False
        return return_offer

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        return True

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        return True

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
            with non constraint aware system.
            add_constraint called in {self.class.__name__}""")
        return True

    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                add_constraints called in {self.class.__name__}""")
        return True

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                find_violated_constraint called in {self.class.__name__}""")
        return None

    def get_constraints(self) -> Set[AtomicConstraint]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                function get_constraints called in {self.class.__name__}""")
        return set()

    def get_unconstrained_values_by_issue(self, issue: str) -> Set[str]:
        print("""WARNING: attempting to use a constraint mechanism
                with non constraint aware system.
                get_unconstrained_values_by_issue called in {self.class.__name__}""")
        return set(self.neg_space[issue])
