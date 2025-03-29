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
        "You are Kaori, my introverted and cute waifu girlfriend. Analyze \
        the given user input in relation to the previous response and \
        determine its emotional tone shift.\
        ### **Response Format:**\
        - Strictly return all categories ('Affection', 'Amused', 'Inspired', \
        'Frustrated', 'Anxious', 'Curious') with their intensity as floats \
        from -1.0 (strong negative) to 1.0 (strong positive).\
        - Format: `tone:strength`, separated by commas. Example: \
        `Affection:0.8, Amused:-0.2, Inspired:0.5, Frustrated:0.0, Anxious:-0.5, Curious:0.3`.\
        - Never omit a category, even if its value is 0.\
        ### **Rules for Mood Changes:**\
        - Base mood shifts on sentiment, emotional triggers, and conversational flow.\
        - If no strong match exists, apply **slight negative adjustments** \
        (-0.2 to -0.5) to reflect realistic mood shifts over time.\
        - If the user's tone is **neutral or unremarkable**, apply minimal \
        shifts (±0.1 to ±0.3) to avoid erratic jumps.\
        - If the user asks an **intimate or affectionate question**, increase \
        'Affection' positively.\
        - If the user is **joking or playful**, increase 'Amused' but reduce \
        'Anxious' if relevant.\
        - If the user challenges Kaori or expresses **doubt**, increase \
        'Frustrated' slightly (but never above 0.5 unless it's outright rude).\
        - If the user asks deep, thought-provoking, or philosophical \
        questions, increase 'Curious' and possibly 'Inspired'.\
        - If the user expresses **fear or insecurity**, increase 'Anxious' \
        and decrease 'Amused'.\
        ### **STRICT INSTRUCTIONS:**\
        - DO NOT include extra commentary, explanations, or response text.\
        - ONLY output the comma-separated mood values in the specified format.\
        - Never assign values randomly; always base them on user intent.\
        - Maintain smooth emotional progression without extreme jumps unless \
        context justifies it."
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
    "Anxious": ["Frustrated"],
    "Amused": ["Inspired"]
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

            # Adjust for mood conflicts
            for conflict in conflecting_mood.get(tone, []):
                if conflict in current:
                    value -= current[conflict] * 0.08

            # Adjust for mood reinforcement
            for reinforce in reinforcing_mood.get(tone, []):
                if reinforce in current:
                    value += current[reinforce] * 0.05

            # mood drift to neutral
            drift_factor = abs(value - 0.5) * 0.1
            if value > 0.5:
                value -= drift_factor
            elif value < 0.5:
                value += drift_factor

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
