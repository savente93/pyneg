Quich theory overview
=======================

.. basic-terms:

Basic terminology
----------------------

.. In this section we'll give a very brief overvew into negotiaton theory to explain some of the terms used thoughout this documentaiton. 
.. For a more complete discussion of the theory see `<http://http://orca.cf.ac.uk/{lit_rev_id}/>`_ see :ref:`representations` for more information on how these are represented in this library.

In this section we'll give a very brief overvew into negotiaton theory to explain some of the terms used thoughout this documentaiton. 

*Issues* are the subject of the negotiatons, and the *values* are possible options for those issues. The collection of these issues as is called the *negotiation space* and is denoted as :math:`\Omega`. For example, if we wanted to model a job contract negotiaton the negotiation space might consist of the following issues and their values:

- Salary: [2.000£, 4.000£]
- Hours per week: [30, 34, 38] 
- Vacation days per year: [20, 24, 28]
- Company Car: [Yes, No]

Note that there is no inherent ordering between issues or values. In this context an *offer*, denoted as  :math:`\omega` is a mapping between issues and their values. In the example above that might be `(Salary->2.000, Hours per week->30, Vacation days per year->24, Company Car:->Yes)`

An agent's preference profile is what determines which offers agents prefer over others. In this case they are all specified by *utility functions* which are denoted as :math:`u`. In the example above we might value getting a Salary of 2.000 as 100 points but 4.000 as 1000 since it would allow us to do more than just double the things (potentially). Conversely if we like the job, we might not care at aall how many hours per week we work (within the allowed range). We might not care too much about vacation or the car individually, but if we get both we could go on a read trip. This would be represented by the car itself being worth 10 points and every vacation day above 20 would be worth 1 point, however a vacation of 28 days together with the car would be worth another 100 points. 

The more theoretical mathematically inclined reader might find it useful to conceptuallise of issues as finite sets :math:`\Lambda`, the negotioation space as the products of those sets :math:`\Omega = \prod \Lambda`, in which case offers are simply vectors in that space :math:`\omega\in\Omega` and utility functions are functions :math:`u: \Omega\to\mathbb{R}`.



.. _linear-additivity:

Linear additivity
-------------------
While utility functions can be repesented and calculated in any arbitrary way, sometimes it if desirable to have a function that is easily computable even if it is less expressive. One type of such utility functions are called *linear additive* utility functions, or simply linear utilities for short. Such linear utilities are of the form:

.. math:: 
    u(\omega) = \sum_{i=0}^N e_i(\omega_i)w_i

Here the :math:`w_i` represent the relative importance of the issues, which should form a distribution and the :math:`e_i` are local utility functions :math:`e_i: \Lambda_i \to \mathbb{R}`. This formalises that the utility of an assignment is independent of the other assignments. 

For example, the utility function described above would not be an example of a linear utility function since more points get awarded if a combination of assignments occur (vacation as well as car). However if we only consider the utility gained for the Salary and nothing else that would be considered a linear utility. 

.. _constraint-discovery:

Constraint discovery
----------------------

A *constraint* is an expression that denotes that any offer that does not meet certain conditions will be rejected. Currently only *atomic constraints* are supported. An *atomic constraint* is an expression that one perticular issue value assignment is unacceptable. For example, in the job negotiation example above an atomic constraint might be that any offer which states that the company car would be provided would be rejected. In this instance that would be denoted as "Company Car != Yes". This can allow adversaries to traverse the negotiation space more efficiently. 
