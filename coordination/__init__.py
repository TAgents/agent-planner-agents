"""
Coordination module for ADK Multiagent System.

Exports the create_coordinator_agent async factory function.
The root_agent is created in the agent.py module.
"""

# Only import the factory function, not the root_agent
# This helps avoid circular imports
from .agent import create_coordinator_agent