from unittest import TestCase
from pyneg.comms import Offer, AtomicConstraint, MessageType, Message
from pyneg.engine import ConstrainedRandomGenerator, ConstrainedLinearEvaluator


class TestConstraintRandomGenerator(TestCase):

    def setUp(self):
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

        self.uniform_weights = {
            issue: 1/len(self.neg_space.keys()) for issue in self.neg_space.keys()}

        self.evaluator = ConstrainedLinearEvaluator(
            self.utilities, self.uniform_weights, self.non_agreement_cost, None)

        self.generator = ConstrainedRandomGenerator(self.neg_space, self.utilities,
                                                    self.evaluator, self.non_agreement_cost,
                                                    self.kb, self.reservation_value, 20)

    def test_own_offer_does_not_violate_constraint(self):
        self.generator.add_constraint(AtomicConstraint("boolean", "True"))
        generated_message = self.generator.generate_offer()
        self.assertAlmostEqual(generated_message.offer["boolean"]['True'], 0.0)

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"integer_4": -10000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4")
                        in self.generator.constraints)

    def test_all_values_get_constrained_terminates_negotiation(self):
        low_util_dict = {"integer_{i}".format(
            i=i): -10000 for i in range(len(self.neg_space['integer']))}
        self.generator.add_utilities(low_util_dict)
        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

    def test_all_values_can_get_constrained(self):
        low_util_dict = {"integer_{i}".format(
            i=i): -100000 for i in range(len(self.neg_space['integer']))}
        self.evaluator.add_utilities(low_util_dict)
        constraints = self.evaluator.constraints
        self.assertTrue(
            all([constr.issue == "integer" for constr in constraints]))
        self.assertEqual(
            len([constr.issue == "integer" for constr in constraints]),
            len(self.neg_space['integer']))

    def test_multiple_issues_can_get_constrained(self):
        low_util_dict = {"integer_4": -1000, "'float_0.9'": -1000}
        self.evaluator.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("integer", "4"), AtomicConstraint(
            "float", "0.9")}.issubset(self.evaluator.constraints))
