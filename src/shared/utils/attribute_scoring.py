from collections import defaultdict
from shared.schemas.schemas import AttributeUpdate

EXERCISE_ATTRIBUTES = {
    "pushup":        [("strength", 40)],
    "squat":         [("strength", 40)],
    "pullup":        [("strength", 20)],
    "situp":         [("strength", 20)],
    "vertical_jump": [("jumping", 0.40)],
    "long_jumps":    [("jumping", 2.5)],
    "treadmill":     [("sprint_speed", 100), ("acceleration", 90), ("agility", 70)],
    "double":        [("balance", 10), ("dribbling", 15)],
    "kick":          [("finishing", 10)],
}


ACTIVE_ATTRS = sorted({attr for lst in EXERCISE_ATTRIBUTES.values() for (attr, _) in lst})


def _score(value, target):
    if not target or target <= 0:
        return 0
    return max(0, min(100, int(round(100.0 * float(value) / float(target)))))


def compute_attributes(results):
    best = {}
    for r in results:
        challenge = getattr(r, "challenge", None)
        name = getattr(challenge, "challenge_name", None)
        if not name:
            continue
        val = r.result_value or 0
        if name not in best or val > best[name]:
            best[name] = val

    subs = defaultdict(list)
    for name, val in best.items():
        for attr, target in EXERCISE_ATTRIBUTES.get(name, []):
            subs[attr].append(_score(val, target))

    data = {}
    for attr in ACTIVE_ATTRS:
        vals = subs.get(attr, [])
        data[attr] = int(round(sum(vals) / len(vals))) if vals else 0
    return AttributeUpdate(**data)
