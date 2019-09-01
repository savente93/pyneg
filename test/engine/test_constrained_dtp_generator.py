from unittest import TestCase
from pyneg.engine import DTPGenerator
from pyneg.comms import Offer


class TestConstraintDTPGenerator(TestCase):

    def setUp(self):
        self.neg_space = {
            "boolean": [True, False],
            "integer": list(range(10)),
            "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
        }
        self.utilities = {
            "boolean_True": 100,
            "boolean_False": 10,
            "integer_9": 100,
            "integer_3": 10,
            "integer_1": 0.1,
            "integer_4": -10,
            "integer_5": -100,
            "'float_0.1'": 1
        }
        self.kb = [
            "boolean_True :- integer_2, 'float_0.1'."
        ]
        self.reservation_value = 0
        self.non_agreement_cost = -1000

        # should have a utility of 100
        self.nested_test_offer = {
            "boolean": {"True": 1, "False": 0},
            "integer": {str(i): 0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0 for i in range(10)}
        }
        self.nested_test_offer["integer"]["3"] = 1
        self.nested_test_offer['float']["0.6"] = 1

        self.nested_test_offer = Offer(self.nested_test_offer)

        self.optimal_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.optimal_offer["integer"]["9"] = 1.0
        self.optimal_offer['float']["0.1"] = 1.0

        self.optimal_offer = Offer(self.optimal_offer)

        self.generator = DTPGenerator(self.neg_space, self.utilities,
                                      self.non_agreement_cost, self.reservation_value,
                                      self.kb)

    def test_responds_to_violating_offer_with_constraint(self):
        self.arbitrary_utilities = {
            "boolean_True": 100,
            "'float_0.5'": pi
        }
        self.agent = ConstrAgent(self.agent_name,
                                 self.arbitrary_utilities,
                                 self.arbitrary_kb,
                                 self.arbitrary_reservation_value,
                                 self.arbitrary_non_agreement_cost,
                                 self.generic_issues)

        self.opponent = ConstrAgent(self.opponent_name,
                                    self.arbitrary_utilities,
                                    self.arbitrary_kb,
                                    self.arbitrary_reservation_value,
                                    self.arbitrary_non_agreement_cost,
                                    self.generic_issues)
        self.agent.setup_negotiation(self.generic_issues)
        self.agent.opponent = self.opponent

        # set strategy to something constant so we can predict what message it will generate
        self.agent.strat_dict = self.nested_test_offer.copy()

        self.agent.add_own_constraint(AtomicConstraint("boolean", "False"))
        self.agent.receive_message(Message(self.opponent.agent_name,
                                           self.agent.agent_name,
                                           "offer",
                                           self.violating_offer))

        response = self.agent.generate_next_message_from_transcript()
        self.assertEqual(Message(self.agent.agent_name,
                                 self.opponent.agent_name,
                                 "offer",
                                 self.agent.strat_dict,
                                 AtomicConstraint("boolean", "False")),
                         response)

    def test_dtp_generates_optimal_bid_in_simple_negotiation_setting(self):
        result = self.generator.generate_offer()
        self.assertEqual(result, self.optimal_offer)

    def test_doesnt_generate_same_offer_five_times(self):
        # since some elements might be randomly picked it can sometimes happen that the elements are the same but it
        # shouldn't keep happening so we'll try it a couple of times
        last_offer = self.generator.generate_offer()
        for _ in range(5):
            new_offer = self.generator.generate_offer()
            self.assertNotEqual(last_offer, new_offer)
            last_offer = new_offer

    def test_generatingOfferRecordsItInUtilities(self):
        _ = self.generator.generate_offer()
        self.assertTrue(Offer({"'float_0.1'": 1.0, 'boolean_True': 1.0, 'boolean_False': 0.0, 'integer_1': 0.0, 'integer_3': 0.0, 'integer_4': 0.0,
                               'integer_5': 0.0, 'integer_9': 1.0}).get_sparse_str_repr() in self.generator.generated_offers.keys())

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
        self.generator = DTPGenerator(
            self.neg_space,
            self.arbitraryUtilities,
            self.non_agreement_cost,
            self.reservation_value,
            self.kb)

        # should not raise an exception
        _ = self.generator.generate_offer()

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
        self.generator = DTPGenerator(
            self.neg_space,
            self.arbitraryUtilities,
            self.non_agreement_cost,
            self.reservation_value,
            self.kb)

        with self.assertRaises(StopIteration):
            self.generator.generate_offer()

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

    def test_valuesViolatingConstraintWithNonAgreementCost(self):
        constraint = AtomicConstraint("boolean", "True")
        self.agent.add_own_constraint(constraint)
        self.assertEqual(self.agent.calc_offer_utility(
            self.optimal_offer), self.agent.non_agreement_cost)

    def test_getting_utility_below_threshold_creates_constraint(self):
        self.asdf.automatic_constraint_generation = True
        low_util_dict = {"integer_4": -1000}
        self.asdf.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4")
                        in self.asdf.own_constraints)

    def test_all_values_get_constrained_terminates_negotiation(self):
        self.agent.automatic_constraint_generation = True
        low_util_dict = {"integer_{i}".format(
            i=i): -1000 for i in range(len(self.agent.issues['integer']))}
        self.agent.add_utilities(low_util_dict)
        self.assertTrue(
            self.agent.generate_next_message_from_transcript().is_termination())

    def test_getting_utility_below_threshold_creates_constraint(self):
        low_util_dict = {"integer_4": -100000}
        self.evaluator.add_utilities(low_util_dict)
        self.assertTrue(AtomicConstraint("integer", "4")
                        in self.evaluator.constraints)

    def test_all_values_can_get_constrained(self):
        low_util_dict = {"integer_{i}".format(
            i=i): -100000 for i in range(len(self.neg_space['integer']))}
        self.evaluator.add_utilities(low_util_dict)
        constraints = self.evaluator.constraints
        self.assertTrue(
            all([constr.issue == "integer" for constr in constraints]))
        self.assertEqual(
            len([constr.issue == "integer" for constr in constraints]),
            len(self.neg_space['integer']))

    def test_multiple_issues_can_get_constrained(self):
        low_util_dict = {"integer_4": -1000, "'float_0.9'": -1000}
        self.evaluator.add_utilities(low_util_dict)
        self.assertTrue({AtomicConstraint("integer", "4"), AtomicConstraint(
            "float", "0.9")}.issubset(self.evaluator.constraints))
