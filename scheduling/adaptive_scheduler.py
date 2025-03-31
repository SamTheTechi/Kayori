import os
import re
import pytz
import discord
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from geopy.distance import geodesic
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from util.chunker import split_text
from util.document import location_constructor, memory_constructor
from util.store import location, natures, update_context
from util.geoutli import get_forcast_weather, get_location
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
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


pc = Pinecone(api_key=os.getenv("PINECONE2"))

if "location" not in [index["name"] for index in pc.list_indexes()]:
    spec = ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
    pc.create_index("location", dimension=768, spec=spec)
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
    return prompt.content


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


# location change
def process_location(lat, lon, threshold=0.85, min_distance=5):

    user_location = get_location(lat, lon)

    suburb = user_location.get("suburb", "Unknown")
    city = user_location.get("city", "Unknown")
    location_text = f"latitude: {lat}, longitude: {
        lon}, suburb: {suburb}, city: {city}."

    results = vector_store.similarity_search_with_relevance_scores(
        query=location_text, k=1)

    if results:
        document, score = results[0]

        lat_match = float(
            re.search(r'latitude:\s*([\d.]+)', document.page_content).group(1))
        lon_match = float(
            re.search(r'longitude:\s*([\d.]+)', document.page_content).group(1))

        distance = geodesic((lat, lon), (lat_match, lon_match)).km

        current_time = datetime.now(pytz.utc).astimezone(
            pytz.timezone("Asia/Kolkata")).isoformat()
        last_time = document.metadata["time"]
        current_timestamp = datetime.fromisoformat(current_time)
        last_timestamp = datetime.fromisoformat(last_time)

        time_difference = abs(
            (current_timestamp - last_timestamp).total_seconds()) / 86400
        print(time_difference)

        if (score >= threshold and distance <= min_distance) or (time_difference < 15 and score >= threshold):
            return (False, "unknown", "unknown")

    vector_store.add_documents(
        [location_constructor(lat, lon, suburb, city)])

    return (True, suburb, city)


async def location_change(
        client,
        agent_executer,
        config,
        vector_str
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response, suburb, city = process_location(
            location["latitude"], location["longitude"])

        if not response:
            return

        docs = vector_str.similarity_search(query=f"{suburb},{city}", k=2)
        response_text = ""

        val = [
            SystemMessage(
                f"Location change detected: The user is now in {suburb}, {city}. \
                Tease them playfully if it's unexpected, or acknowledge it subtly if anticipated. \
                Keep it casual and human-like—no robotic responses. Avoide greeting"
            ),
            *[AIMessage(content=f"{doc.page_content}") for doc in docs],
            HumanMessage("** User location change detected **")
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
        chunkted = split_text(response_text)
        vector_str.add_documents(
            [memory_constructor(chunk) for chunk in chunkted])
        update_context(response_text)

    except Exception as e:
        print(f"error {e}")
