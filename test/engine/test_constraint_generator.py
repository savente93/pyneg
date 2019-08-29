
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
