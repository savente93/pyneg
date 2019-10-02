from unittest import TestCase

from pyneg.comms import Offer, AtomicConstraint
from pyneg.agent import *
from pyneg.utils import generate_random_scenario, neg_scenario_from_util_matrices


class TestAgentFactory(TestCase):

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
            "integer_5": -10000,
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

        self.violating_offer = {
            "boolean": {"True": 1.0, "False": 0.0},
            "integer": {str(i): 0.0 for i in range(10)},
            "float": {"{0:.1f}".format(i * 0.1): 0.0 for i in range(10)}
        }
        self.violating_offer["integer"]["2"] = 1.0
        self.violating_offer['float']["0.1"] = 1.0

    def test_reservation_value_is_lower_than_estimated_max_utility(self):
        agent_a = make_constrained_linear_concession_agent("A", self.neg_space, self.utilities, 0.5,
                                                                        self.non_agreement_cost, set(), None)
        self.assertTrue(agent_a._absolute_reservation_value <= agent_a._engine.calc_offer_utility(self.optimal_offer))

<<<<<<< HEAD
    def test_reservation_value_is_estimated_correctly_for_linear_utility_function(self):
        self.utilities = {
            "boolean_True": 100,
            "boolean_False": -100,
            "integer_1": 10,"integer_2": -10,
            "integer_3": 10,"integer_4": -10,
            "integer_5": 10,"integer_6": -10,
            "integer_7": 10,"integer_8": -10,
            "'float_0.1'": 1,"'float_0.2'": -1,
            "'float_0.3'": 1,"'float_0.4'": -1,
            "'float_0.5'": 1,"'float_0.6'": -1,
            "'float_0.7'": 1,"'float_0.8'": -1,
        }


        agent_a = make_constrained_linear_concession_agent("A", self.neg_space, self.utilities, 0.5,
                                                                        self.non_agreement_cost, set(), None)

        self.assertAlmostEqual(agent_a._absolute_reservation_value, 0.5*(100/3+10/3+1/3))




    def test_factory_correctly_determines_constraints(self):
        agent_a = make_constrained_linear_concession_agent("A", self.neg_space, self.utilities, 0.5,
                                                                        self.non_agreement_cost, set(), None)

        self.assertTrue(AtomicConstraint("integer","5") in agent_a.get_constraints())

    def test_detects_constraints_in_generated_scenarios(self):
        numb_of_constraints = 6
        u_a, u_b = generate_random_scenario((4,4),numb_of_constraints)
        neg_space, utils_a, utils_b = neg_scenario_from_util_matrices(u_a,u_b)
        agent_a = make_constrained_linear_concession_agent("A", neg_space, utils_a, 0.5,
                                                                        self.non_agreement_cost, set(), None)

        self.assertEqual(len(agent_a.get_constraints()), numb_of_constraints, agent_a.get_constraints())

    def test_solution_found_by_unconstrained_agents_satisfies_constraints(self):
        numb_of_constraints = 2
        u_a, u_b = generate_random_scenario((4, 4), numb_of_constraints)
        neg_space, utils_a, utils_b = neg_scenario_from_util_matrices(u_a, u_b)
        rand_a = make_linear_concession_agent("A", neg_space, utils_a, 0.1,
                                                                        self.non_agreement_cost, None)

        rand_b = make_linear_concession_agent("B", neg_space, utils_b, 0.1,
                                                                       self.non_agreement_cost, None)


        constr_a = make_constrained_linear_concession_agent("A", neg_space, utils_a, 0.3,
                                                                         self.non_agreement_cost, set(), None)

        constr_b = make_constrained_linear_concession_agent("B", neg_space, utils_b, 0.3,
                                                                         self.non_agreement_cost, set(), None)

        rand_a.negotiate(rand_b)

        last_message = rand_a._transcript[-1]
        self.assertTrue(last_message.is_acceptance(), rand_a._transcript)
        self.assertTrue(constr_a._engine.satisfies_all_constraints(last_message.offer))
        self.assertTrue(constr_b._engine.satisfies_all_constraints(last_message.offer))

=======

    def test_factory_correctly_determines_constraints(self):
        agent_a = AgentFactory.make_constrained_linear_concession_agent("A", self.neg_space, self.utilities, 0.5,
                                                                        self.non_agreement_cost, None, set())

        self.assertTrue(AtomicConstraint("integer","5") in agent_a.get_constraints())

>>>>>>> add constraint test form different branch
