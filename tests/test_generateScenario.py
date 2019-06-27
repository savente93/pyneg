import unittest

from generateScenario import *


class TestConfigurationGeneration(unittest.TestCase):

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

    def tearDown(self) -> None:
        pass

    def test_generates_matrices_of_right_length(self):
        a, b = generate_utility_matrices(self.standard_n, self.standard_m, self.standard_tau_a)
        self.assertEqual(len(a), self.standard_n)
        self.assertEqual(len(b), self.standard_n)

    def test_generates_matrices_of_right_width(self):
        a, b = generate_utility_matrices(self.standard_n, self.standard_m, self.standard_tau_a)
        self.assertTrue(all([len(a[key]) == self.standard_m for key in a.keys()]))
        self.assertTrue(all([len(b[key]) == self.standard_m for key in b.keys()]))

    def test_tau_of_0_creates_only_0_or_1(self):
        a, b = generate_utility_matrices(self.standard_n, self.standard_m, -1)
        self.assertFalse(not any([bool(val) for val in a[issue].values()] for issue in a.keys()))
        self.assertTrue(all([bool(val) for val in b[issue].values()] for issue in b.keys()))

    def test_trivial_2_by_2_example_is_counted_correctly(self):
        u_a, u_b = generate_utility_matrices(2, 2, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 1, 1)
        self.assertEqual(a, 3)
        self.assertEqual(b, 3)
        self.assertEqual(both, 2)

    def test_rho_0_counts_all_possibilities_2_by_2(self):
        u_a, u_b = generate_utility_matrices(2, 2, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == 4)

    def test_rho_0_counts_all_possibilities_2_by_3(self):
        u_a, u_b = generate_utility_matrices(2, 3, 1)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == 3**2)

    def test_rho_0_counts_all_possibilities_5_by_6(self):
        u_a, u_b = generate_utility_matrices(self.standard_n, self.standard_m, self.standard_tau_a)
        a, b, both = count_acceptable_offers(u_a, u_b, 0, 0)
        self.assertTrue(a == b == both == self.standard_m ** self.standard_n)

    def test_rho_exceeds_n_makes_counts_0(self):
        u_a, u_b = generate_utility_matrices(self.standard_n, self.standard_m, self.standard_tau_a)
        a, b, both = count_acceptable_offers(u_a, u_b, self.standard_n + 1, self.standard_n + 1)
        self.assertTrue(a == b == both == 0)

    def test_sum_of_rho_exceeds_n_makes_counts_0(self):
        u_a, u_b = generate_utility_matrices(self.standard_n, self.standard_m, self.standard_tau_a)
        a, b, both = count_acceptable_offers(u_a, u_b, self.standard_n / 2, self.standard_n/2 + 1)
        self.assertTrue(both == 0)
