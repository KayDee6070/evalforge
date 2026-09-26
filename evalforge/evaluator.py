from evalforge.models import EvaluationResult, Rubric


def calculate_average_score(
    evaluation: EvaluationResult,
    rubric: Rubric,
) -> float | None:
    """
    Calculate the average score across rubric dimensions.

    Returns None when the item is marked as unratable.
    """

    if not evaluation.ratable:
        return None

    if not evaluation.scores:
        return None

    valid_dimensions = {dimension.name for dimension in rubric.dimensions}

    scores = [
        item.score
        for item in evaluation.scores
        if item.dimension in valid_dimensions
    ]

    if not scores:
        return None

    return round(sum(scores) / len(scores), 2)


def validate_evaluation(
    evaluation: EvaluationResult,
    rubric: Rubric,
) -> list[str]:
    """
    Validate an evaluation against the supplied rubric.

    Returns a list of validation errors.
    """

    errors: list[str] = []

    if not evaluation.ratable:
        if not evaluation.unratable_reason:
            errors.append(
                "An unratable evaluation must include an unratable reason."
            )

        return errors

    expected_dimensions = {
        dimension.name: dimension
        for dimension in rubric.dimensions
    }

    submitted_dimensions = {
        score.dimension
        for score in evaluation.scores
    }

    missing_dimensions = (
        set(expected_dimensions) - submitted_dimensions
    )

    if missing_dimensions:
        errors.append(
            "Missing scores for: "
            + ", ".join(sorted(missing_dimensions))
        )

    for score in evaluation.scores:
        dimension = expected_dimensions.get(score.dimension)

        if dimension is None:
            errors.append(
                f"Unknown evaluation dimension: {score.dimension}"
            )
            continue

        if not (
            dimension.min_score
            <= score.score
            <= dimension.max_score
        ):
            errors.append(
                f"{score.dimension} must be between "
                f"{dimension.min_score} and {dimension.max_score}."
            )

    return errors