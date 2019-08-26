from typing import Dict, Tuple, Union, cast
from re import sub, search
from abstract_agent import Verbosity
from numpy import isclose
AtomicDict = Dict[str, float]
NestedDict = Dict[str, Dict[str, float]]


class Offer:
    def __init__(self, values_by_issue: Union[NestedDict, AtomicDict],
                 indent_level: int = 1, verbose=Verbosity.none):
        self.indent_level = indent_level
        if isinstance(next(iter(values_by_issue.items())), dict):
            self.values_by_issue: NestedDict = cast(
                NestedDict, values_by_issue)
        elif isinstance(next(iter(values_by_issue.items())), float):
            # convert to nested dict so checking for validity is easier
            self.values_by_issue = Offer.nested_dict_from_atom_dict(
                values_by_issue)
        else:
            raise ValueError(
                "invalid offer structure: {}".format(values_by_issue))

        for issue in self.values_by_issue.keys():
            if not isclose(sum(self.values_by_issue[issue].values()), 1):
                raise ValueError(
                    "Invalid offer, {issue} doesn't sum to 1".format(issue=issue))
            for value, prob in self.values_by_issue[issue].items():
                if not (isclose(prob, 1) or isclose(prob, 0)):
                    raise ValueError(
                        "Invalid offer, {issue} has non-binary assignement".format(issue=issue))
                if value not in self.values_by_issue[issue].keys():
                    raise ValueError(
                        "Invalid offer, {issue} has unknown value: {value}".format(issue=issue, value=value))

    def get_atom_dict(self) -> Dict[str, float]:
        atom_dict: Dict[str, float] = {}
        for issue in self.values_by_issue.keys():
            for value in self.values_by_issue[issue].keys():
                atom: str = self.atom_from_issue_value(issue, value)
                atom_dict[atom] = self.values_by_issue[issue][value]

        return atom_dict

    # will return the one value which is assigned 1
    # there is guaranteed to be exactly 1
    def get_chosen_value(self, issue: str) -> str:
        for val in self.values_by_issue[issue]:
            if isclose(self.values_by_issue[issue][val], 1):
                return val

        # should never happen
        raise RuntimeError("invalid internal offer state.")

    def __getitem__(self, key: Union[Tuple[str, str], str]) -> float:
        if isinstance(key, tuple):
            issue, value = key
            return self.values_by_issue[issue][value]
        else:
            return self.values_by_issue[key]

    @staticmethod
    def nested_dict_from_atom_dict(atom_dict) -> NestedDict:
        nested_dict: NestedDict = {}
        for atom in atom_dict.keys():
            # following patern is guaranteed to work since no _ in the names are allowed
            issue, value = Offer.issue_value_tuple_from_atom(atom)
            if issue not in nested_dict.keys():
                nested_dict[issue] = {}

            nested_dict[issue][value] = float(atom_dict[atom])

        return nested_dict

    @staticmethod
    def issue_value_tuple_from_atom(atom: str) -> Tuple[str, str]:
        s = search("(.*)_(.*)", atom)
        if not s:
            raise ValueError(
                "Could not parse atom: {atom}".format(atom=atom))

        issue, value = s.group(1, 2)
        # atoms containing floats have an extra ' which we need to remove
        issue = sub("'", "", issue)
        value = sub("'", "", value)
        return issue, value

    @staticmethod
    def atom_from_issue_value(issue: str, value: str) -> str:
        if "." in str(value):
            return "'{issue}_{val}'".format(issue=issue, val=value)
        else:
            return"{issue}_{val}".format(issue=issue, val=value)

    def __repr__(self) -> str:
        string = ""
        for issue in self.values_by_issue.keys():
            string += " " * self.indent_level * 4 + '{}: '.format(issue)
            for key in self.values_by_issue[issue].keys():
                if self.values_by_issue[issue][key] == 1:
                    string += "{}\n".format(key)
                    break
        return string[:-1]  # remove trailing newline

    def get_problog_dists(self) -> str:
        return_string = ""
        for issue in self.values_by_issue.keys():
            atom_list = []
            for value in self.values_by_issue[issue].keys():
                atom = Offer.atom_from_issue_value(
                    issue, value)
                atom_list.append("{prob}::{atom}".format(
                    prob=self.values_by_issue[issue][value], atom=atom))

            return_string += ";".join(atom_list) + ".\n"

        return return_string
