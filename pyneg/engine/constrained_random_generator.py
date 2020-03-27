"""
Defines the :class:`ConstrainedRandomGenerator` class, the contraint aware version of
:class:`RandomGenerator` see that entry for more information.
"""
from typing import Optional, Set, List, Union, TYPE_CHECKING

from numpy import isclose
from pyneg.engine import Strategy # pylint: disable=ungrouped-imports
from pyneg.comms import AtomicConstraint, Offer
from pyneg.types import NegSpace, AtomicDict
from pyneg.utils import atom_from_issue_value
from pyneg.engine import Evaluator, RandomGenerator


class ConstrainedRandomGenerator(RandomGenerator):
    """
        This class is equal to the :class:`RandomGenerator` class but with
        additional logic to handle constraints. See :class:`RandomGenerator` for
        more information on how the offers are sampled.
    """
    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 non_agreement_cost: float,
                 kb: List[str],
                 acceptability_threshold: float,
                 max_rounds: int,
                 constr_value: float,
                 initial_constraints: Set[AtomicConstraint],
                 auto_constraints=True,
                 max_generation_tries: int = 500):
        self.constr_value = constr_value
        self.constraints: Set[AtomicConstraint] = set()
        super().__init__(neg_space, utilities, evaluator,
                         non_agreement_cost, kb, acceptability_threshold,
                         max_rounds, max_generation_tries=max_generation_tries)

        self.auto_constraints = auto_constraints
        self.constraints_satisfiable = True
        if initial_constraints:
            self.add_constraints(initial_constraints)
        self._index_max_utilities()
        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }
        self.evaluator.add_utilities(new_utils)

        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())

        return self.constraints_satisfiable


    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())
        self.evaluator.add_utilities(new_utils)
        return self.constraints_satisfiable

    def generate_offer(self) -> Offer:
        if not self.constraints_satisfiable:
            self.active = False
            raise StopIteration()
        try:
            offer = super().generate_offer()
        except StopIteration:
            self.active = False
            raise StopIteration()
        if not self.satisfies_all_constraints(offer):
            raise RuntimeError()
        return offer

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        self.constraints.add(constraint)
        self.evaluator.add_constraint(constraint)
        return self.make_strat_constraint_compliant()


    def add_constraints(self, new_constraints: Set[AtomicConstraint]) -> bool:
        self.constraints.update(new_constraints)
        self.evaluator.add_constraints(self.constraints)
        return self.make_strat_constraint_compliant()

    def discover_constraints(self) -> Set[AtomicConstraint]:
        """
        Attempts to deduce new constraints from the current knowledge base.
        see :ref:`constraint-discovery` for more information.

        :return: A set containing all the newly discovered constraints.
        :rtype: Set[AtomicConstraint]
        """
        new_constraints = set()
        for issue in self.neg_space.keys():
            best_case = sum(
                [bc for i, bc in self.max_utility_by_issue.items() if i != issue])

            for value in self.neg_space[issue]:
                atom = atom_from_issue_value(issue, value)
                if atom in self.utilities.keys():
                    value_util = self.utilities[atom]
                else:
                    value_util = 0

                if best_case + value_util < self.acceptability_threshold:
                    new_constraints.add(AtomicConstraint(issue, value))

        return new_constraints

    def get_unconstrained_values_by_issue(self, issue):
        issue_constrained_values = set(
            constr.value for constr in self.constraints if constr.issue == issue)
        issue_unconstrained_values = set(
            self.neg_space[issue]) - issue_constrained_values
        return issue_unconstrained_values

    def satisfies_all_constraints(self, to_check: Union[Offer, Strategy]) -> bool:
        """
        Checks whether the given offer or strategy  satisfies all known constraints.

        :param to_check: The offer or strategy to check
        :type to_check: Union[Offer, Strategy]
        :raises TypeError: if an object of unknown type is passed.
        :return: True iff the given offer or strategy satisfies all known constraints.
        :rtype: bool
        """
        if isinstance(to_check, Offer):
            for constr in self.constraints:
                if not constr.is_satisfied_by_offer(to_check):
                    return False
        elif isinstance(to_check, Strategy):
            for constr in self.constraints:
                if not constr.is_satisfied_by_strat(to_check):
                    return False
        else:
            raise TypeError(f"""object is of type {type(to_check)} instead of
                                Union[Offer, Strategy]. Object: {to_check}""")

        return True

    def _index_max_utilities(self):
        """
        Index the currently known utilities so we can use this as a heuristic during
        the constraint discovery process. See :ref:`constraint-discovery` for more information.
        """
        self.max_utility_by_issue = {
            issue: 0 for issue in self.neg_space.keys()}
        for issue in self.neg_space.keys():
            max_issue_util = -(2 ** 31)
            for value in self.neg_space[issue]:
                util = self.evaluator.calc_assignment_util(issue, value)
                if util > max_issue_util:
                    max_issue_util = util
                    self.max_utility_by_issue[issue] = max_issue_util

    def make_strat_constraint_compliant(self) -> bool:
        """
        When we receive a new constraint we'll need to update the stratagy.
        This also checks whether a solution is still possible under the constraints.

        :return: Whether the process has succeeded. If False, no sollutions are possible.
        :rtype: bool
        """
        for constr in self.constraints:
            issue = constr.issue
            unconstrained_values = self.get_unconstrained_values_by_issue(
                issue)
            if not unconstrained_values:
                self.constraints_satisfiable = False
                # Unsatisfiable constraint so we're terminating on
                # the next message so we won't need to update the strat
                return False

            for value in self.neg_space[issue]:
                if not constr.is_satisfied_by_assignment(issue, value):
                    self.strategy.set_prob(issue, value, 0)

            # it's possible we just made the last value in the strategy 0 so
            # we have to figure out a value that is still unconstrained
            # and set that one to 1
            value_dist_sum = sum(self.strategy.get_value_dist(issue).values())
            if isclose(value_dist_sum, 0):
                self.strategy.set_prob(issue, next(
                    iter(unconstrained_values)), 1)
            else:
                self.strategy.normalise_issue(issue)

        return True

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        for constr in self.constraints:
            for issue in offer.get_issues():
                chosen_value = offer.get_chosen_value(issue)
                if not constr.is_satisfied_by_assignment(issue, chosen_value):
                    return AtomicConstraint(issue, chosen_value)

        return None

    def get_constraints(self):
        return self.constraints
