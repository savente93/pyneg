from numpy import isclose


class Constraint():
    pass


class NoGood(Constraint):
    def __init__(self, issue, value):
        self.issue = str(issue)
        self.value = str(value)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        if self.issue != other.issue:
            return False

        if self.value != other.value:
            return False

        return True

    def isSatisfiedByAssignement(self, issue, value):
        return not (issue == self.issue and value == self.value)

    def isSatisfiedByStrat(self, strat):
        for issue in strat.keys():
            for value in strat[issue]:
                if isclose(strat[issue][value], 0):
                    continue

                if not self.isSatisfiedByAssignement(issue, value):
                    return False

        return True

    def __hash__(self):
        return hash((self.issue, self.value))

    def __repr__(self):
        return "NoGood({issue},{value})".format(issue=self.issue, value=self.value)
