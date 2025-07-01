import toml
import random
from typing import Dict
from templates.mood import mood_template
from util.llm_provider import llm_initializer
from pydantic import BaseModel, confloat
from services.state_store import get_mood, set_mood

config = toml.load("config.toml")
llm = llm_initializer(temperature=0.7)


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
        return {}


async def update(target: Dict[str, float], current: Dict[str, float]):
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

    await set_mood(**current)


async def analyse_mood(content: str) -> str:
    prompt = await (mood_template | llm).ainvoke({"user": content})
    parsed_mood = parse(prompt.content, await get_mood())
    if not parsed_mood:
        return ""

    try:
        Validation(**parsed_mood)
        current_mood = {k: float(v) for k, v in (await get_mood()).items()}

        await update(parsed_mood, current_mood)

        # Get tone with strongest intensity
        key = max(parsed_mood, key=lambda k: abs(parsed_mood[k]))
        val = parsed_mood[key]

        if abs(val) >= 0.85:
            return random.choice(emojis[key] if val > 0 else opposite_emojis[key])
        else:
            return ""

    except Exception as e:
        print(f"error {e}")
        return ""
