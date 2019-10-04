from unittest import TestCase
from functools import reduce
from numpy import arange

from pyneg.comms import Offer
from pyneg.engine import EnumGenerator, LinearEvaluator
from pyneg.utils import neg_scenario_from_util_matrices, nested_dict_from_atom_dict


class TestEnumGenerator(TestCase):

    def setUp(self):
        self.issues, self.utilities, _ = neg_scenario_from_util_matrices(
            arange(9).reshape((3, 3)) ** 2, arange(9).reshape((3, 3)))
        self.arbitrary_reservation_value = 0
        self.max_util = 93
        self.arbitrary_non_agreement_cost = -1000
        self.uniform_weights = {
            issue: 1 / len(self.issues.keys()) for issue  in self.issues.keys()}
        self.evaluator = LinearEvaluator(
            self.utilities, self.uniform_weights, self.arbitrary_non_agreement_cost)

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
            {'issue0_0': 0.0, 'issue0_1': 1.0, 'issue0_2': 0.0,
             'issue1_0': 0.0, 'issue1_1': 1.0, 'issue1_2': 0.0,
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
            self.issues, self.utilities, self.evaluator, self.max_util + 1)

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

    def test_terminates_after_all_offers_are_generated(self):
        neg_space_size = reduce(lambda x, y: x * y, [len(self.issues[issue]) for issue in self.issues.keys()])
        offer_list = []
        for i in range(neg_space_size):
            offer = self.generator.generate_offer()
            print(offer)
            print(i)
            offer_list.append(offer)

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

    def test_generates_all_possible_offers(self):
        neg_space_size = reduce(lambda x, y: x * y, [len(self.issues[issue]) for issue in self.issues.keys()])
        offer_list = []
        for _ in range(neg_space_size):
            offer_list.append(self.generator.generate_offer())
        self.assertEqual(len(offer_list), neg_space_size)

    def test_all_offers_are_generated_in_dec_order_of_util(self):

        temp_neg_space = {
            "boolean": ["True", "False"],
            "integer": list(map(str, range(10))),
            "float": ["{0:.1f}".format(0.1 * i) for i in range(10)]
        }
        neg_space_size = reduce(lambda x, y: x * y, [len(temp_neg_space[issue]) for issue in temp_neg_space.keys()])

        temp_utilities = {
            "boolean_True": 1000.0,
            "boolean_False": 10.0,
            "integer_9": 100.0,
            "integer_3": 10.0,
            "integer_1": 0.1,
            "integer_4": -10.0,
            "integer_5": -100.0,
            "'float_0.1'": 1.0
        }
        temp_reservation_value = -(10 ** 10) + 1
        temp_non_agreement_cost = -(10 ** 10)
        evaluator = LinearEvaluator(temp_utilities, {issue: 1/3 for issue in temp_neg_space.keys()},
                                               temp_non_agreement_cost)
        generator = EnumGenerator(temp_neg_space, temp_utilities, evaluator, temp_reservation_value)
        offer = generator.generate_offer()
        util = evaluator.calc_offer_utility(offer)
        transcript = [(offer, util)]
        for i in range(neg_space_size-1):
            offer = generator.generate_offer()
            util = evaluator.calc_offer_utility(offer)
            transcript.append((offer, util))
            self.assertTrue(transcript[-1][1] <= transcript[-2][1], transcript[-5:])

        print("\n".join(map(str,transcript)))



