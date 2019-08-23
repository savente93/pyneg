import unittest as ut
from math import pi
from rand_agent import RandAgent, Verbosity
from consession_agent import ConsessionAgent
from utils import neg_scenario_from_util_matrices
from message import Message
from uuid import uuid4
import numpy as np


class TestConsessionAgent(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.agent_name = "agent"
        self.opponent_name = "opponent"
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            np.arange(9).reshape((3, 3))**2, np.arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0.75
        self.arbitrary_non_agreement_cost = -1000

        self.agent = ConsessionAgent(self.agent_name,
                                     self.utilities,
                                     [],
                                     self.arbitrary_reservation_value,
                                     self.arbitrary_non_agreement_cost,
                                     self.issues)

        self.opponent = ConsessionAgent(self.opponent_name,
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
        next_best_offer = self.agent.nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        )
        self.assertTrue(self.agent.is_offer_valid(next_best_offer))
        _ = self.agent.generate_offer()
        _ = self.agent.generate_offer()
        thrid = self.agent.generate_offer()
        self.assertEqual(next_best_offer, thrid, thrid)

    def test_terminates_after_options_become_unacceptable(self):
        self.agent = ConsessionAgent(self.agent,
                                     self.utilities,
                                     [],
                                     1,
                                     self.arbitrary_non_agreement_cost,
                                     self.issues)
        self.agent.opponent = self.opponent
        self.agent.generate_offer()
        next_message = self.agent.generate_next_message_from_transcript()
        self.assertTrue(next_message.is_termination(), next_message)
