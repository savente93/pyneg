import unittest
import numpy as np
from pyneg.utils import generate_binary_utility_matrices, count_acceptable_offers, neg_scenario_from_util_matrices


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        self.standard_n = 5
        self.standard_m = 6
        self.standard_tau_a = 3
        self.u_a = np.zeros((self.standard_n, self.standard_m))
        self.u_b = np.zeros((self.standard_n, self.standard_m))

    def tearDown(self) -> None:
        pass

    def test_generates_matrices_of_right_dimentions(self):
        a, b = generate_binary_utility_matrices(
            self.u_a.shape, self.standard_tau_a)
        self.assertTrue(a.shape == (self.standard_n, self.standard_m))
        self.assertTrue(b.shape == (self.standard_n, self.standard_m))

    def test_tau_of_0_creates_only_0_or_1(self):
        a, b = generate_binary_utility_matrices(self.u_a.shape, 0)
        self.assertTrue(np.all(a == 0))
        self.assertTrue(np.all(b == 1))

    def test_trivial_2_by_2_example_is_counted_correctly(self):
        u_a, u_b = generate_binary_utility_matrices((2, 2), 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 1 / 3, 1 / 3)
        self.assertEqual(a, 3)
        self.assertEqual(b, 3)
        self.assertEqual(both, 2)

    def test_rho_0_counts_all_possibilities_2_by_2(self):
        self.standard_m = 2
        self.standard_n = 2
        self.u_a = np.zeros((self.standard_n, self.standard_m))
        self.u_b = np.zeros((self.standard_n, self.standard_m))
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == 4)

    def test_rho_0_counts_all_possibilities_2_by_3(self):
        self.standard_m = 3
        self.standard_n = 2
        self.u_a = np.zeros((self.standard_n, self.standard_m))
        self.u_b = np.zeros((self.standard_n, self.standard_m))
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == 3 ** 2)

    def test_rho_0_counts_all_possibilities_5_by_6(self):
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == self.standard_m ** self.standard_n)

    def test_rho_exceeds_n_makes_counts_0(self):
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        a, b, both = count_acceptable_offers(
            u_a, u_b, self.standard_n + 1, self.standard_n + 1)
        self.assertTrue(a == b == both == 0)

    def test_sum_of_rho_exceeds_n_makes_counts_0(self):
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        _, _, both = count_acceptable_offers(
            u_a, u_b, self.standard_n / 2, self.standard_n / 2 + 1)
        self.assertTrue(both == 0)

    def test_neg_scenario_from_util_matrices_returns_propper_types(self):
        u_a, u_b = generate_binary_utility_matrices(self.u_a.shape, 1)
        issues, utils_a, utils_b = neg_scenario_from_util_matrices(u_a, u_b)
        # check that issue has type Dict[str, List[str]]
        self.assertTrue(isinstance(issues, dict))
        self.assertTrue(isinstance(next(iter(issues.values())),
                                   list), type(next(iter(issues.values()))))
        self.assertTrue(isinstance(
            next(iter(next(iter(issues.values())))), str))

        self.assertTrue(isinstance(utils_a, dict))
        self.assertTrue(isinstance(next(iter(utils_a.values())),
                                   float))
        self.assertTrue(isinstance(next(iter(utils_a.keys())), str))

        self.assertTrue(isinstance(utils_b, dict))
        self.assertTrue(isinstance(next(iter(utils_b.values())), float))
        self.assertTrue(isinstance(next(iter(utils_b.keys())), str))
