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

        self.invalidSparseTestOffer = {
            "boolean": {"True": -1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.sparseNestedTestOffer = {
            "boolean": {"True": 1},
            "integer": {"2": 1},
            "float": {"0.6": 1}
        }

        # should have a utility of 100
        self.denseNestedTestOffer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i*0.1): 0 for i in range(10)}
        }
        self.denseNestedTestOffer["integer"]["3"] = 1
        self.denseNestedTestOffer['float']["0.6"] = 1


        self.agent = ConstrProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.agent.agentName = "agent"
        self.opponent = ConstrProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.opponent.agentName = "opponent"
        self.agent.setupNegotiation(self.genericIssues)

        self.acceptanceMessage = Message(self.agent.agentName,self.opponent.agentName,"accept",self.denseNestedTestOffer)
        self.acceptanceMessage = Message(self.agent.agentName, self.opponent.agentName, "terminate",
                                         self.denseNestedTestOffer)
        self.constraintMessage = Message(self.agent.agentName,self.opponent.agentName,
            "offer", self.denseNestedTestOffer, self.arbitraryConstraint)

    def tearDown(self):
        pass

    def test_receiveValidNegotiationRequest(self):
        self.assertTrue(self.opponent.receiveNegotiationRequest(
            self.agent, self.genericIssues))

    def test_receiveAcceptationMessageEndsNegotiation(self):
        self.agent.negotiationActive = True
        self.agent.receiveMessage(terminationMessage)
        self.assertFalse(self.agent.negotiationActive)

    def test_receiveAcceptationMessageNegotiationWasUncusessful(self):
        terminationMessage = Message("accept")
        self.agent.receiveMessage(terminationMessage)
        self.assertTrue(self.agent.sucessfull)

    def test_receiveTerminationMessageEndsNegotiation(self):
        terminationMessage = Message(self.agent.agentName,self"terminate")
        self.agent.negotiationActive = True
        self.agent.receiveMessage(terminationMessage)
        self.assertFalse(self.agent.negotiationActive)

    def test_receiveTerminationMessageNegotiationWasUncusessful(self):
        terminationMessage = Message("terminate")
        self.agent.receiveMessage(terminationMessage)
        self.assertFalse(self.agent.successful)

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
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        response = self.agent.receiveMessage(Message(kind="offer", content={
            "boolean": {"False": 1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }))
        self.assertEqual(
            Message(kind="constraint", content=self.arbitraryConstraint), response)

    def test_receivingConstraintAdjustsStratAccordingly(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertAlmostEqual(self.agent.stratDict['boolean']['False'], 0)

    def test_testingConstraintSatisfactionDoesntAffectStoredConstraints(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.agent.satisfiesAllConstraints(
            self.denseNestedTestOffer)
        self.assertTrue(self.agent.ownConstraints ==
                        set([self.arbitraryConstraint]))

    def test_negotiationsWithConstraintsEndsSucessfully(self):
        self.agent.addOwnConstraint(self.arbitraryConstraint)
        self.assertTrue(self.agent.negotiate(self.opponent))
