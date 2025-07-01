import os
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from util.llm_provider import llm_initializer
from util.geo_utli import get_forcast_weather
from templates.weather import weather_template
from services.state_store import get_live_location, get_mood
load_dotenv()

llm = llm_initializer(temperature=0.5)


# Generates a weather report using an LLM.
def weather_agent(data: str) -> str:
    prompt = (weather_template | llm).invoke({"data": data})
    return prompt.content


async def weather(client, agent_executer, config):  # Sends a weather report to the user.
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""

        location = await get_live_location()

        weather_repoat = weather_agent(get_forcast_weather(
            location["latitude"], location["longitude"]))

        val = [
            SystemMessage(
                f"The Todays Weather repoat is {
                    weather_repoat}, briefly tell the user"
            ),
            HumanMessage("what's the weather dear")
        ]

        mood = await get_mood()
        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(mood["Affection"]),
             "Amused": str(mood["Amused"]),
             "Inspired": str(mood["Inspired"]),
             "Frustrated": str(mood["Frustrated"]),
             "Concerned": str(mood["Concerned"]),
             "Curious": str(mood["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        await user.send(response_text)

    except Exception as e:
        print(f"error while genereating weather repoat {e}")
