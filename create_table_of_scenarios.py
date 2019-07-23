from pandas import DataFrame
from generateScenario import *

n = 6
m = 5


def create_table(n, m):
    u_a = np.zeros((n, m))
    u_b = np.zeros((n, m))
    results = DataFrame(columns=["n", "m", "tau_a", "tau_b", "rho_a", "rho_b", "a_accepts", "b_accepts", "both_accept",
                                 "p_a", "p_b"])

    for tau_a in range(0, n):
        for tau_b in range(0, n):

            # Rho is now relative to the maximal utility
            for rho_a in np.linspace(0, 1, 10):
                for rho_b in np.linspace(0, 1, 10):
                    u_a, u_b = generate_utility_matrices(u_a, u_b, tau_a, tau_b)
                    a, b, both = count_acceptable_offers(u_a, u_b, rho_a, rho_b)
                    results = results.append({"n": n, "m": m, "tau_a": tau_a, "tau_b": tau_b, "rho_a": rho_a,
                                              "rho_b": rho_b, "a_accepts": a, "b_accepts": b, "both_accept": both,
                                              "p_a": both / a if a != 0 else 0, "p_b": both / b if b != 0 else 0},
                                             ignore_index=True)

    print(results)
    results.to_csv("results.csv")


create_table(n, m)
