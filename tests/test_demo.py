from evalforge.demo import load_demo_evaluations


def test_demo_evaluations_load():
    evaluations = load_demo_evaluations()

    assert len(evaluations) == 12


def test_demo_evaluations_have_expected_structure():
    evaluations = load_demo_evaluations()

    first = evaluations[0]

    assert first["item_id"] == "qa-001"
    assert first["evaluator"] == "Demo Evaluator"
    assert first["source"] == "Demo"
    assert first["ratable"] is True

    assert isinstance(first["scores"], list)
    assert len(first["scores"]) == 5

    assert first["scores"][0]["dimension"] == "Correctness"
    assert first["scores"][0]["score"] == 1


def test_demo_evaluations_cover_all_models_items():
    evaluations = load_demo_evaluations()

    item_ids = {
        evaluation["item_id"]
        for evaluation in evaluations
    }

    assert item_ids == {
        "qa-001",
        "qa-002",
        "qa-003",
        "qa-004",
        "qa-005",
        "qa-006",
        "qa-007",
        "qa-008",
        "qa-009",
        "qa-010",
        "qa-011",
        "qa-012",
    }