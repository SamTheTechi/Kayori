import os
import discord
from pinecone import Pinecone
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from util.store import location, natures, update_context
from util.weather import get_forcast_weather
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime, timezone
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
load_dotenv()

# inislisation
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=intents)
geolocator = Nominatim(user_agent="kaori")
pc = Pinecone(api_key=os.getenv("PINECONE2"))
pineconeIndex = pc.Index("location")
embedding = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('EMBD'),
    model_name="sentence-transformers/all-mpnet-base-v2"
)
vector_store = PineconeVectorStore(embedding=embedding, index=pineconeIndex)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.2
)


def get_location(lat, lon):
    loca = geolocator.reverse(f"{str(lat)},{str(lon)}")
    address = loca.raw.get('address', {})

    state = address.get('state', 'Unknown')
    suburb = address.get('suburb', 'Unknown')
    city = address.get('city', address.get('town', 'Unknown'))

    return {"suburb": suburb, "city": city, "state": state}


template1 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a weather forecast agent. Your task is to analyze the provided JSON data, which contains timestamps and weather conditions.\
        Generate a **40-word summary** of today's weather in a format that is easy for other LLMs to understand.\
        forcast_data {data}"
    ),
    HumanMessagePromptTemplate.from_template("how's the todays weather?")
])


def weather_agent(data: str) -> str:
    prompt = (template1 | llm).invoke({"data": data})
    print(data)
    print(prompt.content)
    return prompt.content


def process_location(lat, lon, threshold=0.85, min_distance=5):

    user_location = get_location(location["latitude"], location["longitude"])

    location_text = f"Location: {lat}, {lon}. suburb:{
        user_location.get("suburb")} city: {user_location.get("city")}."

    results = vector_store.similarity_search(location_text, k=1)

    if results:
        match = results[0]
        score = match.score

        stored_lat = float(match.metadata.get("lat", 0))
        stored_lon = float(match.metadata.get("lon", 0))

        distance = geodesic((lat, lon), (stored_lat, stored_lon)).km

        if score >= threshold and distance <= min_distance:
            return False

    vector_store.add_texts(
        [location_text],
        metadatas=[{"lat": lat, "lon": lon, "timestamp": str(
            datetime.now(timezone.utc).isoformat())}]
    )

    return True


async def location_change(
        client,
        agent_executer,
        config,
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response = process_location(
            location["latitude"], location["longitude"])

        if not response:
            return

        response_text = ""
        current_time = datetime.now(timezone.utc).isoformat()

        val = [
            SystemMessage(
                "The user seems to have changed locations."
                "express curiosity. If it's expected, acknowledge it subtly."
                f"The current time is {current_time}."
            ),
            HumanMessage("Hey, I'm heading somewhere!")
        ]

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        await user.send(response_text)
        update_context(response_text)

    except Exception as e:
        print(f"allpu {e}")


async def weather(
        client,
        agent_executer,
        config,
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        weather_repoat = weather_agent(get_forcast_weather(
            location["latitude"], location["longitude"]))
        val = [
            SystemMessage(
                f"The Todays Weather repoat is {
                    weather_repoat}, briefly tell the user"
            ),
            HumanMessage("what's the weather dear")
        ]

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        print("morning wished")
        await user.send(response_text)
        update_context(response_text)

    except Exception as e:
        print(f"allpu {e}")
