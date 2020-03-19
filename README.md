PyNeg is a Python library for experimenting and benchmarking automated negotiatons. Using both Numpy and ProbLog as a background it can take advantage of probabalistic models and complex knowledge bases. 

Some simple negotiation strategies have already been implemented and provide a template for how to implement new negotiation strategies and how to combine the various parts into an agent. This library favours composition over inheretance and thus is very modular.

for a more detailed explanation please refer to the [documentation](https://pyneg.readthedocs.io/en/latest/index.html).

### Minimal Working Example


```python
>>> from pyneg.agent.agent_factory import make_linear_concession_agent 
>>> neg_space = {"first":[0, 1, 2, 3, 4], "second":[5,6,7,8,9]}  
>>> utilities_a = {"second_5":10,"second_9":-10,"first_0":-5,"first_3":5}  
>>> utilities_b = {"second_5":-5,"second_7":5,"first_0":10,"first_4":-10}  
>>> res_a = 0.1  
>>> res_b = 0.1  
>>> non_agreement_cost = -10**100   
>>> agent_a = make_linear_concession_agent("A",neg_space,utilities_a,res_a,non_agreement_cost)  
>>> agent_b = make_linear_concession_agent("B",neg_space,utilities_b,res_b,non_agreement_cost)  
>>> agent_a.negotiate(agent_b) 
True
>>> agent_a._transcript 
[(A=>B;OFFER;[first->3, second->5]),
(B=>A;OFFER;[first->0, second->7]),
(A=>B;OFFER;[first->1, second->5]),
(B=>A;OFFER;[first->0, second->6]),
(A=>B;OFFER;[first->2, second->5]),
(B=>A;OFFER;[first->0, second->8]),
(A=>B;OFFER;[first->4, second->5]),
(B=>A;OFFER;[first->0, second->9]),
(A=>B;OFFER;[first->3, second->6]),
(B=>A;OFFER;[first->1, second->7]),
(A=>B;OFFER;[first->0, second->5]),
(B=>A;ACCEPT;[first->0, second->5])]
```

