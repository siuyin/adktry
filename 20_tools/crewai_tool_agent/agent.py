import os

from google.genai import types
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import ScrapeWebsiteTool


root_agent=Agent(
        name="crewai_tool_agent",
        model=LiteLlm(os.getenv("MODEL")),
        description="Agent to scrape AP News website",
        instruction="Scrape the AP News website to get the latest news.",
        generate_content_config=types.GenerateContentConfig(temperature=0),
        tools=[CrewaiTool(
            name="scrape_apnews",
            description="Scrapes the latest news content from the Associated Press (AP) website",
            tool=ScrapeWebsiteTool("https://apnews.com/")),
            ],
        )

