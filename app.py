import hashlib
from pathlib import Path

import plotly.express as px
import streamlit as st

from evalforge.analytics import (
    build_error_tag_dataframe,
    build_evaluation_dataframe,
    build_score_dataframe,
)
from evalforge.dataset import (
    load_dataset,
    load_uploaded_dataset,
)
from evalforge.evaluator import (
    calculate_average_score,
    validate_evaluation,
)
from evalforge.models import (
    DimensionScore,
    EvaluationResult,
)
from evalforge.rubric import load_rubric
from evalforge.storage import (
    load_evaluations,
    save_evaluation,
)


DEFAULT_DATASET_PATH = Path("datasets/sample_benchmark.json")
RUBRIC_PATH = Path("rubrics/general_qa.yaml")


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="EvalForge",
    page_icon="⚒️",
    layout="wide",
)


# ---------------------------------------------------------
# Load rubric
# ---------------------------------------------------------

rubric = load_rubric(RUBRIC_PATH)


# ---------------------------------------------------------
# Dataset selection
# ---------------------------------------------------------

with st.sidebar:
    st.header("Dataset")

    uploaded_file = st.file_uploader(
        "Upload benchmark dataset",
        type=["json", "csv"],
        help=(
            "Required fields: id, prompt, response. "
            "Optional fields: model_name, category."
        ),
    )


if uploaded_file is not None:
    try:
        uploaded_content = uploaded_file.getvalue()

        items = load_uploaded_dataset(
            uploaded_file.name,
            uploaded_content,
        )

        dataset_signature = hashlib.sha256(
            uploaded_content
        ).hexdigest()

        dataset_name = uploaded_file.name

    except Exception as exc:
        st.error(
            f"Could not load uploaded dataset: {exc}"
        )
        st.stop()

else:
    items = load_dataset(DEFAULT_DATASET_PATH)

    dataset_signature = "default-sample-dataset"
    dataset_name = DEFAULT_DATASET_PATH.name


if not items:
    st.error(
        "The selected dataset contains no benchmark items."
    )
    st.stop()


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "dataset_signature" not in st.session_state:
    st.session_state.dataset_signature = dataset_signature

if (
    st.session_state.dataset_signature
    != dataset_signature
):
    st.session_state.dataset_signature = dataset_signature
    st.session_state.current_index = 0


if "current_index" not in st.session_state:
    st.session_state.current_index = 0


if st.session_state.current_index >= len(items):
    st.session_state.current_index = 0


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("⚒️ EvalForge")

st.caption(
    "A human-centered platform for evaluating and analyzing "
    "AI-generated responses."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.divider()

    st.header("Evaluation Session")

    evaluator_name = st.text_input(
        "Evaluator name",
        value="Kuntal",
    )

    selected_index = st.selectbox(
        "Benchmark item",
        options=range(len(items)),
        index=st.session_state.current_index,
        format_func=lambda i: (
            f"{items[i].id} — "
            f"{items[i].category or 'uncategorized'}"
        ),
    )

    if selected_index != st.session_state.current_index:
        st.session_state.current_index = selected_index
        st.rerun()

    stored_sidebar = load_evaluations(
        dataset_key=dataset_signature
    )

    st.divider()

    st.caption("Current dataset")

    st.write(f"**{dataset_name}**")

    st.metric(
        "Dataset items",
        len(items),
    )

    st.metric(
        "Saved evaluations",
        len(stored_sidebar),
    )

    st.caption(
        f"Rubric: {rubric.name}"
    )


current_item = items[
    st.session_state.current_index
]


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

evaluate_tab, dashboard_tab = st.tabs(
    [
        "📝 Evaluate",
        "📊 Dashboard",
    ]
)


# =========================================================
# EVALUATION TAB
# =========================================================

with evaluate_tab:

    progress = (
        st.session_state.current_index + 1
    ) / len(items)

    st.progress(
        progress,
        text=(
            f"Item "
            f"{st.session_state.current_index + 1} "
            f"of {len(items)}"
        ),
    )

    left, right = st.columns([1, 1])

    # -----------------------------------------------------
    # Prompt and response
    # -----------------------------------------------------

    with left:
        st.subheader("Prompt")

        st.info(
            current_item.prompt
        )

        st.subheader("Model Response")

        with st.container(border=True):
            st.write(
                current_item.response
            )

        st.caption(
            f"Model: "
            f"{current_item.model_name or 'Unknown'} "
            f"• Category: "
            f"{current_item.category or 'Uncategorized'}"
        )

    # -----------------------------------------------------
    # Human evaluation
    # -----------------------------------------------------

    with right:
        st.subheader("Evaluation")

        ratable = st.radio(
            "Is this response ratable?",
            ["Yes", "No"],
            horizontal=True,
            key=f"ratable_{dataset_signature}_{current_item.id}",
        )

        scores = []
        unratable_reason = None

        if ratable == "No":

            unratable_reason = st.text_area(
                "Why is this item unratable?",
                placeholder=(
                    "Explain why a reliable evaluation "
                    "cannot be made."
                ),
                key=(
                    f"unratable_"
                    f"{dataset_signature}_"
                    f"{current_item.id}"
                ),
            )

        else:

            for dimension in rubric.dimensions:

                st.markdown(
                    f"**{dimension.name}**"
                )

                st.caption(
                    dimension.description
                )

                score = st.slider(
                    dimension.name,
                    min_value=dimension.min_score,
                    max_value=dimension.max_score,
                    value=3,
                    key=(
                        f"{dataset_signature}_"
                        f"{current_item.id}_"
                        f"{dimension.name}"
                    ),
                    label_visibility="collapsed",
                )

                comment = st.text_input(
                    f"{dimension.name} comment",
                    key=(
                        f"{dataset_signature}_"
                        f"{current_item.id}_"
                        f"{dimension.name}_comment"
                    ),
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

        # -------------------------------------------------
        # Error taxonomy
        # -------------------------------------------------

        st.markdown("### Error Tags")

        error_tags = st.multiselect(
            "Select observed issues",
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
            key=(
                f"errors_"
                f"{dataset_signature}_"
                f"{current_item.id}"
            ),
            label_visibility="collapsed",
        )

        overall_comment = st.text_area(
            "Overall comment",
            placeholder="Optional overall assessment",
            key=(
                f"overall_"
                f"{dataset_signature}_"
                f"{current_item.id}"
            ),
        )

        # -------------------------------------------------
        # Score preview
        # -------------------------------------------------

        if ratable == "Yes":

            preview = EvaluationResult(
                item_id=current_item.id,
                evaluator=(
                    evaluator_name
                    or "Anonymous"
                ),
                ratable=True,
                scores=scores,
                error_tags=error_tags,
                overall_comment=(
                    overall_comment or None
                ),
            )

            average = calculate_average_score(
                preview,
                rubric,
            )

            if average is not None:
                st.metric(
                    "Average Score",
                    f"{average:.2f} / 5",
                )

        # -------------------------------------------------
        # Save evaluation
        # -------------------------------------------------

        if st.button(
            "Save Evaluation",
            type="primary",
            use_container_width=True,
        ):

            evaluation = EvaluationResult(
                item_id=current_item.id,
                evaluator=(
                    evaluator_name
                    or "Anonymous"
                ),
                ratable=(
                    ratable == "Yes"
                ),
                unratable_reason=(
                    unratable_reason
                ),
                scores=(
                    scores
                    if ratable == "Yes"
                    else []
                ),
                error_tags=error_tags,
                overall_comment=(
                    overall_comment or None
                ),
            )

            errors = validate_evaluation(
                evaluation,
                rubric,
            )

            if errors:

                for error in errors:
                    st.error(error)

            else:

                evaluation_id = save_evaluation(
                    evaluation,
                    dataset_key=dataset_signature,
                )

                st.success(
                    "Evaluation saved successfully. "
                    f"ID: {evaluation_id}"
                )


# =========================================================
# DASHBOARD TAB
# =========================================================

with dashboard_tab:

    st.subheader("Evaluation Analytics")

    evaluations = load_evaluations(
        dataset_key=dataset_signature
    )

    evaluation_df = (
        build_evaluation_dataframe(
            evaluations,
            items,
        )
    )

    score_df = build_score_dataframe(
        evaluations,
        items,
    )

    error_df = build_error_tag_dataframe(
        evaluations
    )

    if evaluation_df.empty:

        st.info(
            "No evaluations have been recorded "
            "for this dataset yet."
        )

    else:

        # -------------------------------------------------
        # Summary metrics
        # -------------------------------------------------

        total_evaluations = len(
            evaluation_df
        )

        ratable_count = int(
            evaluation_df[
                "ratable"
            ].sum()
        )

        model_count = int(
            evaluation_df[
                "model_name"
            ].nunique()
        )

        scored_evaluations = (
            evaluation_df[
                "average_score"
            ]
            .dropna()
        )

        if scored_evaluations.empty:
            overall_average = None
        else:
            overall_average = (
                scored_evaluations.mean()
            )

        (
            metric1,
            metric2,
            metric3,
            metric4,
        ) = st.columns(4)

        metric1.metric(
            "Total Evaluations",
            total_evaluations,
        )

        metric2.metric(
            "Ratable",
            ratable_count,
        )

        metric3.metric(
            "Models Evaluated",
            model_count,
        )

        metric4.metric(
            "Overall Average",
            (
                f"{overall_average:.2f} / 5"
                if overall_average
                is not None
                else "—"
            ),
        )

        st.divider()

        # -------------------------------------------------
        # Dimension scores
        # -------------------------------------------------

        if not score_df.empty:

            st.subheader(
                "Average Score by Dimension"
            )

            dimension_scores = (
                score_df
                .groupby(
                    "dimension",
                    as_index=False,
                )["score"]
                .mean()
            )

            dimension_scores[
                "score"
            ] = (
                dimension_scores[
                    "score"
                ]
                .round(2)
            )

            dimension_chart = px.bar(
                dimension_scores,
                x="dimension",
                y="score",
                text="score",
                labels={
                    "dimension":
                        "Evaluation Dimension",
                    "score":
                        "Average Score",
                },
            )

            dimension_chart.update_layout(
                yaxis_range=[0, 5],
            )

            st.plotly_chart(
                dimension_chart,
                use_container_width=True,
            )

        # -------------------------------------------------
        # Model comparison
        # -------------------------------------------------

        if not score_df.empty:

            st.subheader(
                "Model Performance"
            )

            model_scores = (
                score_df
                .groupby(
                    [
                        "model_name",
                        "dimension",
                    ],
                    as_index=False,
                )["score"]
                .mean()
            )

            model_scores[
                "score"
            ] = (
                model_scores[
                    "score"
                ]
                .round(2)
            )

            model_chart = px.bar(
                model_scores,
                x="dimension",
                y="score",
                color="model_name",
                barmode="group",
                labels={
                    "dimension":
                        "Dimension",
                    "score":
                        "Average Score",
                    "model_name":
                        "Model",
                },
            )

            model_chart.update_layout(
                yaxis_range=[0, 5],
            )

            st.plotly_chart(
                model_chart,
                use_container_width=True,
            )

        # -------------------------------------------------
        # Error analysis
        # -------------------------------------------------

        st.subheader(
            "Error Analysis"
        )

        if error_df.empty:

            st.info(
                "No error tags have been recorded."
            )

        else:

            error_chart = px.bar(
                error_df,
                x="count",
                y="error_tag",
                orientation="h",
                text="count",
                labels={
                    "error_tag":
                        "Error Type",
                    "count":
                        "Occurrences",
                },
            )

            st.plotly_chart(
                error_chart,
                use_container_width=True,
            )

        # -------------------------------------------------
        # Evaluation history
        # -------------------------------------------------

        st.subheader(
            "Evaluation History"
        )

        history = evaluation_df[
            [
                "evaluation_id",
                "item_id",
                "evaluator",
                "model_name",
                "category",
                "ratable",
                "average_score",
                "created_at",
            ]
        ].copy()

        history.columns = [
            "ID",
            "Item",
            "Evaluator",
            "Model",
            "Category",
            "Ratable",
            "Average Score",
            "Created",
        ]

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )