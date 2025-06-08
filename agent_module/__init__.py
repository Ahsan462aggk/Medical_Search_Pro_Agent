"""Agent module for scholarly article search and summarization."""

# Import and expose the root agent
from .agent import root_agent

# Explicitly declare what should be importable
__all__ = ['root_agent']

# For compatibility with older versions of Python
from . import agent  # This ensures the module is loaded

# This is required for ADK to find the root_agent
agent = root_agent