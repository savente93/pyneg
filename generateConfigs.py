from scipy.stats import norm
from numpy import arange
from random import randint
from numpy.random import normal
def difficulty(n,m,mu_a,sigma_a,rho_a,mu_b,sigma_b,rho_b ):
	return 1-(norm(0,1).cdf((rho_a-n*m*mu_a)/(n*m*sigma_a))*norm(0,1).cdf((rho_b-n*m*mu_b)/(n*m*sigma_b)))

def findDiffConfig(diff,strat="Random"):
	n = 1
	m = 1
	mu_a = 0
	sigma_a = 1
	rho_a = 0
	mu_b = 0
	sigma_b = 1
	rho_b = 0
	while abs(difficulty(n,m,mu_a,sigma_a,rho_a,mu_b,sigma_b,rho_b) - diff) >= 0.001:
		n = randint(1,15)
		m = randint(1,15)
		mu_a = normal(0,10)
		sigma_a = normal(0,10)
		rho_a = normal(0,10)
		mu_b = normal(0,10)
		sigma_b = normal(0,10)
		rho_b = normal(0,10)

	return n,m,mu_a,sigma_a,rho_a,mu_b,sigma_b,rho_b, strat


def generateConfigs(lst,strat="Random"):
	for diff in arange(0.1,1,0.1):
		config = findDiffConfig(diff)
		lst.append(config)

configs = []
for _ in range(10):
	generateConfigs(configs,"Random")
for _ in range(10):
	generateConfigs(configs,"Constrained")


print(len(configs))
print(configs)