from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from pandas import Series
from time import time
from rand_agent import RandAgent
from problog.program import PrologString
from problog import get_evaluatable
import gc
from enum import IntEnum
import numpy as np
from copy import deepcopy

standard_max_rounds = 100


class Verbosity(IntEnum):
    none = 0
    messages = 1
    reasoning = 2
    debug = 3


class EnumAgent(RandAgent):
    # TODO implement consession rate
    def __init__(self, name, utilities, kb, reservation_value, non_agreement_cost, issues, max_rounds=standard_max_rounds,
                 verbose=Verbosity.none, issue_weights=None, linear_additive_utility=True):
        super().__init__(name, utilities, kb, reservation_value, non_agreement_cost, issues, max_rounds,
                         verbose=Verbosity.none, issue_weights=issue_weights)
        self.utility_computation_method = "python"
        self.linear_additive_utility = True
        self.verbose = verbose
        if not max_rounds:
            self.max_rounds = standard_max_rounds
        else:
            self.max_rounds = max_rounds

        self.non_agreement_cost = non_agreement_cost
        self.relative_reservation_value = reservation_value
        self.absolute_reservation_value = None
        self.successful = False
        self.negotiation_active = False
        self.total_offers_generated = 0
        self.message_count = 0
        self.generator_ready = False
        self.strat_name = "Enumeration"
        self.agent_name = name
        self.strat_dict = {}
        self.transcript = []
        self.kb = []
        self.utilities = {}
        self.issues = None
        self.decision_facts = []
        self.next_message_to_send = None
        self.opponent = None
        self.start_time = 0
        self.issue_weights = None
        self.max_utility_by_issue = {}

        if issues:
            self.set_issues(issues, issue_weights)
        if utilities:
            self.set_utilities(utilities, reservation_value)

        self.set_kb(kb)

    def init_offer_generator(self):
        if not self.utilities or not self.issues:
            return

        nested_utils = self.nested_dict_from_atom_dict(self.utilities)
        # sort value, util pairs in decending order according to util

        def sorter(issue):
            return sorted(
                nested_utils[issue].items(),
                reverse=True,
                key=lambda tup: tup[1])
        self.sorted_utils = {issue: sorter(issue)
                             for issue in self.issues.keys()}

        self.current_offer_indices = {
            issue: 0 for issue in self.issues.keys()}
        self.current_offer_indices[next(
            iter(self.current_offer_indices.keys()))] = -1
        self.generator_ready = True

    def generate_offer(self):
        if not self.generator_ready:
            self.init_offer_generator()

        best_next_util = -1000
        issue_to_incr = -1
        for issue in self.issues.keys():
            next_offer_indeces = deepcopy(self.current_offer_indices)
            next_offer_indeces[issue] += 1
            # a = [self.sorted_utils[issue][next_offer_indeces[issue]][1]
            #      for issue in self.issues]
            next_util = np.dot([self.sorted_utils[i][next_offer_indeces[i]][1]
                                for i in self.issues.keys()], list(self.issue_weights.values()))
            if next_util >= best_next_util and next_util >= self.absolute_reservation_value:
                best_next_util = next_util
                issue_to_incr = issue

        if issue_to_incr == -1:
            # no next acceptable offer was found
            return None
        else:
            self.current_offer_indices[issue_to_incr] += 1
            offer = {issue: {
                val: 0 for val in self.issues[issue]} for issue in self.issues.keys()}
            for issue in self.issues.keys():
                offer[issue][self.sorted_utils[issue]
                             [self.current_offer_indices[issue]][0]] = 1
            return offer
