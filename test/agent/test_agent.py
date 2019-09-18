from unittest import TestCase

from pyneg.agent import AgentFactory
from pyneg.comms import Offer, Message
from pyneg.types import MessageType


class TestAgent(TestCase):

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

        self.acceptance_message = Message(
            self.agent_name, self.opponent_name, MessageType.ACCEPT, self.nested_test_offer)
        self.termination_message = Message(
            self.agent_name, self.opponent_name, MessageType.EXIT, None)
        self.offer_message = Message(
            self.agent_name, self.opponent_name, MessageType.OFFER, self.nested_test_offer)
        self.uniform_weights = {
            issue: 1 / len(values) for issue, values in self.neg_space.items()}

        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", self.neg_space, self.utilities, self.reservation_value, self.non_agreement_cost,
            self.uniform_weights)
        self.opponent = AgentFactory.make_linear_concession_agent(
            "opponent", self.neg_space, self.utilities, self.reservation_value, self.non_agreement_cost,
            self.uniform_weights)

        self.agent._call_for_negotiation(self.opponent, self.agent._neg_space)

    def test_both_agents_setup_correctly(self):
        self.assertTrue(self.agent.negotiation_active)
        self.assertTrue(self.agent.opponent == self.opponent)
        self.assertTrue(self.opponent.negotiation_active)
        self.assertTrue(self.opponent.opponent == self.agent)

    def test_counts_messages_correctly_in_successful_negotiation(self):
        self.agent.negotiate(self.opponent)
        # one offer and one acceptance message
        self.assertEqual(len(self.agent._transcript), 2)

    def test_counts_messages_correctly_in_unsuccessful_negotiation(self):
        arbitrary_utilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.set_utilities(arbitrary_utilities)
        self.opponent.negotiate(self.agent)
        self.assertEqual(len(self.agent._transcript), 2, self.agent._transcript)

    def test_after_negotiation_both_agents_have_same_transcript(self):
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent._transcript, self.opponent._transcript)

    def test_easy_negotiation_ends_successfully(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_utils = {"first_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost, temp_uniform_weights)
        self.opponent = AgentFactory.make_linear_concession_agent(
            "opponent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights)

        self.agent.negotiate(self.opponent)
        self.assertTrue(self.agent.successful, self.agent._transcript)
        self.assertFalse(self.agent.negotiation_active, self.agent._transcript)

    def test_easy_negotiation_ends_with_acceptance_message(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_utils = {"first_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost, temp_uniform_weights)
        self.opponent = AgentFactory.make_linear_concession_agent(
            "opponent", temp_neg_space, temp_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights)
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent._transcript[-1].is_acceptance())
        self.assertTrue(self.opponent._transcript[-1].is_acceptance(),self.opponent._transcript)

    def test_slightly_harder_negotiation_ends_successfully(self):
        temp_neg_space = {"first": ["True", "False"],
                          "second": ["True", "False"]}
        temp_agent_utils = {"first_True": 10000}
        temp_opponent_utils = {"second_True": 10000}
        temp_uniform_weights = {
            issue: 1 / len(values) for issue, values in temp_neg_space.items()}
        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", temp_neg_space, temp_agent_utils, self.reservation_value, self.non_agreement_cost, temp_uniform_weights)
        self.opponent = AgentFactory.make_linear_concession_agent(
            "opponent", temp_neg_space, temp_opponent_utils, self.reservation_value, self.non_agreement_cost,
            temp_uniform_weights)
        self.agent.negotiate(self.opponent)

        self.assertTrue(self.agent.successful)
        self.assertFalse(self.agent.negotiation_active)
        self.assertTrue(self.opponent.successful)
        self.assertFalse(self.opponent.negotiation_active)

    def test_impossible_negotiation_ends_unsuccessfully(self):
        temp_neg_space = {"first": ["True", "False"]}
        temp_agent_utils = {"first_True": -10000, "first_False": 10000}
        temp_opponent_utils = {"first_True": 10000, "first_False": -10000}
        temp_uniform_weights = {
            issue: 1 / len(issue) for issue in temp_neg_space.keys()}
        temp_reservation_value = 1000
        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", temp_neg_space, temp_agent_utils, temp_reservation_value, self.non_agreement_cost,
            temp_uniform_weights)
        self.opponent = AgentFactory.make_linear_concession_agent(
            "opponent", temp_neg_space, temp_opponent_utils, temp_reservation_value, self.non_agreement_cost,
            temp_uniform_weights)
        self.agent.negotiate(self.opponent)
        self.assertFalse(self.agent.successful,self.agent._transcript)
        self.assertFalse(self.agent.negotiation_active,self.agent._transcript)
        self.assertFalse(self.opponent.successful,self.opponent._transcript)
        self.assertFalse(self.opponent.negotiation_active,self.opponent._transcript)

    def test_receive_valid_negotiation_request(self):
        self.assertTrue(self.opponent.receive_negotiation_request(self.agent, self.agent._neg_space))

    def test_receive_acceptation_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.acceptance_message)
        self.agent._generate_next_message()
        self.assertFalse(self.agent.negotiation_active)

    def test_receive_acceptation_message_negotiation_was_successful(self):
        self.agent.receive_message(self.acceptance_message)
        self.agent._generate_next_message()
        self.assertTrue(self.agent.successful)

    def test_receive_termination_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.termination_message)
        self.agent._generate_next_message()
        self.assertFalse(self.agent.negotiation_active)

    def test_receive_termination_message_negotiation_was_unsuccessful(self):
        self.agent.receive_message(self.termination_message)
        self.agent._generate_next_message()
        self.assertFalse(self.agent.successful)

    def test_rho_of_0_still_accepts_negative_offer(self):
        self.utilities = {
            "boolean_True": -10000,
            "boolean_False": -10000,
            "integer_9": -10000,
            "integer_3": -10000,
            "integer_1": -10000,
            "integer_4": -10000,
            "integer_5": -10000,
            "'float_0.1'": -10000
        }
        self.agent = AgentFactory.make_linear_concession_agent(
            "agent", self.neg_space, self.utilities, 0.0, self.non_agreement_cost,
            self.uniform_weights)
        self.assertTrue(self.agent._accepts(self.optimal_offer))