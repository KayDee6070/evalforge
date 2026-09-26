import pandas as pd

from evalforge.models import BenchmarkItem


def build_score_dataframe(
    evaluations: list[dict],
    benchmark_items: list[BenchmarkItem],
) -> pd.DataFrame:
    """
    Convert stored evaluations into one row per scored dimension.
    """

    item_lookup = {item.id: item for item in benchmark_items}

    rows = []

    for evaluation in evaluations:
        if not evaluation["ratable"]:
            continue

        item = item_lookup.get(evaluation["item_id"])

        for score in evaluation["scores"]:
            rows.append(
                {
                    "evaluation_id": evaluation["id"],
                    "item_id": evaluation["item_id"],
                    "evaluator": evaluation["evaluator"],
                    "model_name": (
                        item.model_name if item else "Unknown"
                    ),
                    "category": (
                        item.category if item else "Unknown"
                    ),
                    "dimension": score["dimension"],
                    "score": score["score"],
                }
            )

    return pd.DataFrame(rows)


def build_evaluation_dataframe(
    evaluations: list[dict],
    benchmark_items: list[BenchmarkItem],
) -> pd.DataFrame:
    """
    Convert stored evaluations into one row per evaluation.
    """

    item_lookup = {item.id: item for item in benchmark_items}

    rows = []

    for evaluation in evaluations:
        item = item_lookup.get(evaluation["item_id"])

        scores = [
            score["score"]
            for score in evaluation["scores"]
        ]

        average_score = (
            round(sum(scores) / len(scores), 2)
            if scores
            else None
        )

        rows.append(
            {
                "evaluation_id": evaluation["id"],
                "item_id": evaluation["item_id"],
                "evaluator": evaluation["evaluator"],
                "model_name": (
                    item.model_name if item else "Unknown"
                ),
                "category": (
                    item.category if item else "Unknown"
                ),
                "ratable": evaluation["ratable"],
                "average_score": average_score,
                "created_at": evaluation["created_at"],
            }
        )

    return pd.DataFrame(rows)


def build_error_tag_dataframe(
    evaluations: list[dict],
) -> pd.DataFrame:
    """
    Count how often each error tag appears.
    """

    tags = []

    for evaluation in evaluations:
        tags.extend(evaluation["error_tags"])

    if not tags:
        return pd.DataFrame(
            columns=["error_tag", "count"]
        )

    return (
        pd.Series(tags)
        .value_counts()
        .rename_axis("error_tag")
        .reset_index(name="count")
    )