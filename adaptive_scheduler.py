from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
import os
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from util.store import get_last_time
from util.weather import get_forcast_weather
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
geolocator = Nominatim(user_agent="kaori")


location = {
    "latitude": 25.4250076,
    "longitude": 81.8269705,
}

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.2
)


def get_location(lat, lon):
    loca = geolocator.reverse(f"{lat},{lon}")
    address = loca.raw.get('address', {})

    state = address.get('state', 'Unknown')
    suburb = address.get('suburb', 'Unknown')
    city = address.get('city', address.get('town', 'Unknown'))

    return {"suburb": suburb, "city": city, "state": state}


template1 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "you are weather forcase agent, your task is to take this json data which contain timestamp and weather_condition, your task is to tell about the todays weather in 20 words\
        forcast_data {data}"
    ),
    HumanMessagePromptTemplate.from_template("how's the todays weather?")
])


def weather(data: str) -> str:
    prompt = (template2 | llm).invoke({"data": data})
    return prompt.content


print(weather(get_forcast_weather(
    location["latitude"], location["longitude"])))

template2 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "you are weather forcase agent, your task is to take this json data which contain timestamp and weather_condition, your task is to tell about the todays weather in 20 words\
        forcast_data {data}"
    ),
    HumanMessagePromptTemplate.from_template("how's the todays weather?")
])


def location_change():
