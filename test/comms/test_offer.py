from unittest import TestCase

from pyneg.comms import Offer


class TestOffer(TestCase):

    def setUp(self):
        self.neg_space = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }
        self.uniform_strat_dict = {
            "boolean": {"True": 0.5, "False": 0.5},
            "integer": {str(i): 0.1 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.1 for i in range(10)}
        }

        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["3"] = 1
        self.nested_test_offer['float']["0.6"] = 1

    def test_strat_with_neg_numb_is_invalid(self):
        self.nested_test_offer["boolean"]["True"] = -0.5
        with self.assertRaises(ValueError):
            Offer(self.nested_test_offer)

    def test_strat_with_whole_numb_is_invalid(self):
        self.nested_test_offer["boolean"]["True"] = 20
        with self.assertRaises(ValueError):
            Offer(self.nested_test_offer)

    def test_valid_dict_is_valid(self):
        Offer(self.nested_test_offer)

    def test_non_binary_offer_is_rejected(self):
        with self.assertRaises(ValueError):
            Offer(self.uniform_strat_dict)

    def test_repr(self):
        print(Offer(self.nested_test_offer).get_sparse_str_repr())

