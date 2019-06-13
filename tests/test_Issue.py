import unittest
from Issue import BooleanIssue, NumericIssue


class TestIssue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.booleanIssue = BooleanIssue("BooleanIssue")
        self.numericIssue = NumericIssue(
            "NumericIssue", [1, 5, 100, 2**31, -1, -3.1412341234], False)

    def tearDown(self):
        pass

    def test_repr(self):
        self.assertEqual("BooleanIssue", repr(self.booleanIssue))

    def test_BooleanIssueIsNotOrdinal(self):
        self.assertFalse(self.booleanIssue.isOrdinal)

    def test_BooleanIssueIsNotNumeric(self):
        self.assertFalse(self.booleanIssue.isNumeric)

    def test_BooleanIssueName(self):
        self.assertEqual(self.booleanIssue.name, "BooleanIssue")

    def test_NumericIssueIsOrdinal(self):
        self.assertTrue(self.numericIssue.isOrdinal)

    def test_NumericIssueIsNumeric(self):
        self.assertFalse(self.booleanIssue.isNumeric)

    def test_NumericIssueName(self):
        self.assertEqual(self.numericIssue.name, "NumericIssue")
