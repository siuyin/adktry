import os
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types

from dotenv import load_dotenv


import sys
sys.path.append("../..")

from . import prompt

load_dotenv()

def _render_reference(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse:
    del callback_context
    if ( not llm_response or
            not llm_response.content.parts or
            not llm_response.grounding_metadata ):
        return llm_response

    references=[]
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title,uri,text="","",""
        if chunk.retrieved_context:
            title=chunk.retrieved_context.title
            uri=chunk.retrieved_context.uri
            text=chunk.retrieved_context.text
        elif chunk.web:
            title=chunk.web.title
            uri=chunk.web.uri
        parts=[s for s in (title,text) if s]
        if uri and parts:
            parts[0]=f"[{parts[0]}]({uri})"
        if parts:
            references.append("* "+": ".join(parts)+"\n")

    if references:
        reference_text="".join(["\n\nreference:\n\n"] + references)
        llm_response.content.parts.append(types.Part(text=reference_text))

    if all(part.text is not None for part in llm_response.content.parts):
        all_text="\n".join(part.text for part in llm_response.content.parts)
        llm_response.content.parts[0].text = all_text
        del llm_response.content.parts[1:]

    return llm_response


critic_agent=Agent(
        model=os.getenv("MODEL"),
        name='critic_agent',
        instruction=prompt.CRITIC_PROMPT,
        tools=[google_search],
        )
