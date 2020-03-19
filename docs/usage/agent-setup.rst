Setting up agents for a negotiation
=====================================

Using the factories
--------------------

Because inheritance is ill suited to deal with the number of possible combinations that agents can reason about utility and generate offers, this library uses factories and something resemling composition over inheritance. That means that the :code:`__init__` methods of most classes don't do a lot since all of that is handled by the factories. Rather than describing all of the individual classes and factories a description of the possible components of the agents is given here along with a list of available factories. 

Linear evaluation agents 
-------------------------

Linear agents evaluate offers in the way described in :ref`linear-additivity`. Todo this they need a importance distribution across the issues. If none is provided they will use a uniform distribution. Note that his will modify how much utility specific offers get. Factories will adjust the reservation value accordingly. 

.. code-block:: python

    >>> neg_space = {"first":[0, 1, 2, 3, 4], "second":[5,6,7,8,9]}  
    >>> utils = {"second_5":10,"second_9":-10,"first_0":-5,"first_3":5}  
    >>> reservation_value = 0.1  
    >>> non_agreement_cost = -10**100   
    >>> linear_agent = make_linear_concession_agent("Antonia",neg_space,utils,reservation_value,non_agreement_cost)  
    >>> linear_agent
    Antonia 

Random agents
--------------

Random agents define probability distributions over all the values per issue. They generate offers by sampling from those distributions. The linear random agents use numpy as a backend and consequently are much faster but also cannot handle knowledge bases. For example:

.. code-block:: python

    >>> neg_space = {"first":[0, 1, 2, 3, 4], "second":[5,6,7,8,9]}  
    >>> utils = {"second_5":10,"second_9":-10,"first_0":-5,"first_3":5}  
    >>> reservation_value = 0.1  
    >>> non_agreement_cost = -10**100   
    >>> importance_weights = {"first": 0.7, "second": 0.3}
    >>> agent = make_linear_random_agent("Lulu",neg_space,utils,reservation_value,non_agreement_cost,importance_weights)  
    >>> agent
    Lulu

Problog agents
----------------

ProbLog agents use ProbLog as a backend and can consequently calculate utilities and generate optimal offers in negotiations that have knowledge bases. 


.. code-block:: python

    >>> neg_space = {"first":[0, 1, 2, 3, 4], "second":[5,6,7,8,9]}  
    >>> utils = {"second_5":10,"second_9":-10,"first_0":-5,"first_3":5}  
    >>> reservation_value = 0.1  
    >>> non_agreement_cost = -10**100   
    >>> knowledge_base = ["first_3 :- first_2"]
    >>> agent = make_random_agent("Harrison",neg_space,utilities_a,res_a,non_agreement_cost,knowledge_base)  
    >>> agent
    Harrison


Constraint aware agents
------------------------

Finally constraint aware agents can reason about constraints both when they can be created and then they make negotiations impossible. 

.. code-block:: python

    >>> neg_space = {"first":[0, 1, 2, 3, 4], "second":[5,6,7,8,9]}  
    >>> utils = {"second_5":10,"second_9":-10,"first_0":-5,"first_3":5, "first_1":-1000}  
    >>> reservation_value = 0.1  
    >>> non_agreement_cost = -10**100   
    >>> init_constraints = set(AtomicConstraint("second","7"))
    >>> constr_agent = make_linear_concession_agent("Liam",neg_space,utils,reservation_value,non_agreement_cost)  
    >>> constr_agent
    Liam
    >>> constr_agent._engine.get_constraints() 
    {first!=1, second!=7, second!=9}