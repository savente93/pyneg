from unittest import TestCase
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict
from pyneg.engine import ConstrainedEnumGenerator, ConstrainedLinearEvaluator
from pyneg.comms import Offer, AtomicConstraint
from numpy import arange
from math import pi


class TestConstrainedEnumGenerator(TestCase):

    def setUp(self):
        self.neg_space, self.utilities, _ = neg_scenario_from_util_matrices(
            arange(9).reshape((3, 3))**2, arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0
        self.arbitrary_non_agreement_cost = -1000
        self.uniform_weights = {
            issue: 1/len(values) for issue, values in self.neg_space.items()}
        self.evaluator = ConstrainedLinearEvaluator(
            self.utilities, self.uniform_weights, self.arbitrary_non_agreement_cost, None)
        self.violating_offer = Offer({
            "issue0": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue1": {"0": 0.0, "1": 0.0, "2": 1.0},
            "issue2": {"0": 0.0, "1": 0.0, "2": 1.0}
        })
        self.generator = ConstrainedEnumGenerator(
            self.neg_space, self.utilities, self.evaluator, self.arbitrary_reservation_value, None)
        self.difficult_constraint = AtomicConstraint("issue2", "2")
        self.generator.add_constraint(self.difficult_constraint)

    def test_responds_to_violating_offer_with_constraint(self):
        self.generator.add_constraint(self.difficult_constraint)
        constr = self.generator.find_violated_constraint(self.violating_offer)
        self.assertEqual(constr, self.difficult_constraint)

    def test_generates_best_offer_first_time(self):
        best_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 1.0, 'issue2_2': 0.0}))
        generated_offer = self.generator.generate_offer()
        self.assertEqual(best_offer, generated_offer)

    def test_generates_next_best_offer_second_time(self):
        next_best_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 1.0, 'issue2_2': 0.0}))

        _ = self.generator.generate_offer()
        second = self.generator.generate_offer()
        self.assertEqual(next_best_offer, second)

    def test_generates_next_next_best_offer_third_time(self):
        next_next_best_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 1.0, 'issue2_2': 0.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        thrid = self.generator.generate_offer()
        self.assertEqual(next_next_best_offer, thrid)

    def test_generates_expected_offer_forth_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
             'issue1_0': 0.0, 'issue1_1': 1.0, 'issue1_2': 0.0,
             'issue2_0': 0.0, 'issue2_1': 1.0, 'issue2_2': 0.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        offer = self.generator.generate_offer()
        self.assertEqual(expected_offer, offer)

    def test_generates_expected_offer_fith_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 1.0, 'issue1_2': 0.0,
             'issue2_0': 0.0, 'issue2_1': 1.0, 'issue2_2': 0.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        offer = self.generator.generate_offer()
        offer_diff = self.evaluator.calc_offer_utility(
            expected_offer)-self.evaluator.calc_offer_utility(offer)
        self.assertEqual(expected_offer, offer, offer_diff)

    def test_terminates_after_options_become_unacceptable(self):
        self.generator = ConstrainedEnumGenerator(
            self.neg_space, self.utilities, self.evaluator, 100, None)

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

    def test_own_offer_does_not_violate_constraint(self):
        self.generator.add_constraint(AtomicConstraint("issue1", "2"))
        generated_offer = self.generator.generate_offer()
        self.assertTrue(
            self.generator.satisfies_all_constraints(generated_offer))

    def test_generates_valid_offers_when_constraints_are_present(self):
        self.generator.add_constraints({AtomicConstraint("issue0", "2"),
                                        AtomicConstraint("issue1", "2"),
                                        AtomicConstraint("issue2", "2")})
        generated_offer = self.generator.generate_offer()
        self.generator.satisfies_all_constraints(generated_offer)

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"issue1_0": -100000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("issue1", "0")
                        in self.generator.constraints)

    def test_all_values_can_get_constrained(self):
        low_util_dict = {"issue2_{i}".format(
            i=i): -100000 for i in range(len(self.neg_space['issue2']))}
        self.generator.add_utilities(low_util_dict)
        constraints = self.generator.constraints
        snd_issue_constraints = set([constr for constr in constraints if constr.issue ==
                                     "issue2"])
        self.assertEqual(constraints, snd_issue_constraints, constraints)
        self.assertEqual(
            len(snd_issue_constraints),
            len(self.neg_space['issue2']), constraints)

    def test_multiple_issues_can_get_constrained(self):
        low_util_dict = {"issue2_0": -1000, "issue0_1": -1000}
        self.generator.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("issue2", "0"), AtomicConstraint(
            "issue0", "1")}.issubset(self.generator.constraints))

    def test_terminates_after_constrains_become_unsatisfiable(self):
        self.generator.add_constraints({
            AtomicConstraint("issue0", "0"),
            AtomicConstraint("issue0", "1"),
            AtomicConstraint("issue0", "2")})

        with self.assertRaises(StopIteration):
            _ = self.generator.generate_offer()
