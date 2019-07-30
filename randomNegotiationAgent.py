from numpy import isclose
from re import search, sub
from message import Message
from numpy.random import choice
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from pandas import Series
from time import time
from problog.program import PrologString
from problog import get_evaluatable
import gc
from enum import IntEnum

class Verbosity(IntEnum):
    none = 0
    messages = 1
    reasoning = 2
    debug = 3


class RandomNegotiationAgent:
    def __init__(self, uuid, utilities, kb, reservation_value, non_agreement_cost, issues=None, max_rounds=100,
                 smart=True, name="", verbose=Verbosity.none, reporting=False, utility_computation_method="python",
                 issue_weights=None, linear_additive_utility=True):

        if utility_computation_method not in ['problog', 'python']:
            raise ValueError("unknown utility computation method")
        if (not linear_additive_utility and issue_weights) or (not linear_additive_utility and utility_computation_method == 'python'):
            raise ValueError("Cannot use issue weights or python computation for non-linear-additive utility")
        self.utility_computation_method = utility_computation_method
        self.verbose = verbose
        self.uuid = uuid
        self.reporting = reporting
        self.max_rounds = max_rounds
        self.non_agreement_cost = non_agreement_cost
        self.relative_reservation_value = reservation_value
        self.absolute_reservation_value = None
        self.successful = False
        self.negotiation_active = False
        self.total_offers_generated = 0
        self.message_count = 0
        self.strat_name = "Random"
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
        if self.utility_computation_method == "python":
            self.linear_additive_utility = True
        else:
            self.linear_additive_utility = linear_additive_utility
        # self.utilityCache = {}

        if issues:
            self.set_issues(issues, issue_weights)
        if utilities:
            self.set_utilities(utilities, reservation_value)

        self.max_generation_tries = 500

        self.set_kb(kb)
        self.smart = smart

    def set_kb(self, new_kb):
        if len(new_kb) > 0:
            self.linear_additive_utility = False
            self.utility_computation_method = "problog"
            self.issue_weights = {}

        self.kb = new_kb

    def receive_negotiation_request(self, opponent, issues):
        # allows others to initiate negotiations with us
        # we always accept calls for negotiation if we can init properly
        try:
            self.setup_negotiation(issues)
            self.opponent = opponent
            return True
        except:
            # something went wrong setting up so reject request
            print("{} failed to setup negotiation properly".format(self.agent_name))
            return False

    def call_for_negotiation(self, opponent, issues):
        # allows us to initiate negotiations with others
        response = opponent.receive_negotiation_request(self, issues)
        if response:
            self.opponent = opponent
        return response

    def should_terminate(self, msg):
        return self.message_count > self.max_rounds

    def send_message(self, opponent, msg):
        self.message_count += 1
        if self.verbose >= Verbosity.messages:
            print("{} is sending {}".format(self.agent_name, msg))
        opponent.receive_message(msg)

    def negotiate(self, opponent):
        # self is assumed to have setup the negotiation (including issues) beforehand
        self.negotiation_active = self.call_for_negotiation(opponent, self.issues)

        # make initial offer
        # if self.negotiationActive:
        #     oppResponse = opponent.receiveMessage(self.generateOfferMessage())
        self.start_time = time()
        while self.negotiation_active:
            self.next_message_to_send = self.generate_next_message_from_transcript()
            if self.next_message_to_send:
                opponent.receive_message(self.next_message_to_send)
                self.receive_response(opponent)

        return self.successful

    def receive_response(self, sender):
        response = sender.generate_next_message_from_transcript()
        self.record_message(response)

    def record_message(self, msg):
        if msg:
            self.message_count += 1
            self.transcript.append(msg)

    def generate_next_message_from_transcript(self):
        try:
            last_message = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generate_offer_message()

        if last_message.is_acceptance():
            self.negotiation_active = False
            self.successful = True
            self.report()
            return None

        if last_message.is_termination():
            self.negotiation_active = False
            self.successful = False
            self.report()
            return None

        if self.should_terminate(last_message):
            self.negotiation_active = False
            self.successful = False
            self.report()
            return Message(self.agent_name, self.opponent.agent_name, "terminate", last_message.offer)

        if self.accepts(last_message.offer):
            self.negotiation_active = False
            self.successful = True
            self.report()
            return Message(self.agent_name, self.opponent.agent_name, "accept", last_message.offer)

        return self.generate_offer_message()

    def setup_negotiation(self, issues):
        if self.verbose >= Verbosity.reasoning:
            print("{} is setting up the negotiation issues: {}".format(
                self.agent_name, issues))
        self.set_issues(issues)
        self.init_uniform_strategy()
        self.index_max_utilities()
        if self.verbose >= Verbosity.reasoning:
            print("{} Starting utilities: {}".format(
                self.agent_name, self.utilities))
            print("{} Starting strategy: {}".format(
                self.agent_name, self.strat_dict))

    def report(self):
        if self.verbose >= Verbosity.messages:
            if self.successful:
                print("Negotiation succeeded after {} rounds!".format(
                    self.message_count))
            else:
                print("Negotiation failed after {} rounds!".format(
                    self.message_count))
        if self.reporting:
            log = Series()
            log.rename(self.uuid)
            log['runtime'] = time() - self.start_time
            log['success'] = self.successful
            log['total_message_count'] = self.message_count + self.opponent.message_count
            log['numb_of_own_constraints'] = 0
            log['numb_of_discovered_constraints'] = 0
            log['numb_of_opponent_constraints'] = 0
            log['strat'] = self.strat_name
            log['opponent_strat'] = self.opponent.strat_name
            log['utility'] = self.calc_offer_utility(self.transcript[-1].offer)
            log['opponent_utility'] = self.opponent.calc_offer_utility(self.transcript[-1].offer)
            log['total_generated_offers'] = self.total_offers_generated + self.opponent.total_offers_generated
            log['issue_count'] = len(self.issues)
            log['issue_cardinality'] = len(next(iter(self.issues)))  # issue cardinality is uniform
            log['rho_a'] = self.relative_reservation_value
            log['rho_b'] = self.opponent.relative_reservation_value
            log.to_csv(abspath(join(dirname(__file__), "logs/{}.log".format(self.uuid))), header=0)

    def receive_message(self, msg):
        if self.verbose >= Verbosity.messages:
            print("{}: received message: {}".format(self.agent_name, msg))
        self.record_message(msg)

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
            self.issue_weights = {issue: 1/len(self.issues) for issue in self.issues.keys()}
        else:
            if not self.is_dist(weights) and len(weights) != len(self.issues.keys()):
                raise ValueError("{} Tried to set non dist weights: {}".format(self.agent_name, weights))
            issue_iter = iter(self.issues.keys())
            for i in range(len(weights)):
                self.issue_weights[next(issue_iter)] = weights[i]

        self.init_uniform_strategy()
        # TODO must find a way to avoid having to clear the KB every time a new issue is raised
        self.set_kb([])

    def is_strat_valid(self, strat):
        # strat should have something on all issues
        for issue in strat.keys():
            # Facts should be a distribution
            if not isclose(sum(strat[issue].values()), 1):
                return False
            for value, prob in strat[issue].items():
                if not 0 <= prob <= 1:
                    return False
                if value not in self.issues[issue]:
                    return False
        return True

    def is_offer_valid(self, offer):
        for issue in offer.keys():
            if not isclose(sum(offer[issue].values()), 1):
                if self.verbose >= Verbosity.debug:
                    print("Failed sum in issue {}!".format(issue))
                return False
            for value, prob in offer[issue].items():
                if not (isclose(prob, 1) or isclose(prob, 0)):
                    if self.verbose >= Verbosity.debug:
                        print("Failed value in issue {}!".format(issue))
                    return False
                if value not in self.issues[issue]:
                    if self.verbose >= Verbosity.debug:
                        print("Failed, unkown fact in issue {}!".format(issue))
                    return False
        return True

    def set_strat(self, strat):
        self.generate_decision_facts()
        if not self.is_strat_valid(strat):
            raise ValueError("Invalid strat: {}".format(strat))

        self.strat_dict = strat

    def set_utilities(self, utilities, relative_reservation_value=None):
        self.utilities = utilities
        if self.verbose >= Verbosity.debug:
            print("{}'s utilities: {}".format(self.agent_name, self.utilities))

        if relative_reservation_value and self.issues:
            self.index_max_utilities()
            self.relative_reservation_value = relative_reservation_value
            self.absolute_reservation_value = relative_reservation_value * self.get_max_utility()

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

    def init_uniform_strategy(self):
        for issue in self.issues.keys():
            if issue not in self.strat_dict.keys():
                self.strat_dict[issue] = {}
            for val in self.issues[issue]:
                self.strat_dict[issue][str(val)] = 1 / len(self.issues[issue])

    def compile_problog_model(self, offer):
        decision_facts_string = self.format_problog_strat(offer)
        query_string = self.format_query_string()
        kb_string = "\n".join(self.kb) + "\n"
        return decision_facts_string + kb_string + query_string

    @staticmethod
    def issue_value_tuple_from_atom(atom):
        s = search("(.*)_(.*)", atom)
        if not s:
            raise ValueError(
                "Could not parse atom: {atom}".format(atom=atom))

        issue, value = s.group(1, 2)
        # atoms containing floats have an extra ' which we need to remove
        issue = sub("'", "", issue)
        value = sub("'", "", value)
        return issue, value

    @staticmethod
    def atom_from_issue_value(issue, value):
        if "." in str(value):
            return "'{issue}_{val}'".format(issue=issue, val=value)
        else:
            return"{issue}_{val}".format(issue=issue, val=value)

    @staticmethod
    def is_dist(weights):
        if not isclose(sum(weights), 1):
            return False
        if not all(map(lambda x: 0 <= x <= 1, weights)):
            return False

        return True

    # @staticmethod
    # def snake_case_to_camel_case(string):
    #     return ''.join(x.capitalize() or '_' for x in string.split('_'))

    def calc_offer_utility(self, offer):
        if not offer:
            return self.non_agreement_cost
        if not self.is_offer_valid(offer):
            raise ValueError("Invalid offer received")

        score = 0

        if self.utility_computation_method == "problog":
            problog_model = self.compile_problog_model(offer)
            if self.verbose >= Verbosity.debug and self.linear_additive_utility:
                print("calculating offer with problog and issue weights")
            elif self.verbose >= Verbosity.debug and not self.linear_additive_utility:
                print("calculating offer with problog and no issue weights")
            # probability_of_facts = self.file_based_problog(problog_model)
            probability_of_facts = get_evaluatable("sdd").create_from(PrologString(problog_model)).evaluate().copy()
            probability_of_facts = {str(atom): prob for atom, prob in probability_of_facts.items()}
            for fact, reward in self.utilities.items():
                if fact in probability_of_facts.keys():
                    if self.linear_additive_utility:
                        issue, _ = self.issue_value_tuple_from_atom(fact)
                        score += reward * probability_of_facts[fact] * self.issue_weights[issue]
                        if self.verbose >= Verbosity.debug:
                            print("{} is worth {} with weight {} contributing a total of {}.".format(fact,reward * probability_of_facts[fact],self.issue_weights[issue],reward * probability_of_facts[fact]*self.issue_weights[issue]))
                    else:
                        score += reward * probability_of_facts[fact]
                        if self.verbose >= Verbosity.debug:
                            print("{} is contributing {} to the score of this offer.".format(fact,reward * probability_of_facts[fact]))
            if self.verbose >= Verbosity.reasoning:
                print("{}: offer is worth {}".format(self.agent_name, score))
            # self.utilityCache[frozenOffer] = score
            gc.collect()
            return score

        elif self.utility_computation_method == "python":
            if self.verbose >= Verbosity.debug:
                print("calculating offer with python")
            return self.calc_lookup_utility(offer)

    def calc_lookup_utility(self, offer):
        score = 0
        for issue in offer.keys():
            for value in offer[issue].keys():
                atom = self.atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    if self.verbose >= Verbosity.debug:
                        print("Adding utility: {} for atom {}".format(self.utilities[atom], atom))
                        if self.verbose >= Verbosity.debug:
                            print("{} is worth {} with weight {} contributing a total of {}.".format(atom,
                                                                                                     self.utilities[atom] * offer[issue][value],
                                                                                                     self.issue_weights[issue],
                                                                                                     self.utilities[atom] * offer[issue][value] * self.issue_weights[issue]))

                    score += self.utilities[atom] * offer[issue][value] * self.issue_weights[issue]

        return score

    def calc_strat_utility(self, strat):
        if not self.is_strat_valid(strat):
            raise ValueError("Invalid strat detected: {}".format(strat))
        problog_model = self.compile_problog_model(strat)
        # fact_probabilities = self.file_based_problog(problog_model)

        probability_of_facts = get_evaluatable("sdd").create_from(PrologString(problog_model)).evaluate().copy()
        probability_of_facts = {str(atom): prob for atom, prob in probability_of_facts.items()}

        score = 0
        for fact, reward in self.utilities.items():
            issue, _ = self.issue_value_tuple_from_atom(fact)
            score += reward * probability_of_facts[fact] * self.issue_weights[issue]

        return score

    def index_max_utilities(self):

        if self.verbose >= Verbosity.debug:
            print("{} is indexing max utilities".format(self.agent_name))

        self.max_utility_by_issue = {}
        for issue in self.issues.keys():
            max_issue_util = -(2**31)
            for value in self.issues[issue]:
                atom = self.atom_from_issue_value(issue, value)
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

    def get_max_utility(self):
        if self.max_utility_by_issue:
            return(sum(self.max_utility_by_issue.values()))
        else:
            return 0

    @staticmethod
    def file_based_problog(model):
        # using the python implementation of problog causes memory leaks
        # so we use the commandline interface separately to avoid this as a temp fix
        model_path = abspath(join(dirname(__file__), 'models/temp_model_{}.pl'.format(getpid())))
        with open(model_path, "w") as temp_file:
            temp_file.write(model)

        process = sp.Popen(["problog", model_path], stdout=sp.PIPE)
        output, error = process.communicate()

        ans = {}

        for string in output.decode("ascii").split("\n"):
            if string:
                key, prob = string.strip().split(":\t")
                ans[key] = float(prob)

        remove(model_path)

        return ans

    def accepts(self, offer):
        if self.verbose >= Verbosity.reasoning:
            print("{}: considering \n{}".format(
                self.agent_name, self.format_offer(offer)))

        if not offer:
            return False

        if type(offer) == Message:
            util = self.calc_offer_utility(offer.offer)
        else:
            util = self.calc_offer_utility(offer)

        if self.verbose >= Verbosity.reasoning:
            if self.verbose >= Verbosity.debug:
                print("absolute reservation value: {}\n offer utility: {}".format(self.absolute_reservation_value,util))
            if util >= self.absolute_reservation_value:
                print("{}: offer is acceptable\n".format(self.agent_name))
            else:
                print("{}: offer is not acceptable\n".format(self.agent_name))
        return util >= self.absolute_reservation_value

    @staticmethod
    def format_problog_strat(strat_dict):
        return_string = ""
        for issue in strat_dict.keys():
            atom_list = []
            for value in strat_dict[issue].keys():
                atom = RandomNegotiationAgent.atom_from_issue_value(issue, value)
                atom_list.append("{prob}::{atom}".format(prob=strat_dict[issue][value], atom=atom))

            return_string += ";".join(atom_list) + ".\n"

        return return_string

    def add_utilities(self, new_utils):
        self.utilities = {
            **self.utilities,
            **new_utils
        }

    def format_query_string(self):
        query_string = ""

        for utilFact in self.utilities.keys():
            # we shouldn't ask problog for facts that we currently have no rules for
            # like we might not have after new issues are set so we'll skip those
            if any([utilFact in rule for rule in self.kb]) or any(
                    [utilFact in atom for atom in self.atom_dict_from_nested_dict(self.strat_dict).keys()]):
                query_string += "query({utilFact}).\n".format(utilFact=utilFact)

        return query_string

    def generate_offer_message(self):
        offer = self.generate_offer()
        if not offer:
            termination_message = Message(self.agent_name, self.opponent.agent_name, "terminate", None)
            self.record_message(termination_message)
            return termination_message
        # Generate offer can return a termination message
        # if no acceptable offer can be found so we would check for that
        if type(offer) == dict:
            return Message(self.agent_name, self.opponent.agent_name, kind="offer", offer=offer)
        elif type(offer) == Message:
            return offer

    def generate_offer(self):
        listed_strat = {}
        for issue in self.strat_dict.keys():
            listed_strat[issue] = list(map(list, zip(*self.strat_dict[issue].items())))

        for _ in range(self.max_generation_tries):
            self.total_offers_generated += 1
            offer = {}
            for issue in self.strat_dict.keys():
                # convert from dict to two lists so we can use np.random.choice
                chosen_value = str(choice(listed_strat[issue][0], 1, p=listed_strat[issue][1])[0])
                offer[issue] = {key: 0 for key in self.strat_dict[issue].keys()}
                offer[issue][chosen_value] = 1
            if self.accepts(offer):
                return offer

        # we can't find a solution we can accept so just give up
        return None

    def nested_dict_from_atom_dict(self, atom_dict):
        nested_dict = {}
        for atom in atom_dict.keys():
            # following pater is guaranteed to work since no _ in the names are allowed
            issue, value = self.issue_value_tuple_from_atom(atom)
            if issue not in nested_dict.keys():
                nested_dict[issue] = {}

            nested_dict[issue][value] = float(atom_dict[atom])

        for issue in self.strat_dict.keys():
            for value in self.strat_dict[issue].keys():
                if value not in nested_dict[issue].keys():
                    nested_dict[issue][value] = 0.0

        return nested_dict

    @staticmethod
    def atom_dict_from_nested_dict(nested_dict):
        atom_dict = {}
        for issue in nested_dict.keys():
            for value in nested_dict[issue].keys():
                atom = RandomNegotiationAgent.atom_from_issue_value(issue,value)
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
