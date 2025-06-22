from typing import Dict


def balance_mood(nature: Dict[str, float]) -> Dict[str, float]:
    for tone, strength in nature.items():
        if (strength > 0.6):
            nature[tone] = 0.2
        elif (strength < -0.6):
            nature[tone] = -0.2

    return nature
