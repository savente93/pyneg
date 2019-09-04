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
                return possible_offer
