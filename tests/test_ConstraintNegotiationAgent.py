import unittest
from uuid import uuid4

from math import pi
from numpy.random import choice

from constraint import AtomicConstraint
from constraintNegotiationAgent import ConstraintNegotiationAgent
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
        self.arbitrary_opponent_constraint = AtomicConstraint("boolean", "True")
        self.arbitrary_integer_constraint = AtomicConstraint("integer", "2")
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "integer_2": -1000,
            "'float_0.1'": -3.2,
            "'float_0.5'": pi
            # TODO still need to look at compound and negative atoms
        }

        self.arbitrary_kb = []
        self.arbitrary_reservation_value = 0
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
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_utilities,
                                                   self.arbitrary_kb,
                                                   self.arbitrary_reservation_value,
                                                   self.arbitrary_non_agreement_cost,
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
        self.assertTrue(self.arbitrary_own_constraint in self.agent.own_constraints)

    def test_receiving_opponent_constraint_saves_constraint(self):
        self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
        self.assertTrue(self.arbitrary_opponent_constraint in self.agent.opponent_constraints)

    def test_own_strat_satisfies_all_constraints(self):
        # make sure that these constraints are compatible
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.add_opponent_constraint(self.arbitrary_integer_constraint)
        for constr in self.agent.get_all_constraints():
            self.assertTrue(constr.is_satisfied_by_strat(self.agent.strat_dict), constr)

    def test_strat_violating_constr_is_caught(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        for constr in self.agent.own_constraints:
            self.assertTrue(constr.is_satisfied_by_strat(self.agent.strat_dict), constr)

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
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_utilities,
                                                   self.arbitrary_kb,
                                                   self.arbitrary_reservation_value,
                                                   self.arbitrary_non_agreement_cost,
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
        self.agent.add_opponent_constraint(self.arbitrary_opponent_constraint)
        self.assertAlmostEqual(
            self.agent.strat_dict[self.arbitrary_opponent_constraint.issue][self.arbitrary_opponent_constraint.value],
            0)

    def test_testing_constraint_satisfaction_doesnt_affect_stored_constraints(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.satisfies_all_constraints(
            self.nested_test_offer)
        self.assertEqual(self.agent.own_constraints,
                         {self.arbitrary_own_constraint,
                          AtomicConstraint("integer", "2"),
                          AtomicConstraint("float", "0.1")})

    def test_easy_negotiations_with_constraints_ends_successfully(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_does_not_accept_violating_offer(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertFalse(self.agent.accepts(self.violating_offer))

    def test_worth_of_violating_offer_is_non_agreement_cost(self):
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.assertEqual(self.agent.calc_offer_utility(self.violating_offer), self.arbitrary_non_agreement_cost)

    def test_ends_negotiation_after_finding_non_compatible_constraints(self):
        opponent_constraint = AtomicConstraint("boolean", "True")
        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.agent.receive_message(
            Message(self.opponent.agent_name, self.agent.agent_name, "offer", self.nested_test_offer,
                    constraint=opponent_constraint))
        agent_response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name, self.opponent.agent_name, "terminate", None), agent_response)

    def test_receiving_constraint_on_binary_constraint_doesnt_result_in_zero_strategy(self):
        self.agent.strat_dict = self.nested_test_offer
        self.agent.receive_message(
            Message(self.opponent.agent_name, self.agent.agent_name, "offer", self.nested_test_offer,
                    constraint=AtomicConstraint("boolean", "True")))
        # violating offer simply has the correct value for the boolean issue, there is no other connection
        self.assertEqual(self.agent.strat_dict, self.violating_offer)

    def test_receiving_offer_with_constraint_records_constraint(self):
        self.agent.receive_message(self.constraint_message)
        self.assertTrue(self.constraint_message.constraint in self.agent.opponent_constraints)

    def test_negotiation_with_incompatable_constraints_fails(self):
        self.generic_issues = {
            "boolean": [True, False]
        }
        self.agent = ConstraintNegotiationAgent(uuid4(),
                                                self.arbitrary_utilities, self.arbitrary_kb,
                                                self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                                verbose=0)
        self.agent.agent_name = "agent"
        self.opponent = ConstraintNegotiationAgent(uuid4(),
                                                   self.arbitrary_utilities, self.arbitrary_kb,
                                                   self.arbitrary_reservation_value, self.arbitrary_non_agreement_cost,
                                                   verbose=0)
        self.opponent.agent_name = "opponent"
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.call_for_negotiation(self.opponent, self.generic_issues)

        self.agent.add_own_constraint(self.arbitrary_own_constraint)
        self.opponent.add_own_constraint(AtomicConstraint("boolean", "True"))
        self.opponent.utilities["boolean_False"] = 1000
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
        self.assertFalse(self.agent.receive_negotiation_request(self.opponent, self.generic_issues))

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"integer_4": -100}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4") in self.agent.own_constraints)

    def test_create_constraint_with_generated_low_utility(self):
        issues = {"dummy0": [range(3)], "dummy1": [range(3)], "dummy2": [range(3)], "dummy3": [range(3)],
                  "dummy4": [range(3)]}
        self.agent = ConstraintNegotiationAgent(uuid4(), {'dummy0_0': -9.720708632311071, 'dummy0_1': -8.63928402687458,
                                                          'dummy1_0': -6.3767007099133695,
                                                          'dummy1_1': -13.27054211283465,
                                                          'dummy2_0': -8.398045297459051,
                                                          'dummy2_1': -10.849588704772344,
                                                          'dummy3_0': -7.781756350803565,
                                                          'dummy3_1': -10.777802560828997,
                                                          'dummy4_0': -5.216102446495702,
                                                          'dummy4_1': -11.210197384007735},
                                                [], 10, -100, issues, -11.6, name="agent", mean_utility=-7.139,
                                                std_utility=2.460)
        self.assertFalse(len(self.agent.get_all_constraints()) == 0)




