# pylint: disable=C0103
"""
This module defines a lot of helper functions. Most are used
for setting up scenarios for simulations or bechmarks, or
are used to go from one format to another.

Functions:
    - issue_value_tuple_from_atom
    - atom_from_issue_value
    - atom_dict_from_nested_dict
    - nested_dict_from_atom_dict
    - generate_binary_utility_matrices
    - generate_gradient_utility_matrices
    - generate_lex_utility_matrices
    - count_acceptable_offers
    - neg_scenario_from_util_matrices
    - setup_random_scenarios
    - generate_random_scenario
    - insert_difficult_constraints
"""

from itertools import product
from os import mkdir, path
from re import search, sub
from typing import Dict, List, Tuple
from uuid import uuid4

import numpy as np
from numpy.random import randint

from pyneg.types import NestedDict

def issue_value_tuple_from_atom(atom: str) -> Tuple[str, str]:
    """
    takes an atomic representation of an issue value asignement and converts it into a tuple.
    Also correctly handles atoms that include . in the name, e.g. "'float_0.9'" which can trip up
    ProbLog. This is the inverse of :func:`atom_from_isue_value`.

    >>> issue_value_tuple_from_atom('Boolean_True')
    ("Boolean","True)
    >>> issue_value_tuple_from_atom("'float_0.9'")
    ('float', '0.9')


    :param atom:  the atom to parse
    :type atom: str
    :raises ValueError: if the given atom does not have a valid format
    :return: A tuple containing the issue and value respectively.
    :rtype: Tuple[str, str]
    """
    reg_search = search("(.*)_(.*)", atom)
    if not reg_search:
        raise ValueError(
            "Could not parse atom: {atom}".format(atom=atom))

    issue, value = reg_search.group(1, 2)

    # atoms containing floats have an extra ' which we need to remove
    issue = sub("'", "", issue)
    value = sub("'", "", value)
    return issue, value


def atom_from_issue_value(issue: str, value: str) -> str:
    """
    takes a tuple representation of an issue value asignement and converts it into an atmoic one.
    Also correctly handles atoms that include . in the name, e.g. ("float","0.9") which can trip up
    ProbLog. This is the inverse of :func:`issue_value_tuple_from_atom`.

    >>> issue_value_tuple_from_atom(("Boolean","True))
    'Boolean_True'
    >>> issue_value_tuple_from_atom(('float', '0.9'))
    "'float_0.9'"


    :param issue: The issue
    :type issue: str
    :param value: the value
    :type value: str
    :raises ValueError: if the given atom does not have a valid format
    :return: A tuple containing the issue and value respectively.
    :rtype: str
    """
    if "_" in issue or "_" in value:
        raise ValueError(f"{issue} or {value} contained illigal character: _")

    if "." in str(value):
        return f"'{issue}_{value}'"

    return f"{issue}_{value}"


def atom_dict_from_nested_dict(nested_dict: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Converts a nested disctionary into an atomic one. Useful when communicating with
    ProbLog. This is the inverse of :func:`nested_dict_from_atom_dict`

    >>> atom_dict_from_nested_dict({"boolean": {"True": 1.0, "False": 0.0}})
    {"boolean_True":1.0,"boolean_False":0.0}

    :param nested_dict: The nested dictionary to convert
    :type nested_dict: Dict[str, Dict[str, float]]
    :return: the atomic representation of the given nested dictionary
    :rtype: Dict[str, float]
    """
    atom_dict = {}
    for issue in nested_dict.keys():
        for value in nested_dict[issue].keys():
            atom = atom_from_issue_value(
                issue, value)
            atom_dict[atom] = nested_dict[issue][value]

    return atom_dict

def nested_dict_from_atom_dict(atom_dict: Dict[str, float]) -> NestedDict:
    """
    Converts an atomic disctionary into a nested one. Useful when communicating with
    ProbLog. This is the inverse of :func:`atom_dict_from_nested_dict`

    >>> atom_dict_from_nested_dict({"boolean_True":1.0,"boolean_False":0.0})
    {"boolean": {"True": 1.0, "False": 0.0}}


    :param atom_dict: [description]
    :type atom_dict: [type]
    :return: [description]
    :rtype: NestedDict
    """
    nested_dict: NestedDict = {}
    for atom in atom_dict.keys():
        # following patern is guaranteed to work since no _ in the names are allowed
        issue, value = issue_value_tuple_from_atom(atom)
        if issue not in nested_dict.keys():
            nested_dict[issue] = {}

        nested_dict[issue][value] = float(atom_dict[atom])

    return nested_dict


def generate_binary_utility_matrices(shape, tau_a, tau_b=None):
    """
    Generate binary utility matrices that agents can use to negotiate.
    Most useful when simulating. Shape refers to the shape of the matrix
    and tau_a refers to an index in the matrix past which all entries are 1 for
    one of the agent and 0 for the other. The default behaviour is specifically designed to
    generate utility matrices that have no common ground so consessions will
    be necessary to reach an agreement.

    >>> generate_binary_utility_matrices((5,5),3)
    (array([[1., 1., 1., 0., 0.],
        [1., 1., 1., 0., 0.],
        [1., 1., 1., 0., 0.],
        [1., 1., 1., 0., 0.],
        [1., 1., 1., 0., 0.]]),
     array([[0., 0., 0., 1., 1.],
        [0., 0., 0., 1., 1.],
        [0., 0., 0., 1., 1.],
        [0., 0., 0., 1., 1.],
        [0., 0., 0., 1., 1.]]))


    :param shape: Shape that the matrices should have
    :type shape: Tuple[int,int]
    :param tau_a: index
    :type tau_a: index of the tipping point in A's matrix
    :param tau_b: index of the tipping point in B's matrix, equal to tau_a if None
    :type tau_b: Optional[int]
    :return: a tuple of binary utility matrices
    :rtype: Tuple[Array[float], Array[float]]
    """
    u_a = np.zeros(shape)
    u_b = np.zeros(shape)
    if not tau_b:
        tau_b = tau_a

    u_a[:, :tau_a] = 1
    u_b[:, tau_b:] = 1
    return u_a, u_b


def generate_gradient_utility_matrices(shape, tau_a, tau_b=None):
    """
    Generate utility matrices that have a gradient along the horizontal axis that agents
    can use to negotiate. Shape refers to the shape of the matrix
    and tau_a refers to an index in the matrix that will have utlity 0 along the vertical axis.
    The default behaviour is specifically designed to generate utility matrices
    that have opposing desires but some possible common ground as a
    slightly more fogiving setup to :func:`generate_binary_utility_matrices`

    >>> generate_gradient_utility_matrices((5,5),3)
        (array([[-1000.,  -500.,     0.,   500.,  1000.],
                [-1000.,  -500.,     0.,   500.,  1000.],
                [-1000.,  -500.,     0.,   500.,  1000.],
                [-1000.,  -500.,     0.,   500.,  1000.],
                [-1000.,  -500.,     0.,   500.,  1000.]]),

         array([[ 1000.,   500.,     0.,  -500., -1000.],
                [ 1000.,   500.,     0.,  -500., -1000.],
                [ 1000.,   500.,     0.,  -500., -1000.],
                [ 1000.,   500.,     0.,  -500., -1000.],
                [ 1000.,   500.,     0.,  -500., -1000.]]))


    :param shape: Shape that the matrices should have
    :type shape: Tuple[int,int]
    :param tau_a: index
    :type tau_a: index of the tipping point in A's matrix
    :param tau_b: index of the tipping point in B's matrix, equal to tau_a if None
    :type tau_b: Optional[int]
    :return: a tuple of utility matrices
    :rtype: Tuple[Array[float], Array[float]]
    """
    n, m = shape
    if not tau_b:
        tau_b = tau_a

    # starts at -1000 and linearly increases to 0 at tau_a then linearly increases until 1000 at m
    u_a = np.append(np.tile(np.linspace(-1000, 0, tau_a), (n, 1)),
                    np.tile(np.linspace(0, 1000, m - tau_a + 1), (n, 1))[:, 1:], axis=1)

    u_b = np.append(np.tile(np.linspace(1000, 0, tau_b), (n, 1)),
                    np.tile(np.linspace(0, -1000, m - tau_b + 1), (n, 1))[:, 1:], axis=1)

    return u_a, u_b


def generate_lex_utility_matrices(shape: Tuple[int, int], order: int):
    """
    Generate utility matrices that have increasing lexicographical utilty. that agents
    can use to negotiate. Shape refers to the shape of the matrix and order refers
    to the exponent of the utility entries. mostly used for testing and benchmarking.

    >>> generate_lex_utility_matrices((5,5),3)
    >>>
    (array([[    0,     1,     8,    27,    64],
            [  125,   216,   343,   512,   729],
            [ 1000,  1331,  1728,  2197,  2744],
            [ 3375,  4096,  4913,  5832,  6859],
            [ 8000,  9261, 10648, 12167, 13824]]),
    array([[13824, 12167, 10648,  9261,  8000],
            [ 6859,  5832,  4913,  4096,  3375],
            [ 2744,  2197,  1728,  1331,  1000],
            [  729,   512,   343,   216,   125],
            [   64,    27,     8,     1,     0]]))


    :param shape: Shape that the matrices should have
    :type shape: Tuple[int, int]
    :param order: exponent of the index matrices
    :type order: int
    :return: a tuple of utility matrices
    :rtype: Tuple[Array[float], Array[float]]
    """
    n, m = shape
    u_a = np.arange(n * m).reshape(n, m) ** order
    u_b = np.flip(np.arange(n * m)).reshape(n, m) ** order

    return u_a, u_b


def count_acceptable_offers(
        u_a,
        u_b,
        rho_a_percentile: float,
        rho_b_percentile: float,
        w_a=None,
        w_b=None) -> Tuple[int, int, int]:
    """
    Counts the number of acceptable offers for each agent as well as the number of offers that is
    acceptable to both. Uses vecor arithmetic to speed up the calculation
    and therefore can only be used in linear additive situations.

    :param u_a: utility matrix for A
    :type u_a: Array[float]
    :param u_b: Utility matrix for B
    :type u_b: Array[float]
    :param rho_a_percentile: Percentage of maximum utility that A considders to be acceptable.
    :type rho_a_percentile: float
    :param rho_b_percentile: Percentage of maximum utility that B considders to be acceptable.
    :type rho_b_percentile: float
    :param w_a: distribution of issue importance, defaults to uniform
    :type w_a: Optional[Array[float]]
    :param w_b: distribution of issue importance, defaults to uniform
    :type w_b: Optional[Array[float]]
    :return: A tuple with entries representing the number of offers that \
        are acceptable to A, B and both resp.
    :rtype: Tuple[int,int,int]
    """
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
    """
    Constructs a negotiation scenario from given utlity matrices.
    this means that it generates a negotiation space as well as
    utility functions for both agents and returns all three in a tuple.

    :param u_a: Utility matrix of A
    :type u_a: ndarray
    :param u_b: Utility matrix of B
    :type u_b: ndarray
    :return: Negotiation space and utility functions needed to simulate a negotiation
    :rtype: Tuple[NegSpace,NestedDict,NestedDict]
    """
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

def setup_random_scenarios(root_dir, shape, numb_of_scenarios, numb_constraints):
    """
    Generates `numb_of_scenarios` utility matrices with uniform random integers as entries.
    Afterwards a number of constraints is injected into the scenarios and they are all saved
    in sepereate directories under `root_dir`. This is useful for setting up larger scale
    simulations or benchmarks for statistical analysis.

    :param root_dir: The path to the directory where all the scenarios will be saved.
    :type root_dir: str
    :param shape: shape of the utility matrcies that should be generated.
    :type shape: Tuple[int, int]
    :param numb_of_scenarios: The number of scenarios to generate
    :type numb_of_scenarios: int
    :param numb_constraints: The number of constraints inject into each scenario.
    :type numb_constraints: int
    """

    lower = 0
    upper = 100

    base_a = randint(lower, upper, shape[0]*shape[1]).reshape(shape)
    base_b = randint(lower, upper, shape[0]*shape[1]).reshape(shape)

    for _ in range(numb_of_scenarios):
        uuid = uuid4()

        scenario_dir = path.join(root_dir, str(uuid))
        mkdir(scenario_dir)

        for cntr in range(numb_constraints):
            instance_dir = path.join(scenario_dir, str(cntr))
            mkdir(instance_dir)
            constr_a, constr_b = insert_difficult_constraints(
                base_a, base_b, cntr)
            np.save(path.join(instance_dir, "a.npy"), constr_a)
            np.save(path.join(instance_dir, "b.npy"), constr_b)


def generate_random_scenario(shape, numb_constraints):
    """
    Generates a negotiation space and utility functions with random integers between 0 and 100.
    and returns them as a tuple. Useful for testing.

    :param shape: The shape that the utlity matrices should be
    :type shape: Tuple[int,int]
    :param numb_constraints: The number of constraints that should be injected.
    :type numb_constraints: int
    :return: A tuple of the negotiation space and utility functions.
    :rtype: Tuple[NegSpace,NestedDict,NestedDict]
    """

    lower = 0
    upper = 100

    base_a = randint(lower, upper, shape[0]*shape[1]).reshape(shape)
    base_b = randint(lower, upper, shape[0]*shape[1]).reshape(shape)

    return insert_difficult_constraints(base_a, base_b, numb_constraints)


def insert_difficult_constraints(a, b, numb):
    """
    This function wil inject values into utility matrices such that a constraint will
    be created there. `numb` constraints will be created into _each_ of the utility matrices
    for a total of `2*numb` constraints. The constraints will be created at assignments
    that the opponent has the higest utility to make them extra difficult.

    :param a: utility matrix for A
    :type a: array
    :param b: utility matrix for B
    :type b: array
    :param numb: Number of constraints to inject into each matrix.
    :type numb: int
    :return: A copy of the utility matrices with the constraints added.
    :rtype: Tuple[Array, Array]
    """
    constr = -1000
    a_ret = a.copy()
    b_ret = b.copy()
    for ind in map(lambda x: np.unravel_index(x, a.shape), b.flatten().argsort()[::-1][:numb]):
        i, j = ind
        a_ret[i, j] = constr

    for ind in map(lambda x: np.unravel_index(x, a.shape), a.flatten().argsort()[::-1][:numb]):
        i, j = ind
        b_ret[i, j] = constr

    return a_ret, b_ret
