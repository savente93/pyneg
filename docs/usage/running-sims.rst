Running negotiations
=====================

The main entry point for a negotiaiton is the :code:`negotiate` method, which takes the opponent as an argument. This method checks that the agents are compatible (i.e. checks that they have the same negotiation space) and then initiates the negotiation. 


Analysing results
------------------
The return value of the :code:`negotiate` method is a boolean representing whether the negotiation was successful. During the negotiation each agent maintains a transcript in the :code:`_transcript` variable. At the end of the negotiation both agents should have the same transcript.  This transcript can be used for benchmarking. 

