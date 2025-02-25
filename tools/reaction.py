import os
from typing import Dict
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from pydantic import BaseModel, confloat
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.2,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    },
)

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Your name is Kaori, my cute personal waifu assistant. Your\
        task is to analyze the given sentence and determine its nature.\
        Based on the content, return exactly all seven expressions\
        from the following tones along with their expression strengths\
        as floats between -1.0 and 1.0, where 1.0 means positive, -1.0\
        means negative, and 0.0 is neutral: 'Amused', 'Inspired',\
        'Loving', 'Cynical', 'Guilty', 'Insecure', and 'Sceptical'.\
        Each expression should be in the format 'tone:strength' and\
        the expressions should be separated by commas. Do not include\
        any additional commentary or text."
    ),
    HumanMessagePromptTemplate.from_template('{data}')
])


class Validation(BaseModel):
    Amused: confloat(ge=-1.0, le=1.0)
    Inspired: confloat(ge=-1.0, le=1.0)
    Loving: confloat(ge=-1.0, le=1.0)
    Cynical: confloat(ge=-1.0, le=1.0)
    Guilty: confloat(ge=-1.0, le=1.0)
    Insecure: confloat(ge=-1.0, le=1.0)
    Sceptical: confloat(ge=-1.0, le=1.0)


def extractExpression(response: Dict[str, float]) -> str:
    return


def parse(response: str, current: Dict[str, float]) -> Dict[str, float]:
    natures = response.split(',')
    target = {}
    for nature in natures:
        try:
            tone, strength = nature.strip().split(':')
            target[tone.strip()] = float(strength.strip())
        except ValueError:
            return {}
    return target


def update(target: Dict[str, float], current: Dict[str, float]) -> Dict[str, float]:
    for tone, strength in target.items():
        if tone in current:
            current[tone] += strength * 0.1
            current[tone] = round(max(-1.0, min(current[tone], 1.0)), 2)
    return current


async def analyseNature(data: str, nature: Dict[str, float]) -> Dict[str, float]:
    prompt = await (template | llm).ainvoke({"data": data})
    mood = parse(prompt.content, nature)

    try:
        Validation(**mood)
        result = update(mood, nature)
        return result
    except Exception:
        return nature
