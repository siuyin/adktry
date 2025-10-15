import os
from google.adk.agents import SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent

llm_auditor=SequentialAgent(
        name="llm_auditor",
        description="""Evaluates LLM generated answers,
        verifies accuracy through the web and refines response
        to align with real-world knowlege""",
        sub_agents=[critic_agent,reviser_agent],
        )

root_agent=llm_auditor
