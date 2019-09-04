from typing import Optional, Set, Dict, List, Iterable
from pyneg.comms import Offer
from pyneg.types import NegSpace, NestedDict, AtomicDict
from .evaluator import Evaluator
from .strategy import Strategy
from numpy.random import choice
from pyneg.comms import AtomicConstraint
from .generator import Generator
from .enum_generator import EnumGenerator
from pyneg.utils import atom_from_issue_value
from copy import deepcopy
from uuid import uuid4


class ConstrainedEnumGenerator(EnumGenerator):
    def __init__(self, neg_space: NegSpace,
                 utilities: AtomicDict,
                 evaluator: Evaluator,
                 acceptance_threshold: float,
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True) -> None:
        self.acceptance_threshold = acceptance_threshold
        self.constraints = set()
        super().__init__(neg_space, utilities, evaluator, acceptance_threshold)
        if initial_constraints:
            self.constraints.add(initial_constraints)
        self.auto_constraints = auto_constraints
        self.max_utility_by_issue = {}
        self.constraints_satisfiable = True
        self.index_max_utilities()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self.constraints.add(constraint)
        self.evaluator.add_constraint(constraint)
        self.index_max_utilities()

    def add_constraints(self, constraints: List[AtomicConstraint]) -> None:
        self.constraints.update(constraints)
        self.evaluator.add_constraints(constraints)
        self.index_max_utilities()

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
                unconstrained_values = self.get_unconstrained_values_by_issue(
                    issue)
                if len(unconstrained_values) == 0:
                    self.constraints_satisfiable = False
                    return

                best_val = self.sorted_utils[issue][0]
                if best_val in unconstrained_values:
                    self.max_utility_by_issue[issue] = self.utilities[atom_from_issue_value(
                        issue, best_val)]

    def get_unconstrained_values_by_issue(self, issue):
        issue_constrained_values = set(
            constr.value for constr in self.constraints if constr.issue == issue)
        issue_unconstrained_values = set(
            self.neg_space[issue]) - issue_constrained_values
        return issue_unconstrained_values

    def add_utilities(self, new_utils):
        super().add_utilities(new_utils)

        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())

    def expland_assignment(self, sorted_offer_indices):
        for issue in self.neg_space.keys():
            copied_offer_indices = deepcopy(sorted_offer_indices)
            if copied_offer_indices[issue] + 1 >= len(self.sorted_utils[issue]):
                continue
            copied_offer_indices[issue] += 1
            offer = self.offer_from_index_dict(copied_offer_indices)
            util = self.evaluator.calc_offer_utility(offer)
            if self.offer_from_index_dict(copied_offer_indices) not in self.generated_offers:
                # might seem stratge but if we hit a constraint we still need to keep searching in this direction
                if util >= self.acceptability_threshold or not self.satisfies_all_constraints(offer):
                    self.assignement_frontier.put(
                        (-util, uuid4(), copied_offer_indices))
                    self.generated_offers.add(
                        self.offer_from_index_dict(copied_offer_indices))

    def generate_offer(self) -> Offer:
        if self.assignement_frontier.empty() or not self.constraints_satisfiable:
            raise StopIteration()

        negative_util, uuid, indices = self.assignement_frontier.get()
        self.expland_assignment(indices)
        offer = self.offer_from_index_dict(indices)
        if self.satisfies_all_constraints(offer):
            return offer
        else:
            return self.generate_offer()

    # def generate_offer(self) -> Offer:

    #     try:
    #         offer = super().generate_offer()
    #         while not self.satisfies_all_constraints(offer):
    #             offer = super().generate_offer()
    #     except StopIteration:
    #         raise StopIteration()
    #     return offer

    def accepts(self, offer: Offer) -> bool:
        util = self.evaluator.calc_offer_utility(offer)
        return util >= self.acceptability_threshold and self.satisfies_all_constraints(offer)

    def discover_constraints(self) -> Iterable[AtomicConstraint]:
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

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        for constr in self.constraints:
            for issue in offer.get_issues():
                chosen_value = offer.get_chosen_value(issue)
                if not constr.is_satisfied_by_assignment(issue, chosen_value):
                    return AtomicConstraint(issue, chosen_value)

        return None
