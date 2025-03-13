from typing import Dict


def balance_mood(nature: Dict[str, float]) -> Dict[str, float]:
    for tone, strength in nature.items():
        if (strength > 0.7):
            nature[tone] = 0.7
        elif (strength < 0.3):
            nature[tone] = 0.3

    return nature
