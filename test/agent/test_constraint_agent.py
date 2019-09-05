from unittest import TestCase

from pyneg.agent import AgentFactory
from pyneg.comms import Offer, AtomicConstraint, Message
from pyneg.types import MessageType


class TestConstraintAgent(TestCase):

    def setUp(self):
        self.agent_name = "A"
        self.opponent_name = "B"
        self.neg_space = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }
        self.utilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
            "'float_0.1'": 1
        }

        self.kb = [
            "boolean_True :- integer_2, 'float_0.1'."
        ]
        self.reservation_value = 0
        self.non_agreement_cost = -1000

        # should have a utility of 100
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["3"] = 1
        self.nested_test_offer['float']["0.6"] = 1
        self.nested_test_offer = Offer(self.nested_test_offer)

        self.optimal_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.optimal_offer["integer"]["9"] = 1.0
        self.optimal_offer['float']["0.1"] = 1.0
        self.optimal_offer = Offer(self.optimal_offer)

        self.violating_offer = Offer({
            "issue0": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue1": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue2": {"0": 0.0, "1": 0.0, "2": 1.0}
        })
        self.violating_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.violating_offer["integer"]["9"] = 1.0
        self.violating_offer['float']["0.1"] = 1.0
        self.violating_offer = Offer(self.violating_offer)

        self.integer_constraint = AtomicConstraint("integer", "9")
        self.boolean_constraint = AtomicConstraint("boolean", "True")

        self.acceptance_message = Message(
            self.agent_name, self.opponent_name, MessageType.accept, self.nested_test_offer)
        self.termination_message = Message(
            self.agent_name, self.opponent_name, MessageType.terminate, None)
        self.offer_message = Message(
            self.agent_name, self.opponent_name, MessageType.offer, self.nested_test_offer)
        self.constraint_message = Message(
            self.agent_name, self.opponent_name, MessageType.offer, self.nested_test_offer, self.boolean_constraint)

        self.uniform_weights = {
            issue: 1 / len(values) for issue, values in self.neg_space.items()}

        self.agent = AgentFactory.make_constrained_linear_consession_agent(
            "agent", self.neg_space, self.utilities, self.reservation_value, self.non_agreement_cost,
            self.uniform_weights, None, 20)
        self.opponent = AgentFactory.make_constrained_linear_consession_agent(
            "opponent", self.neg_space, self.utilities, self.reservation_value, self.non_agreement_cost,
            self.uniform_weights, None, 20)

    def test_counts_messages_correctly_in_successful_negotiation(self):
        self.agent.negotiate(self.opponent)
        # one offer and one acceptance message
        self.assertEqual(len(self.agent.transcript), 2)

    def test_counts_messages_correctly_in_unsuccessful_negotiation(self):
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
        self.assertEqual(len(self.agent.transcript), 2)

    def test_responds_to_violating_offer_with_constraint(self):
        self.agent.add_constraint(self.integer_constraint)

        self.agent.receive_message(Message(self.opponent_name,
                                           self.agent_name,
                                           MessageType.offer,
                                           self.violating_offer))

        response = self.agent.generate_next_message()
        self.assertEqual(response.constraint,
                         AtomicConstraint("boolean", "False"))

    def test_records_constraint_if_received(self):
        self.opponent.add_own_constraint(AtomicConstraint("boolean", "True"))
        self.opponent.receive_message(self.constraint_message)
        self.agent.generate_next_message()

        self.assertTrue(AtomicConstraint("boolean", "True")
                        in self.agent.opponent_constraints)

    def test_generates_constraint_if_offer_violates_it(self):
        self.opponent.add_constraint(AtomicConstraint("boolean", "True"))
        self.opponent.receive_message(self.violating_offer)
        opponent_response = self.opponent.generate_next_message()

        self.assertTrue(
            opponent_response.constraint == AtomicConstraint("boolean", "True"))

    def test_easy_negotiations_with_constraints_ends_successfully(self):
        self.agent.add_constraint(self.boolean_constraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_receiving_offer_with_constraint_records_constraint(self):
        self.agent.receive_message(self.constraint_message)
        self.assertTrue(
            self.constraint_message.constraint in self.agent.constraints)

    def test_after_negotiation_both_agents_have_same_transcript(self):
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent.transcript, self.opponent.transcript)

    def test_sending_message_increments_message_count(self):
        self.agent.send_message(self.opponent, Message(
            self.opponent_name, self.agent_name, MessageType.empty, None))
        self.assertEqual(len(self.agent.transcript), 1)

    def test_easy_negotiation_ends_successfully(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_utils = {"first_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_constrained_linear_consession_agent(
            "agent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost, temp_uniform_weights,
            None, 20)
        self.opponent = AgentFactory.make_constrained_linear_consession_agent(
            "opponent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)

        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.successful and not self.agent.negotiation_active)

    def test_easy_negotiation_ends_with_acceptance_message(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_utils = {"first_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_constrained_linear_consession_agent(
            "agent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost, temp_uniform_weights,
            None, 20)
        self.opponent = AgentFactory.make_constrained_linear_consession_agent(
            "opponent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.transcript[-1].is_acceptance() and self.opponent.transcript[-1].is_acceptance())

    def test_slightly_harder_negotiation_ends_successfully(self):
        temp_neg_space = {"first": ["True", "False"],
                          "second": ["True", "False"]}
        temp_agent_utils = {"first_True": 10000}
        temp_opponent_utils = {"second_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_constrained_linear_consession_agent(
            "agent", temp_neg_space, temp_agent_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)
        self.opponent = AgentFactory.make_constrained_linear_consession_agent(
            "opponent", temp_neg_space, temp_opponent_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)
        self.agent.negotiate(self.opponent)

        self.assertTrue(
            self.agent.successful and not self.agent.negotiation_active and self.opponent.successful and not self.opponent.negotiation_active)

    def test_impossible_negotiation_ends_unsuccessfully(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_agent_utils = {"first_True": -10000, "first_False": 10000}
        temp_opponent_utils = {"first_True": 10000, "first_False": -10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_constrained_linear_consession_agent(
            "agent", temp_neg_space, temp_agent_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)
        self.opponent = AgentFactory.make_constrained_linear_consession_agent(
            "opponent", temp_neg_space, temp_opponent_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights, None, 20)
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            not self.agent.successful and not self.agent.negotiation_active and not self.opponent.successful and not self.opponent.negotiation_active)

    def test_receive_valid_negotiation_request(self):
        self.assertTrue(self.opponent.receive_negotiation_request(
            self.agent, self.neg_space))

    def test_receive_acceptation_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.acceptance_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(
            self.agent.negotiation_active or self.opponent.negotiation_active)

    def test_receive_acceptation_message_negotiation_was_successful(self):
        self.agent.receive_message(self.acceptance_message)
        self.agent.generate_next()
        self.assertTrue(self.agent.successful)

    def test_receive_termination_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.termination_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(self.agent.negotiation_active)

    def test_receive_termination_message_negotiation_was_unsuccessful(self):
        self.agent.receive_message(self.termination_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(self.agent.successful)
