from unittest import TestCase
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict
from pyneg.engine import ConstraintEnumGenerator, ConstraintLinearEvaluator
from pyneg.comms import Offer, AtomicConstraint
from numpy import arange
from math import pi


class TestConstraintEnumGenerator(TestCase):

    def setUp(self):
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            arange(9).reshape((3, 3))**2, arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0.1000
        self.arbitrary_non_agreement_cost = -1000
        uniform_weights = {
            issue: 1/len(values) for issue, values in self.issues.items()}
        self.evaluator = ConstraintLinearEvaluator(
            self.utilities, uniform_weights, self.arbitrary_non_agreement_cost)
        self.violating_offer = {
            "issue0": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue1": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue2": {"0": 0.0, "1": 0.0, "2": 1.0}
        }
        self.generator = ConstraintEnumGenerator(
            self.issues, self.utilities, self.evaluator, self.arbitrary_reservation_value)

    def test_responds_to_violating_offer_with_constraint(self):

        self.generator.add_constraint(AtomicConstraint("issue2", "2"))
        constr = self.generator.generate_constraints(self.violating_offer)
        self.assertEqual(constr, AtomicConstraint("issue2", "2"))

    def test_generates_best_offer_first_time(self):
        best_offer = Offer(nested_dict_from_atom_dict({'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
                                                       'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                       'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}))
        generated_offer = self.gen.generate_offer()
        self.assertEqual(best_offer, generated_offer)

    def test_generates_next_best_offer_second_time(self):
        next_best_offer = Offer(nested_dict_from_atom_dict({'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
                                                            'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                            'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}))

        _ = self.gen.generate_offer()
        second = self.gen.generate_offer()
        self.assertEqual(next_best_offer, second)

    def test_generates_next_next_best_offer_third_time(self):
        next_next_best_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        thrid = self.gen.generate_offer()
        self.assertEqual(next_next_best_offer, thrid)

    def test_generates_expected_offer_forth_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
             'issue1_0': 0.0, 'issue1_1': 1.0, 'issue1_2': 0.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        offer = self.gen.generate_offer()
        self.assertEqual(expected_offer, offer)

    def test_generates_expected_offer_fith_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        _ = self.gen.generate_offer()
        offer = self.gen.generate_offer()
        self.assertEqual(expected_offer, offer)

    def test_terminates_first_time_if_no_options_are_acceptable(self):
        self.gen = ConstraintEnumGenerator(
            self.issues, self.utilities, self.evaluator, 1, None)

        _ = self.gen.generate_offer()

        with self.assertRaises(StopIteration):
            self.gen.generate_offer()

    def test_terminates_after_options_become_unacceptable(self):
        self.gen = ConstraintEnumGenerator(
            self.issues, self.utilities, self.evaluator, 1.1, None)

        with self.assertRaises(StopIteration):
            _ = self.gen.generate_offer()

    def test_own_offer_does_not_violate_constraint(self):
        self.generator.add_constraint(AtomicConstraint("issue1", "2"))
        generated_offer = self.generator.generate_offer()
        self.assertTrue(
            self.generator.satisfies_all_constraints(generated_offer))

    def test_generates_valid_offers_when_constraints_are_present(self):
        self.generator.add_constraint(AtomicConstraint("issue0", "2"))
        self.generator.add_constraint(AtomicConstraint("issue1", "2"))
        self.generator.add_constraint(AtomicConstraint("issue2", "2"))
        generated_offer = self.generator.generate_offer()
        self.generator.satisfies_all_constraints(generated_offer)

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"issue1_0": -100000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("issue1", "0")
                        in self.generator.own_constraints)

    def test_all_values_can_get_constrained(self):
        low_util_dict = {"issue2_{i}".format(
            i=i): -100000 for i in range(len(self.generator.neg_space['issue2']))}
        self.generator.add_utilities(low_util_dict)
        constraints = self.generator.constraints
        self.assertTrue(
            all([constr.issue == "issue2" for constr in constraints]))
        self.assertEqual(
            len([constr.issue == "issue2" for constr in constraints]),
            len(self.generator.neg_space['issue2']))

    def test_multiple_issues_can_get_constrained(self):
        low_util_dict = {"issue2_0": -1000, "issue0_1": -1000}
        self.evaluator.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("issue2", "0"), AtomicConstraint(
            "issue0", "1")}.issubset(self.evaluator.constraints))
