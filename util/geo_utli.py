import os
import aiohttp
import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
load_dotenv()

geolocator = Nominatim(user_agent="kayori")

WEAHTER_API_KEY = os.getenv("WEATHER_API")
if not WEAHTER_API_KEY:
    raise ValueError("weather api_key not found")


# Retrieves the current location based on latitude and longitude.
def get_current_location(lat, lon):
    loca = geolocator.reverse(f"{str(lat)},{str(lon)}")
    address = loca.raw.get('address', {})

    state = address.get('state', 'Unknown')
    suburb = address.get('suburb', 'Unknown')
    city = address.get('city', address.get('town', 'Unknown'))

    return {"suburb": suburb, "city": city, "state": state}


async def aget_current_location(lat: float, lon: float):
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            }
            headers = {"User-Agent": "kayori"}
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    address = data.get("address", {})
                    state = address.get('state', 'Unknown')
                    suburb = address.get('suburb', 'Unknown')
                    city = address.get('city', address.get('town', 'Unknown'))
                    return {"suburb": suburb, "city": city, "state": state}
    except Exception as e:
        print(f"[Location API Error] {e}")
    return {"suburb": "Unknown", "city": "Unknown", "state": "Unknown"}

# Retrieves the current weather conditions for a given location.


def get_current_weather(lat, lon):
    url = f"http://api.weatherapi.com/v1/current.json?key={
        WEAHTER_API_KEY}&q={str(lat)},{str(lon)}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature_c": data["current"]["temp_c"],
            "feels_like_c": data["current"]["feelslike_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "cloud_cover": data["current"]["cloud"],
            "visibility_km": data["current"]["vis_km"],
            "wind_speed_kph": data["current"]["wind_kph"],
            "wind_direction": data["current"]["wind_dir"],
        }
    else:
        return {"error": "Failed to fetch weather data"}


# Retrieves the weather forecast for a given location.
def get_forcast_weather(lat, lon):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={
        WEAHTER_API_KEY}&q={str(lat)},{str(lon)}&days=1&aqi=no&alerts=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        today_forecast = data["forecast"]["forecastday"][0]

        hourly_data = []
        for hour in today_forecast["hour"]:
            hourly_data.append({
                "time": hour["time"],
                "condition": hour["condition"]["text"],
            })

        return {
            "forecast": hourly_data
        }
    else:
        return {"error": "Failed to fetch weather data"}
