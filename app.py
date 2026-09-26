import json
from pathlib import Path

import streamlit as st

from evalforge.evaluator import calculate_average_score, validate_evaluation
from evalforge.models import BenchmarkItem, DimensionScore, EvaluationResult
from evalforge.rubric import load_rubric
from evalforge.storage import load_evaluations, save_evaluation


DATASET_PATH = Path("datasets/sample_benchmark.json")
RUBRIC_PATH = Path("rubrics/general_qa.yaml")


def load_benchmark() -> list[BenchmarkItem]:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return [BenchmarkItem.model_validate(item) for item in data]


st.set_page_config(
    page_title="EvalForge",
    page_icon="⚒️",
    layout="wide",
)

st.title("⚒️ EvalForge")
st.caption("Human-centered evaluation of AI-generated responses")

rubric = load_rubric(RUBRIC_PATH)
items = load_benchmark()

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

current_item = items[st.session_state.current_index]

with st.sidebar:
    st.header("Evaluation Session")

    evaluator_name = st.text_input(
        "Evaluator name",
        value="Kuntal",
    )

    selected_index = st.selectbox(
        "Benchmark item",
        options=range(len(items)),
        index=st.session_state.current_index,
        format_func=lambda i: f"{items[i].id} — {items[i].category}",
    )

    if selected_index != st.session_state.current_index:
        st.session_state.current_index = selected_index
        st.rerun()

    stored = load_evaluations()

    st.divider()
    st.metric("Saved evaluations", len(stored))

left, right = st.columns([1, 1])

with left:
    st.subheader("Prompt")
    st.info(current_item.prompt)

    st.subheader("Model Response")

    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border: 1px solid #444;
            border-radius: 10px;
            min-height: 150px;
        ">
        {current_item.response}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.caption(
        f"Model: {current_item.model_name or 'Unknown'} "
        f"• Category: {current_item.category or 'Uncategorized'}"
    )

with right:
    st.subheader("Evaluation")

    ratable = st.radio(
        "Is this response ratable?",
        ["Yes", "No"],
        horizontal=True,
    )

    scores = []
    unratable_reason = None

    if ratable == "No":
        unratable_reason = st.text_area(
            "Why is this item unratable?",
            placeholder="Explain why a reliable evaluation cannot be made.",
        )

    else:
        for dimension in rubric.dimensions:
            st.markdown(f"**{dimension.name}**")
            st.caption(dimension.description)

            score = st.slider(
                dimension.name,
                min_value=dimension.min_score,
                max_value=dimension.max_score,
                value=3,
                key=f"{current_item.id}_{dimension.name}",
                label_visibility="collapsed",
            )

            comment = st.text_input(
                f"{dimension.name} comment",
                key=f"{current_item.id}_{dimension.name}_comment",
                placeholder="Optional comment",
                label_visibility="collapsed",
            )

            scores.append(
                DimensionScore(
                    dimension=dimension.name,
                    score=score,
                    comment=comment or None,
                )
            )

    st.markdown("### Error tags")

    error_tags = st.multiselect(
        "Select any issues you observed",
        [
            "Factual Error",
            "Hallucination",
            "Incomplete Answer",
            "Instruction Violation",
            "Irrelevant Content",
            "Reasoning Error",
            "Formatting Issue",
            "Unclear Writing",
        ],
        label_visibility="collapsed",
    )

    overall_comment = st.text_area(
        "Overall comment",
        placeholder="Optional overall assessment",
    )

    if ratable == "Yes":
        preview = EvaluationResult(
            item_id=current_item.id,
            evaluator=evaluator_name or "Anonymous",
            ratable=True,
            scores=scores,
            error_tags=error_tags,
            overall_comment=overall_comment or None,
        )

        average = calculate_average_score(preview, rubric)

        if average is not None:
            st.metric("Average score", f"{average:.2f} / 5")

    if st.button(
        "Save Evaluation",
        type="primary",
        use_container_width=True,
    ):
        evaluation = EvaluationResult(
            item_id=current_item.id,
            evaluator=evaluator_name or "Anonymous",
            ratable=ratable == "Yes",
            unratable_reason=unratable_reason,
            scores=scores if ratable == "Yes" else [],
            error_tags=error_tags,
            overall_comment=overall_comment or None,
        )

        errors = validate_evaluation(evaluation, rubric)

        if errors:
            for error in errors:
                st.error(error)
        else:
            evaluation_id = save_evaluation(evaluation)

            st.success(
                f"Evaluation saved successfully. ID: {evaluation_id}"
            )