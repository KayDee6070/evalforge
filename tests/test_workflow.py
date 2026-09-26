from evalforge.models import DimensionScore
from evalforge.workflow import (
    build_current_evaluation,
    find_existing_evaluations,
    normalize_evaluator_name,
)


def test_normalize_evaluator_name():
    assert normalize_evaluator_name(" Kuntal ") == "Kuntal"
    assert normalize_evaluator_name("") == "Anonymous"
    assert normalize_evaluator_name("   ") == "Anonymous"


def test_find_existing_evaluations():
    evaluations = [
        {
            "item_id": "qa-001",
            "evaluator": "Kuntal",
        },
        {
            "item_id": "qa-002",
            "evaluator": "Kuntal",
        },
        {
            "item_id": "qa-001",
            "evaluator": "Another Evaluator",
        },
    ]

    matches = find_existing_evaluations(
        evaluations,
        item_id="qa-001",
        evaluator="kuntal",
    )

    assert len(matches) == 1
    assert matches[0]["item_id"] == "qa-001"


def test_build_ratable_evaluation():
    scores = [
        DimensionScore(
            dimension="Correctness",
            score=5,
        )
    ]

    evaluation = build_current_evaluation(
        item_id="qa-001",
        evaluator="Tester",
        ratable="Yes",
        unratable_reason=None,
        scores=scores,
        error_tags=["Factual Error"],
        overall_comment="Example comment",
    )

    assert evaluation.ratable is True
    assert len(evaluation.scores) == 1
    assert evaluation.error_tags == ["Factual Error"]
    assert evaluation.overall_comment == "Example comment"


def test_build_unratable_evaluation_removes_scores():
    scores = [
        DimensionScore(
            dimension="Correctness",
            score=5,
        )
    ]

    evaluation = build_current_evaluation(
        item_id="qa-002",
        evaluator="Tester",
        ratable="No",
        unratable_reason="Missing context",
        scores=scores,
        error_tags=[],
        overall_comment="",
    )

    assert evaluation.ratable is False
    assert evaluation.scores == []
    assert evaluation.unratable_reason == "Missing context"
    assert evaluation.overall_comment is None