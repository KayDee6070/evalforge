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
from evalforge.export import (
    evaluations_to_csv,
    evaluations_to_json,
)
from evalforge.models import (
    DimensionScore,
    EvaluationResult,
)
from evalforge.rubric import (
    load_rubric,
    load_uploaded_rubric,
)
from evalforge.storage import (
    load_evaluations,
    save_evaluation,
)


DEFAULT_DATASET_PATH = Path("datasets/sample_benchmark.json")
DEFAULT_RUBRIC_PATH = Path("rubrics/general_qa.yaml")


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="EvalForge",
    page_icon="⚒️",
    layout="wide",
)


# ---------------------------------------------------------
# Sidebar uploads
# ---------------------------------------------------------

with st.sidebar:
    st.header("Dataset")

    uploaded_dataset = st.file_uploader(
        "Upload benchmark dataset",
        type=["json", "csv"],
        help=(
            "Required fields: id, prompt, response. "
            "Optional fields: model_name, category."
        ),
    )

    st.header("Rubric")

    uploaded_rubric = st.file_uploader(
        "Upload evaluation rubric",
        type=["yaml", "yml"],
        help=(
            "Upload a YAML rubric containing a name, "
            "description, and scoring dimensions."
        ),
    )


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

if uploaded_dataset is not None:
    try:
        dataset_content = uploaded_dataset.getvalue()

        items = load_uploaded_dataset(
            uploaded_dataset.name,
            dataset_content,
        )

        dataset_signature = hashlib.sha256(
            dataset_content
        ).hexdigest()

        dataset_name = uploaded_dataset.name

    except Exception as exc:
        st.error(
            f"Could not load uploaded dataset: {exc}"
        )
        st.stop()

else:
    items = load_dataset(
        DEFAULT_DATASET_PATH
    )

    dataset_signature = "default-sample-dataset"
    dataset_name = DEFAULT_DATASET_PATH.name


if not items:
    st.error(
        "The selected dataset contains no benchmark items."
    )
    st.stop()


# ---------------------------------------------------------
# Load rubric
# ---------------------------------------------------------

if uploaded_rubric is not None:
    try:
        rubric_content = uploaded_rubric.getvalue()

        rubric = load_uploaded_rubric(
            rubric_content
        )

        rubric_signature = hashlib.sha256(
            rubric_content
        ).hexdigest()

        rubric_name = uploaded_rubric.name

    except Exception as exc:
        st.error(
            f"Could not load uploaded rubric: {exc}"
        )
        st.stop()

else:
    rubric = load_rubric(
        DEFAULT_RUBRIC_PATH
    )

    rubric_signature = "default-general-qa-rubric"
    rubric_name = DEFAULT_RUBRIC_PATH.name


# ---------------------------------------------------------
# Evaluation scope
# ---------------------------------------------------------

# Preserve compatibility with evaluations already created
# using the original built-in dataset + rubric.
if (
    dataset_signature == "default-sample-dataset"
    and rubric_signature == "default-general-qa-rubric"
):
    evaluation_scope_key = "default-sample-dataset"

elif rubric_signature == "default-general-qa-rubric":
    evaluation_scope_key = dataset_signature

else:
    evaluation_scope_key = hashlib.sha256(
        (
            dataset_signature
            + ":"
            + rubric_signature
        ).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "evaluation_scope" not in st.session_state:
    st.session_state.evaluation_scope = (
        evaluation_scope_key
    )

if (
    st.session_state.evaluation_scope
    != evaluation_scope_key
):
    st.session_state.evaluation_scope = (
        evaluation_scope_key
    )
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
# Sidebar session controls
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
        dataset_key=evaluation_scope_key
    )

    st.divider()

    st.caption("Current dataset")
    st.write(f"**{dataset_name}**")

    st.metric(
        "Dataset items",
        len(items),
    )

    st.caption("Current rubric")
    st.write(f"**{rubric.name}**")

    st.caption(
        f"{len(rubric.dimensions)} scoring dimensions"
    )

    st.metric(
        "Saved evaluations",
        len(stored_sidebar),
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
    # Prompt and model response
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

        st.divider()

        with st.expander(
            "View Evaluation Rubric"
        ):
            st.markdown(
                f"### {rubric.name}"
            )

            st.write(
                rubric.description
            )

            for dimension in rubric.dimensions:
                st.markdown(
                    f"**{dimension.name}**"
                )

                st.write(
                    dimension.description
                )

                st.caption(
                    f"Score range: "
                    f"{dimension.min_score}–"
                    f"{dimension.max_score}"
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
            key=(
                f"ratable_"
                f"{evaluation_scope_key}_"
                f"{current_item.id}"
            ),
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
                    f"{evaluation_scope_key}_"
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
                    value=(
                        dimension.min_score
                        + (
                            dimension.max_score
                            - dimension.min_score
                        )
                        // 2
                    ),
                    key=(
                        f"{evaluation_scope_key}_"
                        f"{current_item.id}_"
                        f"{dimension.name}"
                    ),
                    label_visibility="collapsed",
                )

                comment = st.text_input(
                    f"{dimension.name} comment",
                    key=(
                        f"{evaluation_scope_key}_"
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
                f"{evaluation_scope_key}_"
                f"{current_item.id}"
            ),
            label_visibility="collapsed",
        )

        overall_comment = st.text_area(
            "Overall comment",
            placeholder="Optional overall assessment",
            key=(
                f"overall_"
                f"{evaluation_scope_key}_"
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
                    f"{average:.2f}",
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
                    dataset_key=evaluation_scope_key,
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

    st.caption(
        f"Dataset: {dataset_name} "
        f"• Rubric: {rubric.name}"
    )

    evaluations = load_evaluations(
        dataset_key=evaluation_scope_key
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
            "for this dataset and rubric yet."
        )

    else:

        # -------------------------------------------------
        # Export results
        # -------------------------------------------------

        st.subheader("Export Results")

        export_name = (
            f"{Path(dataset_name).stem}_evaluations"
        )

        csv_export = evaluations_to_csv(
            evaluations
        )

        json_export = evaluations_to_json(
            evaluations
        )

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.download_button(
                "⬇️ Download CSV",
                data=csv_export,
                file_name=(
                    f"{export_name}.csv"
                ),
                mime="text/csv",
                use_container_width=True,
            )

        with export_col2:
            st.download_button(
                "⬇️ Download JSON",
                data=json_export,
                file_name=(
                    f"{export_name}.json"
                ),
                mime="application/json",
                use_container_width=True,
            )

        st.divider()


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
                f"{overall_average:.2f}"
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

            maximum_score = max(
                dimension.max_score
                for dimension
                in rubric.dimensions
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
                yaxis_range=[
                    0,
                    maximum_score,
                ],
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

            maximum_score = max(
                dimension.max_score
                for dimension
                in rubric.dimensions
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
                yaxis_range=[
                    0,
                    maximum_score,
                ],
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