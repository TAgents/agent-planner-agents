# This file makes agents a Python package.
# It makes the agents discoverable by the ADK CLI.

# DO NOT import from coordination.agent here to avoid circular import
# Instead, create a pointer to where the root agent is located
import importlib

def get_root_agent():
    """Helper function to get the root agent from coordination module."""
    coordination_module = importlib.import_module('coordination.agent')
    return coordination_module.root_agent

# Create an agent attribute that points to a module with a root_agent attribute
# This is what ADK CLI looks for
class AgentModule:
    @property
    def root_agent(self):
        return get_root_agent()

agent = AgentModule()