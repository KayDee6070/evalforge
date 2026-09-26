import json

import pytest

from evalforge.dataset import (
    load_uploaded_dataset,
)


def test_load_uploaded_json_dataset():
    data = [
        {
            "id": "item-1",
            "prompt": "What is 2 + 2?",
            "response": "4",
            "model_name": "TestModel",
            "category": "math",
        }
    ]

    content = json.dumps(data).encode("utf-8")

    items = load_uploaded_dataset(
        "benchmark.json",
        content,
    )

    assert len(items) == 1
    assert items[0].id == "item-1"
    assert items[0].prompt == "What is 2 + 2?"
    assert items[0].response == "4"
    assert items[0].model_name == "TestModel"
    assert items[0].category == "math"


def test_load_uploaded_csv_dataset():
    content = (
        "id,prompt,response,model_name,category\n"
        'item-1,"Say hello","Hello!","TestModel","general"\n'
    ).encode("utf-8")

    items = load_uploaded_dataset(
        "benchmark.csv",
        content,
    )

    assert len(items) == 1
    assert items[0].id == "item-1"
    assert items[0].response == "Hello!"
    assert items[0].model_name == "TestModel"


def test_json_dataset_must_be_list():
    content = json.dumps(
        {
            "id": "item-1",
            "prompt": "Test",
            "response": "Test",
        }
    ).encode("utf-8")

    with pytest.raises(
        ValueError,
        match="must contain a list",
    ):
        load_uploaded_dataset(
            "benchmark.json",
            content,
        )


def test_csv_requires_core_columns():
    content = (
        "id,prompt\n"
        'item-1,"Missing response"\n'
    ).encode("utf-8")

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        load_uploaded_dataset(
            "benchmark.csv",
            content,
        )


def test_unsupported_dataset_format():
    with pytest.raises(
        ValueError,
        match="Unsupported dataset format",
    ):
        load_uploaded_dataset(
            "benchmark.txt",
            b"hello",
        )