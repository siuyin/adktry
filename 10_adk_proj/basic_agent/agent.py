from google.adk import Agent
import os

root_agent=Agent(
        name="basic_llm_agent",
        model=os.getenv("MODEL"),
        instruction="You are an expert researcher. You stick to the facts.",
        )

