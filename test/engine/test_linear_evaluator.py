from unittest import TestCase


class TestLinearEvaluator(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        raise NotImplementedError()


#     def test_calc_offer_utility_python(self):
#         self.agent.set_utilities(self.arbitrary_utilities)
#         self.agent.setup_negotiation(self.generic_issues)
#         self.agent.init_uniform_strategy()
#         expected_offer_utility = 100/3-1000/3 + pi/3

#         self.assertAlmostEqual(self.agent.calc_offer_utility(
#             self.nested_test_offer), expected_offer_utility)

#     def test_calc_strat_utility_python(self):
#         self.agent.set_utilities(self.arbitrary_utilities)
#         self.agent.setup_negotiation(self.generic_issues)
#         self.agent.init_uniform_strategy()
#         expected_uniform_strat_util = (
#             100*0.5) / 3 + (-1000*0.1)/3 + (-3.2*0.1 + pi*0.1)/3
#         self.assertAlmostEqual(self.agent.calc_strat_utility(
#             self.agent.strat_dict), expected_uniform_strat_util)


#     def test_accepts_acceptable_offer(self):
#         self.nested_test_offer['integer']["2"] = 0
#         self.nested_test_offer['integer']["3"] = 1
#         self.agent.record_message(
#             Message(self.opponent, self.agent, kind="offer", offer=self.nested_test_offer))
#         self.agent.generate_next_message_from_transcript()
#         self.assertTrue(
#             self.agent.successful and not self.agent.negotiation_active and self.agent.message_count == 1)

#         self.arbitrary_utilities = {
#             "boolean_True": 100,
#             "integer_2": -1000,
#             "'float_0.1'": -3.2,
#             "'float_0.5'": pi
#             # TODO still need to look at compound and negative atoms
#         }
