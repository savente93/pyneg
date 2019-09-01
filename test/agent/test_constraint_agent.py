from unittest import TestCase
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict
from pyneg.engine import EnumGenerator, LinearEvaluator
from pyneg.comms import Offer
from numpy import arange


class TestAgent(TestCase):

    def setUp(self):
        raise NotImplementedError()

    def test_countsMessagesCorrectlyInSuccessfulNegotiation(self):
        self.agent.negotiate(self.opponent)
        # one offer and one acceptance message
        self.assertEqual(self.agent.message_count, 2)

    def test_countsMessagesCorrectlyInUnsuccessfulNegotiation(self):
        self.arbitrary_utilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.set_utilities(self.arbitrary_utilities)
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent.message_count, 2)


#     def test_easy_negotiations_with_constraints_ends_successfully(self):
#         self.agent.add_own_constraint(self.arbitrary_own_constraint)
#         self.assertTrue(self.agent.negotiate(self.opponent))

#     def test_receiving_offer_with_constraint_records_constraint(self):
#         self.agent.receive_message(self.constraint_message)
#         self.assertTrue(
#             self.constraint_message.constraint in self.agent.opponent_constraints)

#     def test_receiving_own_constraint_saves_constraint(self):
#         self.agent.add_own_constraint(self.arbitrary_own_constraint)
#         self.assertTrue(
#             self.arbitrary_own_constraint in self.agent.own_constraints)

#     def test_receiving_opponent_constraint_saves_constraint(self):
#         self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
#         self.assertTrue(
#             self.arbitrary_opponent_constraint in self.agent.opponent_constraints)


#     def test_responds_to_violating_offer_with_constraint(self):
#         self.arbitrary_utilities = {
#             "boolean_True": 100,
#             "'float_0.5'": pi
#         }
#         self.agent = ConstrAgent(self.agent_name,
#                                  self.arbitrary_utilities,
#                                  self.arbitrary_kb,
#                                  self.arbitrary_reservation_value,
#                                  self.arbitrary_non_agreement_cost,
#                                  self.generic_issues)

#         self.opponent = ConstrAgent(self.opponent_name,
#                                     self.arbitrary_utilities,
#                                     self.arbitrary_kb,
#                                     self.arbitrary_reservation_value,
#                                     self.arbitrary_non_agreement_cost,
#                                     self.generic_issues)
#         self.agent.setup_negotiation(self.generic_issues)
#         self.agent.opponent = self.opponent

#         # set strategy to something constant so we can predict what message it will generate
#         self.agent.strat_dict = self.nested_test_offer.copy()

#         self.agent.add_own_constraint(AtomicConstraint("boolean", "False"))
#         self.agent.receive_message(Message(self.opponent.agent_name,
#                                            self.agent.agent_name,
#                                            "offer",
#                                            self.violating_offer))

#         response = self.agent.generate_next_message_from_transcript()
#         self.assertEqual(Message(self.agent.agent_name,
#                                  self.opponent.agent_name,
#                                  "offer",
#                                  self.agent.strat_dict,
#                                  AtomicConstraint("boolean", "False")),
#                          response)
#     def test_after_negotiation_both_agents_have_same_transcript(self):
#         self.agent.negotiate(self.opponent)
#         self.assertEqual(self.agent.transcript, self.opponent.transcript)

#     def test_sending_message_increments_message_count(self):
#         self.agent.send_message(self.opponent, Message(
#             self.opponent, self.agent, "empty", None))
#         self.assertEqual(self.agent.message_count, 1)

#     def test_easy_negotiation_ends_successfully(self):
#         self.agent.set_issues({"first": ["True", "False"]})
#         self.agent.utilities = {"first_True": 10000}
#         self.opponent.utilities = {"first_True": 10000}
#         self.agent.negotiate(self.opponent)
#         self.assertTrue(
#             self.agent.successful and not self.agent.negotiation_active)

#     def test_easy_negotiation_ends_with_acceptance_message(self):
#         self.agent.set_issues({"first": ["True", "False"]})
#         self.agent.utilities = {"first_True": 10000}
#         self.opponent.utilities = {"first_True": 10000}
#         self.agent.negotiate(self.opponent)
#         self.assertTrue(self.agent.transcript[-1].is_acceptance())
#         print(len(self.agent.transcript))

#     def test_slightly_harder_negotiation_ends_successfully(self):
#         self.agent.set_issues({"first": ["True", "False"],
#                                "second": ["True", "False"]})
#         self.agent.utilities = {"first_True": 10000}
#         self.opponent.utilities = {"second_True": 10000}
#         self.agent.negotiate(self.opponent)
#         self.assertTrue(
#             self.agent.successful and not self.agent.negotiation_active)

#     def test_impossible_negotiation_ends_unsuccessfully(self):
#         self.agent.max_rounds = 10  # make sure the test goes a little faster
#         self.opponent.max_rounds = 10

#         self.agent.set_issues({"first": ["True", "False"]})
#         self.agent.add_utilities({"first_True": -10000, "first_False": 10000})
#         self.opponent.add_utilities(
#             {"first_True": 10000, "first_False": -10000})

#         self.agent.negotiate(self.opponent)
#         self.assertTrue(
#             not self.agent.successful and not self.agent.negotiation_active)

#     def test_receive_valid_negotiation_request(self):
#         self.assertTrue(self.opponent.receive_negotiation_request(
#             self.agent, self.generic_issues))

#     def test_receive_acceptation_message_ends_negotiation(self):
#         self.agent.negotiation_active = True
#         self.agent.receive_message(self.acceptance_message)
#         self.agent.generate_next_message_from_transcript()
#         self.assertFalse(self.agent.negotiation_active)

#     def test_receive_acceptation_message_negotiation_was_successful(self):
#         self.agent.receive_message(self.acceptance_message)
#         self.agent.generate_next_message_from_transcript()
#         self.assertTrue(self.agent.successful)

#     def test_receive_termination_message_ends_negotiation(self):
#         self.agent.negotiation_active = True
#         self.agent.receive_message(self.termination_message)
#         self.agent.generate_next_message_from_transcript()
#         self.assertFalse(self.agent.negotiation_active)

#     def test_receive_termination_message_negotiation_was_unsuccessful(self):
#         self.agent.receive_message(self.termination_message)
#         self.agent.generate_next_message_from_transcript()
#         self.assertFalse(self.agent.successful)
