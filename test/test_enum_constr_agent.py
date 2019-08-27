import unittest as ut
from math import pi
from rand_agent import RandAgent, Verbosity
from enum_agent import EnumAgent
from constr_enum_agent import EnumConstrAgent
from atomic_constraint import AtomicConstraint
from utils import neg_scenario_from_util_matrices
from message import Message
from uuid import uuid4
import numpy as np


class TestEnumConstrAgent(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.agent_name = "agent"
        self.opponent_name = "opponent"
        N = 3
        M = 3
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            np.arange(N*M).reshape((N, M))**2, np.arange(N*M).reshape((N, M))**2)
        self.arbitrary_reservation_value = 0.5
        self.arbitrary_non_agreement_cost = -(
            np.arange(N*M) ** 2).max() * 100 * N
        # self.constr_val = -(np.arange(N*M) ** 2).max() * 10 * N

        self.agent = EnumConstrAgent(self.agent_name,
                                     self.utilities,
                                     [],
                                     self.arbitrary_reservation_value,
                                     self.arbitrary_non_agreement_cost,
                                     self.issues)
        self.opponent = EnumConstrAgent(self.opponent_name,
                                        self.utilities,
                                        [],
                                        self.arbitrary_reservation_value,
                                        self.arbitrary_non_agreement_cost,
                                        self.issues)
        self.agent.setup_negotiation(self.issues)
        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent
        self.best_offer = self.agent.nested_dict_from_atom_dict({'issue0_1': 0, 'issue0_2': 1,
                                                                 'issue1_0': 0, 'issue1_1': 0, 'issue1_2': 1,
                                                                 'issue2_0': 0, 'issue2_1': 0, 'issue2_2': 1})
        self.next_best_offer = self.agent.nested_dict_from_atom_dict({'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
                                                                      'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                                      'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0})
        self.best_opponent_offer = self.agent.nested_dict_from_atom_dict({'issue0_0': 1, 'issue0_1': 0, 'issue0_2': 0,
                                                                          'issue1_0': 1, 'issue1_1': 0, 'issue1_2': 0,
                                                                          'issue2_0': 1, 'issue2_1': 0, 'issue2_2': 0})
        self.next_best_opponent_offer = self.agent.nested_dict_from_atom_dict({'issue0_0': 1, 'issue0_1': 0, 'issue0_2': 0,
                                                                               'issue1_0': 1, 'issue1_1': 0, 'issue1_2': 0,
                                                                               'issue2_0': 0, 'issue2_1': 1, 'issue2_2': 0})
        self.own_constraint = AtomicConstraint("issue0", "0")
        self.opponent_constraint = AtomicConstraint("issue2", "2")
        self.acceptance_message = Message(self.agent.agent_name,
                                          self.opponent.agent_name,
                                          "accept",
                                          self.best_offer)
        self.termination_message = Message(self.agent.agent_name,
                                           self.opponent.agent_name,
                                           "terminate",
                                           None)
        self.constraint_message = Message(self.agent.agent_name, self.opponent.agent_name,
                                          "offer",
                                          self.best_offer,
                                          self.opponent_constraint)
        self.offer_message = Message(self.agent.agent_name,
                                     self.opponent.agent_name,
                                     "offer",
                                     self.best_offer)

    def tearDown(self):
        pass

    def test_generates_best_offer_first_time(self):
        self.assertTrue(self.agent.is_offer_valid(self.best_offer))
        self.assertEqual(self.best_offer, self.agent.generate_offer())

    def test_generates_next_best_offer_second_time(self):
        self.assertTrue(self.agent.is_offer_valid(self.next_best_offer))
        _ = self.agent.generate_offer()
        second = self.agent.generate_offer()
        self.assertEqual(self.next_best_offer, second, second)

    def test_terminates_after_options_become_unacceptable(self):
        self.agent = EnumAgent(self.agent_name,
                               self.utilities,
                               [],
                               1,
                               self.arbitrary_non_agreement_cost,
                               self.issues)
        self.agent.opponent = self.opponent
        self.agent.generate_offer()
        next_message = self.agent.generate_next_message_from_transcript()
        self.assertTrue(next_message.is_termination(), next_message)

    def test_receiving_own_constraint_saves_constraint(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.assertTrue(
            self.own_constraint in self.agent.own_constraints)

    def test_receiving_opponent_constraint_saves_constraint(self):
        self.agent.add_opponent_constraint(self.opponent_constraint)
        self.assertTrue(
            self.opponent_constraint in self.agent.opponent_constraints)

    def test_setting_own_constraint_adds_low_utility(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.assertTrue(("issue0_0", self.arbitrary_non_agreement_cost)
                        in self.agent.utilities.items(), self.agent.utilities)

    def test_setting_opponent_constraint_adds_low_utility(self):
        self.agent.add_opponent_constraint(self.opponent_constraint)
        self.assertTrue(("issue2_2", self.arbitrary_non_agreement_cost)
                        in self.agent.utilities.items())

    def test_responds_to_violating_offer_with_constraint(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.agent.receive_message(Message(self.opponent.agent_name,
                                           self.agent.agent_name,
                                           "offer",
                                           self.best_opponent_offer))

        response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name,
                                 self.opponent.agent_name,
                                 "offer",
                                 self.best_offer,
                                 self.own_constraint),
                         response)

    def test_testing_constraint_satisfaction_doesnt_affect_stored_constraints(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.agent.add_opponent_constraint(self.opponent_constraint)
        self.agent.satisfies_all_constraints(
            self.next_best_offer)

        self.assertEqual(self.agent.get_all_constraints(),
                         {self.own_constraint,
                             self.opponent_constraint})

    def test_easy_negotiations_with_constraints_ends_successfully(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_does_not_accept_violating_offer(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.assertFalse(self.agent.accepts(self.best_opponent_offer))

    def test_worth_of_violating_offer_is_non_agreement_cost(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.assertEqual(self.agent.calc_offer_utility(
            self.best_opponent_offer), self.arbitrary_non_agreement_cost)

    def test_ends_negotiation_after_finding_non_compatible_constraints(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.agent.add_own_constraint(AtomicConstraint("issue0", "1"))
        self.agent.receive_message(
            Message(self.opponent.agent_name,
                    self.agent.agent_name,
                    "offer",
                    self.best_opponent_offer,
                    constraint=AtomicConstraint("issue0", "2")))
        agent_response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name,
                                 self.opponent.agent_name, "terminate", None), agent_response)

    def test_receiving_offer_with_constraint_records_constraint(self):
        self.agent.receive_message(self.constraint_message)
        self.assertTrue(
            self.constraint_message.constraint in self.agent.opponent_constraints)

    def test_adds_constraints_even_if_utilities_are_positvie(self):
        self.generic_issues = {
            "boolean": [True, False]
        }
        self.arbitrary_agent_utilities = {
            "boolean_True": 1000
        }
        self.agent = EnumConstrAgent(self.agent_name,
                                     self.arbitrary_agent_utilities,
                                     [],
                                     self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                     self.generic_issues, auto_constraints=True)

        self.assertTrue(AtomicConstraint("boolean", "False")
                        in self.agent.own_constraints)

    def test_negotiation_with_incompatable_constraints_fails(self):
        self.generic_issues = {
            "boolean": [True, False]
        }
        self.arbitrary_agent_utilities = {
            "boolean_True": 1000
        }
        self.arbitrary_opponent_utilities = {
            "boolean_False": 1000
        }
        self.agent = EnumConstrAgent(self.agent_name,
                                     self.arbitrary_agent_utilities,
                                     [],
                                     self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                     self.generic_issues)

        self.opponent = EnumConstrAgent(self.opponent_name,
                                        self.arbitrary_opponent_utilities, [],
                                        self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                        self.generic_issues)

        self.agent.setup_negotiation(self.generic_issues)
        self.agent.negotiate(self.opponent)
        self.assertFalse(self.agent.successful or self.opponent.successful)
        self.assertFalse(self.agent.constraints_satisfiable)

    def test_wont_generate_offers_when_incompatable_constraints_are_present(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.agent.add_own_constraint(AtomicConstraint("issue0", "1"))
        self.agent.add_opponent_constraint(AtomicConstraint("issue0", "2"))
        with self.assertRaises(RuntimeError):
            self.agent.generate_offer()

    def test_refuses_negotiation_if_constraints_are_incompatable(self):
        self.agent.add_own_constraint(self.own_constraint)
        self.agent.add_own_constraint(AtomicConstraint("issue0", "1"))
        self.agent.add_opponent_constraint(AtomicConstraint("issue0", "2"))
        self.assertFalse(self.agent.receive_negotiation_request(
            self.opponent, self.issues))

    def test_getting_utility_below_threshold_creates_constraint(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"issue0_0": self.arbitrary_non_agreement_cost}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("issue0", "0")
                        in self.agent.own_constraints, self.agent.own_constraints)

    def test_all_values_can_get_constrained(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"issue0_{i}".format(
            i=i): self.arbitrary_non_agreement_cost for i in range(len(self.agent.issues['issue0']))}
        print(low_util_dict)
        self.agent.add_utilities(low_util_dict)
        self.assertEqual(
            len(self.agent.get_unconstrained_values_by_issue("issue0")), 0)

    def test_all_values_get_constrained_terminates_negotiation(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"issue0_{i}".format(
            i=i): self.arbitrary_non_agreement_cost for i in range(len(self.agent.issues['issue0']))}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(
            self.agent.generate_next_message_from_transcript().is_termination())

    def test_multiple_issues_can_get_constrained(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"issue0_0": self.arbitrary_non_agreement_cost,
                         "issue1_2": self.arbitrary_non_agreement_cost}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("issue0", "0"), AtomicConstraint(
            "issue1", "2")}.issubset(self.agent.own_constraints))

    def test_doesnt_create_unessecary_constraints_when_setting_multiple_utils(self):
        temp_issues = {
            "boolean1": [True, False],
            "boolean2": [True, False]
        }
        temp_utils = {
            "boolean1_True": self.arbitrary_non_agreement_cost,
            "boolean1_False": 0,
            "boolean2_True": 1000,
            "boolean2_False": 1000

        }
        self.agent = EnumConstrAgent(self.agent_name,
                                     temp_utils, [], 0.1, -(2**31), temp_issues)
        self.agent.add_utilities(temp_utils)
        self.assertEqual(len(self.agent.own_constraints), 1)

    def test_constraint_doesnt_trigger_if_offer_doesnt_assign_it(self):
        temp_issues = {
            "integer1": range(3),
            "integer2": range(3)
        }
        temp_utils = {
            "integer1_0": self.arbitrary_non_agreement_cost,
            "integer1_1": 10,
            "integer1_2": 0,
            "integer2_0": 0,
            "integer2_1": 10,
            "integer2_2": 10
        }
        self.agent = EnumConstrAgent(self.agent_name,
                                     temp_utils, [], 0.1, -(2**31), temp_issues)
        self.agent.add_utilities(temp_utils)
        self.agent.opponent = self.opponent
        offer = {
            "integer1": {"0": 0, "1": 0, "2": 1},
            "integer2": {"0": 1, "1": 0, "2": 0}
        }
        offer_msg = Message(self.opponent.agent_name,
                            self.agent.agent_name, "offer", offer)
        self.agent.receive_message(offer_msg)
        response = self.agent.generate_next_message_from_transcript()
        self.assertFalse(response.constraint)

    def test_impossible_negotiation_ends_unsuccesfull_and_does_not_crash(self):
        # case was found during simulations
        utils_a = {'issue0_0': 36,
                   'issue0_1': -1000,
                   'issue0_2': 74,
                   'issue1_0': -1000,
                   'issue1_1': 90,
                   'issue1_2': 48,
                   'issue2_0': -1000,
                   'issue2_1': 33,
                   'issue2_2': -1000}

        utils_b = {'issue0_0': 10,
                   'issue0_1': 58,
                   'issue0_2': -1000,
                   'issue1_0': -1000,
                   'issue1_1': -1000,
                   'issue1_2': -1000,
                   'issue2_0': 97,
                   'issue2_1': 11,
                   'issue2_2': 61}

        issues = {'issue0': [0, 1, 2], 'issue1': [
            0, 1, 2], 'issue2': [0, 1, 2]}
        non_agreement_cost = -(2 ** 24)
        self.agent = EnumConstrAgent("agent", utils_a, [], 0.5, non_agreement_cost,
                                     issues)
        self.opponent = EnumConstrAgent("opponent", utils_b, [], 0.5, non_agreement_cost,
                                        issues)

        self.agent.setup_negotiation(issues)
        self.agent.negotiate(self.opponent)
        self.assertFalse(self.agent.successful)

    def test_boundary_conditions_are_correctly_handled_when_generating_offers(self):
        # found during simulation
        utils_a = {'issue0_0': 62, 'issue0_1': 36, 'issue0_2': 89, 'issue1_0': 40,
                   'issue1_1': 48, 'issue1_2': 75, 'issue2_0': 22, 'issue2_1': -1000, 'issue2_2': 72}
        utils_b = {'issue0_0': 74, 'issue0_1': 77, 'issue0_2': -1000, 'issue1_0': 77,
                   'issue1_1': 60, 'issue1_2': 78, 'issue2_0': 26, 'issue2_1': 97, 'issue2_2': 38}
        issues = {'issue0': [0, 1, 2], 'issue1': [
            0, 1, 2], 'issue2': [0, 1, 2]}
        rho_a = 0.0
        rho_b = 0.0

        non_agreement_cost = -(2 ** 24)  # just a really big number

        agent_a = EnumConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                  issues)
        agent_b = EnumConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                  issues)

        self.assertTrue(agent_a.negotiate(agent_b))

    def test_terminates_nicely_when_cant_generate_offers(self):
        utils_a = {'issue0_0': -1000, 'issue0_1': -1000, 'issue0_2': 32, 'issue1_0': -1000,
                   'issue1_1': -1000, 'issue1_2': -1000, 'issue2_0': -1000, 'issue2_1': -1000, 'issue2_2': -1000}
        utils_b = {'issue0_0': -1000, 'issue0_1': -1000, 'issue0_2': -1000, 'issue1_0': -1000,
                   'issue1_1': -1000, 'issue1_2': -1000, 'issue2_0': 43, 'issue2_1': -1000, 'issue2_2': -1000}
        issues = {'issue0': [0, 1, 2], 'issue1': [
            0, 1, 2], 'issue2': [0, 1, 2]}
        rho_a = 1.0
        rho_b = 1.0

        non_agreement_cost = -(2 ** 24)  # just a really big number

        agent_a = EnumConstrAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                                  issues)
        agent_b = EnumConstrAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                                  issues)

        self.assertFalse(agent_a.setup_negotiation(issues))
