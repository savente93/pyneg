from unittest import TestCase
from pyneg.comms import Offer, AtomicConstraint, MessageType, Message
from pyneg.engine import ConstrainedRandomGenerator, ConstrainedLinearEvaluator


class TestConstrainedRandomGenerator(TestCase):
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

        self.violating_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.violating_offer["integer"]["2"] = 1.0
        self.violating_offer['float']["0.1"] = 1.0

        self.violating_offer = Offer(self.violating_offer)

        self.uniform_weights = {
            issue: 1/len(self.neg_space.keys()) for issue in self.neg_space.keys()}

        self.evaluator = ConstrainedLinearEvaluator(
            self.utilities, self.uniform_weights, self.non_agreement_cost, None)

        self.generator = ConstrainedRandomGenerator(self.neg_space, self.utilities,
                                                    self.evaluator, self.non_agreement_cost,
                                                    self.kb, self.reservation_value, set())

    def test_own_offer_does_not_violate_constraint(self):
        self.generator.add_constraint(AtomicConstraint("boolean", "True"))
        generated_offer = self.generator.generate_offer()
        chosen_offer_value = generated_offer.get_chosen_value("boolean")
        self.assertNotEqual(chosen_offer_value, "True")

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
        self.generator.add_utilities(low_util_dict)
        constraints = self.generator.constraints
        integer_constraints = set([constr for constr in constraints if constr.issue ==
                                   "integer"])
        self.assertEqual(constraints, integer_constraints, constraints)
        self.assertEqual(
            len(integer_constraints),
            len(self.neg_space['integer']), constraints)

    def test_multiple_issues_can_get_constrained(self):
        low_util_dict = {"integer_4": -100000, "'float_0.9'": -100000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("integer", "4"), AtomicConstraint(
            "float", "0.9")}.issubset(self.generator.constraints))

    def test_doesnt_generate_same_offer_five_times(self):
        # since some elements might be randomly picked it can sometimes happen that the elements are the same but it
        # shouldn't keep happening so we'll try it a couple of times
        last_offer = self.generator.generate_offer()
        for _ in range(5):
            new_offer = self.generator.generate_offer()
            self.assertNotEqual(last_offer, new_offer)
            last_offer = new_offer

    def test_terminates_after_constrains_become_unsatisfiable(self):
        incompatible_constraints = set([
            AtomicConstraint("boolean", "True"),
            AtomicConstraint("boolean", "False")])
        self.generator.add_constraints(incompatible_constraints)

        with self.assertRaises(StopIteration):
            _ = self.generator.generate_offer()

    def test_responds_to_violating_offer_with_constraint(self):
        self.generator.add_constraint(AtomicConstraint("boolean", "True"))
        constr = self.generator.find_violated_constraint(self.violating_offer)
        self.assertTrue(constr in {AtomicConstraint(
            "boolean", "True"), AtomicConstraint("integer", "5")})

    def test_doesnt_create_unessecary_constraints_when_setting_multiple_utils(self):
        temp_issues = {
            "boolean1": [True, False],
            "boolean2": [True, False]
        }
        temp_utils = {
            "boolean1_True": -10000000,
            "boolean1_False": 0,
            "boolean2_True": 1000,
            "boolean2_False": 1000
        }
        uniform_weights = {
            issue: 1/len(temp_issues.keys()) for issue in temp_issues.keys()}

        temp_evaluator = ConstrainedLinearEvaluator(
            temp_utils, uniform_weights, self.non_agreement_cost, None)

        temp_generator = ConstrainedRandomGenerator(temp_issues, temp_utils,
                                                    temp_evaluator, self.non_agreement_cost,
                                                    [], 0, set())
        self.assertEqual(len(self.generator.constraints),
                         1, self.generator.constraints)

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"integer_4": -100000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4")
                        in self.generator.constraints)
