from util.geo_utli import get_current_weather
from services.state_store import get_live_location
from langchain.tools import tool


@tool
async def WeatherTool() -> dict:
    """Fetches current weather of the users location"""
    location = await get_live_location()
    return get_current_weather(location["latitude"], location["longitude"])
