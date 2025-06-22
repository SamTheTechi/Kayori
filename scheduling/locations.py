import os
import re
import pytz
from datetime import datetime
from geopy.distance import geodesic
from dotenv import load_dotenv
from services.vector_db import initalise_vector_db
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from langchain_core.documents import Document
from util.chunker import split_text
from util.document import location_constructor
from util.store import location, natures, update_context
from util.geo_utli import get_location


load_dotenv()
# location change
USER_ID = int(os.getenv("USER_ID"))
vector_store = initalise_vector_db(name="location", api_key="PINECONE2")


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
        user = await client.fetch_user(USER_ID)
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
             "Concerned": str(natures["Concerned"]),
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
            [Document(chunk) for chunk in chunkted])
        update_context(response_text)

    except Exception as e:
        print(f"error {e}")
