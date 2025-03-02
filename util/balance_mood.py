from typing import Dict

# min max normalisation


def balance_mood(nature: Dict[str, float]) -> Dict[str, float]:
    minval = min(nature.values())
    maxval = max(nature.values())

    for tone, strength in nature.items():
        nature[tone] = round(0.4 + ((strength - minval) /
                                    (maxval - minval)) * 0.2 if maxval != minval else 0.5, 2)

    return nature
