import unittest
from src.constraint import NoGood


class TestNoGood(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.testNoGood = NoGood("dummy1", "True")

    def tearDown(self):
        pass

    def test_noGoodWithDifferentIssueAreUnequal(self):
        other = NoGood("Dummy1", "True")
        self.assertFalse(self.testNoGood == other)

    def test_noGoodWithDifferentValueAreUnequal(self):
        other = NoGood("dummy1", "False")
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
