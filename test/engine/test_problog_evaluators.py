from unittest import TestCase

from pyneg.comms import Offer
from pyneg.engine import ProblogEvaluator
from pyneg.engine import Strategy


class TestProblogEvaluator(TestCase):

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
            "integer_5": -100
        }
        self.reservation_value = 0
        self.non_agreement_cost = -1000

        self.kb = [
            "boolean_True :- integer_2, 'float_0.1'."
        ]

        # should have a utility of 100
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["2"] = 1
        self.nested_test_offer['float']["0.6"] = 1

        self.nested_test_offer = Offer(self.nested_test_offer)

        self.uniform_strat = Strategy({
            "boolean": {"True": 0.5, "False": 0.5},
            "integer": {str(i): 0.1 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.1 for i in range(10)}
        })

        self.optimal_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.optimal_offer["integer"]["9"] = 1.0
        self.optimal_offer['float']["0.1"] = 1.0

        self.optimal_offer = Offer(self.optimal_offer)

        self.evaluator = ProblogEvaluator(
            self.neg_space, self.utilities, self.non_agreement_cost, self.kb)

    def test_calc_offer_utility(self):
        expected_offer_utility = 100

        self.assertAlmostEqual(self.evaluator.calc_offer_utility(
            self.nested_test_offer), expected_offer_utility)

    def test_calc_optimal_offer_utility(self):
        expected_offer_utility = 100 + 100

        self.assertAlmostEqual(self.evaluator.calc_offer_utility(
            self.optimal_offer), expected_offer_utility)

    def test_calc_strat_utility(self):
        expected_uniform_strat_util = (
                                              100 * 0.5 + 0.5 * 10) + (
                                                  100 * 0.1 + 10 * 0.1 + 0.1 * 0.1 - 10 * 0.1 - 100 * 0.1)
        self.assertAlmostEqual(self.evaluator.calc_strat_utility(
            self.uniform_strat), expected_uniform_strat_util)

    # see https://dtai.cs.kuleuven.be/problog/tutorial/dtproblog/01_umbrella.html
    def test_umbrella_scenario(self):
        umbrella_neg_space = {
            "umbrella": [True, False],
            "raincoat": [True, False],
        }
        umbrella_utilities = {
            "broken_umbrella": -40,
            "raincoat_True": -20,
            "umbrella_True": -2,
            "dry": 60
        }
        self.reservation_value = 0
        self.non_agreement_cost = -1000

        umbrella_kb = [
            "broken_umbrella:- umbrella_True, rain, wind.",
            "dry:- rain, raincoat_True.",
            "dry:- rain, umbrella_True, not broken_umbrella.",
            "dry:- not(rain).",
            "0.3::rain.",
            "0.5::wind."
        ]

        self.evaluator = ProblogEvaluator(
            umbrella_neg_space, umbrella_utilities, self.non_agreement_cost, umbrella_kb)
        offer = Offer({
            "umbrella": {"True": 1.0, "False": 0.0},
            "raincoat": {"True": 0.0, "False": 1.0}
        })
        util = self.evaluator.calc_offer_utility(offer)
        self.assertAlmostEqual(util, 43)
