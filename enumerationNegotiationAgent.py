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


class EnumerationNegotiationAgent(RandAgent):
    def __init__(self, uuid, utilities, kb, reservation_value, non_agreement_cost, issues, max_rounds=standard_max_rounds,
                 smart=True, name="", verbose=Verbosity.none, reporting=False, issue_weights=None, linear_additive_utility=True):
        self.utility_computation_method = "python"
        self.linear_additive_utility = True
        self.verbose = verbose
        self.uuid = uuid
        self.reporting = reporting
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
        self.smart = smart

    def generate_decision_facts(self):
        self.decision_facts = []
        for issue in self.issues.keys():
            fact_list = []
            for value in self.issues[issue]:
                if "." in str(value):
                    fact_list.append("'{issue}_{value}'".format(
                        issue=issue, value=value))
                else:
                    fact_list.append("{issue}_{value}".format(
                        issue=issue, value=value))
            self.decision_facts.append(fact_list)

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

    @staticmethod
    def atom_dict_from_nested_dict(nested_dict):
        atom_dict = {}
        for issue in nested_dict.keys():
            for value in nested_dict[issue].keys():
                atom = RandAgent.atom_from_issue_value(
                    issue, value)
                atom_dict[atom] = nested_dict[issue][value]

        return atom_dict

    @staticmethod
    def format_offer(offer, indent_level=1):
        if type(offer) == Message:
            offer = offer.offer
        string = ""
        if not offer:
            return string
        for issue in offer.keys():
            string += " " * indent_level * 4 + '{}: '.format(issue)
            for key in offer[issue].keys():
                if offer[issue][key] == 1:
                    string += "{}\n".format(key)
                    break
        return string[:-1]  # remove trailing newline
