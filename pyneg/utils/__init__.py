"""
Defines some functions that are useful but
don't really belong else where.
Most are used for setting up scenarios, or message/offer
format conversion.
"""

from .utils import generate_binary_utility_matrices
from .utils import generate_gradient_utility_matrices
from .utils import generate_lex_utility_matrices
from .utils import count_acceptable_offers
from .utils import neg_scenario_from_util_matrices
from .utils import atom_from_issue_value
from .utils import issue_value_tuple_from_atom
from .utils import nested_dict_from_atom_dict
from .utils import atom_dict_from_nested_dict
from .utils import setup_random_scenarios
from .utils import generate_random_scenario
