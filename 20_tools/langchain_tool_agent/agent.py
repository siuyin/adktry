import os

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.langchain_tool import LangchainTool # import

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv

load_dotenv()

root_agent=Agent(
        name="langchain_tool_agent",
        model=LiteLlm(os.getenv("MODEL")),
        description="Answers questions using Wikipedia",
        instruction="""Research the topic suggested by the user,
        Share the information you have found with the user.""",
        tools=[ LangchainTool(tool=WikipediaQueryRun( api_wrapper=WikipediaAPIWrapper() )) ],
        )

