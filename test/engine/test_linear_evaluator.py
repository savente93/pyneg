from unittest import TestCase
from pyneg.engine import LinearEvaluator
from pyneg.comms import Offer
from math import pi


class TestLinearEvaluator(TestCase):

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
        self.reservation_value = 0
        self.non_agreement_cost = -1000

        # should have a utility of 100
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["2"] = 1
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

        self.uniform_strat = {
            "boolean": {"True": 0.5, "False": 0.5},
            "integer": {str(i): 0.1 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.1 for i in range(10)}
        }

        self.uniform_weights = {
            issue: 1/len(self.neg_space.keys()) for issue in self.neg_space.keys()}

        self.evaluator = LinearEvaluator(
            self.utilities, self.uniform_weights, self.non_agreement_cost)

    def test_calc_offer_utility(self):
        expected_offer_utility = 100/3

        self.assertAlmostEqual(self.evaluator.calc_offer_utility(
            self.nested_test_offer), expected_offer_utility)

    def test_calc_optimal_offer_utility(self):
        expected_offer_utility = 100/3 + 100/3 + 1/3

        self.assertAlmostEqual(self.evaluator.calc_offer_utility(
            self.optimal_offer), expected_offer_utility)

    def test_calc_strat_utility_python(self):
        expected_uniform_strat_util = (
            100*0.5+0.5*10) / 3 + (100*0.1+10*0.1+0.1*0.1-10*0.1-100*0.1)/3 + (1*0.1)/3
        self.assertAlmostEqual(self.evaluator.calc_strat_utility(
            self.uniform_strat), expected_uniform_strat_util)
