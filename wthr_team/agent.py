from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from typing import Optional

MISTRAL = "ollama_chat/mistral"  # works well

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'report' key with weather details.
            If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
            "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
            "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
            "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
            }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

def say_hello(name: Optional[str] = None) -> str: 
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!" # Default greeting if name is None or not explicitly passed
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    return greeting


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

greeting_agent = None
try:
    greeting_agent = Agent(
            name="greeting_agent",
            model = LiteLlm(model=MISTRAL),
            instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
            "Use the 'say_hello' tool to generate the greeting. "
            "If the user provides their name, make sure to pass it to the tool. "
            "Do not engage in any other conversation or tasks.",
            description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
            tools=[say_hello],
            )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    farewell_agent = Agent(
            name="farewell_agent",
            model = LiteLlm(model=MISTRAL),
            instruction = "You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
            "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
            "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
            "Do not perform any other actions.",
            description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
            tools=[say_goodbye],
            )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")

root_agent = Agent(
        name = "weather_agent_v1",
        model = LiteLlm(model=MISTRAL),
        description = "The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction = "You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
        "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
        "You have specialized sub-agents: "
        "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
        "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
        "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
        "If it's a weather request, handle it yourself using 'get_weather'. "
        "For anything else, respond appropriately or state you cannot handle it.",
        tools = [get_weather], # Pass the function directly
        sub_agents = [greeting_agent, farewell_agent],
        )
