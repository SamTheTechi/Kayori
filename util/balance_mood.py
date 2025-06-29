from services.state_store import get_mood, set_mood


async def balance_mood():
    try:
        raw = await get_mood()
        moods = {k: float(v) for k, v in raw.items()}

        for tone, strength in moods.items():
            if (strength > 0.6):
                moods[tone] = 0.2
            elif (strength < -0.6):
                moods[tone] = -0.2

        moods[tone] = max(-1.0, min(1.0, moods[tone]))

        await set_mood(**moods)
    except Exception as e:
        print(e)
