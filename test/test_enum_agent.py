import unittest as ut
from math import pi
from rand_agent import RandAgent, Verbosity
from enum_agent import EnumAgent
from utils import neg_scenario_from_util_matrices
from message import Message
from uuid import uuid4
import numpy as np


class TestEnumAgent(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            np.arange(9).reshape((3, 3))**2, np.arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0.75
        self.arbitrary_non_agreement_cost = -1000

        self.agent = EnumAgent("agent",
                               self.utilities,
                               [],
                               self.arbitrary_reservation_value,
                               self.arbitrary_non_agreement_cost,
                               self.issues)
        self.opponent = EnumAgent("opponent",
                                  self.utilities,
                                  [],
                                  self.arbitrary_reservation_value,
                                  self.arbitrary_non_agreement_cost,
                                  self.issues)
        self.agent.setup_negotiation(self.issues)
        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

    def tearDown(self):
        pass

    def test_generates_best_offer_first_time(self):
        best_offer = self.agent.nested_dict_from_atom_dict({'issue0_1': 0, 'issue0_2': 1,
                                                            'issue1_0': 0, 'issue1_1': 0, 'issue1_2': 1,
                                                            'issue2_0': 0, 'issue2_1': 0, 'issue2_2': 1})
        self.assertTrue(self.agent.is_offer_valid(best_offer))
        self.assertEqual(best_offer, self.agent.generate_offer())

    def test_generates_next_best_offer_second_time(self):
        next_best_offer = self.agent.nested_dict_from_atom_dict({'issue0_1': 1.0, 'issue0_2': 0.0,
                                                                 'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                                 'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0})
        self.assertTrue(self.agent.is_offer_valid(next_best_offer))
        _ = self.agent.generate_offer()
        second = self.agent.generate_offer()
        self.assertEqual(next_best_offer, second, second)

    def test_generates_next_next_best_offer_third_time(self):
        next_best_offer = self.agent.nested_dict_from_atom_dict({'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
                                                                 'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                                 'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0})
        self.assertTrue(self.agent.is_offer_valid(next_best_offer))
        _ = self.agent.generate_offer()
        _ = self.agent.generate_offer()
        thrid = self.agent.generate_offer()
        self.assertEqual(next_best_offer, thrid, thrid)

    def test_terminates_after_options_become_unacceptable(self):
        self.agent = self.agent = EnumAgent("agent",
                                            self.utilities,
                                            [],
                                            1,
                                            self.arbitrary_non_agreement_cost,
                                            self.issues)
        self.agent.opponent = self.opponent
        self.agent.generate_offer()
        next_message = self.agent.generate_next_message_from_transcript()
        self.assertTrue(next_message.is_termination(), next_message)

    def test_boundary_conditions_are_correctly_handled_when_generating_offers(self):
        # found during simulation
        utils_a = {'issue0_0': -1000, 'issue0_1': -1000, 'issue0_2': 32, 'issue1_0': -1000,
                   'issue1_1': -1000, 'issue1_2': 88, 'issue2_0': -1000, 'issue2_1': -1000, 'issue2_2': -1000}
        utils_b = {'issue0_0': -1000, 'issue0_1': -1000, 'issue0_2': -1000, 'issue1_0': -1000,
                   'issue1_1': 48, 'issue1_2': -1000, 'issue2_0': 43, 'issue2_1': -1000, 'issue2_2': -1000}
        issues = {'issue0': [0, 1, 2], 'issue1': [
            0, 1, 2], 'issue2': [0, 1, 2]}
        rho_a = 1.0
        rho_b = 1.0

        non_agreement_cost = -(2 ** 24)  # just a really big number

        agent_a = EnumAgent("agent_a", utils_a, [], rho_a, non_agreement_cost,
                            issues)
        agent_b = EnumAgent("agent_b", utils_b, [], rho_b, non_agreement_cost,
                            issues)

        self.assertFalse(agent_a.negotiate(agent_b))
