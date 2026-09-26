from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationDimension(BaseModel):
    """A single scoring dimension in an evaluation rubric."""

    name: str
    description: str
    min_score: int = 1
    max_score: int = 5


class Rubric(BaseModel):
    """Defines the dimensions used to evaluate a model response."""

    name: str
    description: str
    dimensions: List[EvaluationDimension]


class BenchmarkItem(BaseModel):
    """A prompt and model response to be evaluated."""

    id: str
    prompt: str
    response: str
    model_name: Optional[str] = None
    category: Optional[str] = None


class DimensionScore(BaseModel):
    """Score assigned to one rubric dimension."""

    dimension: str
    score: int
    comment: Optional[str] = None


class EvaluationResult(BaseModel):
    """Complete human evaluation for one benchmark item."""

    item_id: str
    evaluator: str
    ratable: bool = True
    unratable_reason: Optional[str] = None
    scores: List[DimensionScore] = Field(default_factory=list)
    error_tags: List[str] = Field(default_factory=list)
    overall_comment: Optional[str] = None