from constrProbAwareAgent import ConstrProbAwareAgent
from constraint import NoGood
from math import pi
from message import Message
genericIssues = {
    "boolean": [True, False],
    "integer": list(range(10)),
    "float": [float("{0:.2f}".format(0.1 * i)) for i in range(10)]
}
arbitraryConstraint = NoGood("boolean", "False")
arbitraryReservationValue = 0
constraintMessage = Message(
    "constraint", arbitraryConstraint)
arbitraryUtilities = {
    "boolean_True": 100,
    "integer_2": -1000,
    "'float_0.1'": -3.2,
    "'float_0.5'": pi
    # TODO still need to look at compound and negative atoms
}
arbitraryKb = [
    "boolean_True :- integer_2, 'float_0.1'."
]
denseNestedTestOffer = {
    "boolean": {"True": 1, "False": 0},
    "integer": {str(i): 0 for i in range(10)},
    "float": {"{0:.1f}".format(i*0.1): 0 for i in range(10)}
}
denseNestedTestOffer["integer"]["3"] = 1
denseNestedTestOffer['float']["0.6"] = 1
agent = ConstrProbAwareAgent(
    arbitraryUtilities, arbitraryKb, arbitraryReservationValue)
opponent = ConstrProbAwareAgent(
    arbitraryUtilities, arbitraryKb, arbitraryReservationValue)
agent.setupNegotiation(genericIssues)
