from itertools import product

import numpy as np


def generate_utility_dicts(u_a, u_b, n, m, tau_a, tau_b=None):
    if not tau_b:
        tau_b = tau_a

    for i in range(n):
        u_a[i] = {}
        u_b[i] = {}
        for j in range(m):
            if j < tau_a:
                u_a[i][j] = 1
            else:
                u_a[i][j] = 0

            if j < tau_b:
                u_b[i][j] = 0
            else:
                u_b[i][j] = 1

    return u_a, u_b


def generate_utility_matrices(shape, tau_a, tau_b=None, kind="binary"):
    if kind == "binary":
        u_a = np.zeros(shape)
        u_b = np.zeros(shape)
        if not tau_b:
            tau_b = tau_a

        u_a[:, :tau_a] = 1
        u_b[:, tau_b:] = 1
        return u_a, u_b

    elif kind == "gradient":

        n, m = shape
        if not tau_b:
            tau_b = tau_a

        # starts at -1000 and linearly increases to 0 at tau_a then linearly increases until 1000 at m
        u_a = np.append(np.tile(np.linspace(-1000, 0, tau_a), (n, 1)),
                        np.tile(np.linspace(0, 1000, m - tau_a + 1), (n, 1))[:, 1:], axis=1)

        u_b = np.append(np.tile(np.linspace(1000, 0, tau_b), (n, 1)),
                        np.tile(np.linspace(0, -1000, m - tau_b + 1), (n, 1))[:, 1:], axis=1)

        return u_a, u_b

    else:
        raise ValueError("Trying to generate unknown type of utility matrix: {}".format(kind))




def pretty_print_matrix(mat):
    n = len(mat)
    m = len(mat[0])
    max_elt = max([max(row) for row in mat.values()])
    max_len = len(str(max_elt))
    print((" " * (max_len + 2)) + ", ".join(map(lambda x: "{:>{}}".format(x, max_len), map(str, range(m)))))
    for i in range(n):
        st = "{}, ".format(i) + ", ".join(
            map(lambda x: "{:>{}}".format(x, max_len), map(lambda j: str(mat[i][j]), range(len(mat[i])))))
        print(st)
    print()


def count_acceptable_offers(u_a, u_b, rho_a_percentile, rho_b_percentile, w_a=None, w_b=None):
    # offers = product(*[range(u_a.shape[1]) for _ in range(u_a.shape[0])])
    # assignment_utils_a = np.zeros((0, u_a.shape[0]))
    # if not weights_a:
    #     weights_a = np.ones(u_a.shape[0]) / u_a.shape[0]
    # if not weights_b:
    #     weights_b = np.ones(u_b.shape[0]) / u_b.shape[0]
    # assignment_utils_b = np.zeros((0, u_b.shape[0]))
    # for offer in offers:
    #     assignment_utils_a = np.append(assignment_utils_a,[[u_a[j, offer[j]] for j in range(u_a.shape[0])]], axis=0)
    #     assignment_utils_b = np.append(assignment_utils_b, [[u_b[j, offer[j]] for j in range(u_a.shape[0])]], axis=0)
    #
    # a_accepts = np.dot(assignment_utils_a, weights_a) >= rho_a / u_a.shape[0]
    # b_accepts = np.dot(assignment_utils_b, weights_b) >= rho_b / u_b.shape[0]
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

    # issue_iter = iter(u_a)
    # all_offers = list(product(*[list(u_a[next(issue_iter)].keys()) for _ in range(len(u_a.keys()))]))
    # if weights_a:
    #     a_accepts = partial(accepts, u=u_a, rho=rho_a / len(weights_a), weights=weights_a)
    # else:
    #     a_accepts = partial(accepts, u=u_a, rho=rho_a)
    #
    # if weights_b:
    #     b_accepts = partial(accepts, u=u_b, rho=rho_b / len(weights_b), weights=weights_b)
    # else:
    #     b_accepts = partial(accepts, u=u_b, rho=rho_b)
    #
    # acceptable_to_a = list(map(a_accepts, all_offers))
    # acceptable_to_b = list(map(b_accepts, all_offers))
    # acceptable_to_both = [acceptable_to_a[i] and acceptable_to_b[i] for i in range(len(acceptable_to_a))]

    # return sum(acceptable_to_a), sum(acceptable_to_b), sum(acceptable_to_both)


def util(offer, u, weights=None):
    if weights:
        return sum(map(lambda x: u[x][offer[x]] * weights[offer[x]], range(len(offer))))
    else:
        return sum(map(lambda x: u[x][offer[x]], range(len(offer))))


def accepts(offer, u, rho, weights=None):
    return util(offer, u, weights) >= rho


if __name__ == "main":
    a = {}
    b = {}
    print(generate_utility_dicts(a, b, 10, 10, 5))
    # count_acceptable_offers(u_a, u_b, 3, 3)
