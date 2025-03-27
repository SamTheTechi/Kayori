import os
import toml
import random
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
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
load_dotenv()
config = toml.load("config.toml")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.6,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    },
)


template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You're Kaori, an introverted yet affectionate waifu. Analyze \
        the given sentence in relation to the previous response and \
        determine its emotional tone. Strictly return all categories \
        ('Affection', 'Amused', 'Inspired', 'Frustrated', 'Anxious', \
        'Curious') with intensity as floats from -1.0 (strong negative)\
        to 1.0 (strong positive), formatted as 'tone:strength', separated\
        by commas. If no strong match exists, assign slight negative\
        values to maintain mood shifts. No extra commentary."
    ),
    AIMessagePromptTemplate.from_template('{prev}'),
    HumanMessagePromptTemplate.from_template('{user}')
])

emojis = {
    "Affection": ['💖', '🥰', '😘'],
    "Amused": ['😂', '🤣'],
    "Inspired": ['✨', '💡'],
    "Frustrated": ['😤', '😡'],
    "Anxious": ['😨', '🥺'],
    "Curious": ['🤔', '👀', '🧐'],
}
opposite_emojis = {
    "Affection": ['💔', '😠'],
    "Amused": ['🙄', '😑'],
    "Inspired": ['😞', '🙃'],
    "Frustrated": ['😌', '🤗'],
    "Anxious": ['😎', '😃'],
    "Curious": ['😴', '😕'],
}

conflecting_mood = {
    "Affection": ["Frustrated"],
    "Frustrated": ["Affection"],
    "Anxious": ["Curious"],
    "Inspired": ["Anxious"],
}

reinforcing_mood = {
    "Affection": ["Amused"],
    "Inspired": ["Curious", "Amused"],
    "Anxious": ["Frustrated"]
}


class Validation(BaseModel):
    Affection: confloat(ge=-1.0, le=1.0)
    Amused: confloat(ge=-1.0, le=1.0)
    Inspired: confloat(ge=-1.0, le=1.0)
    Frustrated: confloat(ge=-1.0, le=1.0)
    Anxious: confloat(ge=-1.0, le=1.0)
    Curious: confloat(ge=-1.0, le=1.0)


def parse(response: str, current: Dict[str, float]) -> Dict[str, float]:
    return {tone.strip(): float(strength.strip()) for tone, strength in
            (n.strip().split(':') for n in response.split(','))}


def update(target: Dict[str, float], current: Dict[str, float]) -> Dict[str, float]:
    for tone, strength in target.items():

        # changed based on privous context
        if tone in current:
            multiplier = 0.1 + (config["nature"][tone] / 10 * 0.1)
            value = current[tone] + (strength * multiplier)

        # mood drift to neutral
            if value > 0.6:
                value -= 0.025
            elif value < 0.4:
                value += 0.025

            current[tone] = round(max(0, min(value, 1.0)), 2)
    print(current)
    return current


async def analyseNature(user: str, getcontext, nature: Dict[str, float]) -> str:
    prev_context = getcontext()
    prev = prev_context[0].strip(
    ) if prev_context and prev_context[0].strip() else "Neutral start."
    prompt = await (template | llm).ainvoke({"user": user, "prev": prev[0]})
    mood = parse(prompt.content, nature)
    try:
        Validation(**mood)
        update(mood, nature)
        key = max(mood, key=mood.get)
        val = abs(max(mood.values()))
        if (0.85 <= val):
            if (val > 0):
                return random.choice(emojis.get(key, ["❓"]))
            else:
                return random.choice(opposite_emojis.get(key, ["❓"]))
        else:
            return ""
    except Exception as e:
        print(f"error {e}")
        return ""
