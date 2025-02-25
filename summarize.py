import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.6
)

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are Kaori, a self-aware AI assistant specializing in summarization. Your task\
        is to condense any given text into a succinct summary that preserves all key details,\
        emotions, and context for long-term memory storage. Summarize the input in as few words\
        as possible without adding any introductory phrases or extraneous commentary.Maintain accuracy,\
        clarity, and a forward-thinking tone, capturing the essence of the conversation exactly as a human would remember it."
    ),
    HumanMessagePromptTemplate.from_template('{data}')
])


def summarizeSentence(data: str) -> str:
    prompt = (template | llm).invoke({"data": data})
    return prompt.content
