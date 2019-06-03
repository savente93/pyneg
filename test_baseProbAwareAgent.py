import unittest as ut
from math import pi
from random import choice
from problog.logic import Term
from baseProbAwareAgent import BaseProbAwareAgent
from message import Message


class TestBaseProbAwareAgent(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # print("In method", self._testMethodName)
        self.genericIssues = {
            "boolean": ["True", "False"],
            "integer": list(map(str, list(range(10)))),
            "float": ["{0:.1f}".format(0.1 * i) for i in range(10)]
        }
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
        self.arbitraryReservationValue = 75
        self.arbitraryNonAgreementCost = -1000

        self.validSparseNestedTestOffer = {
            "boolean": {"True": 1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.validSparseAtomTestOffer = {
            "boolean_True": 1,
            "integer_2": 1,
            "'float_0.5'": 1
        }

        self.invalidSparseNestedTestOffer = {
            "boolean": {"True": -1},
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.invalidSparseNestedTestOfferwithissueMissing = {
            "integer": {"2": 1},
            "float": {"0.5": 1}
        }

        self.denseNestedTestOffer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i*0.1): 0 for i in range(10)}
        }
        self.denseNestedTestOffer["integer"]["2"] = 1
        self.denseNestedTestOffer['float']["0.5"] = 1

        self.denseAtomTestOffer = {
            "boolean_True": 1,
            "boolean_False": 0,
            "integer_0": 0,
            "integer_1": 0,
            "integer_2": 1,
            "integer_3": 0,
            "integer_4": 0,
            "integer_5": 0,
            "integer_6": 0,
            "integer_7": 0,
            "integer_8": 0,
            "integer_9": 0,
            "'float_0.0'": 0,
            "'float_0.1'": 0,
            "'float_0.2'": 0,
            "'float_0.3'": 0,
            "'float_0.4'": 0,
            "'float_0.5'": 1,
            "'float_0.6'": 0,
            "'float_0.7'": 0,
            "'float_0.8'": 0,
            "'float_0.9'": 0
        }

        self.agent = BaseProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.agent.agentName = "agent"
        self.opponent = BaseProbAwareAgent(
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost, verbose=0)
        self.opponent.agentName = "opponent"
        self.agent.setupNegotiation(self.genericIssues)
        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

        self.acceptanceMessage = Message(self.agent.agentName, self.opponent.agentName, "accept",
                                         self.denseNestedTestOffer)
        self.terminationMessage = Message(self.agent.agentName, self.opponent.agentName, "terminate",
                                          self.denseNestedTestOffer)
        self.offerMessage = Message(self.agent.agentName, self.opponent.agentName,
                                    "offer", self.denseNestedTestOffer)

    def tearDown(self):
        pass

    def test_generateDecisionFacts(self):
        expected_facts = [
            ["boolean_True", "boolean_False"],
            ["integer_0", "integer_1", "integer_2",
                "integer_3", "integer_4", "integer_5", "integer_6", "integer_7", "integer_8", "integer_9"],
            ["'float_0.0'", "'float_0.1'", "'float_0.2'",
                "'float_0.3'", "'float_0.4'", "'float_0.5'", "'float_0.6'", "'float_0.7'", "'float_0.8'", "'float_0.9'"],
        ]

        self.agent.generateDecisionFacts()

        self.assertEqual(
            self.agent.decisionFacts,
            expected_facts)

    def test_initUniformStrategy(self):
        expected_strat = {
            "boolean": {"True": 1/2, "False": 1/2},
            "integer": {str(i): 1/10 for i in range(10)},
            "float": {"{:.1f}".format(0.1*i): 1/10 for i in range(10)}
        }

        self.agent.initUniformStrategy()
        self.assertEqual(expected_strat, self.agent.stratDict)

    def test_calcOfferUtility(self):

        expectedOfferUttility = -900 + pi

        self.assertAlmostEqual(self.agent.calcOfferUtility(
            self.denseNestedTestOffer), expectedOfferUttility)

    def test_calcStratUtility(self):
        self.agent.initUniformStrategy()
        expectedUniformStratUtil = 50-100-3.2/10+pi/10
        self.assertAlmostEqual(self.agent.calcStratUtility(
            self.agent.stratDict), expectedUniformStratUtil)

    def test_accept(self):
        self.assertFalse(self.agent.accepts(
            self.denseNestedTestOffer))

    def test_umbrellaCalc(self):
        umbrellaUtils = {
            "broken_umbrella": -40,
            "raincoat_True": -20,
            "umbrella_True": -2,
            "dry": 60
        }

        umbrellaIssues = {
            "umbrella": [True, False],
            "raincoat": [True, False]
        }

        umbrellaKb = [
            "0.3::rain.",
            "0.5::wind.",
            "broken_umbrella:- umbrella_True, rain, wind.",
            "dry:- rain, raincoat_True.",
            "dry:- rain, umbrella_True, not broken_umbrella.",
            "dry:- not(rain)."
        ]

        umbrellaOffer = {
            "umbrella": {"True": 1, "False": 0},
            "raincoat": {"False": 1, "True": 0}
        }

        umbrellaAgent = BaseProbAwareAgent(
            umbrellaUtils, umbrellaKb, 0, 0, umbrellaIssues, smart=False)
        umbrellaAnswer = 43

        self.assertAlmostEqual(umbrellaAgent.calcOfferUtility(
            umbrellaOffer), umbrellaAnswer)

    def test_formatProblogStrat(self):
        self.agent.initUniformStrategy()
        expectedProblogStratString = "0.5::boolean_True;0.5::boolean_False.\n" + \
            "0.1::integer_0;0.1::integer_1;0.1::integer_2;0.1::integer_3;0.1::integer_4;0.1::integer_5;0.1::integer_6;0.1::integer_7;0.1::integer_8;0.1::integer_9.\n" + \
            "0.1::'float_0.0';0.1::'float_0.1';0.1::'float_0.2';0.1::'float_0.3';0.1::'float_0.4';0.1::'float_0.5';0.1::'float_0.6';0.1::'float_0.7';0.1::'float_0.8';0.1::'float_0.9'.\n"

        self.assertEqual(self.agent.formatProblogStrat(
            self.agent.stratDict), expectedProblogStratString)

    def test_generateOffer(self):
        self.agent.stratDict = self.denseNestedTestOffer
        # set reservation value so search doesn't exit
        self.agent.reservationValue = -1000
        offer = self.agent.generateOffer()
        self.assertEqual(offer,
                         self.denseNestedTestOffer)

    def test_generateOfferExitsIfUnableToFindSolution(self):
        self.agent.maxGenerationTries = 10
        self.agent.stratDict = self.denseNestedTestOffer
        self.assertEqual(self.agent.generateOffer(),
                         Message(self.agent.agentName,
                                 self.opponent.agentName,
                                 "terminate",
                                 None))

    def test_validOfferIsAccepted(self):
        self.assertTrue(self.agent.isOfferValid(
            self.denseNestedTestOffer))

    def test_validStratIsAccepted(self):
        self.assertTrue(self.agent.isStratValid(
            self.agent.stratDict))

    def test_nonBinaryOfferIsRejected(self):
        self.assertFalse(self.agent.isOfferValid(
            self.agent.stratDict))

    def test_invalidOfferIsRjected(self):
        with self.assertRaises(ValueError):
            self.agent.accepts(self.agent.stratDict)

    def test_mispelledOfferIsRejected(self):
        self.denseNestedTestOffer['boolean']['True'] = 1.0
        del self.denseNestedTestOffer['boolean']['True']
        with self.assertRaises(ValueError):
            self.agent.accepts(self.denseNestedTestOffer)

    def test_stratWithNonDistIsRejected(self):
        self.agent.stratDict["boolean"]["True"] = 0.23424123412341234123412341234123412341234
        self.assertFalse(self.agent.isStratValid(
            self.agent.stratDict))

    def test_stratWithUnknownFactsIsNotValid(self):
        self.agent.stratDict['boolean']['true'] = 0.0
        self.assertFalse(self.agent.isStratValid(
            self.agent.stratDict))

    def test_offerWithUnknownFactsIsNotValid(self):
        offerWithUnknownFact = self.validSparseNestedTestOffer
        offerWithUnknownFact['boolean']['true'] = 1.0
        del offerWithUnknownFact['boolean']['True']
        self.assertFalse(self.agent.isOfferValid(
            offerWithUnknownFact))

    def test_settingValidSparseStratSuceeds(self):
        self.agent.setStrat(self.validSparseNestedTestOffer)

    def test_settinginvalidSparseStratRaisesError(self):
        with self.assertRaises(ValueError):
            self.agent.setStrat(self.invalidSparseNestedTestOffer)

    def test_calcingUtilityOfInvalidOfferRaisesError(self):
        # B in boolean is capitalised while it shouldn't be
        self.agent.stratDict['Boolean_True'] = 0.0
        with self.assertRaises(ValueError):
            self.agent.calcOfferUtility(
                self.agent.stratDict)

    def test_generateValidOffer(self):
        self.agent.smart = True
        self.assertTrue(self.agent.accepts(
            self.agent.generateOffer()))

    def test_sparseAtomDictToNestedDictValid(self):
        self.assertEqual(self.validSparseNestedTestOffer, self.agent.atomDictToNestedDict(
            self.validSparseAtomTestOffer))

    def test_validSparseNestedDictToAtomDict(self):
        self.assertEqual(self.validSparseAtomTestOffer, self.agent.nestedDictToAtomDict(
            self.validSparseNestedTestOffer))

    def test_denseAtomDictToNestedDictValid(self):
        self.assertEqual(self.denseNestedTestOffer, self.agent.atomDictToNestedDict(
            self.denseAtomTestOffer))

    def test_validSparseAtomDictToNestedDict(self):
        self.assertEqual(self.denseAtomTestOffer, self.agent.nestedDictToAtomDict(
            self.denseNestedTestOffer))

    def test_resettingIssuesResetsStrategy(self):
        newIssues = {"first": ["True", "False"]}
        self.agent.setIssues(newIssues)
        self.assertTrue(self.agent.isStratValid(
            self.agent.stratDict))

    def test_acceptsAcceptableOffer(self):
        self.denseNestedTestOffer['integer']["2"] = 0
        self.denseNestedTestOffer['integer']["3"] = 1
        self.agent.recordMessage(
            Message(self.opponent, self.agent, kind="offer", offer=self.denseNestedTestOffer))
        self.agent.generateNextMessageFromTranscript()
        self.assertTrue(
            self.agent.successful and not self.agent.negotiationActive and self.agent.messageCount == 1)

    def test_gettingEmptyMessageIncrementsMessageCount(self):
        self.agent.receiveMessage(
            Message(self.opponent, self.agent, "empty", None))
        self.assertEqual(self.agent.messageCount, 1)

    def test_sendingMessageIncrementsMessageCount(self):
        self.agent.sendMessage(self.opponent, Message(
            self.opponent, self.agent, "empty", None))
        self.assertEqual(self.agent.messageCount, 1)

    def test_terminatesNegotiationAfterMaxRounds(self):
        self.agent.maxRounds = 3
        for _ in range(self.agent.maxRounds+1):
            self.agent.recordMessage(
                Message(self.opponent, self.agent, "offer", self.denseNestedTestOffer))
        response = self.agent.generateNextMessageFromTranscript()
        self.assertEqual(
            Message(self.opponent, self.agent, kind="terminate", offer=self.denseNestedTestOffer), response)

    def test_easyNegotiationEndsSucessfully(self):
        self.agent.setIssues({"first": ["True", "False"]})
        self.agent.utilities = {"first_True": 10000}
        self.opponent.utilities = {"first_True": 10000}
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.successful and not self.agent.negotiationActive)

    def test_slightlyHarderNegotiationEndsSucessfully(self):
        self.agent.setIssues({"first": ["True", "False"],
                              "second": ["True", "False"]})
        self.agent.utilities = {"first_True": 10000}
        self.opponent.utilities = {"second_True": 10000}
        self.agent.negotiate(self.opponent)
        self.assertTrue(
            self.agent.successful and not self.agent.negotiationActive)

    def test_impossibleNegotiationEndsUnsuccessfully(self):
        self.agent.maxRounds = 10  # make sure the test goes a little faster
        self.opponent.maxRounds = 10

        self.agent.setIssues({"first": ["True", "False"]})
        self.agent.addUtilities({"first_True": -10000, "first_False": 10000})
        self.opponent.addUtilities(
            {"first_True": 10000, "first_False": -10000})

        self.agent.negotiate(self.opponent)
        self.assertTrue(
            not self.agent.successful and not self.agent.negotiationActive)

    def test_receivedMessageCanBeRecalled(self):
        msg = Message(self.opponent.agentName,
                      self.agent.agentName, "offer", self.denseNestedTestOffer)
        self.agent.receiveMessage(msg)
        self.assertEqual(self.agent.transcript[-1], msg)

    def test_receiveValidNegotiationRequest(self):
        self.assertTrue(self.opponent.receiveNegotiationRequest(
            self.agent, self.genericIssues))

    def test_receiveAcceptationMessageEndsNegotiation(self):
        self.agent.negotiationActive = True
        self.agent.receiveMessage(self.acceptanceMessage)
        self.agent.generateNextMessageFromTranscript()
        self.assertFalse(self.agent.negotiationActive)

    def test_receiveAcceptationMessageNegotiationWasUncusessful(self):
        self.agent.receiveMessage(self.acceptanceMessage)
        self.agent.generateNextMessageFromTranscript()
        self.assertTrue(self.agent.successful)

    def test_receiveTerminationMessageEndsNegotiation(self):
        self.agent.negotiationActive = True
        self.agent.receiveMessage(self.terminationMessage)
        self.agent.generateNextMessageFromTranscript()
        self.assertFalse(self.agent.negotiationActive)

    def test_receiveTerminationMessageNegotiationWasUncusessful(self):
        self.agent.receiveMessage(self.terminationMessage)
        self.agent.generateNextMessageFromTranscript()
        self.assertFalse(self.agent.successful)