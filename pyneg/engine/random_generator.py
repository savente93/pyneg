from typing import List, Dict

from numpy.random import choice

from pyneg.comms import Offer
from pyneg.types import NegSpace, AtomicDict
from .evaluator import Evaluator
from .generator import Generator
from .strategy import Strategy


class RandomGenerator(Generator):
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 non_agreement_cost: float,
                 kb: List[str],
                 acceptability_threshold: float,
                 max_generation_tries: int = 500):

        self.utilities = utilities
        self.kb = kb
        self.neg_space = {issue: list(map(str, values))
                          for issue, values in neg_space.items()}
        self.non_agreement_cost = non_agreement_cost
        self.evaluator = evaluator
        self.init_uniform_strategy(neg_space)
        self.max_generation_tries = max_generation_tries
        self.acceptability_threshold = acceptability_threshold

    def init_uniform_strategy(self, neg_space: NegSpace) -> None:
        strat_dict: Dict[str, Dict[str, float]] = {}
        for issue in neg_space.keys():
            if issue not in strat_dict.keys():
                strat_dict[issue] = {}
            for val in neg_space[issue]:
                strat_dict[issue][str(val)] = 1 / len(neg_space[issue])

        self.strategy = Strategy(strat_dict)

    def generate_offer(self) -> Offer:
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
            raise StopIteration()

        return return_offer
