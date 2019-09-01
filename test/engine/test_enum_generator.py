from unittest import TestCase
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict
from pyneg.engine import EnumGenerator, LinearEvaluator
from pyneg.comms import Offer
from numpy import arange


class TestEnumGenerator(TestCase):

    def setUp(self):
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            arange(9).reshape((3, 3))**2, arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0.1000
        self.arbitrary_non_agreement_cost = -1000
        uniform_weights = {
            issue: 1/len(values) for issue, values in self.issues.items()}
        self.evaluator = LinearEvaluator(
            self.utilities, uniform_weights, self.arbitrary_non_agreement_cost)

        self.generator = EnumGenerator(
            self.issues, self.utilities, self.evaluator, self.arbitrary_reservation_value)

    def test_generates_best_offer_first_time(self):
        best_offer = Offer(nested_dict_from_atom_dict({'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
                                                       'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                       'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}))
        generated_offer = self.generator.generate_offer()
        self.assertEqual(best_offer, generated_offer)

    def test_generates_next_best_offer_second_time(self):
        next_best_offer = Offer(nested_dict_from_atom_dict({'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
                                                            'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
                                                            'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}))

        _ = self.generator.generate_offer()
        second = self.generator.generate_offer()
        self.assertEqual(next_best_offer, second)

    def test_generates_next_next_best_offer_third_time(self):
        next_next_best_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        thrid = self.generator.generate_offer()
        self.assertEqual(next_next_best_offer, thrid)

    def test_generates_expected_offer_forth_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 0.0, 'issue0_1': 0.0, 'issue0_2': 1.0,
             'issue1_0': 0.0, 'issue1_1': 1.0, 'issue1_2': 0.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        offer = self.generator.generate_offer()
        self.assertEqual(expected_offer, offer)

    def test_generates_expected_offer_fith_time(self):
        expected_offer = Offer(nested_dict_from_atom_dict(
            {'issue0_0': 1.0, 'issue0_1': 0.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 0.0, 'issue1_2': 1.0,
             'issue2_0': 0.0, 'issue2_1': 0.0, 'issue2_2': 1.0}
        ))

        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        _ = self.generator.generate_offer()
        offer = self.generator.generate_offer()
        self.assertEqual(expected_offer, offer)

    def test_terminates_first_time_if_no_options_are_acceptable(self):
        self.generator = EnumGenerator(
            self.issues, self.utilities, self.evaluator, 1)

        _ = self.generator.generate_offer()

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

    def test_terminates_after_options_become_unacceptable(self):
        self.generator = EnumGenerator(
            self.issues, self.utilities, self.evaluator, 1.1)

        with self.assertRaises(StopIteration):
            _ = self.generator.generate_offer()
