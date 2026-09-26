import json
import sqlite3
from pathlib import Path

from evalforge.models import EvaluationResult


DEFAULT_DB_PATH = Path("data/evalforge.db")


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a database connection and ensure the parent folder exists."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(db_path)


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Create the evaluations table if it does not already exist."""

    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                evaluator TEXT NOT NULL,
                ratable INTEGER NOT NULL,
                unratable_reason TEXT,
                scores TEXT NOT NULL,
                error_tags TEXT NOT NULL,
                overall_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_evaluation(
    evaluation: EvaluationResult,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """Save an evaluation and return its database ID."""

    initialize_database(db_path)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO evaluations (
                item_id,
                evaluator,
                ratable,
                unratable_reason,
                scores,
                error_tags,
                overall_comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation.item_id,
                evaluation.evaluator,
                int(evaluation.ratable),
                evaluation.unratable_reason,
                json.dumps(
                    [score.model_dump() for score in evaluation.scores]
                ),
                json.dumps(evaluation.error_tags),
                evaluation.overall_comment,
            ),
        )

        return cursor.lastrowid


def load_evaluations(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """Load all stored evaluations."""

    initialize_database(db_path)

    with get_connection(db_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT *
            FROM evaluations
            ORDER BY created_at DESC
            """
        ).fetchall()

    results = []

    for row in rows:
        item = dict(row)
        item["ratable"] = bool(item["ratable"])
        item["scores"] = json.loads(item["scores"])
        item["error_tags"] = json.loads(item["error_tags"])
        results.append(item)

    return results