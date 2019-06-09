import unittest
from math import pi
from constraintNegotiationAgent import ConstraintNegotiationAgent
from message import Message
from constraint import NoGood
from numpy.random import choice


class TestConstraintNegotiationAgent(unittest.TestCase):

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

        self.arbitraryOwnConstraint = NoGood("boolean", "False")
        self.arbitraryOpponentConstraint = NoGood("boolean", "True")
        self.arbitraryIntegerConstraint = NoGood("integer","2")
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

        self.agent = ConstraintNegotiationAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.agent.agentName = "agent"
        self.opponent = ConstraintNegotiationAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.opponent.agentName = "opponent"
        self.agent.setupNegotiation(self.genericIssues)
        self.agent.callForNegotiation(self.opponent, self.genericIssues)

        self.acceptanceMessage = Message(self.agent.agentName,self.opponent.agentName, "accept", self.denseNestedTestOffer)
        self.terminationMessage = Message(self.agent.agentName, self.opponent.agentName, "terminate",
                                         self.denseNestedTestOffer)
        self.constraintMessage = Message(self.agent.agentName,self.opponent.agentName,
            "offer", self.denseNestedTestOffer, self.arbitraryOpponentConstraint)
        self.offerMessage = Message(self.agent.agentName, self.opponent.agentName,
                                         "offer", self.denseNestedTestOffer)
        # print("In method: {}".format( self._testMethodName))

    def tearDown(self):
        pass

    def test_receiveingOwnConstraintSavesConstraint(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.assertTrue(self.arbitraryOwnConstraint in self.agent.ownConstraints)

    def test_receiveingOpponentConstraintSavesConstraint(self):
        self.agent.addOpponentConstraint(self.arbitraryOpponentConstraint)
        self.assertTrue(self.arbitraryOpponentConstraint in self.agent.opponentConstraints)

    def test_ownStratSatisfiesAllConstraints(self):
        # make sure that these constraints are compatable
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.agent.addOpponentConstraint(self.arbitraryIntegerConstraint)
        for constr in self.agent.getAllConstraints():
            self.assertTrue(constr.isSatisfiedByStrat(self.agent.stratDict), constr)

    def test_stratViolatingConstrIsCaught(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
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

    def test_receivingOwnConstraintAdjustsStratAccordingly(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.assertAlmostEqual(self.agent.stratDict[self.arbitraryOwnConstraint.issue][self.arbitraryOwnConstraint.value], 0)

    def test_receivingOpponentConstraintAdjustsStratAccordingly(self):
        self.agent.addOpponentConstraint(self.arbitraryOpponentConstraint)
        self.assertAlmostEqual(self.agent.stratDict[self.arbitraryOpponentConstraint.issue][self.arbitraryOpponentConstraint.value], 0)


    def test_testingConstraintSatisfactionDoesntAffectStoredConstraints(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.agent.satisfiesAllConstraints(
            self.denseNestedTestOffer)
        self.assertEqual(self.agent.ownConstraints,
                        set([self.arbitraryOwnConstraint]))

    def test_easyNegotiationsWithConstraintsEndsSuccessfully(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.assertTrue(self.agent.negotiate(self.opponent))

    def test_doesNotAcceptViolatingOffer(self):
        # self.agent.receiveMessage(self.violatingOffer)
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.assertFalse(self.agent.accepts(self.violatingOffer))

    def test_worthOfViolatingOfferIsNonAgreementCost(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.assertEqual(self.agent.calcOfferUtility((self.violatingOffer)),self.arbitraryNonAgreementCost)

    def test_endsNegotiationAfterFindingNonCompatibleConstraints(self):
        opponentConstraint = NoGood("boolean","True")
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
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

    def test_negotiationWithIncompatableConstraintsFails(self):
        # just to make sure the tests don't take for ever
        self.agent.maxRounds = 20
        self.agent.maxRounds = 20
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.opponent.addOwnConstraint(NoGood("boolean","True"))
        self.agent.negotiate(self.opponent)
        self.assertFalse(self.agent.successful or self.opponent.successful)

    def test_wontGenerateOffersWhenIncompatableConstraintsArePresent(self):
        self.agent.addOpponentConstraint(self.arbitraryOpponentConstraint)
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        with self.assertRaises(RuntimeError):
            self.agent.generateOffer()

    # def test_generatesOffersThatSatisfyConstraints(self):
    #     trails = 50
    #     self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
    #     self.agent.addOpponentConstraint(self.arbitraryIntegerConstraint)
    #     for _ in range(trails):
    #         offer = self.agent.generateOfferMessage().offer
    #         self.assertTrue(self.agent.satisfiesAllConstraints(offer))

    def test_addingRandomConstraintsAdjustsStrategyCorrectly(self):
        iters = 10
        for _ in range(iters):
            issue = choice(list(self.genericIssues.keys()))
            if issue == "boolean":
                continue
            value = str(choice(list(self.genericIssues[issue])))
            self.agent.addOwnConstraint(NoGood(issue, value))
            self.assertAlmostEqual(self.agent.stratDict[issue][value],0,msg="failed with constraint base: {}".format(self.agent.ownConstraints))

    def test_refusesNegotiationIfConstraintsAreIncompatable(self):
        self.agent.addOwnConstraint(self.arbitraryOwnConstraint)
        self.agent.addOwnConstraint(self.arbitraryOpponentConstraint)
        self.assertFalse(self.agent.receiveNegotiationRequest(self.opponent,self.genericIssues))