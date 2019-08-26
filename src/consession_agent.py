from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
from abstract_agent import AbstractAgent, Verbosity
from enum import IntEnum
import numpy as np
from copy import deepcopy
from offer import Offer
from typing import Optional, Dict, List


class ConsessionAgent(AbstractAgent):
    def __init__(self,
                 name: str,
                 neg_space: Dict[str, List[str]],
                 utilities: Dict[str, float],
                 reservation_value: float,
                 max_rounds: int = None,
                 verbose: Verbosity = Verbosity.none,):

        super().__init__(name, neg_space, utilities, reservation_value,
                         verbose=Verbosity.none, max_rounds=max_rounds)
        self.strat_name = "Enumeration"
        self.max_utility_by_issue = {}

    def init_offer_generator(self):
        if not self.utilities:
            return

        nested_utils = Offer.nested_dict_from_atom_dict(self.utilities)
        # sort value, util pairs in decending order according to util

        def sorter(issue):
            return sorted(
                nested_utils[issue].items(),
                reverse=True,
                key=lambda tup: tup[1])
        self.sorted_utils = {issue: sorter(issue)
                             for issue in self.neg_space.keys()}

        self.current_offer_indices = {
            issue: 0 for issue in self.neg_space.keys()}
        self.current_offer_indices[next(
            iter(self.current_offer_indices.keys()))] = -1
        self.generator_ready = True

    def generate_offer(self) -> Offer:
        if not self.generator_ready:
            self.init_offer_generator()

        best_next_util = -1000
        issue_to_incr = -1
        for issue in self.neg_space.keys():
            next_offer_indeces = deepcopy(self.current_offer_indices)
            next_offer_indeces[issue] += 1
            next_util = sum([self.sorted_utils[i][next_offer_indeces[i]][1]
                             for i in self.neg_space.keys()])
            if next_util >= best_next_util and next_util >= self.absolute_reservation_value:
                best_next_util = next_util
                issue_to_incr = issue

        if issue_to_incr == -1:
            # no next acceptable offer was found
            return None
        else:
            self.current_offer_indices[issue_to_incr] += 1
            offer = {issue: {
                val: 0 for val in self.neg_space[issue]} for issue in self.neg_space.keys()}
            for issue in self.neg_space.keys():
                offer[issue][self.sorted_utils[issue]
                             [self.current_offer_indices[issue]][0]] = 1
            return offer

    @staticmethod
    def atom_dict_from_nested_dict(nested_dict):
        atom_dict = {}
        for issue in nested_dict.keys():
            for value in nested_dict[issue].keys():
                atom = Offer.atom_from_issue_value(
                    issue, value)
                atom_dict[atom] = nested_dict[issue][value]

        return atom_dict
