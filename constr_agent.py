from os.path import abspath, dirname, join
from re import search, sub
from time import time
from pandas import Series
from numpy import isclose
from atomic_constraint import AtomicConstraint
from message import Message
from rand_agent import RandAgent, Verbosity


class ConstrAgent(RandAgent):
    def __init__(self, name, utilities, kb, reservation_value, non_agreement_cost, issues,
                 max_rounds=None, verbose=Verbosity.none, util_method="python", auto_constraints=True):
        self.own_constraints = set()
        self.opponent_constraints = set()
        self.auto_constraints = auto_constraints
        super().__init__(name, utilities, kb, reservation_value, non_agreement_cost,
                         issues=issues, verbose=verbose, util_method=util_method, max_rounds=max_rounds)
        self.utilities = {}
        self.add_utilities(utilities)
        self.negotiation_active = False
        self.agent_name = name
        self.successful = False
        self.strat_name = "Constrained"
        self.message_count = 0
        self.constraints_satisfiable = True

    def index_max_utilities(self):
        if self.verbose >= Verbosity.debug:
            print("{} is indexing max utilities".format(self.agent_name))

        self.max_utility_by_issue = {}
        for issue in self.issues.keys():
            max_issue_util = -(2**31)
            for value in self.issues[issue]:
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

        self.absolute_reservation_value = self.relative_reservation_value * self.get_max_utility()

    def add_utilities(self, new_utils):
        for atom, util in new_utils.items():
            self.utilities[atom] = util

        if self.auto_constraints and self.issues:
            for atom, util in new_utils.items():
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

    def set_issues(self, issues, weights=None):
        self.decision_facts = []
        self.strat_dict = {}
        for issue, lst in issues.items():
            if "_" in str(issue) or "'" in str(issue):
                raise ValueError("Issue names should not contain _")
            for val in lst:
                if "_" in str(val) or "'" in str(val):
                    raise ValueError("Issue names should not contain _")

        self.issues = {key: list(map(str, issues[key]))
                       for key in issues.keys()}
        self.generate_decision_facts()
        if not weights:
            self.issue_weights = {
                issue: 1/len(self.issues) for issue in self.issues.keys()}
        else:
            if not self.is_dist(weights) and len(weights) != len(self.issues.keys()):
                raise ValueError("{} Tried to set non dist weights: {}".format(
                    self.agent_name, weights))
            issue_iter = iter(self.issues.keys())
            for i in range(len(weights)):
                self.issue_weights[next(issue_iter)] = weights[i]

        self.init_uniform_strategy()
        self.index_max_utilities()
        # TODO must find a way to avoid having to clear the KB every time a new issue is raised
        self.set_kb([])

    def init_uniform_strategy(self):
        # if there are no constraints we can skip all of the checks
        if not self.get_all_constraints():
            super().init_uniform_strategy()
            return

        for issue in self.issues.keys():
            self.strat_dict[issue] = {}
            # issue_constrained_values = [
            #     constr.value for constr in self.get_all_constraints() if constr.issue == issue]
            issue_un_constrained_values = self.get_unconstrained_values_by_issue(
                issue)
            for val in self.issues[issue]:
                if val in issue_un_constrained_values:
                    self.strat_dict[issue][val] = 1 / \
                        len(issue_un_constrained_values)
                else:
                    self.strat_dict[issue][val] = 0.0

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

            if self.verbose >= Verbosity.debug:
                print("stratagy before adding constraint: {}".format(self.strat_dict))
        self.own_constraints.add(constraint)
        self.make_strat_constraint_compliant(constraint)

        if not self.atom_from_issue_value(constraint.issue, constraint.value) in self.utilities.keys():
            self.add_utilities({self.atom_from_issue_value(
                constraint.issue, constraint.value): self.non_agreement_cost})
        self.index_max_utilities()
        if self.verbose >= Verbosity.debug:
            print("strategy after adding constraint: {}".format(self.strat_dict))

    def add_opponent_constraint(self, constraint):
        if self.verbose >= Verbosity.reasoning:
            print("{} is adding opponent constraint: {}".format(
                self.agent_name, constraint))
        if self.verbose >= Verbosity.debug:
            print("strategy before adding constraint: {}".format(self.strat_dict))
        self.opponent_constraints.add(constraint)
        self.make_strat_constraint_compliant(constraint)
        if not self.constraints_satisfiable:
            return

        if not self.atom_from_issue_value(constraint.issue, constraint.value) in self.utilities.keys():
            self.add_utilities({self.atom_from_issue_value(
                constraint.issue, constraint.value): self.non_agreement_cost})
        self.add_utilities({self.atom_from_issue_value(
            constraint.issue, constraint.value): self.non_agreement_cost})
        self.index_max_utilities()

        if self.verbose >= Verbosity.debug:
            print("strategy after adding constraint: {}".format(self.strat_dict))

    def make_strat_constraint_compliant(self, constraint):
        for issue in self.strat_dict.keys():
            issue_constrained_values = [
                constr.value for constr in self.get_all_constraints() if constr.issue == issue]
            issue_unconstrained_values = set(
                self.strat_dict[issue].keys()) - set(issue_constrained_values)

            if len(issue_unconstrained_values) == 0:
                if self.verbose >= Verbosity.reasoning:
                    print("Found incompatible constraint: {}".format(constraint))

                self.constraints_satisfiable = False
                # Unsatisfiable constraint so we're terminating on the next message so we won't need to update the strat
                return

            for value in self.strat_dict[issue].keys():
                if not constraint.is_satisfied_by_assignment(issue, value):
                    self.strat_dict[issue][value] = 0

            # it's possible we just made the last value in the strategy 0 so
            # we have to figure out which value is still unconstrained
            # and set that one to 1
            if sum(self.strat_dict[issue].values()) == 0:
                self.strat_dict[issue][next(
                    iter(issue_unconstrained_values))] = 1
            else:
                strat_sum = sum(self.strat_dict[issue].values())
                self.strat_dict[issue] = {
                    key: prob / strat_sum for key, prob in self.strat_dict[issue].items()}

    def satisfies_all_constraints(self, offer):
        all_constraints = self.get_all_constraints()
        for constr in all_constraints:
            if not constr.is_satisfied_by_strat(offer):
                return False
        return True

    def generate_next_message_from_transcript(self):
        try:
            last_message = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generate_offer_message()

        if self.verbose >= Verbosity.reasoning:
            print("{} is using {} to generate next offer.".format(
                self.agent_name, last_message))

        if last_message.constraint:
            if self.verbose >= Verbosity.reasoning:
                print("{} is adding opponent constraint {}".format(
                    self.agent_name, last_message.constraint))
            self.add_opponent_constraint(last_message.constraint)

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

    def generate_offer_message(self, constr=None):
        try:
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

    def generate_offer(self):
        if self.constraints_satisfiable:
            return super().generate_offer()
        else:
            raise RuntimeError(
                "Cannot generate offer with incompatable constraints: {}".format(self.get_all_constraints()))

    def generate_violated_constraint(self, offer):

        for constr in self.own_constraints:
            for issue in offer.keys():
                for value in offer[issue].keys():
                    if not constr.is_satisfied_by_assignment(issue, value) and not isclose(offer[issue][value], 0):
                        return AtomicConstraint(issue, value)

    def calc_offer_utility(self, offer):
        if not offer:
            return self.non_agreement_cost
        if not self.is_offer_valid(offer):
            raise ValueError("Invalid offer received: {}".format(offer))
        if not self.satisfies_all_constraints(offer):
            return self.non_agreement_cost

        return super().calc_offer_utility(offer)

    def should_terminate(self, msg):
        return self.message_count >= self.max_rounds or not self.constraints_satisfiable

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
        super().setup_negotiation(issues)
        if self.verbose >= Verbosity.reasoning:
            print("{}: starting constraints: {}".format(
                self.agent_name, self.own_constraints))

    def negotiate(self, opponent):
        if self.constraints_satisfiable:
            return super().negotiate(opponent)
        else:
            return False
