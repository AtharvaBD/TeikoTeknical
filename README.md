# Loblaw Bio — Immune Cell Population Analysis

Analysis pipeline and interactive dashboard for Bob Loblaw's miraclib melanoma trial data.
Given `cell-count.csv`, this project loads the data into a relational SQLite database,
computes per-sample cell population frequencies, tests for significant differences between
treatment responders and non-responders, and explores a baseline patient subset — all
surfaced through a Streamlit dashboard.

## Repository structure

```
.
├── cell-count.csv              # input data (place in repo root)
├── load_data.py                # Part 1: builds cell_count.db from the CSV
├── config.yml                  # output paths (e.g. boxplot image location)
├── requirements.txt
├── Makefile
├── melanoma_male_bcell_avg.py  # standalone script for the Part 4 quantitative question
└── pipeline/
    ├── InitialAnalysis.py      # Part 2: per-sample population frequencies
    ├── StatistialAnalysis.py   # Part 3: responder vs non-responder stats + boxplots
    ├── DataSubsetAnalysis.py   # Part 4: baseline melanoma/PBMC/miraclib subset breakdown
    └── InteractiveDashboard.py # Streamlit dashboard (Parts 2–4)
```

## Setup

```
make setup
```

Installs everything listed in `requirements.txt` (pandas, PyYAML, scipy, statsmodels,
matplotlib, streamlit, plotly).

## Running the pipeline

```
make pipeline
```

This runs `load_data.py`, which:

1. Deletes any existing `cell_count.db` (so the pipeline is safely re-runnable).
2. Creates the schema described below.
3. Reads `cell-count.csv` and loads it into `projects`, `subjects`, `samples`, and
   `cell_counts`.

You can also run the individual analysis scripts directly for console output, e.g.:

```
python pipeline/InitialAnalysis.py
python pipeline/StatistialAnalysis.py
python pipeline/DataSubsetAnalysis.py
python melanoma_male_bcell_avg.py
```

## Running the dashboard

```
make dashboard
```

This starts a local Streamlit server presenting Parts 2–4 as three tabs, reading directly
from `cell_count.db`:

- **Part 2 — Initial Analysis**: per-sample, per-population frequency table with sample
  filtering.
- **Part 3 — Statistical Analysis**: responder vs. non-responder boxplots per population,
  plus a Welch's t-test (FDR-corrected) significance table.
- **Part 4 — Data Subset Analysis**: baseline (melanoma, PBMC, miraclib,
  `time_from_treatment_start = 0`) sample table, with breakdowns by project, response, and
  sex (each with a totals row).

Dashboard link: **[add your deployed dashboard URL here]**

## Database schema

SQLite, four tables:

- **`projects`** — `project_id` (PK). One row per project.
- **`subjects`** — `subject_id` (PK), `project` (FK → `projects.project_id`), `condition`,
  `age`, `sex`, `treatment`, `response`. One row per patient.
- **`samples`** — `sample_id` (PK), `subject_id` (FK → `subjects.subject_id`),
  `sample_type` (PBMC/WB), `time_from_treatment_start`. One row per sample.
- **`cell_counts`** — `sample_id` (FK → `samples.sample_id`), `population`, `count`,
  composite PK on `(sample_id, population)`. Long-format: one row per (sample, population)
  pair, five rows per sample (b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte).

`subjects` and `samples` are normalized 1:many off `projects` and `subjects` respectively;
`cell_counts` is kept in long (tidy) format rather than one wide row per sample so that
adding a new population later requires no schema change.

## Design notes

- **Relative frequency** is reported as a **percentage** (0–100), per the spec, computed
  per sample as `100 * count / total_count_for_that_sample`.
- **Significance testing** uses **Welch's t-test** (does not assume equal variance between
  groups) per population, with **Benjamini-Hochberg FDR correction** across the 5
  simultaneous tests (one per population) to control the false-discovery rate — with 5
  tests at α=0.05, there's a meaningful chance of at least one false positive without
  this correction. Group sizes here are large (n≈330 per group), so the t-test's
  normality assumption is well supported by the Central Limit Theorem.

## Part 4 — quantitative answer

Considering melanoma males of all sample and treatment types, the average number of B
cells for responders at `time_from_treatment_start = 0` is **10206.15** (see
`melanoma_male_bcell_avg.py`).