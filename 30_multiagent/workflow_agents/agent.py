import os
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools import exit_loop
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)


def append_to_state(
    tool_context: ToolContext, field: str, response: str
) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
    field (str): a field name to append to
    response (str): a string to append to the field

    Returns:
    dict[str,str]: {"status": "success"}
    """
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    return {"status": "success"}


def write_file(
    tool_context: ToolContext, directory: str, filename: str, content: str
) -> dict[str, str]:
    target_path = os.path.join(directory, filename)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return {"status": "success"}


file_writer = Agent(
    name="file_writer",
    model=model_name,
    description="Creates marketing details and saves a pitch document",
    instruction="""
        PLOT OUTLINE:
        { PLOT_OUTLINE? }

        INSTRUCTIONS:
        - Create a marketable, contemporay movie title suggestion for the movie described in the PLOT OUTLINE. If a title has been suggested in PLOT_OUTLINE, you can use it or replace it with a better one.
        - Use your 'write_file' tool to create a new txt file with the following arguments:
          - for a filename, use the movie title
          - write to the 'movie_pitches' directory
          - for the content to write, extract the following from the PLOT OUTLINE:
            - A logline
            - Synopsis or plot outline
        """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[write_file],
)

screenwriter = Agent(
    name="screenwriter",
    model=model_name,
    description="As a screenwriter, write a logline and a plot outline for a biopic about a historical character.",
    instruction="""
        INSTRUCTIONS:
        Your goal is to write a logline and a tree-act plot outline for an inspiring movie about the historical character(s) described by PROMPT: { PROMPT? }

        - If there is CRITICAL_FEEDBACK, use those thoughts to improve upon the outline.
        - If there is RESEARCH provided, feel free to use details from it, but you are not required to use it at all.
        - If there is a PLOT_OUTLINE, improve upon it.
        - Use the 'append_to_state' tool to write your logline and three-act plot outline to the field 'PLOT_OUTLINE'.
        - Summarize what you focused on in this pass.

        PLOT_OUTLINE:
        { PLOT_OUTLINE? }

        RESEARCH:
        { research? }

        CRITICAL_FEEDBACK:
        { CRITICAL_FEEDBACK? }
        """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[append_to_state],
)

researcher = Agent(
    name="researcher",
    model=model_name,
    description="Answer research questions using Wikipedia.",
    instruction="""
        PROMPT:
        { PROMPT? }

        PLOT_OUTLINE:
        { PLOT_OUTLINE? }

        CRITICAL_FEEDBACK:
        { CRITICAL_FEEDBACK? }

        INSTRUCTIONS:
        - If there is a CRITICAL_FEEDBACK, use your wikipedia tool to do research to solve those suggestions.
        - If there is a PLOT_OUTLINE, use your wikipedia tool to do research and add more historical detail.
        - If these are empty, use your wikipedia tool to gather facts about the person in the PROMPT.
        - Use the 'append_to_state' tool to add your research to the field 'research'.
        - Summarize what you have learned.

        Now use your wikipedia tool to do research.
        """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        LangchainTool(tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())),
        append_to_state,
    ],
)

critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
        INSTRUCTIONS:
        Consider these questions about the PLOT_OUTLINE:
        - Does it meet a satisfying three-act cinematic structure?
        - Do the chracters' struggles seem engaging?
        - Does it feel grounded in a real time period in history?
        - Does it sufficiently incorporate historical details from the RESEARCH?

        If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
        If significant improvements can be made use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
        Explain your decision and briefly summarize the feedback you have provided.

          PLOT_OUTLINE:
          { PLOT_OUTLINE? }

          RESEARCH:
          { research? }
          """,
    tools=[append_to_state, exit_loop],
)

writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[
        researcher,
        screenwriter,
        critic,
    ],
    max_iterations=5,
)

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[
        writers_room,
        file_writer,
    ],
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="Guides the user in crafting a movie plot.",
    instruction="""
        - Let the user knw you will help them write a pitch for a hit movie. Ask them for a historical figure to create a movie about.
        - When they respond, use the 'append_to_state' tool to store the user's respons in the 'PROMPT' state key and transfer to the 'film_concept_team' agent.
        """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[append_to_state],
    sub_agents=[film_concept_team],
)
