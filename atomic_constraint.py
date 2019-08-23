from numpy import isclose


class AtomicConstraint():
    def __init__(self, issue: str, value: str):
        self.issue = str(issue)
        self.value = str(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtomicConstraint):
            return False

        if self.issue != other.issue:
            return False

        if self.value != other.value:
            return False

        return True

    def is_satisfied_by_assignment(self, issue: str, value: str) -> bool:
        return not (issue == self.issue and value == self.value)

    def is_satisfied_by_strat(self, strat: dict) -> bool:
        for issue in strat.keys():
            for value in strat[issue]:
                if isclose(strat[issue][value], 0):
                    continue

                if not self.is_satisfied_by_assignment(issue, value):
                    return False

        return True

    def __hash__(self) -> int:
        return hash((self.issue, self.value))

    def __repr__(self) -> str:
        return "AtomicConstraint({issue},{value})".format(issue=self.issue, value=self.value)
