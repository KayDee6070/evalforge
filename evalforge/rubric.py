from pathlib import Path

import yaml

from evalforge.models import Rubric


def load_rubric(path: str | Path) -> Rubric:
    """Load and validate an evaluation rubric from a YAML file."""

    rubric_path = Path(path)

    if not rubric_path.exists():
        raise FileNotFoundError(
            f"Rubric file not found: {rubric_path}"
        )

    with rubric_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not data:
        raise ValueError(
            "Rubric file is empty."
        )

    return Rubric.model_validate(data)


def load_uploaded_rubric(
    content: bytes,
) -> Rubric:
    """Load and validate a rubric from uploaded YAML bytes."""

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Rubric must be UTF-8 encoded."
        ) from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(
            "Rubric contains invalid YAML."
        ) from exc

    if not data:
        raise ValueError(
            "Rubric file is empty."
        )

    return Rubric.model_validate(data)