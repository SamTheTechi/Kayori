import os
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from util.store import location, natures, update_context
from util.geoutli import get_forcast_weather
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
load_dotenv()

# inislisation

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.4
)


template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a weather forecast agent. Your task is to analyze the provided JSON data, which contains timestamps and weather conditions.\
        Generate a **50-word summary** of today's weather in a format that is easy for other LLMs to understand.\
        forcast_data {data}"
    ),
    HumanMessagePromptTemplate.from_template("how's the todays weather?")
])


def weather_agent(data: str) -> str:
    prompt = (template | llm).invoke({"data": data})
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
             "Concerned": str(natures["Concerned"]),
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
        print(f"error while genereating weather repoat {e}")
