import unittest
from math import pi
from constrProbAwareAgent import ConstrProbAwareAgent
from message import Message
from constraint import NoGood


class TestConstrProbAwareAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.genericIssues = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }

        self.arbitraryConstraint = NoGood("boolean", "False")
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "integer_2": -1000,
            "'float_0.1'": -3.2,
            "'float_0.5'": pi
            # TODO still need to look at compound and negative atoms
        }
        self.arbitraryKb = [
            "boolean_True :- integer_2, 'float_0.1'."
        ]
        self.arbitraryReservationValue = 0
        self.arbitraryNonAgreementCost = -1000

        # should have a utility of 100
        self.denseNestedTestOffer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i*0.1): 0 for i in range(10)}
        }
        self.denseNestedTestOffer["integer"]["3"] = 1
        self.denseNestedTestOffer['float']["0.6"] = 1


        self.violatingOffer = {
            "boolean": {"True": 0, "False": 1},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i*0.1): 0 for i in range(10)}
        }
        self.violatingOffer["integer"]["3"] = 1
        self.violatingOffer['float']["0.6"] = 1

        self.agent = ConstrProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.agent.agentName = "agent"
        self.opponent = ConstrProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.opponent.agentName = "opponent"
        self.agent.setupNegotiation(self.genericIssues)
        self.agent.callForNegotiation(self.opponent, self.genericIssues)

        self.acceptanceMessage = Message(self.agent.agentName,self.opponent.agentName,"accept",self.denseNestedTestOffer)
        self.terminationMessage = Message(self.agent.agentName, self.opponent.agentName, "terminate",
                                         self.denseNestedTestOffer)
        self.constraintMessage = Message(self.agent.agentName,self.opponent.agentName,
            "offer", self.denseNestedTestOffer, self.arbitraryConstraint)
        self.offerMessage = Message(self.agent.agentName, self.opponent.agentName,
                                         "offer", self.denseNestedTestOffer)
        # print("In method: {}".format( self._testMethodName))

    def tearDown(self):
        pass

    def test_receiveConstraintSavesConstraint(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertTrue(self.arbitraryConstraint in self.agent.ownConstraints)

    def test_ownStratSatisfiesAllConstraints(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        for constr in self.agent.ownConstraints:
            self.assertTrue(constr.isSatisfiedByStrat(self.agent.stratDict))

    def test_stratViolatingConstrIsCaught(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.agent.stratDict["boolean"]["False"] = 0.5
        for constr in self.agent.ownConstraints:
            self.assertFalse(constr.isSatisfiedByStrat(self.agent.stratDict))

    def test_respondsToViolatingOfferWithConstraint(self):
        # set stratagy to something constant so we can predict what message it will generate
        self.agent.stratDict = self.denseNestedTestOffer.copy()
        self.agent.addOwnConstraint(NoGood("boolean","False"))
        self.agent.receiveMessage(Message(self.opponent.agentName,self.agent.agentName,"offer",self.violatingOffer))
        response = self.agent.generateNextMessageFromTranscript()
        self.assertEqual(Message(self.agent.agentName,self.opponent.agentName,"offer",self.agent.stratDict, NoGood("boolean","False")),
                         response)

    def test_receivingConstraintAdjustsStratAccordingly(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertAlmostEqual(self.agent.stratDict['boolean']['False'], 0)

    def test_testingConstraintSatisfactionDoesntAffectStoredConstraints(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.agent.satisfiesAllConstraints(
            self.denseNestedTestOffer)
        self.assertEqual(self.agent.ownConstraints,
                        set([self.arbitraryConstraint]))

    def test_easyNegotiationsWithConstraintsEndsSuccessfully(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_doesNotAcceptViolatingOffer(self):
        # self.agent.receiveMessage(self.violatingOffer)
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertFalse(self.agent.accepts(self.violatingOffer))

    def test_worthOfViolatingOfferIsNonAgreementCost(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertEqual(self.agent.calcOfferUtility((self.violatingOffer)),self.arbitraryNonAgreementCost)

    def test_endsNegotiationAfterFindingNonCompatibleConstraints(self):
        opponentConstraint = NoGood("boolean","True")
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.agent.receiveMessage(Message(self.opponent.agentName,self.agent.agentName,"offer",self.denseNestedTestOffer,constraint=opponentConstraint))
        agentResponse = self.agent.generateNextMessageFromTranscript()
        self.assertEqual(Message(self.agent.agentName,self.opponent.agentName,"terminate",None),agentResponse)

    def test_receivingConstraintOnBinaryConstraintDoesntResultInZeroStrategy(self):
        self.agent.stratDict = self.denseNestedTestOffer
        self.agent.receiveMessage(Message(self.opponent.agentName,self.agent.agentName,"offer",self.denseNestedTestOffer,constraint=NoGood("boolean","True")))
        # violating offer simply has the correct value for the boolean issue, there is no other connection
        self.assertEqual(self.agent.stratDict,self.violatingOffer)

    def test_receivingOfferWithConstraintRecordsConstraint(self):
        self.agent.receiveMessage(self.constraintMessage)
        self.assertTrue(self.constraintMessage.constraint in self.agent.opponentConstraints)
