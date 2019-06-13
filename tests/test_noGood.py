import unittest
from constraint import AtomicConstraint


class TestNoGood(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.testNoGood = AtomicConstraint("dummy1", "True")

    def tearDown(self):
        pass

    def test_noGoodWithDifferentIssueAreUnequal(self):
        other = AtomicConstraint("Dummy1", "True")
        self.assertFalse(self.testNoGood == other)

    def test_noGoodWithDifferentValueAreUnequal(self):
        other = AtomicConstraint("dummy1", "False")
        self.assertFalse(self.testNoGood == other)

    def test_equalNoGoodsAreEqual(self):
        self.assertTrue(self.testNoGood, self.testNoGood)

    def test_dictOfNoGoodContainsIt(self):
        d = {self.testNoGood: "hello World"}
        self.assertTrue(self.testNoGood in d.keys())

    def test_satisfyingValueReturnsTrue(self):
        self.assertTrue(
            self.testNoGood.isSatisfiedByAssignement("dummy1", "False"))

    def test_nonSatisfyingValueReturnsFalse(self):
        self.assertFalse(
            self.testNoGood.isSatisfiedByAssignement("dummy1", "True"))

    def test_noGoodIsNotEqualToOtherTypeObject(self):
        self.assertFalse(self.testNoGood == "string")
