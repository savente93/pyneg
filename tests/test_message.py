import unittest
from message import Message
from constraint import NoGood, Constraint


class TestMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.genericOffer = {"first": {"True": 1}, "second": {
            "False": 1}, "third": {"-3": 1}, "forth": {"1.8": 1}}
        self.emptyMessage = Message("A", "B", "empty", None)
        self.acceptMessage = Message("A", "B", "accept", self.genericOffer)
        self.terminationMessage = Message(
            "A", "B", "terminate", self.genericOffer)
        self.constraintMessage = Message(
            "A", "B", "offer", self.genericOffer, NoGood("dummy1", "True"))
        self.offerMessage = Message("A", "B",
                                    "offer", self.genericOffer)

        self.offerString = "    first: True\n    second: False\n    third: -3\n    forth: 1.8"
        self.offerMessageString = "Message(A, B, offer, \n{offer}\n)".format(
            offer=self.offerString)
        self.emptyMessageString = "Message(A, B, empty)".format(
            offer=self.offerString)
        self.acceptMessageString = "Message(A, B, accept, \n{}\n)".format(
            self.offerString)
        self.constraintMessageString = "Message(A, B, offer, \n{offer}, \n{constraint}\n)".format(
            offer=self.offerString, constraint=NoGood("dummy1", "True"))
        self.terminationMessageString = "Message(A, B, terminate, \n{}\n)".format(
            self.offerString)

    def tearDown(self):
        pass

    def test_emptyMessageCantHaveContent(self):
        with self.assertRaises(ValueError):
            Message("A", "B", "empty", "content")

    def test_invalidMessageKindRaisesValueError(self):
        with self.assertRaises(ValueError):
            Message("A", "B", "Unknown type", "random content")

    def test_constraintMessageWithWrongDataTypeRaisesValueError(self):
        with self.assertRaises(ValueError):
            Message("A", "B", "constraint", "wrong data type")

    def test_getConstraintFromNonConstraintMessageRaisesError(self):
        with self.assertRaises(ValueError):
            self.emptyMessage.getConstraint()

    def test_getOffer(self):
        self.assertEqual(self.offerMessage.offer, self.genericOffer)

    def test_getConstraint(self):
        self.assertEqual(self.constraintMessage.getConstraint(),
                         NoGood("dummy1", "True"))

    def test_emptyMessageIsEmpty(self):
        self.assertTrue(self.emptyMessage.isEmpty())

    def test_emptyMessageIsNotTermination(self):
        self.assertFalse(self.emptyMessage.isTermination())

    def test_emptyMessageIsNotOffer(self):
        self.assertFalse(self.emptyMessage.isOffer())

    def test_emptyMessageHasNotConstraint(self):
        self.assertFalse(self.emptyMessage.hasConstraint())

    def test_emptyMessageIsNotAcceptation(self):
        self.assertFalse(self.emptyMessage.isAcceptance())

    def test_acceptationMessageIsNotEmtpy(self):
        self.assertFalse(self.acceptMessage.isEmpty())

    def test_acceptationMessageIsNotTermination(self):
        self.assertFalse(self.acceptMessage.isTermination())

    def test_acceptationMessageIsNotOffer(self):
        self.assertFalse(self.acceptMessage.isOffer())

    def test_acceptationMessageIsAcceptation(self):
        self.assertTrue(self.acceptMessage.isAcceptance())

    def test_terminationMessageIsNotEmtpy(self):
        self.assertFalse(self.terminationMessage.isEmpty())

    def test_terminationMessageIsTermination(self):
        self.assertTrue(self.terminationMessage.isTermination())

    def test_terminationMessageIsNotOffer(self):
        self.assertFalse(self.terminationMessage.isOffer())

    def test_terminationMessageIsNotAcceptation(self):
        self.assertFalse(self.terminationMessage.isAcceptance())

    def test_constraintMessageIsNotEmtpy(self):
        self.assertFalse(self.constraintMessage.isEmpty())

    def test_constraintMessageIsNotTermination(self):
        self.assertFalse(self.constraintMessage.isTermination())

    def test_constraintMessageHasConstraint(self):
        self.assertTrue(self.constraintMessage.hasConstraint())

    def test_constraintMessageIsNotAcceptation(self):
        self.assertFalse(self.constraintMessage.isAcceptance())

    def test_offerMessageIsNotEmtpy(self):
        self.assertFalse(self.offerMessage.isEmpty())

    def test_offerMessageIsNotTermination(self):
        self.assertFalse(self.offerMessage.isTermination())

    def test_offerMessageIsOffer(self):
        self.assertTrue(self.offerMessage.isOffer())

    def test_offerMessageIsNotAcceptation(self):
        self.assertFalse(self.offerMessage.isAcceptance())

    def test_eqIsReflextive(self):
        self.assertTrue(self.offerMessage == self.offerMessage)

    def test_eqIsSymmetrical(self):
        a = self.offerMessage
        b = self.offerMessage
        self.assertTrue(a == b and b == a)

    def test_offerMessageFormating(self):
        self.assertEqual(self.offerMessageString, str(self.offerMessage))

    def test_emptyMessageFormating(self):
        self.assertEqual(self.emptyMessageString, str(self.emptyMessage))

    def test_acceptMessageFormating(self):
        self.assertEqual(self.acceptMessageString,
                         str(self.acceptMessage))

    def test_terminationMessageFormating(self):
        self.assertEqual(
            self.terminationMessageString, str(self.terminationMessage))

    def test_formatEmptyOffer(self):
        self.assertEqual("", self.acceptMessage.formatOffer({}))

    def test_constraintMessageFormating(self):
        self.assertEqual(
            self.constraintMessageString, str(self.constraintMessage))

    def test_nonDictOfferRaisesError(self):
        with self.assertRaises(ValueError):
            Message("A", "B", "offer", Message(
                "A", "B", "offer", {"dummy1": {"True": 1}}))

    def test_nonEmptyMessageWithoutOfferRaisesError(self):
        with self.assertRaises(ValueError):
            Message("A", "B", "offer", None)
