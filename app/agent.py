# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None



import os
import requests


def get_live_ambient_conditions(city: str) -> str:
    """Fetches real live temperature and relative humidity conditions for a city via Open-Meteo API.

    Args:
        city: Name of the city (e.g. 'San Francisco', 'New York', 'London').

    Returns:
        A string containing current live temperature (°C / °F) and relative humidity (%).
    """
    try:
        api_key = os.getenv("WEATHER_API_KEY", "")
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url, timeout=5).json()
        if not geo_res.get("results"):
            return f"Could not find coordinates for city '{city}'."
        
        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_name = loc.get("name", city)
        country = loc.get("country", "")
        
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
        )
        if api_key:
            weather_url += f"&apikey={api_key}"
            
        w_res = requests.get(weather_url, timeout=5).json()
        current = w_res.get("current", {})
        temp_c = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        
        if temp_c is None or humidity is None:
            return f"Could not retrieve ambient weather data for {city_name}."
            
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        return (
            f"Live Ambient Conditions for {city_name}, {country}:\n"
            f"- Temperature: {temp_c}°C ({temp_f}°F)\n"
            f"- Relative Humidity: {humidity}%\n"
            f"Note: High humidity (>60%) slows soil drying; low humidity (<40%) accelerates evaporation."
        )
    except Exception as e:
        return f"Error fetching live weather data for '{city}': {e}"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def calculate_expression(expression: str) -> str:
    """Evaluates a mathematical expression safely.

    Args:
        expression: A mathematical string expression to evaluate, e.g. '12 * (4 + 5)'.

    Returns:
        The result of the calculation as a string.
    """
    try:
        # Safe math evaluation using basic AST/eval restrictions
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression."
        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from app.a2ui_utils import a2ui_callback
from app.firestore_backend import (
    add_or_update_plant,
    get_plant_info,
    list_nursery_stock,
    log_watering_event,
)
from app.image_tool import generate_plant_image
from app.video_tool import generate_plant_video
from app.maps_tools import find_nearby_places, geocode_address

AGENT_ENGINE_RESOURCE = os.getenv(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/734189490959/locations/us-central1/reasoningEngines/164860223712919552",
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_system_prompt = schema_manager.generate_system_prompt(
    role_description="You are Sprout & Sage, an expert botanical and plant care assistant.",
    workflow_description=(
        "Analyze the user's request and return structured UI when appropriate. "
        "You remember the user's stated preferences, plant collection, and specifically ALL user health conditions and allergies "
        "(such as plant sap allergies, pollen sensitivity, latex/sap allergies, or chemical sensitivities). "
        "Always check retrieved memory for user allergies and enforce them strictly when recommending plants, soil mixes, or care routines."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_system_prompt,
    tools=[
        get_weather,
        get_current_time,
        calculate_expression,
        list_nursery_stock,
        get_plant_info,
        add_or_update_plant,
        log_watering_event,
        get_live_ambient_conditions,
        geocode_address,
        find_nearby_places,
        generate_plant_image,
        generate_plant_video,
        PreloadMemoryTool(),
    ],
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE
    ),
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
