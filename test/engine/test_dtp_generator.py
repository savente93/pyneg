from unittest import TestCase

from pyneg.comms import Offer
from pyneg.engine import DTPGenerator


class TestDTPGenerator(TestCase):

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

        self.generator = DTPGenerator(self.neg_space, self.utilities,
                                      self.non_agreement_cost, self.reservation_value,
                                      self.kb)

    def test_dtp_generates_optimal_bid_in_simple_negotiation_setting(self):
        result = self.generator.generate_offer()
        self.assertEqual(result, self.optimal_offer)

    def test_extending_full_offer_does_nothing(self):
        temp_issues = {"issue0": ["0", "1"],
                       "issue1": ["0", "1"],
                       "issue2": ["0", "1"]}
        temp_utils = {"issue0_1": 10.0}
        sparese_offer = {"issue0_1": 1.0,
                         "issue1_1": 1.0,
                         "issue2_1": 1.0,
                         }
        self.generator = DTPGenerator(
            temp_issues, temp_utils, self.non_agreement_cost, 0, [])

        self.assertTrue(
            len(self.generator.extend_partial_offer(sparese_offer)))

    def test_extend_parial_offer(self):
        temp_issues = {"issue0": ["0", "1"],
                       "issue1": ["0", "1"],
                       "issue2": ["0", "1"]}
        temp_utils = {"issue0_1": 10.0}
        partial_offer = {"issue0_1": 1.0}
        self.generator = DTPGenerator(
            temp_issues, temp_utils, self.non_agreement_cost, 0, [])
        extended_offers = self.generator.extend_partial_offer(partial_offer)

        # the best offer was popped during the initialisation of the generator
        # so just put it back for testing purposes
        self.assertEqual({
            Offer({"issue0": {"0": 0.0, "1": 1.0},
                   "issue1": {"0": 0.0, "1": 1.0},
                   "issue2": {"0": 0.0, "1": 1.0}}),

            Offer({"issue0": {"0": 0.0, "1": 1.0},
                   "issue1": {"0": 0.0, "1": 1.0},
                   "issue2": {"0": 1.0, "1": 0.0}}),

            Offer({"issue0": {"0": 0.0, "1": 1.0},
                   "issue1": {"0": 1.0, "1": 0.0},
                   "issue2": {"0": 0.0, "1": 1.0}}),

            Offer({"issue0": {"0": 0.0, "1": 1.0},
                   "issue1": {"0": 1.0, "1": 0.0},
                   "issue2": {"0": 1.0, "1": 0.0}})},
            extended_offers)

    def test_doesnt_generate_same_offer_five_times(self):
        # since some elements might be randomly picked it can sometimes happen that the elements are the same but it
        # shouldn't keep happening so we'll try it a couple of times
        last_offer = self.generator.generate_offer()
        for i in range(5):
            new_offer = self.generator.generate_offer()
            self.assertNotEqual(last_offer, new_offer, i)
            last_offer = new_offer

    def test_generatingOfferRecordsItInUtilities(self):
        _ = self.generator.generate_offer()
        offer = Offer(
            {"'float_0.1'": 1.0, 'boolean_True': 1.0, 'boolean_False': 0.0, 'integer_1': 0.0, 'integer_3': 0.0,
             'integer_4': 0.0,
             'integer_5': 0.0, 'integer_9': 1.0})
        self.assertTrue(offer.get_sparse_repr()
                        in self.generator.generated_offers.keys())

    def test_generatesValidOffersWhenNoUtilitiesArePresent(self):
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.generator = DTPGenerator(
            self.neg_space,
            self.arbitrary_utilities,
            self.non_agreement_cost,
            self.reservation_value,
            self.kb)

        # should not raise an exception
        _ = self.generator.generate_offer()

    def test_ends_negotiation_if_offers_generated_are_not_acceptable(self):
        # simply a set of impossible utilities to check that we exit immediately
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.generator = DTPGenerator(
            self.neg_space,
            self.arbitrary_utilities,
            self.non_agreement_cost,
            500,
            self.kb)

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()
