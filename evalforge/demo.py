import json
from pathlib import Path


DEFAULT_DEMO_PATH = Path("datasets/demo_evaluations.json")


def load_demo_evaluations(
    path: str | Path = DEFAULT_DEMO_PATH,
) -> list[dict]:
    """
    Load bundled demo evaluations and convert them to the same
    structure used by the SQLite storage layer.
    """

    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    evaluations = []

    for index, item in enumerate(data, start=1):
        scores = [
            {
                "dimension": dimension,
                "score": score,
                "comment": None,
            }
            for dimension, score in item["scores"].items()
        ]

        evaluations.append(
            {
                "id": f"demo-{index:03d}",
                "dataset_key": "default-sample-dataset",
                "item_id": item["item_id"],
                "evaluator": item.get(
                    "evaluator",
                    "Demo Evaluator",
                ),
                "ratable": item.get("ratable", True),
                "unratable_reason": item.get(
                    "unratable_reason"
                ),
                "scores": scores,
                "error_tags": item.get(
                    "error_tags",
                    [],
                ),
                "overall_comment": item.get(
                    "overall_comment"
                ),
                "created_at": "Bundled demo",
                "source": "Demo",
            }
        )

    return evaluations