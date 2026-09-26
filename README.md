# ⚒️ EvalForge

[![Tests](https://github.com/KayDee6070/evalforge/actions/workflows/tests.yml/badge.svg)](https://github.com/KayDee6070/evalforge/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**EvalForge** is a human-centered platform for systematically evaluating, comparing, and analyzing AI-generated responses.

It provides a configurable workflow for **LLM evaluation, human feedback, model benchmarking, error analysis, and AI quality assurance**.

### 🌐 [Try the Live Demo](https://evalforge-9cb65yb69rzuy6pjwdkdn2.streamlit.app/)

---

## Screenshots

### Evaluation Interface

Evaluate AI responses across configurable quality dimensions, classify failure modes, and record structured human feedback.

![EvalForge Evaluation Interface](docs/images/evalforge-evaluator.jpeg)

### Analytics Dashboard

Compare model performance, inspect dimension-level scores, analyze common failures, and export results.

![EvalForge Analytics Dashboard](docs/images/evalforge-dashboard.jpeg)

---

## Why EvalForge?

Evaluating language models requires more than deciding whether an answer simply "looks good."

A useful evaluation workflow needs to answer questions such as:

- Is the response actually correct?
- Did the model follow the user's instructions?
- Is important information missing?
- What type of failure occurred?
- Are different evaluators applying the same criteria?
- Which models perform better on specific dimensions?
- What failure patterns occur repeatedly?

EvalForge turns these questions into a structured and reusable evaluation workflow.

---

## Features

### 📝 Structured Human Evaluation

Each model response can be evaluated using multiple quality dimensions.

The evaluator can:

- Mark a response as ratable or unratable
- Score individual rubric dimensions
- Add dimension-level comments
- Add an overall assessment
- Classify observed failure modes
- Save evaluations for later analysis

---

### 📋 Configurable Evaluation Rubrics

Evaluation rubrics are defined using YAML.

EvalForge includes a default **General QA Evaluation** rubric with:

- Correctness
- Relevance
- Instruction Following
- Completeness
- Clarity

A separate coding rubric includes:

- Technical Correctness
- Instruction Following
- Code Quality
- Completeness
- Explanation Quality
- Robustness

Users can upload their own YAML rubrics without changing the application code.

---

### 📂 JSON and CSV Benchmark Upload

Benchmark datasets can be uploaded as either:

- JSON
- CSV

Required fields:

```text
id
prompt
response
```

Optional fields:

```text
model_name
category
```

Example JSON:

```json
[
  {
    "id": "qa-001",
    "prompt": "What is the capital of Australia?",
    "response": "The capital of Australia is Sydney.",
    "model_name": "DemoModel-A",
    "category": "factual_qa"
  }
]
```

Example CSV:

```csv
id,prompt,response,model_name,category
qa-001,"What is the capital of Australia?","The capital of Australia is Sydney.","DemoModel-A","factual_qa"
```

---

## Custom Rubric Format

Example YAML rubric:

```yaml
name: General QA Evaluation

description: >
  A general-purpose rubric for evaluating the quality
  of AI-generated responses.

dimensions:
  - name: Correctness
    description: >
      Measures whether the response is factually accurate
      and free from substantive errors.
    min_score: 1
    max_score: 5

  - name: Relevance
    description: >
      Measures whether the response directly addresses
      the user's request.
    min_score: 1
    max_score: 5
```

EvalForge dynamically generates the evaluation interface from the uploaded rubric.

---

## 🚨 Error Taxonomy

Evaluators can classify model failures using tags such as:

- Factual Error
- Hallucination
- Incomplete Answer
- Instruction Violation
- Irrelevant Content
- Reasoning Error
- Formatting Issue
- Unclear Writing

The dashboard aggregates these error types to reveal recurring model weaknesses.

---

## 📊 Analytics Dashboard

EvalForge converts evaluation records into structured analytics.

The dashboard includes:

- Total evaluation count
- Ratable response count
- Number of evaluated models
- Overall average score
- Average score by rubric dimension
- Model-level performance comparison
- Error-frequency analysis
- Evaluation history
- Demo vs user evaluation labels

---

## Built-in Demo Benchmark

The repository includes a sample benchmark containing:

```text
12 responses
3 demo models
7 task categories
```

Categories include:

- Factual QA
- Science
- Coding
- Reasoning
- Instruction following
- Summarization
- Technical explanation

The benchmark intentionally contains both strong and weak responses so the evaluation workflow and analytics can be explored immediately.

EvalForge also includes **12 bundled sample evaluations** for the default benchmark.

These are explicitly labeled as **Demo** in the dashboard and can be toggled on or off.

---

## Evaluation Workflow

```text
Benchmark Dataset
       │
       ▼
Prompt + Model Response
       │
       ▼
Is the response ratable?
       │
   ┌───┴───┐
   │       │
  No      Yes
   │       │
Reason     ▼
       Rubric Scoring
            │
            ▼
       Error Tagging
            │
            ▼
       Save Evaluation
            │
            ▼
     Analytics Dashboard
            │
            ▼
       CSV / JSON Export
```

---

## Evaluation Session Features

EvalForge includes several workflow features designed for larger evaluation sets:

- Previous / Next navigation
- Progress tracking
- **Save & Next**
- Duplicate-evaluation detection
- Intentional duplicate override
- Evaluator identity tracking
- Dataset and rubric isolation

---

## Dataset + Rubric Isolation

Evaluation results are separated by both dataset and rubric configuration.

For example:

```text
Dataset A + General QA Rubric
        ↓
Evaluation History A

Dataset A + Coding Rubric
        ↓
Evaluation History B

Dataset B + General QA Rubric
        ↓
Evaluation History C
```

This prevents unrelated experiments from contaminating each other's analytics.

---

## Export

Evaluation results can be downloaded directly from the dashboard as:

- CSV
- JSON

CSV exports flatten rubric dimensions into analysis-friendly columns.

JSON exports preserve the full structured evaluation representation.

---

## Architecture

```text
evalforge/
│
├── app.py
│
├── evalforge/
│   ├── __init__.py
│   ├── analytics.py
│   ├── dataset.py
│   ├── demo.py
│   ├── evaluator.py
│   ├── export.py
│   ├── models.py
│   ├── rubric.py
│   └── storage.py
│
├── datasets/
│   ├── sample_benchmark.json
│   ├── sample_benchmark.csv
│   └── demo_evaluations.json
│
├── rubrics/
│   ├── general_qa.yaml
│   └── coding.yaml
│
├── tests/
│   ├── test_dataset.py
│   ├── test_evaluator.py
│   └── test_storage.py
│
├── docs/
│   └── images/
│       ├── evalforge-evaluator.jpeg
│       └── evalforge-dashboard.jpeg
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── LICENSE
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and evaluation logic |
| Streamlit | Interactive evaluation interface |
| Pydantic | Structured models and validation |
| Pandas | Dataset processing and analytics |
| Plotly | Interactive visualizations |
| SQLite | Local evaluation persistence |
| PyYAML | Configurable rubric definitions |
| Pytest | Automated testing |
| GitHub Actions | Continuous integration |

---

## Installation

Clone the repository:

```bash
git clone https://github.com/KayDee6070/evalforge.git
cd evalforge
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running EvalForge

Start the application:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## Running Tests

Run:

```bash
pytest -v
```

The automated test suite currently covers:

- Evaluation scoring
- Ratability handling
- Rubric validation
- Missing rubric dimensions
- Unknown rubric dimensions
- JSON dataset loading
- CSV dataset loading
- Invalid dataset handling
- SQLite persistence
- Dataset isolation

Current local test status:

```text
14 passed
```

GitHub Actions also runs the test suite automatically on pushes and pull requests to `main`.

---

## Live Demo Storage

The hosted Streamlit demo uses local SQLite storage.

This is sufficient for demonstration purposes, but hosted evaluation records should be considered **temporary** because application restarts or redeployments may reset local state.

Users can export evaluations as CSV or JSON before leaving the application.

A production deployment could replace SQLite with persistent storage such as PostgreSQL or another managed database.

---

## Future Work

Potential extensions include:

- LLM-as-a-Judge evaluation
- Human vs automated evaluator agreement
- Cohen's Kappa and inter-rater reliability
- Multiple human evaluators per response
- Pairwise model comparison
- Evaluation assignment workflows
- More benchmark templates
- Persistent hosted database
- FastAPI backend
- Authentication
- Multi-user evaluation sessions

---

## Project Scope

EvalForge focuses on the **human evaluation and analysis layer** of LLM quality assessment.

Automated LLM judging and human-vs-model agreement analysis are intentionally left as future extensions rather than being mixed into the core v1 workflow.

---

## Disclaimer

The evaluation rubrics, benchmark examples, and demo evaluations in this repository were created specifically for EvalForge.

They do not reproduce proprietary evaluation guidelines, private benchmark datasets, or confidential annotation material from third-party platforms.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

**Kuntal Dive**

Master's student in Digital Engineering at Bauhaus-Universität Weimar.

Interests:

- Artificial Intelligence
- LLM Evaluation
- Machine Learning
- AI Quality Assurance
- Model Benchmarking
- Software Engineering
- Data Analysis

### Links

- [Live Demo](https://evalforge-9cb65yb69rzuy6pjwdkdn2.streamlit.app/)
- [GitHub Repository](https://github.com/KayDee6070/evalforge)