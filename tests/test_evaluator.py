from evalforge.evaluator import (
    calculate_average_score,
    validate_evaluation,
)
from evalforge.models import (
    DimensionScore,
    EvaluationResult,
)
from evalforge.rubric import load_rubric


RUBRIC_PATH = "rubrics/general_qa.yaml"


def test_average_score():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-001",
        evaluator="Tester",
        scores=[
            DimensionScore(
                dimension="Correctness",
                score=5,
            ),
            DimensionScore(
                dimension="Relevance",
                score=4,
            ),
            DimensionScore(
                dimension="Instruction Following",
                score=5,
            ),
            DimensionScore(
                dimension="Completeness",
                score=4,
            ),
            DimensionScore(
                dimension="Clarity",
                score=5,
            ),
        ],
    )

    result = calculate_average_score(
        evaluation,
        rubric,
    )

    assert result == 4.6


def test_unratable_has_no_average():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-002",
        evaluator="Tester",
        ratable=False,
        unratable_reason="Missing required context.",
    )

    result = calculate_average_score(
        evaluation,
        rubric,
    )

    assert result is None


def test_complete_evaluation_is_valid():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-003",
        evaluator="Tester",
        scores=[
            DimensionScore(
                dimension="Correctness",
                score=5,
            ),
            DimensionScore(
                dimension="Relevance",
                score=5,
            ),
            DimensionScore(
                dimension="Instruction Following",
                score=5,
            ),
            DimensionScore(
                dimension="Completeness",
                score=5,
            ),
            DimensionScore(
                dimension="Clarity",
                score=5,
            ),
        ],
    )

    errors = validate_evaluation(
        evaluation,
        rubric,
    )

    assert errors == []


def test_missing_dimension_is_invalid():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-004",
        evaluator="Tester",
        scores=[
            DimensionScore(
                dimension="Correctness",
                score=5,
            ),
        ],
    )

    errors = validate_evaluation(
        evaluation,
        rubric,
    )

    assert len(errors) == 1
    assert "Missing scores for" in errors[0]


def test_unknown_dimension_is_invalid():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-005",
        evaluator="Tester",
        scores=[
            DimensionScore(
                dimension="Correctness",
                score=5,
            ),
            DimensionScore(
                dimension="Relevance",
                score=5,
            ),
            DimensionScore(
                dimension="Instruction Following",
                score=5,
            ),
            DimensionScore(
                dimension="Completeness",
                score=5,
            ),
            DimensionScore(
                dimension="Clarity",
                score=5,
            ),
            DimensionScore(
                dimension="Made Up Dimension",
                score=3,
            ),
        ],
    )

    errors = validate_evaluation(
        evaluation,
        rubric,
    )

    assert any(
        "Unknown evaluation dimension"
        in error
        for error in errors
    )


def test_unratable_requires_reason():
    rubric = load_rubric(RUBRIC_PATH)

    evaluation = EvaluationResult(
        item_id="test-006",
        evaluator="Tester",
        ratable=False,
    )

    errors = validate_evaluation(
        evaluation,
        rubric,
    )

    assert len(errors) == 1
    assert "unratable reason" in errors[0].lower()