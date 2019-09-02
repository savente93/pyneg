from unittest import TestCase
from pyneg.comms import Offer, AtomicConstraint, Message, MessageType
from pyneg.engine import ConstrainedProblogEvaluator
from math import pi


class TestConstrainedProblogEvaluator(TestCase):

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

        self.arbitrary_utilities = {
            "boolean_True": 100,
            "integer_2": -1000,
            "'float_0.1'": -3.2,
            "'float_0.5'": pi
        }

        self.violating_offer = {
            "boolean": {"True": 0, "False": 1},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.violating_offer["integer"]["3"] = 1
        self.violating_offer['float']["0.6"] = 1

        self.evaluator = ConstrainedProblogEvaluator(
            self.neg_space,
            self.utilities,
            self.non_agreement_cost,
            self.kb,
            None)

        self.boolean_constraint = AtomicConstraint("boolean", "True")
        self.integer_constraint = AtomicConstraint("integer", "2")

    def test_testing_constraint_satisfaction_doesnt_affect_stored_constraints(self):
        self.evaluator.add_constraint(self.boolean_constraint)
        self.evaluator.add_constraint(self.integer_constraint)
        self.evaluator.satisfies_all_constraints(
            self.nested_test_offer)
        self.assertEqual(self.evaluator.constraints,
                         {self.boolean_constraint,
                          self.integer_constraint})

    def test_worth_of_violating_offer_is_non_agreement_cost(self):
        self.evaluator.add_constraint(self.boolean_constraint)
        self.assertEqual(self.evaluator.calc_offer_utility(
            self.violating_offer), self.non_agreement_cost)

    def test_doesnt_create_unessecary_constraints_when_setting_multiple_utils(self):
        temp_issues = {
            "boolean1": [True, False],
            "boolean2": [True, False]
        }
        temp_utils = {
            "boolean1_True": -100000,
            "boolean1_False": 0,
            "boolean2_True": 1000,
            "boolean2_False": 1000

        }
        self.evaluator = ConstrainedProblogEvaluator(
            temp_issues, temp_utils, self.non_agreement_cost, [], None)
        self.evaluator.add_utilities(temp_utils)
        self.assertEqual(len(self.evaluator.constraints), 1)
