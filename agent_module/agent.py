from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from agent_module.sub_agents.query_ingestor_agent import med_query_ingestor
from agent_module.sub_agents.evidence_builder_agent import med_evidence_builder
from agent_module.sub_agents.email_dispatcher_agent import med_email_dispatcher




# Create the sequential agent
medsearchpro_orchestrator = SequentialAgent(
    name="article_fetcher_and_summarizer",
    sub_agents=[med_query_ingestor, med_evidence_builder, med_email_dispatcher],
    description="Executes a sequence of article fetching, summarization, and email delivery.",
    
)

root_agent = medsearchpro_orchestrator

