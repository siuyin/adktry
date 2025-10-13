import asyncio
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types

import os
from dotenv import load_dotenv

import sys
sys.path.append(".")

load_dotenv()

model_name=LiteLlm(os.getenv("MODEL"))
prompt=os.getenv("PROMPT",default="What is the capital of France?")


async def main():
    app_name="my_agent_app"
    user_id_1="user1"

    root_agent=Agent( model=model_name, name="trivia_agent",
            instruction="Answer questions")

    runner=InMemoryRunner( agent=root_agent, app_name=app_name)

    my_session=await runner.session_service.create_session( app_name=app_name,user_id=user_id_1)

    async def run_prompt(session: Session, new_message: str):
        content=types.Content( role="user",parts=[types.Part.from_text(text=new_message)])
        print("User says:", content.model_dump(exclude_none=True))
        async for event in runner.run_async( user_id=user_id_1, session_id=session.id, new_message=content):
            if event.content.parts and event.content.parts[0].text:
                print(f"{event.author}: {event.content.parts[0].text}")

    await run_prompt(my_session, prompt)

if __name__ == "__main__":
    asyncio.run(main())
