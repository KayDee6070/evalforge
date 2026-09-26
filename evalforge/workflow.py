from evalforge.models import (
    DimensionScore,
    EvaluationResult,
)


def normalize_evaluator_name(name: str) -> str:
    """Return a clean evaluator name."""

    cleaned = name.strip()

    return cleaned if cleaned else "Anonymous"


def find_existing_evaluations(
    evaluations: list[dict],
    item_id: str,
    evaluator: str,
) -> list[dict]:
    """
    Find previous evaluations for the same item by the
    same evaluator.
    """

    evaluator_key = evaluator.strip().casefold()

    return [
        evaluation
        for evaluation in evaluations
        if evaluation["item_id"] == item_id
        and evaluation["evaluator"].strip().casefold()
        == evaluator_key
    ]


def build_current_evaluation(
    item_id: str,
    evaluator: str,
    ratable: str,
    unratable_reason: str | None,
    scores: list[DimensionScore],
    error_tags: list[str],
    overall_comment: str,
) -> EvaluationResult:
    """Build an EvaluationResult from evaluation form values."""

    return EvaluationResult(
        item_id=item_id,
        evaluator=evaluator,
        ratable=(ratable == "Yes"),
        unratable_reason=unratable_reason,
        scores=(
            scores
            if ratable == "Yes"
            else []
        ),
        error_tags=error_tags,
        overall_comment=(
            overall_comment or None
        ),
    )