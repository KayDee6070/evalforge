import json

import pandas as pd


def evaluations_to_json(
    evaluations: list[dict],
) -> str:
    """Export stored evaluations as formatted JSON."""

    return json.dumps(
        evaluations,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def evaluations_to_csv(
    evaluations: list[dict],
) -> str:
    """
    Export evaluations as a flat CSV.

    Each evaluation becomes one row and individual rubric
    dimensions become score/comment columns.
    """

    rows = []

    for evaluation in evaluations:
        row = {
            "evaluation_id": evaluation["id"],
            "dataset_key": evaluation["dataset_key"],
            "item_id": evaluation["item_id"],
            "evaluator": evaluation["evaluator"],
            "ratable": evaluation["ratable"],
            "unratable_reason": evaluation["unratable_reason"],
            "error_tags": ", ".join(
                evaluation["error_tags"]
            ),
            "overall_comment": evaluation["overall_comment"],
            "created_at": evaluation["created_at"],
        }

        for score in evaluation["scores"]:
            dimension = score["dimension"]

            row[f"{dimension}_score"] = score["score"]
            row[f"{dimension}_comment"] = score.get("comment")

        rows.append(row)

    dataframe = pd.DataFrame(rows)

    return dataframe.to_csv(index=False)
