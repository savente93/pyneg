from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from problog.tasks import sample
from problog import get_evaluatable
from problog.logic import Term
from numpy import isclose
from baseProbAwareAgent import BaseProbAwareAgent
from re import match
from message import Message
from constraint import Constraint, NoGood


class ConstrProbAwareAgent(BaseProbAwareAgent):
    def __init__(self, utilities, kb, reservationValue, nonAgreementCost, issues=None, smart=False, maxRounds=10000, verbose=0, name=""):
        super().__init__(utilities, kb, reservationValue,
                         nonAgreementCost, issues=issues, verbose=verbose)
        self.negotiationActive = False
        self.agentName = name
        self.successful = False
        self.stratName = "Constraint aware ProbLog"
        self.messageCount = 0
        self.maxRounds = maxRounds
        self.ownConstraints = set()
        self.opponentConstraints = set()

    def generateConstraintMessage(self, offer):
        for constr in self.ownConstraints:
            for issue in offer.keys():
                for value in offer[issue].keys():
                    if not constr.isSatisfiedByAssignement(issue, value):
                        return Message(kind="constraint", content=NoGood(issue, value))

    def addOwnConstraint(self, constraint):
        if self.verbose >= 2:
            print("{} is adding own constraint: {}".format(
                self.agentName, constraint))
        self.ownConstraints.add(constraint)
        for issue in self.stratDict.keys():
            issueConstrainedValues = [
                constr.value for constr in self.ownConstraints if constr.issue == issue]
            issueUnConstrainedValues = set(
                self.stratDict[issue].values()) - set(issueConstrainedValues)
            if len(issueUnConstrainedValues) == 0:
                if self.verbose >= 2:
                    print("Own constraint base: {}".format(self.ownConstraints))
                    print("received constraint: {}".format(constraint))
                raise RuntimeError(
                    "Unsatisfyable constraints on issue {}".format(issue))

            for value in self.stratDict[issue].keys():
                if not constraint.isSatisfiedByAssignement(issue, value):
                    self.stratDict[issue][value] = 0

            # it's possible we just made the last value in the stratagy 0 so we have to figure out which value is still unconstrained
            # and set that one to 1
            if sum(self.stratDict[issue].values()) == 0:
                self.stratDict[issue][next(iter(issueUnConstrainedValues))]
            else:
                stratSum = sum(self.stratDict[issue].values())
                self.stratDict[issue] = {
                    key: prob/stratSum for key, prob in self.stratDict[issue].items()}

        self.addUtilities({"{issue_value}".format})

    def addOpponentConstraint(self, constraint):
        if self.verbose >= 2:
            print("{} is adding opponent constraint: {}".format(
                self.agentName, constraint))
        self.opponentConstraints.add(constraint)
        for issue in self.stratDict.keys():
            for value in self.stratDict[issue].keys():
                if not constraint.isSatisfiedByAssignement(issue, value):
                    self.stratDict[issue][value] = 0

    def satisfiesAllConstraints(self, offer):
        allConstraints = self.ownConstraints.copy().union(self.opponentConstraints)
        for constr in allConstraints:
            if not constr.isSatisfiedByStrat(offer):
                return False
        return True
