import json
from io import BytesIO
from pathlib import Path

import pandas as pd

from evalforge.models import BenchmarkItem


REQUIRED_FIELDS = {"id", "prompt", "response"}


def load_json_dataset(path: str | Path) -> list[BenchmarkItem]:
    """Load benchmark items from a JSON file."""

    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("JSON dataset must contain a list of items.")

    return [
        BenchmarkItem.model_validate(item)
        for item in data
    ]


def load_csv_dataset(path: str | Path) -> list[BenchmarkItem]:
    """Load benchmark items from a CSV file."""

    path = Path(path)

    dataframe = pd.read_csv(path)

    missing = REQUIRED_FIELDS - set(dataframe.columns)

    if missing:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(sorted(missing))
        )

    items = []

    for record in dataframe.to_dict(orient="records"):
        if pd.isna(record.get("model_name")):
            record["model_name"] = None

        if pd.isna(record.get("category")):
            record["category"] = None

        items.append(
            BenchmarkItem.model_validate(record)
        )

    return items


def load_dataset(path: str | Path) -> list[BenchmarkItem]:
    """Automatically load JSON or CSV benchmark datasets."""

    path = Path(path)

    suffix = path.suffix.lower()

    if suffix == ".json":
        return load_json_dataset(path)

    if suffix == ".csv":
        return load_csv_dataset(path)

    raise ValueError(
        "Unsupported dataset format. Use JSON or CSV."
    )


def load_uploaded_dataset(
    filename: str,
    content: bytes,
) -> list[BenchmarkItem]:
    """Load a JSON or CSV dataset from uploaded file bytes."""

    suffix = Path(filename).suffix.lower()

    if suffix == ".json":
        data = json.loads(content.decode("utf-8"))

        if not isinstance(data, list):
            raise ValueError(
                "JSON dataset must contain a list of items."
            )

        return [
            BenchmarkItem.model_validate(item)
            for item in data
        ]

    if suffix == ".csv":
        dataframe = pd.read_csv(BytesIO(content))

        missing = REQUIRED_FIELDS - set(
            dataframe.columns
        )

        if missing:
            raise ValueError(
                "CSV is missing required columns: "
                + ", ".join(sorted(missing))
            )

        items = []

        for record in dataframe.to_dict(
            orient="records"
        ):
            if pd.isna(record.get("model_name")):
                record["model_name"] = None

            if pd.isna(record.get("category")):
                record["category"] = None

            items.append(
                BenchmarkItem.model_validate(
                    record
                )
            )

        return items

    raise ValueError(
        "Unsupported dataset format. Use JSON or CSV."
    )