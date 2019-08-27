from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from pandas import Series
from time import time
from constr_agent import ConstrAgent
from enum_agent import EnumAgent
from rand_agent import RandAgent
from problog.program import PrologString
from problog import get_evaluatable
import gc
from enum import IntEnum
import numpy as np
from copy import deepcopy
from atomic_constraint import AtomicConstraint

standard_max_rounds = 100


class Verbosity(IntEnum):
    none = 0
    messages = 1
    reasoning = 2
    debug = 3


class EnumConstrAgent(RandAgent):
    def __init__(self, name,
                 utilities,
                 kb,
                 reservation_value,
                 non_agreement_cost,
                 issues,
                 max_rounds=standard_max_rounds,
                 verbose=Verbosity.none, issue_weights=None,
                 linear_additive_utility=True,
                 auto_constraints=True):
        self.own_constraints = set()
        self.opponent_constraints = set()
        self.constraints_satisfiable = True
        super().__init__(name, utilities, kb, reservation_value, non_agreement_cost, issues)
        self.utility_computation_method = "python"
        self.linear_additive_utility = True
        self.verbose = verbose

        self.strat_name = "Constrained Enumeration"
        self.generator_ready = False
        self.auto_constraints = auto_constraints
        self.add_utilities(utilities)

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
        # generating the offer is going to increment the indeces so we want to make sure that
        # it will land on all 0 first time it does this
        self.current_offer_indices[next(
            iter(self.current_offer_indices.keys()))] = -1
        self.generator_ready = True

    def generate_offer(self):

        if not self.constraints_satisfiable:
            raise RuntimeError(
                "Can't generate offer with unsolvable constraints")

        if not self.generator_ready:
            self.init_offer_generator()

        best_next_util = -1000
        issue_to_incr = -1
        for issue in self.issues.keys():
            next_offer_indeces = deepcopy(self.current_offer_indices)
            if next_offer_indeces[issue] + 1 >= len(self.sorted_utils[issue]):
                continue
            next_offer_indeces[issue] += 1
            util_list = []
            for i in self.issues.keys():
                sorted_utils_of_issue = self.sorted_utils[i]
                chosen_util = sorted_utils_of_issue[next_offer_indeces[i]][1]
                util_list.append(chosen_util)
            next_util = np.dot(util_list, list(self.issue_weights.values()))
            if next_util >= best_next_util and next_util >= self.absolute_reservation_value:
                best_next_util = next_util
                issue_to_incr = issue

        if issue_to_incr == -1:
            # no next acceptable offer was found
            return None
        else:
            self.current_offer_indices[issue_to_incr] += 1
            offer = {issue: {val: 0 for val in self.issues[issue]}
                     for issue in self.issues.keys()}
            for issue in self.issues.keys():
                offer[issue][self.sorted_utils[issue]
                             [self.current_offer_indices[issue]][0]] = 1
            return offer

    def generate_offer_message(self, constr=None):
        try:
            offer = self.generate_offer()
            while offer and not self.satisfies_all_constraints(offer):
                offer = self.generate_offer()

        except RuntimeError:
            if self.verbose >= Verbosity.reasoning:
                print("{} is terminating because they were unable to generate an offer".format(
                    self.agent_name))
            offer = None

        if not offer:
            self.negotiation_active = False
            self.successful = False
            termination_message = Message(
                self.agent_name, self.opponent.agent_name, "terminate", None)
            self.record_message(termination_message)
            return termination_message

        if not self.satisfies_all_constraints(offer):
            raise RuntimeError(
                "should not be able to generate constraint violating offer: " +
                "{}\n constraints: {}".format(offer, self.get_all_constraints()))
            # raise RuntimeError("should not be able to generate constraint violating offer")

        if not self.is_offer_valid(offer):
            if self.verbose >= Verbosity.debug:
                raise RuntimeError(
                    "{} generated invalid offer: {}".format(self.agent_name, offer))
            raise RuntimeError(
                "{} generated invalid offer".format(self.agent_name))
        # generate offer can return a termination message if no acceptable offer can be found
        # so we should check for that
        if type(offer) == dict:
            return Message(self.agent_name, self.opponent.agent_name, kind="offer", offer=offer, constraint=constr)
        elif type(offer) == Message:
            offer.constraint = constr
            return offer

    def add_utilities(self, new_utils):
        for atom, util in new_utils.items():
            self.utilities[atom] = util

        if self.auto_constraints and self.issues:
            new_constraints = self.generate_new_constraints()
            for new_constr in new_constraints:
                self.add_own_constraint(new_constr)

    def generate_new_constraints(self):
        if self.verbose >= Verbosity.debug:
            print("{} is checking for new constraints".format(self.agent_name))

        new_constraints = set()
        for issue in self.issues.keys():
            best_case = sum(
                [bc for i, bc in self.max_utility_by_issue.items() if i != issue])

            for value in self.issues[issue]:
                atom = super().atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    value_util = self.utilities[atom]
                else:
                    value_util = 0

                if best_case+value_util < self.absolute_reservation_value:
                    if self.verbose >= Verbosity.reasoning:
                        print("{} is adding new constraint {} because best_case util of {} is too low".format(
                            self.agent_name,
                            AtomicConstraint(issue, value),
                            best_case+value_util))
                    new_constraints.add(AtomicConstraint(issue, value))

        return new_constraints

    def get_unconstrained_values_by_issue(self, issue):
        issue_constrained_values = [
            constr.value for constr in self.get_all_constraints() if constr.issue == issue]
        issue_un_constrained_values = set(
            self.issues[issue]) - set(issue_constrained_values)
        return issue_un_constrained_values

    def add_own_constraint(self, constraint):
        if self.verbose >= Verbosity.reasoning:
            print("{} is adding own constraint: {}".format(
                self.agent_name, constraint))
        self.own_constraints.add(constraint)

        if not self.atom_from_issue_value(constraint.issue, constraint.value) in self.utilities.keys():
            self.add_utilities({self.atom_from_issue_value(
                constraint.issue, constraint.value): self.non_agreement_cost})
        if not all([len(self.get_unconstrained_values_by_issue(issue)) > 0 for issue in self.issues.keys()]):
            self.constraints_satisfiable = False
            return
        self.index_max_utilities()

    def add_opponent_constraint(self, constraint):
        if constraint in self.opponent_constraints:
            return
        if self.verbose >= Verbosity.reasoning:
            print("{} is adding opponent constraint: {}".format(
                self.agent_name, constraint))
        self.opponent_constraints.add(constraint)
        if not self.constraints_satisfiable:
            return

        atom = self.atom_from_issue_value(constraint.issue, constraint.value)
        if not atom in self.utilities.keys():
            self.add_utilities({atom: self.non_agreement_cost})
        else:
            self.utilities[atom] = self.non_agreement_cost

        if not all([len(self.get_unconstrained_values_by_issue(issue)) > 0 for issue in self.issues.keys()]):
            self.constraints_satisfiable = False
            return

        self.index_max_utilities()

    def satisfies_all_constraints(self, offer):
        all_constraints = self.get_all_constraints()
        for constr in all_constraints:
            if not constr.is_satisfied_by_strat(offer):
                return False
        return True

    def generate_violated_constraint(self, offer):
        for constr in self.own_constraints:
            for issue in offer.keys():
                for value in offer[issue].keys():
                    if not constr.is_satisfied_by_assignment(issue, value) and not isclose(offer[issue][value], 0):
                        return AtomicConstraint(issue, value)

    def should_terminate(self, msg):
        return self.message_count >= self.max_rounds or not self.constraints_satisfiable

    def get_all_constraints(self):
        return self.own_constraints.copy().union(self.opponent_constraints)

    def accepts(self, offer):
        if self.verbose >= Verbosity.reasoning:
            print("{}: considering \n{}".format(
                self.agent_name, self.format_offer(offer)))

        if not offer:
            return False

        if not self.satisfies_all_constraints(offer):
            return False

        if type(offer) == Message:
            util = self.calc_offer_utility(offer.offer)
        else:
            util = self.calc_offer_utility(offer)

        if self.verbose >= Verbosity.reasoning:
            if util >= self.absolute_reservation_value:
                print("{}: offer is acceptable\n".format(self.agent_name))
            else:
                print("{}: offer is not acceptable\n".format(self.agent_name))
        return util >= self.absolute_reservation_value

    def receive_negotiation_request(self, opponent, issues):
        # allows others to initiate negotiations with us
        # we always accept calls for negotiation if we can init properly and don't have incompatible constraints
        try:
            if self.constraints_satisfiable:
                self.setup_negotiation(issues)
                self.opponent = opponent
                return True
            else:
                return False
        except:
            # something went wrong setting up so reject request
            print("{} failed to setup negotiation properly".format(self.agent_name))
            return False

    def setup_negotiation(self, issues):
        try:
            super().setup_negotiation(issues)
            return True
        except RuntimeError as e:
            self.constraints_satisfiable = False
            return False

    def negotiate(self, opponent):
        if self.constraints_satisfiable:
            return super().negotiate(opponent)
        else:
            return False

    def index_max_utilities(self):
        if self.verbose >= Verbosity.debug:
            print("{} is indexing max utilities".format(self.agent_name))

        self.max_utility_by_issue = {}
        for issue in self.issues.keys():
            max_issue_util = -(2**31)
            for value in self.issues[issue]:
                if not all([constr.is_satisfied_by_assignment(issue, value) for constr in self.get_all_constraints()]):
                    continue

                atom = self.atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    if not all([constr.is_satisfied_by_assignment(issue, value) for constr in self.get_all_constraints()]):
                        continue
                    util = self.utilities[atom] * self.issue_weights[issue]
                else:
                    util = 0

                if util > max_issue_util:
                    max_issue_util = util
                    self.max_utility_by_issue[issue] = max_issue_util

                if not issue in self.max_utility_by_issue.keys():
                    self.max_utility_by_issue[issue] = 0

            if max_issue_util == -(2**31):
                raise RuntimeError(
                    "issue {} has no unconstrainted values left")

        self.absolute_reservation_value = self.relative_reservation_value * self.get_max_utility()

    def generate_next_message_from_transcript(self):
        try:
            last_message = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generate_offer_message()

        if self.verbose >= Verbosity.reasoning:
            print("{} is using {} to generate next offer.".format(
                self.agent_name, last_message))

        if last_message.is_acceptance():
            self.negotiation_active = False
            self.successful = True
            return None

        if last_message.is_termination():
            self.negotiation_active = False
            self.successful = False
            return None

        if self.should_terminate(last_message):
            self.negotiation_active = False
            self.successful = False
            return Message(self.agent_name, self.opponent.agent_name, "terminate", None)

        if self.accepts(last_message.offer):
            self.negotiation_active = False
            self.successful = True
            return Message(self.agent_name, self.opponent.agent_name, "accept", last_message.offer)

        violated_constraint = self.generate_violated_constraint(
            last_message.offer)
        return self.generate_offer_message(violated_constraint)

    def receive_message(self, msg):
        if not msg:
            return
        if self.verbose >= Verbosity.messages:
            print("{}: received message: {}".format(self.agent_name, msg))
        self.record_message(msg)
        if msg.constraint:
            self.add_opponent_constraint(msg.constraint)
            if self.verbose >= Verbosity.debug:
                print("constraints still consistant: {}".format(
                    self.constraints_satisfiable))

    def calc_offer_utility(self, offer):
        if not offer:
            return self.non_agreement_cost
        if not self.is_offer_valid(offer):
            raise ValueError("Invalid offer received: {}".format(offer))
        if not self.satisfies_all_constraints(offer):
            return self.non_agreement_cost

        return super().calc_offer_utility(offer)
