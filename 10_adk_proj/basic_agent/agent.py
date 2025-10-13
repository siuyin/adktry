from google.adk import Agent
from google.adk.tools import google_search
import os

root_agent=Agent(
        name="basic_llm_agent",
        model=os.getenv("MODEL"),
        instruction="You are an expert researcher. You stick to the facts.",
        tools=[google_search],
        )

