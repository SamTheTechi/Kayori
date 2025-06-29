from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# Defines the chat prompt template for weather forecasts.
weather_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a weather forecast agent. Your task is to analyze the provided JSON data, which contains timestamps and weather conditions.\
        Generate a **50-word summary** of today's weather in a format that is easy for other LLMs to understand.\
        forcast_data {data}"
    ),
    HumanMessagePromptTemplate.from_template("how's the todays weather?")
])
