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
        self.boolean_issue = BooleanIssue("boolean_issue")
        self.numeric_issue = NumericIssue(
            "numeric_issue", [1, 5, 100, 2 ** 31, -1, -3.1412341234], False)

    def tearDown(self):
        pass

    def test_repr(self):
        self.assertEqual("boolean_issue", repr(self.boolean_issue))

    def test_boolean_issue_is_not_ordinal(self):
        self.assertFalse(self.boolean_issue.is_ordinal)

    def test_boolean_issue_is_not_numeric(self):
        self.assertFalse(self.boolean_issue.is_numeric)

    def test_boolean_issue_name(self):
        self.assertEqual(self.boolean_issue.name, "boolean_issue")

    def test_numeric_issue_is_ordinal(self):
        self.assertTrue(self.numeric_issue.is_ordinal)

    def test_numeric_issue_is_numeric(self):
        self.assertFalse(self.boolean_issue.is_numeric)

    def test_numeric_issue_name(self):
        self.assertEqual(self.numeric_issue.name, "numeric_issue")
