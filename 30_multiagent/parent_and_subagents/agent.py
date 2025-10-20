import os

# from dotenv import load_dotenv
from google.adk import Agent

# from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from google.adk.tools.tool_context import ToolContext

# load_dotenv()


def save_attractions_to_state(
    tool_context: ToolContext, attractions: list[str]
) -> dict[str, str]:
    """Saves the list of attractions to state["attractions"]
    Args:
    attractions [str]: a list of strings to add to the list of attractions.

    Returns:
    status dict
    """
    existing_attractions = tool_context.state.get("attractions", [])
    tool_context.state["attractions"] = existing_attractions + attractions
    return {"status": "success"}


attractions_planner = Agent(
    name="attractions_planner",
    # model=LiteLlm(os.getenv("MODEL")),
    model=os.getenv("GEMINI_MODEL"),
    description="Build a list of attractions to visit in a country.",
    instruction="""
        - Provide the user options for attractions to visit within their selected country.
        - When they reply, use your tool to save their selected attraction
        and then provide more possible attractions.
        - If they ask to view the list, provide a bulleted list of
        { attractions? } and then suggest some more.
        """,
    tools=[save_attractions_to_state],
)

travel_brainstormer = Agent(
    name="travel_brainstormer",
    # model=LiteLlm(os.getenv("MODEL")),
    model=os.getenv("GEMINI_MODEL"),
    description="Help a user decide which country to visit.",
    instruction="""
        Provide a few suggestions of popular countries to visit.

        Help the user identify their primary goal of travel:
        adventure, leisure, learning, shopping or viewwing art etc.

        Identify countries that would make great destinations
        based on their priorities.
        """,
)

root_agent = Agent(
    name="steering",
    # model=LiteLlm(os.getenv("MODEL")),
    model=os.getenv("GEMINI_MODEL"),
    description="Start a user on a travel adventure.",
    instruction="""
        Ask the user if they know where they would like to travel
        or if they need some help deciding.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    sub_agents=[travel_brainstormer, attractions_planner],
)
