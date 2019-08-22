import unittest
from uuid import uuid4

from math import pi
from numpy.random import choice

from constraint import AtomicConstraint
from constraintNegotiationAgent import ConstraintNegotiationAgent, Verbosity
from message import Message


class TestConstraintNegotiationAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.generic_issues = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }

        self.arbitrary_own_constraint = AtomicConstraint("boolean", "False")
        self.arbitrary_opponent_constraint = AtomicConstraint(
            "boolean", "True")
        self.arbitrary_integer_constraint = AtomicConstraint("integer", "2")
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "integer_2": -1000,
            "'float_0.1'": -3.2,
            "'float_0.5'": pi
            # TODO still need to look at compound and negative atoms
        }

        self.arbitrary_kb = []
        self.arbitrary_reservation_value = 0.5
        self.arbitrary_non_agreement_cost = -1000

        # should have a utility of 100 if no weights are used
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["3"] = 1
        self.nested_test_offer['float']["0.6"] = 1

        self.violating_offer = {
            "boolean": {"True": 0, "False": 1},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.violating_offer["integer"]["3"] = 1
        self.violating_offer['float']["0.6"] = 1

        self.agent = ConstraintNegotiationAgent(uuid4(),
                                                self.arbitrary_utilities,
                                                self.arbitrary_kb,
                                                self.arbitrary_reservation_value,
                                                self.arbitrary_non_agreement_cost,
                                                self.generic_issues,
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_utilities,
                                                   self.arbitrary_kb,
                                                   self.arbitrary_reservation_value,
                                                   self.arbitrary_non_agreement_cost,
                                                   self.generic_issues,
                                                   verbose=0)
        self.opponent.agent_name = "opponent"
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.call_for_negotiation(self.opponent, self.generic_issues)

        self.acceptance_message = Message(self.agent.agent_name,
                                          self.opponent.agent_name,
                                          "accept",
                                          self.nested_test_offer)
        self.termination_message = Message(self.agent.agent_name,
                                           self.opponent.agent_name,
                                           "terminate",
                                           None)
        self.constraint_message = Message(self.agent.agent_name, self.opponent.agent_name,
                                          "offer",
                                          self.nested_test_offer,
                                          self.arbitrary_opponent_constraint)
        self.offer_message = Message(self.agent.agent_name,
                                     self.opponent.agent_name,
                                     "offer",
                                     self.nested_test_offer)

        # print("In method: {}".format( self._testMethodName))

    def tearDown(self):
        pass

    def test_receiving_own_constraint_saves_constraint(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertTrue(
            self.arbitrary_own_constraint in self.agent.own_constraints)

    def test_receiving_opponent_constraint_saves_constraint(self):
        self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
        self.assertTrue(
            self.arbitrary_opponent_constraint in self.agent.opponent_constraints)

    def test_own_strat_satisfies_all_constraints(self):
        # make sure that these constraints are compatible
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.add_opponent_constraint(self.arbitrary_integer_constraint)
        for constr in self.agent.get_all_constraints():
            self.assertTrue(constr.is_satisfied_by_strat(
                self.agent.strat_dict), constr)

    def test_strat_violating_constr_is_caught(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        for constr in self.agent.own_constraints:
            self.assertTrue(constr.is_satisfied_by_strat(
                self.agent.strat_dict), constr)

    def test_responds_to_violating_offer_with_constraint(self):
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "'float_0.5'": pi
        }
        self.agent = ConstraintNegotiationAgent(uuid4(),
                                                self.arbitrary_utilities,
                                                self.arbitrary_kb,
                                                self.arbitrary_reservation_value,
                                                self.arbitrary_non_agreement_cost,
                                                self.generic_issues,
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_utilities,
                                                   self.arbitrary_kb,
                                                   self.arbitrary_reservation_value,
                                                   self.arbitrary_non_agreement_cost,
                                                   self.generic_issues,
                                                   verbose=0)
        self.opponent.agent_name = "opponent"
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.opponent = self.opponent

        # set strategy to something constant so we can predict what message it will generate
        self.agent.strat_dict = self.nested_test_offer.copy()

        self.agent.add_own_constraint(AtomicConstraint("boolean", "False"))
        self.agent.receive_message(Message(self.opponent.agent_name,
                                           self.agent.agent_name,
                                           "offer",
                                           self.violating_offer))

        response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name,
                                 self.opponent.agent_name,
                                 "offer",
                                 self.agent.strat_dict,
                                 AtomicConstraint("boolean", "False")),
                         response)

    def test_receiving_own_constraint_adjusts_strat_accordingly(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertAlmostEqual(
            self.agent.strat_dict[self.arbitrary_own_constraint.issue][self.arbitrary_own_constraint.value], 0)

    def test_receiving_opponent_constraint_adjusts_strat_accordingly(self):
        self.assertAlmostEqual(self.agent.strat_dict["boolean"]["False"], 0)

    def test_testing_constraint_satisfaction_doesnt_affect_stored_constraints(self):
        # self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.satisfies_all_constraints(
            self.nested_test_offer)
        self.assertEqual(self.agent.own_constraints,
                         {AtomicConstraint("integer", "2"),
                          AtomicConstraint("boolean", "False")})

    def test_easy_negotiations_with_constraints_ends_successfully(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_does_not_accept_violating_offer(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertFalse(self.agent.accepts(self.violating_offer))

    def test_worth_of_violating_offer_is_non_agreement_cost(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertEqual(self.agent.calc_offer_utility(
            self.violating_offer), self.arbitrary_non_agreement_cost)

    def test_ends_negotiation_after_finding_non_compatible_constraints(self):
        opponent_constraint = AtomicConstraint("boolean", "True")
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.receive_message(
            Message(self.opponent.agent_name, self.agent.agent_name, "offer", self.nested_test_offer,
                    constraint=opponent_constraint))
        agent_response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name,
                                 self.opponent.agent_name, "terminate", None), agent_response)

    def test_receiving_constraint_on_binary_constraint_doesnt_result_in_zero_strategy(self):
        self.agent = ConstraintNegotiationAgent(uuid4(),
                                                self.arbitrary_utilities,
                                                self.arbitrary_kb,
                                                self.arbitrary_reservation_value,
                                                self.arbitrary_non_agreement_cost,
                                                self.generic_issues,
                                                automatic_constraint_generation=False)
        self.agent.agent_name = "agent"
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.strat_dict = self.nested_test_offer

        self.agent.receive_message(
            Message(self.opponent.agent_name, self.agent.agent_name, "offer", self.nested_test_offer,
                    constraint=AtomicConstraint("boolean", "True")))
        # violating offer simply has the correct value for the boolean issue,
        # there is no other connection
        self.assertEqual(self.agent.strat_dict, self.violating_offer)

    def test_receiving_offer_with_constraint_records_constraint(self):
        self.agent.receive_message(self.constraint_message)
        self.assertTrue(
            self.constraint_message.constraint in self.agent.opponent_constraints)

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
        self.agent = ConstraintNegotiationAgent(uuid4(),
                                                self.arbitrary_agent_utilities,
                                                self.arbitrary_kb,
                                                self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                                self.generic_issues,
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_opponent_utilities, self.arbitrary_kb,
                                                   self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                                   self.generic_issues, verbose=0)
        self.opponent.agent_name = "opponent"
        self.agent.setup_negotiation(self.generic_issues)
        # self.agent.call_for_negotiation(self.opponent, self.generic_issues)

        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.opponent.add_own_constraint(AtomicConstraint("boolean", "True"))
        self.agent.negotiate(self.opponent)
        self.assertFalse(self.agent.successful or self.opponent.successful)
        self.assertFalse(self.agent.constraints_satisfiable)

    def test_wont_generate_offers_when_incompatable_constraints_are_present(self):
        self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        with self.assertRaises(RuntimeError):
            self.agent.generate_offer()

    def test_adding_random_constraints_adjusts_strategy_correctly(self):
        iters = 10
        for _ in range(iters):
            issue = choice(list(self.generic_issues.keys()))
            if issue == "boolean":
                continue
            value = str(choice(list(self.generic_issues[issue])))
            self.agent.add_own_constraint(AtomicConstraint(issue, value))
            self.assertAlmostEqual(self.agent.strat_dict[issue][value], 0,
                                   msg="failed with constraint base: {}".format(self.agent.own_constraints))

    def test_refuses_negotiation_if_constraints_are_incompatable(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
        self.assertFalse(self.agent.receive_negotiation_request(
            self.opponent, self.generic_issues))

    def test_getting_utility_below_threshold_creates_constraint(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"integer_4": -1000}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4")
                        in self.agent.own_constraints)

    def test_all_values_can_get_constrained(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"integer_{i}".format(
            i=i): -1000 for i in range(len(self.agent.issues['integer']))}
        self.agent.add_utilities(low_util_dict)
        self.assertEqual(
            len(self.agent.get_unconstrained_values_by_issue("integer")), 0)

    def test_all_values_get_constrained_terminates_negotiation(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"integer_{i}".format(
            i=i): -1000 for i in range(len(self.agent.issues['integer']))}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(
            self.agent.generate_next_message_from_transcript().is_termination())

    def test_multiple_issues_can_get_constrained(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"integer_4": -1000, "'float_0.9'": -1000}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("integer", "4"), AtomicConstraint(
            "float", "0.9")}.issubset(self.agent.own_constraints))

    def test_doesnt_create_unessecary_constraints_when_setting_multiple_utils(self):
        temp_issues = {
            "boolean1" : [True, False],
            "boolean2" : [True, False]
        }
        temp_utils = { 
            "boolean1_True" : -1000,
            "boolean1_False": 0,
            "boolean2_True" : 1000,
            "boolean2_False" : 1000

        }
        self.agent = ConstraintNegotiationAgent(uuid4(),
            temp_utils, [], 0.1, -(2**31), temp_issues)
        self.agent.add_utilities(temp_utils)
        self.assertEqual(len(self.agent.own_constraints), 1 )

    def test_constraint_doesnt_trigger_if_offer_doesnt_assign_it(self):
        temp_issues = {
            "integer1" : range(3),
            "integer2" : range(3)
        }
        temp_utils = { 
            "integer1_0" : -10000,
            "integer1_1" : 10,
            "integer1_2" : 0,
            "integer2_0" : 0,
            "integer2_1" : 10,
            "integer2_2" : 10
        }
        self.agent = ConstraintNegotiationAgent(uuid4(),
            temp_utils, [], 0.1, -(2**31), temp_issues,name="agent")
        self.agent.add_utilities(temp_utils)
        self.agent.opponent = self.opponent
        offer = {
            "integer1" : {"0": 0, "1" : 0, "2": 1},
            "integer2" : {"0": 1, "1" : 0, "2": 0}
        }
        offer_msg = Message(self.opponent.agent_name, self.agent.agent_name,"offer", offer)
        self.agent.receive_message(offer_msg)
        response = self.agent.generate_next_message_from_transcript()
        self.assertFalse(response.constraint)
