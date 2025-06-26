import toml
import random
from typing import Dict
from core.llm_provider import llm_initializer
from pydantic import BaseModel, confloat
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)

config = toml.load("config.toml")

llm = llm_initializer(temperature=0.7)


template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are Kaori, my introverted and cute waifu girlfriend. Analyze \
        the given user input in relation to the previous response and \
        determine its emotional tone shift.\
        ### **Response Format:**\
        - Strictly return all categories ('Affection', 'Amused', 'Inspired', \
        'Frustrated', 'Concerned', 'Curious') with their intensity as floats \
        from -1.0 (strong negative) to 1.0 (strong positive).\
        - Format: `tone:strength`, separated by commas. Example: \
        `Affection:0.8, Amused:-0.2, Inspired:0.5, Frustrated:0.0, Concerned:-0.5, Curious:0.3`.\
        - Never omit a category, even if its value is 0.\
        ### **Rules for Mood Changes:**\
        - Base mood shifts on sentiment, emotional triggers, and conversational flow.\
        - If no strong match exists, apply **slight negative adjustments** \
        (-0.1 to -0.3) to reflect realistic mood shifts over time.\
        - If the user's tone is **neutral or unremarkable**, apply minimal \
        shifts (±0.2 to ±0.3) to avoid erratic jumps.\
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
    "Concerned": ['😨', '🥺'],
    "Curious": ['🤔', '👀', '🧐'],
}
opposite_emojis = {
    "Affection": ['💔', '😠'],
    "Amused": ['🙄', '😑'],
    "Inspired": ['😞', '🙃'],
    "Frustrated": ['😌', '🤗'],
    "Concerned": ['😎', '😃'],
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
    "Concerned": ["Frustrated"],
    "Amused": ["Inspired"]
}


class Validation(BaseModel):
    Affection: confloat(ge=-1.0, le=1.0)
    Amused: confloat(ge=-1.0, le=1.0)
    Inspired: confloat(ge=-1.0, le=1.0)
    Frustrated: confloat(ge=-1.0, le=1.0)
    Concerned: confloat(ge=-1.0, le=1.0)
    Curious: confloat(ge=-1.0, le=1.0)


def parse(response: str, current: Dict[str, float]) -> Dict[str, float]:
    try:
        return {tone.strip(): float(strength.strip()) for tone, strength in
                (n.strip().split(':') for n in response.split(','))}
    except Exception as e:
        print(f"Parse error: {e} in response: {response}")


def update(target: Dict[str, float], current: Dict[str, float]) -> Dict[str, float]:
    for tone, strength in target.items():
        if tone in current:
            multiplier = 0.1 + (config["nature"][tone] / 10)
            value = current[tone] + (strength * multiplier)

            # Adjust for mood conflicts
            for conflict in conflecting_mood.get(tone, []):
                if conflict in current:
                    value -= current[conflict] * (config["weights"]["conflict_multiplier"] * 0.01)

            # Adjust for mood reinforcement
            for reinforce in reinforcing_mood.get(tone, []):
                if reinforce in current:
                    value += current[reinforce] * (config["weights"]["reinforce_multiplier"] * 0.01)

            # Mood drift to neutral (0)
            drift_factor = abs(value) * 0.1
            if value > 0:
                value -= drift_factor
            elif value < 0:
                value += drift_factor

            # Clamp between -1.0 and 1.0
            current[tone] = round(max(-1.0, min(value, 1.0)), 2)

    print(current)
    return current


async def analyseMood(user: str, getcontext, nature: Dict[str, float]) -> str:
    prev_context = getcontext()
    prev = prev_context[0].strip() if prev_context and prev_context[0].strip() else "Neutral start."
    prompt = await (template | llm).ainvoke({"user": user, "prev": prev[0]})
    mood = parse(prompt.content, nature)

    try:
        Validation(**mood)
        update(mood, nature)

        # Get tone with strongest intensity
        key = max(mood, key=lambda k: abs(mood[k]))
        val = mood[key]

        if abs(val) >= 0.85:
            if val > 0:
                return random.choice(emojis.get(key, ["❓"]))
            else:
                return random.choice(opposite_emojis.get(key, ["❓"]))
        else:
            return ""

    except Exception as e:
        print(f"error {e}")
        return ""
