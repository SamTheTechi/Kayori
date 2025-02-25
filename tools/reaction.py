import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.5
)

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Your name is Kaori, my cute  personal waifu assistant."
        "Your task is to analyze the given sentence "
        "and determine its nature. Based on the content, return one of the following tones exactly: "
        "'funny', 'superfunny', 'cute', 'love', 'darkhumor', 'okey', or 'no-reaction'. "
        "Do not include any additional commentary or text—just output the nature."
    ),
    HumanMessagePromptTemplate.from_template('{data}')
])
possible_reactions = {
    "funny": ["😂", "😆", "🤣"],
    "superfunny": ["🤣", "😂"],
    "cute": ["", "🥰"],
    "love": ["❤️", "💖", "😍"],
    "darkhumor": ["💀", "☠️"],
    "okey": ["👌"],
    "no-reaction": [""],
}


async def analyseNature(data: str) -> str:
    prompt = await (template | llm).ainvoke({"data": data})
    return prompt.content
