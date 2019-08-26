from typing import Dict, Tuple, Union, cast, Iterable
from re import sub, search
from abstract_agent import Verbosity
from numpy import isclose
from offer import Offer
AtomicDict = Dict[str, float]
NestedDict = Dict[str, Dict[str, float]]


class Strategy(Offer):
    def __init__(self, values_by_issue: Union[NestedDict, AtomicDict],
                 indent_level: int = 1, verbose=Verbosity.none):
        self.indent_level = indent_level
        if isinstance(next(iter(values_by_issue.items())), dict):
            self.values_by_issue: NestedDict = cast(
                NestedDict, values_by_issue)
        elif isinstance(next(iter(values_by_issue.items())), float):
            # convert to nested dict so checking for validity is easier
            self.values_by_issue = self.nested_dict_from_atom_dict(
                values_by_issue)
        else:
            raise ValueError(
                "invalid offer structure: {}".format(values_by_issue))

        for issue in self.values_by_issue.keys():
            if not isclose(sum(self.values_by_issue[issue].values()), 1):
                raise ValueError(
                    "Invalid offer, {issue} doesn't sum to 1".format(issue=issue))
            for value, prob in self.values_by_issue[issue].items():
                if not (0 <= prob <= 1):
                    raise ValueError(
                        "Invalid offer, {issue} has non-binary assignement".format(issue=issue))
                if value not in self.values_by_issue[issue].keys():
                    raise ValueError(
                        "Invalid offer, {issue} has unknown value: {value}".format(issue=issue, value=value))

    def get_value_dist(self, issue: str) -> Dict[str, float]:
        if issue in self.values_by_issue.keys():
            return self.values_by_issue[issue]
        else:
            raise KeyError("Issue {issue} is not known".format(issue=issue))

    def keys(self) -> Iterable[str]:
        return self.values_by_issue.keys()

    def set_prob(self, issue: str, value: str, prob: float) -> None:
        self.values_by_issue[issue][value] = prob
