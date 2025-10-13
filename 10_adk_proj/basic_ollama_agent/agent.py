from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm 
from dotenv import load_dotenv
import os

import sys
sys.path.append(".")

load_dotenv()

root_agent=Agent(
        name="basic_ollama_agent",
        model = LiteLlm( os.getenv("MODEL") ),
        instruction="You are an expert researcher. You stick to the facts.",
        )

