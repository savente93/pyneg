from random import choice
from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from problog.tasks import sample
from problog import get_evaluatable


class RandomAgent():
    def __init__(self, issues, reservationValue=-100):
        self.strat = "Random"
        self.reservationValue = reservationValue
        self.issues = issues

    def accepts(self, offer):
        return self.calcUtility(offer) >= self.reservationValue

    def generateOffer(self):
        offer = {issue: choice(self.issues[issue])
                 for issue in self.issues.keys()}

        while self.calcUtility(offer) < self.reservationValue:
            offer = {issue: choice(self.issues[issue])
                     for issue in self.issues.keys()}
        return offer

    def calcUtility(self, offer):
        e = {
            "randsomMoney": lambda money: money//1000,
            "shootAtTerrorist": lambda s: -10000 if s else 0,
            "hostagesKilled": lambda h: 100*h,
            "getawayVehicleProvided": lambda vehicle: 1000 if vehicle else 0,
            "escapeAllowed": lambda vehicle: 1000 if vehicle else 0
        }

        totalUtility = 0

        for issue in self.issues.keys():
            totalUtility += e[issue](offer[issue])

        return totalUtility
