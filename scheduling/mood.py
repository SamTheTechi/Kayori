import random
from services.state_store import get_mood, set_mood


# Gradually stabilizes mood values towards a baseline of 0.
async def mood_drift():
    # stabilize mood over time toward 0 baseline
    raw = await get_mood()
    natures = {k: float(v) for k, v in raw.items()}

    for tone, strength in natures.items():
        if strength > 0:
            natures[tone] = round(strength - 0.01, 2)
        elif strength < 0:
            natures[tone] = round(strength + 0.01, 2)

        natures[tone] = max(-1.0, min(1.0, natures[tone]))

    await set_mood(**natures)


# Applies a sudden, random fluctuation to one of the mood tones.
async def mood_spike():
    # apply sudden mood fluctuation to a random tone
    raw = await get_mood()
    natures = {k: float(v) for k, v in raw.items()}

    tone = random.choice(list(natures.keys()))
    change = round(random.uniform(0.5, 0.7), 2) * random.choice([-1, 1])
    natures[tone] = round(natures[tone] + change, 2)

    natures[tone] = max(-1.0, min(1.0, natures[tone]))

    await set_mood(**natures)
