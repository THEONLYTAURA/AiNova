from __future__ import annotations

RUBRIC_WEIGHTS = {
    "context": 0.20,
    "task_clarity": 0.20,
    "specificity": 0.15,
    "constraints": 0.15,
    "output_format": 0.10,
    "examples": 0.10,
    "evaluation": 0.10,
}

LEVEL_BANDS = [
    (0, 20, "AI Novice"),
    (21, 40, "AI Beginner"),
    (41, 60, "AI Explorer"),
    (61, 80, "AI Practitioner"),
    (81, 100, "AI Expert"),
]

def clamp_score(value: int | float) -> int:
    return max(0, min(100, int(round(value))))

def composite_score(scores: dict[str, int]) -> int:
    missing = set(RUBRIC_WEIGHTS) - set(scores)
    if missing:
        raise ValueError(f"Missing rubric dimensions: {sorted(missing)}")
    weighted = sum(clamp_score(scores[k]) * w for k, w in RUBRIC_WEIGHTS.items())
    return clamp_score(weighted)

def level_for_score(score: int) -> str:
    score = clamp_score(score)
    for lo, hi, name in LEVEL_BANDS:
        if lo <= score <= hi:
            return name
    raise ValueError("Score outside 0-100")

def prompt_improvement_rate(initial: int, final: int) -> float:
    initial, final = clamp_score(initial), clamp_score(final)
    denominator = 100 - initial
    if denominator <= 0:
        return 0.0
    return round(max(0, final - initial) / denominator * 100, 1)
