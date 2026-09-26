import json
import sqlite3
from pathlib import Path

from evalforge.models import EvaluationResult


DEFAULT_DB_PATH = Path("data/evalforge.db")
DEFAULT_DATASET_KEY = "default-sample-dataset"


def get_connection(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    """Create a database connection and ensure its directory exists."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(db_path)


def initialize_database(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Create the database schema and migrate older EvalForge databases.
    """

    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_key TEXT NOT NULL,
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

        # Check whether this is an older EvalForge database that
        # existed before dataset isolation was introduced.
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(evaluations)"
            ).fetchall()
        }

        if "dataset_key" not in columns:
            connection.execute(
                """
                ALTER TABLE evaluations
                ADD COLUMN dataset_key TEXT
                """
            )

            # Evaluations created before dataset uploads existed
            # necessarily belonged to the built-in sample dataset.
            connection.execute(
                """
                UPDATE evaluations
                SET dataset_key = ?
                WHERE dataset_key IS NULL
                """,
                (DEFAULT_DATASET_KEY,),
            )

        connection.commit()


def save_evaluation(
    evaluation: EvaluationResult,
    dataset_key: str = DEFAULT_DATASET_KEY,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """
    Save an evaluation and return its database ID.
    """

    initialize_database(db_path)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO evaluations (
                dataset_key,
                item_id,
                evaluator,
                ratable,
                unratable_reason,
                scores,
                error_tags,
                overall_comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_key,
                evaluation.item_id,
                evaluation.evaluator,
                int(evaluation.ratable),
                evaluation.unratable_reason,
                json.dumps(
                    [
                        score.model_dump()
                        for score in evaluation.scores
                    ]
                ),
                json.dumps(evaluation.error_tags),
                evaluation.overall_comment,
            ),
        )

        return cursor.lastrowid


def load_evaluations(
    dataset_key: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """
    Load evaluations.

    When dataset_key is supplied, only evaluations belonging to that
    dataset are returned.
    """

    initialize_database(db_path)

    with get_connection(db_path) as connection:
        connection.row_factory = sqlite3.Row

        if dataset_key is None:
            rows = connection.execute(
                """
                SELECT *
                FROM evaluations
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

        else:
            rows = connection.execute(
                """
                SELECT *
                FROM evaluations
                WHERE dataset_key = ?
                ORDER BY created_at DESC, id DESC
                """,
                (dataset_key,),
            ).fetchall()

    results = []

    for row in rows:
        item = dict(row)

        item["ratable"] = bool(item["ratable"])
        item["scores"] = json.loads(item["scores"])
        item["error_tags"] = json.loads(
            item["error_tags"]
        )

        results.append(item)

    return results