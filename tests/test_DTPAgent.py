from DTPAgent import DTPNegotiationAgent
from message import Message
import unittest
from constraint import AtomicConstraint


class TestDTPNegotiationAgent(unittest.TestCase):

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
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9" : 100,
            "integer_3" : 10,
            "integer_1" : 0.1,
            "integer_4" : -10,
            "integer_5" : -100,
            "'float_0.1'" : 1
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
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.denseNestedTestOffer["integer"]["3"] = 1
        self.denseNestedTestOffer['float']["0.6"] = 1


        self.optimalOffer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.optimalOffer["integer"]["9"] = 1.0
        self.optimalOffer['float']["0.1"] = 1.0


        self.agent = DTPNegotiationAgent("",
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost,
            verbose=0)
        self.agent.agentName = "agent"
        self.opponent = DTPNegotiationAgent("",
            self.arbitraryUtilities, self.arbitraryKb, self.arbitraryReservationValue, self.arbitraryNonAgreementCost,
            verbose=0)
        self.opponent.agentName = "opponent"
        self.agent.setupNegotiation(self.genericIssues)
        self.agent.callForNegotiation(self.opponent, self.genericIssues)
        self.optimalOfferMessage = Message(self.agent.agentName, self.opponent.agentName,"offer",self.optimalOffer)
        self.terminationMessage = Message(self.agent.agentName, self.opponent.agentName, "terminate",
                                         None)


        # print("In method: {}".format( self._testMethodName))

    def test_dtUmbrellaExample(self):
        model = ''' ?::umbrella.
                    ?::raincoat.
                    
                    0.3::rain.
                    0.5::wind.
                    broken_umbrella:- umbrella, rain, wind.
                    dry:- rain, raincoat.
                    dry:- rain, umbrella, not broken_umbrella.
                    dry:- not(rain).
                    
                    utility(broken_umbrella,-40).
                    utility(raincoat,-20).
                    utility(umbrella,-2).
                    utility(dry,60).'''

        offer, score = self.agent.non_leaky_dtproblog(model)

        self.assertEqual({"raincoat": 0.0, "umbrella": 1.0}, offer )
        self.assertAlmostEqual(score,43)


    def test_dtpGeneratesOptimalBidInSimpleNegotiationSetting(self):
        expectedMessage = Message(self.agent.agentName,self.opponent.agentName,"offer",self.optimalOffer)
        response = self.agent.generateNextMessageFromTranscript()
        self.assertEqual(expectedMessage, response)

    def test_doesntGenerateSameOfferTwice(self):
        firstMessage = self.agent.generateNextMessageFromTranscript()
        secondMessage = self.agent.generateNextMessageFromTranscript()
        self.assertNotEqual(firstMessage,secondMessage)

    def test_generatingOfferRecordsItInUtilities(self):
        self.agent.generateNextMessageFromTranscript()
        # print(self.agent.generatedOffers)
        # print(self.agent.nestedDictToAtomDict(self.optimalOffer))
        self.assertTrue(({"'float_0.1'": 1.0, 'boolean_True': 1.0, 'integer_1': 0.0, 'integer_3': 0.0, 'integer_4': 0.0, 'integer_5': 0.0, 'integer_9': 1.0}
                         ,201.0) in self.agent.generatedOffers)


    def test_generatesValidOffersWhenNoUtilitiesArePresent(self):
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9" : 100,
            "integer_3" : 10,
            "integer_1" : 0.1,
            "integer_4" : -10,
            "integer_5" : -100,
         }
        # for val in self.agent.stratDict["float"].keys():
        #     self.agent.stratDict["float"][val] = 0
        #
        # self.agent.stratDict["float"]["0.1"] = 1
        response = self.agent.generateNextMessageFromTranscript()
        # self.assertEqual(response,self.optimalOfferMessage)
        self.assertTrue(self.agent.isOfferValid(response.offer))


    def test_generatesValidOffersWhenConstraintsArePresent(self):
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9" : 100,
            "integer_3" : 10,
            "integer_1" : 0.1,
            "integer_4" : -10,
            "integer_5" : -100,
         }
        self.agent.addOwnConstraint(AtomicConstraint("boolean", "True"))
        # for val in self.agent.stratDict["float"].keys():
        #     self.agent.stratDict["float"][val] = 0
        #
        # self.agent.stratDict["float"]["0.1"] = 1
        response = self.agent.generateNextMessageFromTranscript()
        # self.assertEqual(response,self.optimalOfferMessage)
        self.assertTrue(self.agent.isOfferValid(response.offer))

    def test_endsNegotiationIfOffersGeneratedAreNotAcceptable(self):
        # simply a set of impossible utilities to check that we exit immediately
        self.arbitraryUtilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.setUtilities(self.arbitraryUtilities)
        self.assertEqual(self.terminationMessage,self.agent.generateNextMessageFromTranscript())

    def test_countsMessagesCorrectlyInSuccessfulNegotiation(self):
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent.messageCount, 1)

    def test_countsMessagesCorrectlyInUnsuccessfulNegotiation(self):
        self.arbitraryUtilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.setUtilities(self.arbitraryUtilities)
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent.messageCount,1)


    def test_valuesViolatingConstraintWithNonAgreementCost(self):
        constraint = AtomicConstraint("boolean", "True")
        self.agent.addOwnConstraint(constraint)
        self.assertEqual(self.agent.calcOfferUtility(self.optimalOffer),self.agent.nonAgreementCost)

    def test_generatesConstraintIfOfferViolates(self):
        self.opponent.addOwnConstraint(AtomicConstraint("boolean", "True"))
        self.opponent.receiveMessage(self.agent.generateNextMessageFromTranscript())
        opponentResponse = self.opponent.generateNextMessageFromTranscript()
        self.assertEqual(opponentResponse.constraint, AtomicConstraint("boolean", "True"))

    def test_recordsConstraintIfReceived(self):
        self.opponent.addOwnConstraint(AtomicConstraint("boolean", "True"))
        self.opponent.receiveMessage(self.agent.generateNextMessageFromTranscript())
        self.agent.receiveResponse(self.opponent)
        self.agent.generateNextMessageFromTranscript()
        self.assertTrue(AtomicConstraint("boolean", "True") in self.agent.opponentConstraints)

    def test_ownOfferDoesNotViolateConstraint(self):
        self.agent.addOwnConstraint(AtomicConstraint("boolean", "True"))
        generatedMessage = self.agent.generateNextMessageFromTranscript()
        self.assertAlmostEqual(generatedMessage.offer["boolean"]['True'], 0.0)
