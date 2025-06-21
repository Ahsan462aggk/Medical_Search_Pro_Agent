"""Main entry point for the agent module."""
from medical_agent_bot.agent import root_agent as agent

# Make the agent available at the top level
root_agent = agent

if __name__ == "__main__":
    # The agent will be automatically discovered by ADK
    pass
