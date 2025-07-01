import os
import pytz
from datetime import datetime
from geopy.distance import geodesic
from dotenv import load_dotenv
from services.vector_db import initalise_vector_db
from util.get_current_time import get_current_time
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from langchain_core.documents import Document
from util.chunker import split_text
from util.document_constructor import location_constructor
from services.state_store import get_mood, get_live_location, get_pinned_location, set_pinned_location
from util.geo_utli import get_current_location


load_dotenv()
# location change
USER_ID = int(os.getenv("USER_ID"))
vector_store = initalise_vector_db(name="location", api_key="PINECONE")


async def can_trigger(radius: int) -> bool:
    live = await get_live_location()
    pinned = await get_pinned_location()

    if not live or not pinned:
        return False

    distance = geodesic(
        (live["latitude"], live["longitude"]),
        (pinned["latitude"], pinned["longitude"])
    ).km

    if distance > radius:
        await set_pinned_location()
        return True
    else:
        return False


async def process_location(threshold=0.85, days=15):

    live = await get_live_location()
    if not live:
        return (False, False, "Unknown", "Unknown")

    lat = live["latitude"]
    lon = live["longitude"]

    user_location = get_current_location(lat, lon)
    if not user_location:
        return (False, False, "Unknown", "Unknown")

    suburb = user_location.get("suburb", "Unknown")
    city = user_location.get("city", "Unknown")

    location_query = f"latitude: {lat}, longitude: {lon}, suburb: {suburb}, city: {city}."

    results = vector_store.similarity_search_with_relevance_scores(query=location_query, k=1)

    if results:
        document, score = results[0]

        # not a new location, been to this place before
        if score >= threshold:

            time_format = '%Y-%m-%d %H:%M'
            current_time_str = datetime.now(pytz.utc).astimezone(pytz.timezone("Asia/Kolkata")).strftime(time_format)
            last_time_str = document.metadata["time"]

            current_time = datetime.strptime(current_time_str, time_format)
            last_time = datetime.strptime(last_time_str, time_format)

            # check for the time ellipsis
            time_difference = abs(
                (current_time - last_time).total_seconds()) / 86400

            # seems like enough days has passed
            if time_difference > days:

                # deleating old record and adding new in place of it, so timestap get updated
                vector_store.delete(ids=[document.metadata["ID"]])

                vector_store.add_documents(
                    [location_constructor(lat, lon, suburb, city)])

                return (True, False, suburb, city)

            # not enought time have passed to trigger the location_change msg
            else:
                return (False, False, "Unknown", "Unknown")

        # new location seems like new adventure
        else:

            vector_store.add_documents(
                [location_constructor(lat, lon, suburb, city)])
            return (True, True, suburb, city)

    vector_store.add_documents(
        [location_constructor(lat, lon, suburb, city)])
    return (True, True, suburb, city)


# Handles a detected change in the user's location.
async def location_change(client, agent_executer, config, vector_str):
    try:

        # in kilo meters, checks if users goes beyond 5km redius or not
        if await can_trigger(radius=5):
            user = await client.fetch_user(USER_ID)

            response, new_or_old, suburb, city = await process_location()

            if not response:
                return

            response_text = ""

            if new_or_old:
                # template for vistion for first time
                val = [
                    SystemMessage(
                        f"Looks like the user is exploring a new place — {suburb}, {city}! "
                        "Say something playful, exciting, or curious. Maybe tease them for being an adventurer. "
                        "Keep the tone friendly and avoid generic greetings"

                    ),
                    HumanMessage("** User location change detected **")
                ]

            else:
                docs = vector_str.similarity_search(query=f"{suburb},{city}", k=2)

                # template for vistion for been before
                val = [
                    SystemMessage(
                        f"The user has returned to a familiar spot — {suburb}, {city}. "
                        "Make a subtle or nostalgic remark. Maybe pretend you remember something from last time. "
                        "Keep it chill and human-like — no robotic or overly formal replies."

                    ),
                    *[AIMessage(content=f"{doc.page_content}") for doc in docs],
                    HumanMessage("** User location change detected **")
                ]

            natures = await get_mood()
            async for chunk, metadata in agent_executer.astream(
                {
                    "messages": val,
                    "Affection": str(natures["Affection"]),
                    "Amused": str(natures["Amused"]),
                    "Inspired": str(natures["Inspired"]),
                    "Frustrated": str(natures["Frustrated"]),
                    "Concerned": str(natures["Concerned"]),
                    "Curious": str(natures["Curious"]),
                    "current_time": str(get_current_time())
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

    except Exception as e:
        print(f"error {e}")
