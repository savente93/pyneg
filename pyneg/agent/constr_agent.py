from pyneg.comms import AtomicConstraint
from pyneg.agent import Agent


class ConstrainedAgent(Agent):
    def __init__(self):
        super().__init__()
        pass

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        self._engine.add_constraint(constraint)

    def get_unconstrained_values_by_issue(self, issue):
        return self._engine.get_unconstrained_values_by_issue(issue)

    def get_constraints(self):
        return self._engine.get_constraints()

    def _accepts_negotiation_proposal(self, neg_space) -> bool:
        return self._neg_space == neg_space and self._constraints_satisfiable