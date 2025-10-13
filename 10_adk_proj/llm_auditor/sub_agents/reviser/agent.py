import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from dotenv import load_dotenv

import sys
sys.path.append("../..")

from . import prompt

load_dotenv()

_END_OF_EDIT_MARK="---END-OF-EDIT---"

def _remove_end_of_edit_mark(callback_context: CallbackContext,llm_response: LlmResponse) -> LlmResponse:
    del callback_context
    if (not llm_response.content or not llm_response.content.parts):
        return llm_response

    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx+1:]
            part.text=part.text.split(_END_OF_EDIT_MARK,1)[0]
    return llm_response

reviser_agent=Agent(
        #model = LiteLlm( os.getenv("MODEL") ),
        #model = LiteLlm( "ollama_chat/qwen3:0.6b"),
        model = os.getenv("MODEL"),
        name="reviser_agent",
        instruction=prompt.REVISER_PROMPT,
        )
