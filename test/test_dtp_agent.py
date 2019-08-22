from dtp_agent import DTPAgent
from message import Message
import unittest
from atomic_constraint import AtomicConstraint


class TestDTPAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.agent_name = "agent"
        self.opponent_name = "opponent"
        self.generic_issues = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
            "'float_0.1'": 1
            # TODO still need to look at compound and negative atoms
        }
        self.arbitrary_kb = [
            "boolean_True :- integer_2, 'float_0.1'."
        ]
        self.arbitrary_reservation_value = 0
        self.arbitrary_non_agreement_cost = -1000

        # should have a utility of 100
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["3"] = 1
        self.nested_test_offer['float']["0.6"] = 1

        self.optimal_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.optimal_offer["integer"]["9"] = 1.0
        self.optimal_offer['float']["0.1"] = 1.0

        self.agent = DTPAgent(self.agent_name,
                              self.arbitrary_utilities,
                              self.arbitrary_kb,
                              self.arbitrary_reservation_value,
                              self.arbitrary_non_agreement_cost)

        self.opponent = DTPAgent(self.opponent_name,
                                 self.arbitrary_utilities,
                                 self.arbitrary_kb,
                                 self.arbitrary_reservation_value,
                                 self.arbitrary_non_agreement_cost)

        self.agent.setup_negotiation(self.generic_issues)
        self.agent.call_for_negotiation(self.opponent, self.generic_issues)
        self.optimal_offer_message = Message(self.agent.agent_name,
                                             self.opponent.agent_name,
                                             "offer",
                                             self.optimal_offer)
        self.termination_message = Message(
            self.agent.agent_name, self.opponent.agent_name, "terminate", None)

    def test_dt_umbrella_example(self):
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

        offer, score = self.agent.file_based_dtproblog(model)

        self.assertEqual({"raincoat": 0.0, "umbrella": 1.0}, offer)
        self.assertAlmostEqual(score, 43)

    def test_dtp_generates_optimal_bid_in_simple_negotiation_setting(self):
        expected_message = Message(
            self.agent.agent_name, self.opponent.agent_name, "offer", self.optimal_offer)
        response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(expected_message, response)

    def test_doesnt_generate_same_offer_five_times(self):
        # since some elements might be randomly picked it can sometimes happen that the elements are the same but it
        # shouldn't keep happening so we'll try it a couple of times
        first_message = self.agent.generate_next_message_from_transcript()
        second_message = self.agent.generate_next_message_from_transcript()
        third_message = self.agent.generate_next_message_from_transcript()
        forth_message = self.agent.generate_next_message_from_transcript()
        fifth_message = self.agent.generate_next_message_from_transcript()
        self.assertFalse(first_message == second_message ==
                         third_message == forth_message == fifth_message)

    def test_generatingOfferRecordsItInUtilities(self):
        self.agent.generate_next_message_from_transcript()
        self.assertTrue(({"'float_0.1'": 1.0, 'boolean_True': 1.0, 'boolean_False': 0.0, 'integer_1': 0.0, 'integer_3': 0.0, 'integer_4': 0.0,
                          'integer_5': 0.0, 'integer_9': 1.0}, 201.0) in self.agent.generated_offers)

    def test_generatesValidOffersWhenNoUtilitiesArePresent(self):
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        response = self.agent.generate_next_message_from_transcript()
        self.assertTrue(self.agent.is_offer_valid(response.offer))

    def test_generatesValidOffersWhenConstraintsArePresent(self):
        self.arbitraryUtilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.add_own_constraint(AtomicConstraint("boolean", "True"))
        response = self.agent.generate_next_message_from_transcript()
        self.assertTrue(self.agent.is_offer_valid(response.offer))

    def test_endsNegotiationIfOffersGeneratedAreNotAcceptable(self):
        # simply a set of impossible utilities to check that we exit immediately
        self.arbitrary_utilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.set_utilities(self.arbitrary_utilities)
        self.assertEqual(self.termination_message,
                         self.agent.generate_next_message_from_transcript())

    def test_countsMessagesCorrectlyInSuccessfulNegotiation(self):
        self.agent.negotiate(self.opponent)
        # one offer and one acceptance message
        self.assertEqual(self.agent.message_count, 2)

    def test_countsMessagesCorrectlyInUnsuccessfulNegotiation(self):
        self.arbitrary_utilities = {
            "boolean_True": -100,
            "boolean_False": -10,
            "integer_9": -100,
            "integer_3": -10,
            "integer_1": -0.1,
            "integer_4": -10,
            "integer_5": -100,
        }
        self.agent.set_utilities(self.arbitrary_utilities)
        self.agent.negotiate(self.opponent)
        self.assertEqual(self.agent.message_count, 2)

    def test_valuesViolatingConstraintWithNonAgreementCost(self):
        constraint = AtomicConstraint("boolean", "True")
        self.agent.add_own_constraint(constraint)
        self.assertEqual(self.agent.calc_offer_utility(
            self.optimal_offer), self.agent.non_agreement_cost)

    def test_generatesConstraintIfOfferViolates(self):
        self.opponent.add_own_constraint(AtomicConstraint("boolean", "True"))
        self.opponent.receive_message(
            self.agent.generate_next_message_from_transcript())
        opponent_response = self.opponent.generate_next_message_from_transcript()
        # one of the constraints was added manually and the integer ones are added because of their utilities
        # but we can't control which is sent so we check for all of them
        self.assertTrue(opponent_response.constraint == AtomicConstraint("integer", "4") or
                        opponent_response.constraint == AtomicConstraint("integer", "5") or
                        opponent_response.constraint == AtomicConstraint("boolean", "True") or
                        opponent_response.constraint == AtomicConstraint("integer", "2"))

    def test_recordsConstraintIfReceived(self):
        self.opponent.add_own_constraint(AtomicConstraint("boolean", "True"))
        self.opponent.receive_message(
            self.agent.generate_next_message_from_transcript())
        self.agent.receive_response(self.opponent)
        self.agent.generate_next_message_from_transcript()
        # one of the constraints was added manually and the integer ones are added because of their utilities
        # but we can't control which is sent so we check for all of them
        self.assertTrue(AtomicConstraint("integer", "4") in self.agent.opponent_constraints or
                        AtomicConstraint("integer", "5") in self.agent.opponent_constraints or
                        AtomicConstraint("boolean", "True") in self.agent.opponent_constraints)

    def test_ownOfferDoesNotViolateConstraint(self):
        self.agent.add_own_constraint(AtomicConstraint("boolean", "True"))
        generated_message = self.agent.generate_next_message_from_transcript()
        self.assertAlmostEqual(generated_message.offer["boolean"]['True'], 0.0)
