from unittest import TestCase

from pyneg.engine import Strategy
from pyneg.utils import atom_dict_from_nested_dict


class TestStrategy(TestCase):

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

    def test_strat_with_neg_numb_is_invalid(self):
        self.uniform_strat_dict["boolean"]["True"] = -0.5
        with self.assertRaises(ValueError):
            Strategy(self.uniform_strat_dict)

    def test_strat_with_whole_numb_is_invalid(self):
        self.uniform_strat_dict["boolean"]["True"] = 20
        with self.assertRaises(ValueError):
            Strategy(self.uniform_strat_dict)

    def test_strat_with_non_dist_is_invalid(self):
        self.uniform_strat_dict = {
            "boolean": {"True": 0.4, "False": 0.5},
            "integer": {str(i): 0.1 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.1 for i in range(10)}
        }
        with self.assertRaises(ValueError):
            Strategy(self.uniform_strat_dict)

    def test_valid_dict_is_valid(self):
        Strategy(self.uniform_strat_dict)

    def test_valid_atom_dict_is_accepted(self):
        Strategy(atom_dict_from_nested_dict(self.uniform_strat_dict))
