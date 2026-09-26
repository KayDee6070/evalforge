from evalforge.models import (
    DimensionScore,
    EvaluationResult,
)
from evalforge.storage import (
    load_evaluations,
    save_evaluation,
)


def make_evaluation(item_id: str) -> EvaluationResult:
    return EvaluationResult(
        item_id=item_id,
        evaluator="Tester",
        ratable=True,
        scores=[
            DimensionScore(
                dimension="Correctness",
                score=5,
            )
        ],
        error_tags=["Factual Error"],
        overall_comment="Test evaluation",
    )


def test_save_and_load_evaluation(tmp_path):
    db_path = tmp_path / "test.db"

    evaluation = make_evaluation("item-1")

    evaluation_id = save_evaluation(
        evaluation,
        dataset_key="dataset-a",
        db_path=db_path,
    )

    stored = load_evaluations(
        dataset_key="dataset-a",
        db_path=db_path,
    )

    assert evaluation_id == 1
    assert len(stored) == 1
    assert stored[0]["item_id"] == "item-1"
    assert stored[0]["evaluator"] == "Tester"
    assert stored[0]["ratable"] is True
    assert stored[0]["dataset_key"] == "dataset-a"


def test_dataset_isolation(tmp_path):
    db_path = tmp_path / "test.db"

    save_evaluation(
        make_evaluation("item-a"),
        dataset_key="dataset-a",
        db_path=db_path,
    )

    save_evaluation(
        make_evaluation("item-b"),
        dataset_key="dataset-b",
        db_path=db_path,
    )

    dataset_a = load_evaluations(
        dataset_key="dataset-a",
        db_path=db_path,
    )

    dataset_b = load_evaluations(
        dataset_key="dataset-b",
        db_path=db_path,
    )

    assert len(dataset_a) == 1
    assert len(dataset_b) == 1

    assert dataset_a[0]["item_id"] == "item-a"
    assert dataset_b[0]["item_id"] == "item-b"


def test_load_all_evaluations(tmp_path):
    db_path = tmp_path / "test.db"

    save_evaluation(
        make_evaluation("item-a"),
        dataset_key="dataset-a",
        db_path=db_path,
    )

    save_evaluation(
        make_evaluation("item-b"),
        dataset_key="dataset-b",
        db_path=db_path,
    )

    stored = load_evaluations(
        db_path=db_path,
    )

    assert len(stored) == 2