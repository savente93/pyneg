from baseProbAwareAgent import BaseProbAwareAgent
from message import Message
from constraint import Constraint, NoGood


class ConstrProbAwareAgent(BaseProbAwareAgent):
    def __init__(self, utilities, kb, reservationValue, nonAgreementCost, issues=None, maxRounds=10000, verbose=0, name=""):
        super().__init__(utilities, kb, reservationValue,
                         nonAgreementCost, issues=issues, verbose=verbose)
        self.negotiationActive = False
        self.agentName = name
        self.successful = False
        self.stratName = "ACOP"
        self.messageCount = 0
        self.maxRounds = maxRounds
        self.ownConstraints = set()
        self.opponentConstraints = set()


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
                self.stratDict[issue][next(iter(issueUnConstrainedValues))] = 1
            else:
                stratSum = sum(self.stratDict[issue].values())
                self.stratDict[issue] = {
                    key: prob/stratSum for key, prob in self.stratDict[issue].items()}

        self.addUtilities({"{issue}_{value}".format(issue=constraint.issue, value=constraint.value): self.nonAgreementCost})

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

    def generateNextMessageFromTranscript(self):
        try:
            lastMessage = self.transcript[-1]
        except IndexError:
            # if our transcript is empty, we should make the initial offer
            return self.generateOfferMessage()

        if lastMessage.isAcceptance():
            self.negotiationActive = False
            self.successful = True
            self.report()
            return None

        if lastMessage.isTermination():
            self.negotiationActive = False
            self.successful = False
            self.report()
            return None

        if self.shouldTerminate(lastMessage):
            self.negotiationActive = False
            self.successful = False
            self.report()
            return Message(self.agentName, self.opponent.agentName, "terminate", lastMessage.offer)

        if self.accepts(lastMessage.offer):
            self.negotiationActive = False
            self.successful = True
            self.report()
            return Message(self.agentName, self.opponent.agentName, "accept", lastMessage.offer)

        violatedConstraint = self.generateViolatedConstraint(lastMessage.offer)
        return self.generateOfferMessage(violatedConstraint)

    def generateOfferMessage(self,constr = None):
        offer = self.generateOffer()
        # generate Offer can return a termination message if no acceptable offer can be found so we whould check for that
        if type(offer) == dict:
            return Message(self.agentName, self.opponent.agentName, kind="offer", offer=offer, constraint=constr)
        elif type(offer) == Message:
            offer.constraint = constr
            return offer

    def generateViolatedConstraint(self, offer):

        for constr in self.ownConstraints:
            for issue in offer.keys():
                for value in offer[issue].keys():
                    if not constr.isSatisfiedByAssignement(issue, value):
                        return NoGood(issue, value)

    def calcOfferUtility(self, offer):
        if not self.isOfferValid(offer):
            raise ValueError("Invalid offer received")
        if not self.satisfiesAllConstraints((offer)):
            return self.nonAgreementCost

        return super().calcOfferUtility(offer)