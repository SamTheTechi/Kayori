import os
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.2
)

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are an expert debugger specializing in analyzing\
        error codes. provide a concise yet insightfull\
        explanation in 30 words. Focus on pinpointing the root issue"
    ),
    HumanMessagePromptTemplate.from_template('{data}')
])


def errorAnalyzer(data: str) -> str:
    prompt = (template | llm).invoke({"data": data})
    return prompt.content
