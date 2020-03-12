"""
This submodule contains all the logic for operating the agents that doesn't deal with
reasoning about the negotiation space such as proposal evaluation or generation.
This module defines the base and constraint agent classes and the agent factories,
needed to setup those agents.
"""

from pyneg.agent.agent import Agent
from pyneg.agent.constr_agent import ConstrainedAgent
from pyneg.agent.agent_factory import *
