from typing import Optional, Set, List, Iterable

from pyneg.comms import AtomicConstraint
from pyneg.comms import Offer
from pyneg.types import NegSpace, AtomicDict
from pyneg.utils import atom_from_issue_value
from .constrained_problog_evaluator import ConstrainedProblogEvaluator
from .dtp_generator import DTPGenerator


# TODO At the moment this class still assumes a lot of linearity
# at some point this should be recitfied


class ConstrainedDTPGenerator(DTPGenerator):

    def __init__(self,
                 neg_space: NegSpace,
                 utilities: AtomicDict,
                 non_agreement_cost: float,
                 acceptance_threshold: float,
                 kb: List[str],
                 constr_value: float,
                 initial_constraints: Optional[Set[AtomicConstraint]],
                 auto_constraints=True):
        self.constr_value = constr_value
        self.evaluator = ConstrainedProblogEvaluator(
            neg_space, utilities, non_agreement_cost, kb,constr_value, set())
        self.constr_value = constr_value
        self.constraints: Set[AtomicConstraint] = set([])
        if initial_constraints:
            self.constraints.update(initial_constraints)
        self.auto_constraints = auto_constraints
        super().__init__(neg_space, utilities, non_agreement_cost, acceptance_threshold, kb)
        self.index_max_utilities()
        self.constraints_satisfiable = True
        self.add_constraints(self.discover_constraints())

    def reset_generator(self):
        super().reset_generator()
        self.constraints = set()
        self.index_max_utilities()

    def add_constraint(self, constraint: AtomicConstraint) -> bool:
        self.constraints.add(constraint)
        self.evaluator.add_constraint(constraint)
        self.index_max_utilities()
        if len(self.get_unconstrained_values_by_issue(constraint.issue)) == 0:
            self.constraints_satisfiable = False
            return False

        return True

    def add_constraints(self, constraints: Iterable[AtomicConstraint]) -> bool:
        self.constraints.update(constraints)
        self.evaluator.add_constraints(self.constraints)
        self.index_max_utilities()
        for issue in self.neg_space.keys():
            if len(self.get_unconstrained_values_by_issue(issue)) == 0:
                self.constraints_satisfiable = False
                return False

        return True

    def satisfies_all_constraints(self, offer: Offer) -> bool:
        for constr in self.constraints:
            if not constr.is_satisfied_by_offer(offer):
                return False

        return True

    def _add_utilities(self, new_utils):
        super().add_utilities(new_utils)

    def add_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = {
            **self.utilities,
            **new_utils
        }

        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())

        return self.constraints_satisfiable

    def set_utilities(self, new_utils: AtomicDict) -> bool:
        self.utilities = new_utils
        if self.auto_constraints:
            self.add_constraints(self.discover_constraints())

        return self.constraints_satisfiable

    def accepts(self, offer: Offer) -> bool:
        if offer.get_sparse_repr() in self.generated_offers:
            util = self.generated_offers[offer.get_sparse_repr()]
        else:
            util = self.evaluator.calc_offer_utility(offer)
        return util >= self.acceptability_threshold and self.satisfies_all_constraints(offer)

    def compile_dtproblog_model(self):
        model_string = super().compile_dtproblog_model()

        constr_string = ""
        for constr in self.constraints:
            constr_atom = atom_from_issue_value(constr.issue, constr.value)
            constr_string += "utility({},{}).\n".format(constr_atom,
                                                        self.non_agreement_cost)

        return model_string + constr_string

    # TODO figure out a way to do non-linear constraint discovery
    def discover_constraints(self) -> Set[AtomicConstraint]:
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

    def get_unconstrained_values_by_issue(self, issue: str):
        issue_constrained_values = set(
            constr.value for constr in self.constraints if constr.issue == issue)
        issue_unconstrained_values = set(
            self.neg_space[issue]) - issue_constrained_values
        return issue_unconstrained_values

    def find_violated_constraint(self, offer: Offer) -> Optional[AtomicConstraint]:
        for constr in self.constraints:
            for issue in offer.get_issues():
                chosen_value = offer.get_chosen_value(issue)
                if not constr.is_satisfied_by_assignment(issue, chosen_value):
                    return AtomicConstraint(issue, chosen_value)

        return None

    def generate_offer(self) -> Offer:
        if not self.constraints_satisfiable:
            raise StopIteration()
        try:
            offer = super().generate_offer()
        except StopIteration:
            raise StopIteration()
        if not self.satisfies_all_constraints(offer):
            raise RuntimeError()
        return offer

    def index_max_utilities(self):
        self.max_utility_by_issue = {
            issue: 0 for issue in self.neg_space.keys()}
        for issue in self.neg_space.keys():
            unconstrained_values = self.get_unconstrained_values_by_issue(
                issue)
            if len(unconstrained_values) == 0:
                self.constraints_satisfiable = False
                return

            max_issue_util = -(2 ** 31)
            for value in self.neg_space[issue]:
                util = self.evaluator.calc_assignment_util(issue, value)
                if util > max_issue_util:
                    max_issue_util = util
                    self.max_utility_by_issue[issue] = max_issue_util

    def get_constraints(self):
        return self.constraints