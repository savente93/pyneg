from typing import Dict, Union, cast, List

from numpy import isclose

from pyneg.types import NestedDict, AtomicDict
from pyneg.utils import nested_dict_from_atom_dict, atom_from_issue_value


class Offer:
    def __init__(self, values_by_issue: Union[NestedDict, AtomicDict],
                 indent_level: int = 1):
        self.indent_level = indent_level
        if not isinstance(values_by_issue, dict):
            raise TypeError(
                "Expected a dictionary not {}".format(type(values_by_issue)))
        if isinstance(next(iter(values_by_issue.values())), dict):
            self.values_by_issue: NestedDict = cast(
                NestedDict, values_by_issue)
        elif isinstance(next(iter(values_by_issue.values())), float):
            # convert to nested dict so checking for validity is easier
            self.values_by_issue = nested_dict_from_atom_dict(
                values_by_issue)
        else:
            raise ValueError(
                "invalid offer structure: {}".format(values_by_issue))

        for issue in self.values_by_issue.keys():
            if not isclose(sum(self.values_by_issue[issue].values()), 1):
                raise ValueError(
                    "Invalid offer, {issue} doesn't sum to 1 in dict {d}".format(issue=issue, d=self.values_by_issue))
            for value, prob in self.values_by_issue[issue].items():
                if not (isclose(prob, 1) or isclose(prob, 0)):
                    raise ValueError(
                        "Invalid offer, {issue} has non-binary assignement".format(issue=issue))
                if value not in self.values_by_issue[issue].keys():
                    raise ValueError(
                        "Invalid offer, {issue} has unknown value: {value}".format(issue=issue, value=value))

        for issue in self.values_by_issue.keys():
            for value in self.values_by_issue[issue].keys():
                if not isinstance(self.values_by_issue[issue][value], float):
                    self.values_by_issue[issue][value] = float(
                        self.values_by_issue[issue][value])

    # will return the one value which is assigned 1
    # there is guaranteed to be exactly 1
    def get_chosen_value(self, issue: str) -> str:
        for val in self.values_by_issue[issue]:
            if isclose(self.values_by_issue[issue][val], 1):
                return val

        # should never happen
        raise RuntimeError("invalid internal offer state.")

    def __getitem__(self, key: str) -> Dict[str, float]:
        return self.values_by_issue[key]

    def is_assigned(self, issue: str, value: str) -> bool:
        return isclose(self.values_by_issue[issue][value], 1)

    def get_issues(self):
        return self.values_by_issue.keys()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Offer):
            return False

        # This way sparse and dense offers can still be equal
        # but they must have the same issues
        try:
            for issue in self.values_by_issue.keys():
                my_chosen_value = self.get_chosen_value(issue)
                their_chosen_value = other.get_chosen_value(issue)
                if my_chosen_value != their_chosen_value:
                    raise ValueError
        except:
            return False

        return True

    def __repr__(self) -> str:
        return_string = "\n"
        for issue in self.values_by_issue.keys():
            return_string += " " * self.indent_level * 4 + '{}: '.format(issue)
            for key in self.values_by_issue[issue].keys():
                if self.values_by_issue[issue][key] == 1:
                    return_string += "{}\n".format(key)
                    break
        return return_string[:-1]  # remove trailing newline

    def get_problog_dists(self) -> str:
        return_string = ""
        for issue in self.values_by_issue.keys():
            atom_list: List[str] = []
            for value in self.values_by_issue[issue].keys():
                atom = atom_from_issue_value(
                    issue, value)
                atom_list.append("{prob}::{atom}".format(
                    prob=self.values_by_issue[issue][value], atom=atom))

            return_string += ";".join(atom_list) + ".\n"

        return return_string

    def get_sparse_repr(self):
        return frozenset({(issue, self.get_chosen_value(issue)) for issue in self.values_by_issue.keys()})

    def get_sparse_str_repr(self):
        return ",".join([atom_from_issue_value(issue, self.get_chosen_value(issue))
                         for issue in self.values_by_issue.keys()]) + "."

    def __hash__(self):
        return hash(self.get_sparse_repr())
