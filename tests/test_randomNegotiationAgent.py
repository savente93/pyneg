import unittest as ut
from math import pi
from randomNegotiationAgent import RandomNegotiationAgent
from message import Message
from uuid import uuid4


class TestRandomNegotiationAgent(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # print("In method", self._testMethodName)
        self.generic_issues = {
            "boolean": ["True", "False"],
            "integer": list(map(str, list(range(10)))),
            "float": ["{0:.1f}".format(0.1 * i) for i in range(10)]
        }
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "integer_2": -1000,
            "'float_0.1'": -3.2,
            "'float_0.5'": pi
            # TODO still need to look at compound and negative atoms
        }
        self.arbitrary_kb = []
        self.arbitrary_reservation_value = 75/3
        self.arbitrary_non_agreement_cost = -1000

        self.sparse_nested_offer = {
            "boolean": {"True": 1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.sparse_atom_test_offer = {
            "boolean_True": 1,
            "integer_2": 1,
            "'float_0.5'": 1
        }

        self.invalid_sparse_nested_test_offer = {
            "boolean": {"True": -1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.nested_test_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["2"] = 1.0
        self.nested_test_offer['float']["0.5"] = 1.0

        self.atom_test_offer = {
            "boolean_True": 1,
            "boolean_False": 0,
            "integer_0": 0,
            "integer_1": 0,
            "integer_2": 1,
            "integer_3": 0,
            "integer_4": 0,
            "integer_5": 0,
            "integer_6": 0,
            "integer_7": 0,
            "integer_8": 0,
            "integer_9": 0,
            "'float_0.0'": 0,
            "'float_0.1'": 0,
            "'float_0.2'": 0,
            "'float_0.3'": 0,
            "'float_0.4'": 0,
            "'float_0.5'": 1,
            "'float_0.6'": 0,
            "'float_0.7'": 0,
            "'float_0.8'": 0,
            "'float_0.9'": 0
        }

        self.agent = RandomNegotiationAgent(uuid4(),
                                            self.arbitrary_utilities, self.arbitrary_kb,
                                            self.arbitrary_reservation_value,
                                            self.arbitrary_non_agreement_cost)
        self.agent.agent_name = "agent"
        self.opponent = RandomNegotiationAgent(uuid4(),
                                               self.arbitrary_utilities,
                                               self.arbitrary_kb,
                                               self.arbitrary_reservation_value,
                                               self.arbitrary_non_agreement_cost)
        self.opponent.agent_name = "opponent"
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

        self.acceptance_message = Message(self.agent.agent_name,
                                          self.opponent.agent_name,
                                          "accept",
                                          self.nested_test_offer)

        self.termination_message = Message(self.agent.agent_name,
                                           self.opponent.agent_name,
                                           "terminate",
                                           self.nested_test_offer)

        self.offer_message = Message(self.agent.agent_name,
                                     self.opponent.agent_name,
                                     "offer",
                                     self.nested_test_offer)

    def tearDown(self):
        pass

    def test_generateDecisionFacts(self):
        expected_facts = [
            ["boolean_True", "boolean_False"],
            ["integer_0", "integer_1", "integer_2",
             "integer_3", "integer_4", "integer_5", "integer_6", "integer_7", "integer_8", "integer_9"],
            ["'float_0.0'", "'float_0.1'", "'float_0.2'",
             "'float_0.3'", "'float_0.4'", "'float_0.5'", "'float_0.6'", "'float_0.7'", "'float_0.8'", "'float_0.9'"],
        ]

        self.agent.generate_decision_facts()

        self.assertEqual(self.agent.decision_facts, expected_facts)

    def test_init_uniform_strategy(self):
        expected_strat = {
            "boolean": {"True": 1 / 2, "False": 1 / 2},
            "integer": {str(i): 1 / 10 for i in range(10)},
            "float": {"{:.1f}".format(0.1 * i): 1 / 10 for i in range(10)}
        }

        self.agent.init_uniform_strategy()
        self.assertEqual(expected_strat, self.agent.strat_dict)

    def test_calc_offer_utility(self):
        # self.agent.verbose = 4
        expected_offer_utility = 100/3-1000/3 + pi/3
        self.assertAlmostEqual(self.agent.calc_offer_utility(self.nested_test_offer), expected_offer_utility)

    def test_calc_strat_utility(self):
        self.agent.init_uniform_strategy()
        expected_uniform_strat_util = (100/2)/3 + (-1000/10)/3 + (-3.2/10)/3 + (pi/10)/3
        self.assertAlmostEqual(self.agent.calc_strat_utility(self.agent.strat_dict), expected_uniform_strat_util)

    def test_calc_offer_utility_python(self):
        python_agent = RandomNegotiationAgent(uuid4(),
                                              self.arbitrary_utilities, self.arbitrary_kb,
                                              self.arbitrary_reservation_value,
                                              self.arbitrary_non_agreement_cost,
                                              utility_computation_method="python")
        python_agent.verbose = 4
        print(self.agent.linear_additive_utility)
        print(self.agent.utility_computation_method)
        python_agent.agent_name = "agent"
        python_agent.set_utilities(self.arbitrary_utilities)
        python_agent.setup_negotiation(self.generic_issues)
        python_agent.init_uniform_strategy()

        print(python_agent.issue_weights)
        print(python_agent.linear_additive_utility)
        expected_offer_utility = 100/3-1000/3 + pi/3

        self.assertAlmostEqual(python_agent.calc_offer_utility(self.nested_test_offer), expected_offer_utility)

    def test_calc_strat_utility_python(self):
        python_agent = RandomNegotiationAgent(uuid4(),
                                              self.arbitrary_utilities, self.arbitrary_kb,
                                              self.arbitrary_reservation_value,
                                              self.arbitrary_non_agreement_cost,
                                              utility_computation_method="python")
        python_agent.agent_name = "agent"
        python_agent.set_utilities(self.arbitrary_utilities)
        python_agent.setup_negotiation(self.generic_issues)
        python_agent.init_uniform_strategy()
        expected_uniform_strat_util = (50 - 100)/3 - 3.2 / 30 + pi / 30
        self.assertAlmostEqual(python_agent.calc_strat_utility(
            python_agent.strat_dict), expected_uniform_strat_util)


    def test_accept(self):
        self.assertFalse(self.agent.accepts(
            self.nested_test_offer))

    def test_umbrella_calc(self):
        umbrella_utils = {
            "brokenUmbrella": -40,
            "raincoat_True": -20,
            "umbrella_True": -2,
            "dry": 60
        }

        umbrella_issues = {
            "umbrella": [True, False],
            "raincoat": [True, False]
        }

        umbrella_kb = [
            "0.3::rain.",
            "0.5::wind.",
            "brokenUmbrella:- umbrella_True, rain, wind.",
            "dry:- rain, raincoat_True.",
            "dry:- rain, umbrella_True, not brokenUmbrella.",
            "dry:- not(rain)."
        ]

        umbrella_offer = {
            "umbrella": {"True": 1, "False": 0},
            "raincoat": {"False": 1, "True": 0}
        }

        umbrella_agent = RandomNegotiationAgent(uuid4(),
                                                umbrella_utils,
                                                umbrella_kb,
                                                0,
                                                0,
                                                umbrella_issues,
                                                smart=False,
                                                linear_additive_utility=False,
                                                utility_computation_method="problog")
        umbrella_answer = 43

        self.assertAlmostEqual(umbrella_agent.calc_offer_utility(umbrella_offer), umbrella_answer)

    def test_format_problog_strat(self):
        self.agent.init_uniform_strategy()
        expected_problog_strat_string = "0.5::boolean_True;0.5::boolean_False.\n" + \
                                        "0.1::integer_0;" + \
                                        "0.1::integer_1;" + \
                                        "0.1::integer_2;" + \
                                        "0.1::integer_3;" + \
                                        "0.1::integer_4;" + \
                                        "0.1::integer_5;" + \
                                        "0.1::integer_6;" + \
                                        "0.1::integer_7;" + \
                                        "0.1::integer_8;" + \
                                        "0.1::integer_9.\n" + \
                                        "0.1::'float_0.0';" + \
                                        "0.1::'float_0.1';" + \
                                        "0.1::'float_0.2';" + \
                                        "0.1::'float_0.3';" + \
                                        "0.1::'float_0.4';" + \
                                        "0.1::'float_0.5';" + \
                                        "0.1::'float_0.6';" + \
                                        "0.1::'float_0.7';" + \
                                        "0.1::'float_0.8';" + \
                                        "0.1::'float_0.9'.\n"

        self.assertEqual(self.agent.format_problog_strat(
            self.agent.strat_dict), expected_problog_strat_string)

    def test_generate_offer(self):
        self.agent.strat_dict = self.nested_test_offer
        # set reservation value so search doesn't exit
        self.agent.reservation_value = -1000
        offer = self.agent.generate_offer()
        self.assertEqual(offer,
                         self.nested_test_offer)

    def test_generate_offer_exits_if_unable_to_find_solution(self):
        self.agent.max_generation_tries = 10
        self.agent.strat_dict = self.nested_test_offer
        self.assertEqual(self.agent.generate_offer_message(),
                         Message(self.agent.agent_name,
                                 self.opponent.agent_name,
                                 "terminate",
                                 None))

    def test_valid_offer_is_accepted(self):
        self.assertTrue(self.agent.is_offer_valid(
            self.nested_test_offer))

    def test_valid_strat_is_accepted(self):
        self.assertTrue(self.agent.is_strat_valid(
            self.agent.strat_dict))

    def test_non_binary_offer_is_rejected(self):
        self.assertFalse(self.agent.is_offer_valid(
            self.agent.strat_dict))

    def test_invalid_offer_is_rejected(self):
        with self.assertRaises(ValueError):
            self.agent.accepts(self.agent.strat_dict)

    def test_misspelled_offer_is_rejected(self):
        self.nested_test_offer['boolean']['True'] = 1.0
        del self.nested_test_offer['boolean']['True']
        with self.assertRaises(ValueError):
            self.agent.accepts(self.nested_test_offer)

    def test_strat_with_non_dist_is_rejected(self):
        self.agent.strat_dict["boolean"]["True"] = 0.23424123412341234123412341234123412341234
        self.assertFalse(self.agent.is_strat_valid(
            self.agent.strat_dict))

    def test_strat_with_unknown_facts_is_not_valid(self):
        self.agent.strat_dict['boolean']['true'] = 0.0
        self.assertFalse(self.agent.is_strat_valid(
            self.agent.strat_dict))

    def test_offer_with_unknown_facts_is_not_valid(self):
        offer_with_unknown_fact = self.nested_test_offer
        offer_with_unknown_fact['boolean']['true'] = 1.0
        del offer_with_unknown_fact['boolean']['True']
        self.assertFalse(self.agent.is_offer_valid(
            offer_with_unknown_fact))

    def test_setting_valid_sparse_strat_succeeds(self):
        self.agent.set_strat(self.sparse_nested_offer)

    def test_setting_invalid_sparse_strat_raises_error(self):
        with self.assertRaises(ValueError):
            self.agent.set_strat(self.invalid_sparse_nested_test_offer)

    def test_calculating_utility_of_invalid_offer_raises_error(self):
        # B in boolean is capitalised while it shouldn't be
        self.agent.strat_dict['Boolean_True'] = 0.0
        with self.assertRaises(ValueError):
            self.agent.calc_offer_utility(
                self.agent.strat_dict)

    def test_generate_valid_offer(self):
        self.agent.smart = True
        self.assertTrue(self.agent.accepts(
            self.agent.generate_offer()))

    def test_valid_sparse_nested_dict_to_atom_dict(self):
        self.assertEqual(self.sparse_atom_test_offer, self.agent.atom_dict_from_nested_dict(
            self.sparse_nested_offer))

    def test_dense_atom_dict_to_nested_dict_valid(self):
        self.assertEqual(self.nested_test_offer, self.agent.nested_dict_from_atom_dict(
            self.atom_test_offer))

    def test_valid_sparse_atom_dict_to_nested_dict(self):
        self.assertEqual(self.atom_test_offer, self.agent.atom_dict_from_nested_dict(
            self.nested_test_offer))

    def test_atom_to_nested_dict(self):
        self.agent.set_issues({"dummy0": range(3), "dummy1": range(3), "dummy2": range(3)})
        atom_dict = {'dummy0_0': 0.0, 'dummy0_1': 1.0, 'dummy0_2': 0.0, 'dummy1_0': 0.0, 'dummy1_1': 1.0,
                     'dummy1_2': 0.0, 'dummy2_0': 0.0, 'dummy2_1': 0.0, 'dummy2_2': 1.0}
        nested_dict = {'dummy0': {'0': 0.0, '1': 1.0, '2': 0.0}, 'dummy1': {'0': 0.0, '1': 1.0, '2': 0.0},
                       'dummy2': {'0': 0.0, '1': 0.0, '2': 1.0}}
        self.assertEqual(nested_dict, self.agent.nested_dict_from_atom_dict(atom_dict))

    def test_resetting_issues_resets_strategy(self):
        new_issues = {"first": ["True", "False"]}
        self.agent.set_issues(new_issues)
        self.assertTrue(self.agent.is_strat_valid(
            self.agent.strat_dict))

    def test_accepts_acceptable_offer(self):
        self.nested_test_offer['integer']["2"] = 0
        self.nested_test_offer['integer']["3"] = 1
        self.agent.record_message(
            Message(self.opponent, self.agent, kind="offer", offer=self.nested_test_offer))
        self.agent.generate_next_message_from_transcript()
        self.assertTrue(
            self.agent.successful and not self.agent.negotiation_active and self.agent.message_count == 1)

    def test_getting_empty_message_increments_message_count(self):
        self.agent.receive_message(
            Message(self.opponent, self.agent, "empty", None))
        self.assertEqual(self.agent.message_count, 1)

    def test_sending_message_increments_message_count(self):
        self.agent.send_message(self.opponent, Message(
            self.opponent, self.agent, "empty", None))
        self.assertEqual(self.agent.message_count, 1)

    def test_terminates_negotiation_after_max_rounds(self):
        self.agent.max_rounds = 3
        for _ in range(self.agent.max_rounds + 1):
            self.agent.record_message(
                Message(self.opponent, self.agent, "offer", self.nested_test_offer))
        response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(
            Message(self.opponent, self.agent, kind="terminate", offer=self.nested_test_offer), response)

    def test_easy_negotiation_ends_successfully(self):
        self.agent.set_issues({"first": ["True", "False"]})
        self.agent.utilities = {"first_True": 10000}
        self.opponent.utilities = {"first_True": 10000}
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.successful and not self.agent.negotiation_active)

    def test_slightly_harder_negotiation_ends_successfully(self):
        self.agent.set_issues({"first": ["True", "False"],
                               "second": ["True", "False"]})
        self.agent.utilities = {"first_True": 10000}
        self.opponent.utilities = {"second_True": 10000}
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.successful and not self.agent.negotiation_active)

    def test_impossible_negotiation_ends_unsuccessfully(self):
        self.agent.max_rounds = 10  # make sure the test goes a little faster
        self.opponent.max_rounds = 10

        self.agent.set_issues({"first": ["True", "False"]})
        self.agent.add_utilities({"first_True": -10000, "first_False": 10000})
        self.opponent.add_utilities(
            {"first_True": 10000, "first_False": -10000})

        self.agent.negotiate(self.opponent)
        self.assertTrue(
            not self.agent.successful and not self.agent.negotiation_active)

    def test_received_message_can_be_recalled(self):
        msg = Message(self.opponent.agent_name,
                      self.agent.agent_name, "offer", self.nested_test_offer)
        self.agent.receive_message(msg)
        self.assertEqual(self.agent.transcript[-1], msg)

    def test_receive_valid_negotiation_request(self):
        self.assertTrue(self.opponent.receive_negotiation_request(
            self.agent, self.generic_issues))

    def test_receive_acceptation_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.acceptance_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(self.agent.negotiation_active)

    def test_receive_acceptation_message_negotiation_was_unsuccessful(self):
        self.agent.receive_message(self.acceptance_message)
        self.agent.generate_next_message_from_transcript()
        self.assertTrue(self.agent.successful)

    def test_receive_termination_message_ends_negotiation(self):
        self.agent.negotiation_active = True
        self.agent.receive_message(self.termination_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(self.agent.negotiation_active)

    def test_receive_termination_message_negotiation_was_nnsuccessful(self):
        self.agent.receive_message(self.termination_message)
        self.agent.generate_next_message_from_transcript()
        self.assertFalse(self.agent.successful)
