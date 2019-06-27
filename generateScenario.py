from functools import partial
from itertools import product
from multiprocessing import Pool


def generate_utility_matrices(n, m, tau_a, tau_b=None):
    u_a = {}
    u_b = {}
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


def count_acceptable_offers(u_a, u_b, rho_a, rho_b, weights_a=None, weights_b=None):
    pool = Pool()
    issue_iter = iter(u_a)
    all_offers = list(product(*[list(u_a[next(issue_iter)].keys()) for _ in range(len(u_a.keys()))]))
    if weights_a:
        a_accepts = partial(accepts, u=u_a, rho=rho_a / len(weights_a), weights=weights_a)
    else:
        a_accepts = partial(accepts, u=u_a, rho=rho_a)

    if weights_b:
        b_accepts = partial(accepts, u=u_b, rho=rho_b / len(weights_b), weights=weights_b)
    else:
        b_accepts = partial(accepts, u=u_b, rho=rho_b)

    acceptable_to_a = list(map(a_accepts, all_offers))
    acceptable_to_b = list(map(b_accepts, all_offers))
    acceptable_to_both = [acceptable_to_a[i] and acceptable_to_b[i] for i in range(len(acceptable_to_a))]

    return sum(acceptable_to_a), sum(acceptable_to_b), sum(acceptable_to_both)


def util(offer, u, weights=None):
    if weights:
        return sum(map(lambda x: u[x][offer[x]] * weights[offer[x]], range(len(offer))))
    else:
        # print(offer)
        return sum(map(lambda x: u[x][offer[x]], range(len(offer))))


def accepts(offer, u, rho, weights=None):
    return util(offer, u, weights) >= rho


# u_a,u_b = generate_utility_matrices(3,6,3)
# pretty_print_matrix(u_a)
# pretty_print_matrix(u_b)