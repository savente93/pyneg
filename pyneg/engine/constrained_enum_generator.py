from typing import Optional, Set, Dict, List, Iterable
from pyneg.comms import Offer
from pyneg.types import NegSpace, NestedDict, AtomicDict
from .evaluator import Evaluator
from .strategy import Strategy
from numpy.random import choice
from pyneg.comms import AtomicConstraint
from .generator import Generator
from .enum_generator import EnumGenerator


class ConstrainedEnumGenerator(EnumGenerator):
    def __init__(self, neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 acceptability_threshold: float,
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True) -> None:
        super().__init__(neg_space, utilities, evaluator, acceptability_threshold)
        self.constraints = set()
        if initial_constraints:
            self.constraints.add(initial_constraints)
        self.auto_constraints = auto_constraints
        self.max_utility_by_issue = {}

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)
        self.evaluator.add_constraint(constraint)

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)
        self.evaluator.add_constraints(constraints)

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True

    def index_max_utilities(self):
        self.max_utility_by_issue = {
            issue: 0 for issue in self.neg_space.keys()}
        for issue in self.neg_space.keys():
            if len(self.sorted_utils[issue]) > 0:
                self.max_utility_by_issue[issue] = self.sorted_utils[issue][0]
        # for issue in self.neg_space.keys():
        #     max_issue_util = -(2**31)
        #     for value in self.neg_space[issue]:
        #         atom = self.atom_from_issue_value(issue, value)
        #         if atom in self.utilities.keys():
        #             if not all([constr.is_satisfied_by_assignment(issue, value) for constr in self.get_all_constraints()]):
        #                 continue
        #             util = self.utilities[atom] * self.issue_weights[issue]
        #         else:
        #             util = 0

        #         if util > max_issue_util:
        #             max_issue_util = util
        #             self.max_utility_by_issue[issue] = max_issue_util

        #         if not issue in self.max_utility_by_issue.keys():
        #             self.max_utility_by_issue[issue] = 0

        # self.absolute_reservation_value = self.relative_reservation_value * self.get_max_utility()

    def add_utilities(self, new_utils):
        super().add_utilities(new_utils)

        if self.auto_constraints:
            self.add_constraints(self.generate_new_constraints())

    def generate_constraints(self, offer: Offer) -> Iterable[AtomicConstraint]:
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

                if best_case+value_util < self.acceptance_threshold:
                    new_constraints.add(AtomicConstraint(issue, value))

        return new_constraints
