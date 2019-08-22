import unittest

from atomic_constraint import AtomicConstraint


class TestAtomicConstraint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.test_atomic_constraint = AtomicConstraint("dummy1", "True")

    def tearDown(self):
        pass

    def test_no_good_with_different_issue_are_unequal(self):
        other = AtomicConstraint("Dummy1", "True")
        self.assertFalse(self.test_atomic_constraint == other)

    def test_no_good_with_different_value_are_unequal(self):
        other = AtomicConstraint("dummy1", "False")
        self.assertFalse(self.test_atomic_constraint == other)

    def test_equal_no_goods_are_equal(self):
        self.assertTrue(self.test_atomic_constraint,
                        self.test_atomic_constraint)

    def test_dict_of_no_good_contains_it(self):
        d = {self.test_atomic_constraint: "hello World"}
        self.assertTrue(self.test_atomic_constraint in d.keys())

    def test_satisfying_value_returns_true(self):
        self.assertTrue(
            self.test_atomic_constraint.is_satisfied_by_assignment("dummy1", "False"))

    def test_non_satisfying_value_returns_false(self):
        self.assertFalse(
            self.test_atomic_constraint.is_satisfied_by_assignment("dummy1", "True"))

    def test_no_good_is_not_equal_to_other_type_object(self):
        self.assertFalse(self.test_atomic_constraint == "string")
