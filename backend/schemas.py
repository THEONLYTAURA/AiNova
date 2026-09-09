from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict

MAX_PROMPT = 4000

class DimensionScores(BaseModel):
    context: int = Field(ge=0, le=100)
    task_clarity: int = Field(ge=0, le=100)
    specificity: int = Field(ge=0, le=100)
    constraints: int = Field(ge=0, le=100)
    output_format: int = Field(ge=0, le=100)
    examples: int = Field(ge=0, le=100)
    evaluation: int = Field(ge=0, le=100)

class EvaluationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_id: str
    score: int = Field(ge=0, le=100)
    level: str
    dimensions: DimensionScores
    dimension_evidence: dict[str, str]
    weaknesses: list[str]
    improved_prompt: str
    explanation: str
    lesson_dimension: str
    evaluator_version: str
    model: str

class CoachRequest(BaseModel):
    session_id: str | None = None
    prompt: str = Field(min_length=3, max_length=MAX_PROMPT)

class RetryRequest(CoachRequest):
    previous_score: int = Field(ge=0, le=100)

class ChallengeSubmitRequest(CoachRequest):
    challenge_id: str

class SkillTestAnswer(BaseModel):
    question_id: str
    answer: str = Field(min_length=1, max_length=MAX_PROMPT)

class SkillTestSubmitRequest(BaseModel):
    session_id: str | None = None
    answers: list[SkillTestAnswer] = Field(min_length=10, max_length=10)

class ChallengeOut(BaseModel):
    id: str
    title: str
    scenario: str
    category: str | None = None
    difficulty: str | None = None

class ProgressEvent(BaseModel):
    event_type: str
    score: int
    created_at: str

class ProgressResponse(BaseModel):
    events: list[ProgressEvent]
    current_score: int | None = None
    improvement: int | None = None
