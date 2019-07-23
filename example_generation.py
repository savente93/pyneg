import numpy as np
from itertools import product

n = 10
m = 10
tau = m//2
rho = 0.5

u_a = np.zeros((n,m))
u_a[:,tau:] = 1 
u_b = np.ones((n,m))
u_b[:,tau:] = 0 
w = 1/n*np.ones((1,n))

issue_indeces = np.tile(np.arange(n),(m**n,1)) 
value_indeces = np.array(list(product(*[range(m) for _ in range(n)])))

utils_a = np.dot(u_a[issue_indeces,value_indeces],w.T)
utils_b = np.dot(u_b[issue_indeces,value_indeces],w.T)

print(np.sum(utils_a >= rho))
print(np.sum(utils_b >= rho))

#results[(results.loc[:,'p_a'] >0) & (results.loc[:,'p_a'] <1)].loc[:,"p_a"].hist(bins=20); plt.title("Number of configurations found by p_a"); plt.ylabel("Number of configs"); plt.xlabel("P_a"); plt.show()