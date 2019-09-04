from itertools import product
from re import search, sub
from typing import List, Dict
from typing import Tuple

import numpy as np

from pyneg.types import NestedDict


def nested_dict_from_atom_dict(atom_dict) -> NestedDict:
    nested_dict: NestedDict = {}
    for atom in atom_dict.keys():
        # following patern is guaranteed to work since no _ in the names are allowed
        issue, value = issue_value_tuple_from_atom(atom)
        if issue not in nested_dict.keys():
            nested_dict[issue] = {}

        nested_dict[issue][value] = float(atom_dict[atom])

    return nested_dict


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


def atom_from_issue_value(issue: str, value: str) -> str:
    if "." in str(value):
        return "'{issue}_{val}'".format(issue=issue, val=value)
    else:
        return "{issue}_{val}".format(issue=issue, val=value)


def atom_dict_from_nested_dict(nested_dict):
    atom_dict = {}
    for issue in nested_dict.keys():
        for value in nested_dict[issue].keys():
            atom = atom_from_issue_value(
                issue, value)
            atom_dict[atom] = nested_dict[issue][value]

    return atom_dict


def generate_binary_utility_matrices(shape, tau_a, tau_b=None):
    u_a = np.zeros(shape)
    u_b = np.zeros(shape)
    if not tau_b:
        tau_b = tau_a

    u_a[:, :tau_a] = 1
    u_b[:, tau_b:] = 1
    return u_a, u_b


def generate_gradient_utility_matrices(shape, tau_a, tau_b=None):
    n, m = shape
    if not tau_b:
        tau_b = tau_a

    # starts at -1000 and linearly increases to 0 at tau_a then linearly increases until 1000 at m
    u_a = np.append(np.tile(np.linspace(-1000, 0, tau_a), (n, 1)),
                    np.tile(np.linspace(0, 1000, m - tau_a + 1), (n, 1))[:, 1:], axis=1)

    u_b = np.append(np.tile(np.linspace(1000, 0, tau_b), (n, 1)),
                    np.tile(np.linspace(0, -1000, m - tau_b + 1), (n, 1))[:, 1:], axis=1)

    return u_a, u_b


def generate_lex_utility_matrices(shape, order):
    n, m = shape
    u_a = np.arange(n * m).reshape(n, m) ** order
    u_b = np.flip(np.arange(n * m)).reshape(n, m) ** order

    return u_a, u_b


def count_acceptable_offers(u_a, u_b, rho_a_percentile, rho_b_percentile, w_a=None, w_b=None):
    n, m = u_a.shape
    if not w_a:
        w_a = 1 / n * np.ones((1, n))
    if not w_b:
        w_b = 1 / n * np.ones((1, n))

    issue_indices = np.tile(np.arange(n), (m ** n, 1))
    value_indices = np.array(list(product(*[range(m) for _ in range(n)])))

    utils_a = np.dot(u_a[issue_indices, value_indices], w_a.T)
    utils_b = np.dot(u_b[issue_indices, value_indices], w_b.T)

    rho_a_absolute = rho_a_percentile * max(utils_a)
    rho_b_absolute = rho_b_percentile * max(utils_b)

    a_accepts = utils_a >= rho_a_absolute
    b_accepts = utils_b >= rho_b_absolute

    both_accept = np.logical_and(a_accepts, b_accepts)

    return a_accepts.sum(), b_accepts.sum(), both_accept.sum()


def neg_scenario_from_util_matrices(u_a, u_b):
    utils_a = {}
    utils_b = {}
    issues: Dict[str, List[str]] = {}
    number_of_issues_to_generate, issue_cardinality = u_a.shape

    for i in range(number_of_issues_to_generate):
        issues["issue{i}".format(i=i)] = list(map(
            str, list(range(issue_cardinality))))
        for j in range(issue_cardinality):
            utils_a["issue{i}_{j}".format(i=i, j=j)] = u_a[i, j]
            utils_b["issue{i}_{j}".format(i=i, j=j)] = u_b[i, j]

    return issues, utils_a, utils_b
