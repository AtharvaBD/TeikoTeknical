# Loblaw Bio — Immune Cell Population Analysis

Analysis pipeline and interactive dashboard for Bob Loblaw.
Given `cell-count.csv`, this project loads the data into a relational SQLite database,
computes per-sample cell population frequencies, tests for significant differences between
treatment responders and non-responders, and explores a baseline patient subset, all
displayed through an interactive Streamlit dashboard.

## Repository structure

```
.
├── cell-count.csv              # input data (place in repo root)
├── load_data.py                # Part 1: builds cell_count.db from the CSV
├── avgb_cell.py                # Part 4 free-response question (B cell average)
├── InteractiveDashboard.py     # Streamlit dashboard (Parts 2–4)
├── requirements.txt
├── Makefile
└── pipeline/
    ├── InitialAnalysis.py      # Part 2: per-sample population frequencies
    ├── StatistialAnalysis.py   # Part 3: responder vs non-responder stats + boxplots
    └── DataSubsetAnalysis.py   # Part 4: baseline melanoma/PBMC/miraclib subset breakdown
```

## Setup

```
make setup
```

Installs everything listed in `requirements.txt` (pandas, scipy, statsmodels, matplotlib,
streamlit, plotly — `sqlite3` is part of the Python standard library and does not need to
be installed).

## Running the pipeline

```
make pipeline
```

This runs, in order:

1. `load_data.py` — deletes any existing `cell_count.db` (so the pipeline is safely
   re-runnable), creates the schema described below, reads `cell-count.csv`, and loads it
   into `subjects`, `samples`, and `cell_counts`.
2. `pipeline/InitialAnalysis.py` — prints the Part 2 frequency table.
3. `pipeline/StatistialAnalysis.py` — prints the Part 3 responder/non-responder stats and
   saves `Boxplots.png`.
4. `pipeline/DataSubsetAnalysis.py` — prints the Part 4 baseline subset breakdown.
5. `avgb_cell.py` — prints the Part 4 free-response average B cell count.

You can also run any of these individually, e.g.:

```
python pipeline/InitialAnalysis.py
python pipeline/StatistialAnalysis.py
python pipeline/DataSubsetAnalysis.py
python avgb_cell.py
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
  sex (each with a totals row), plus the average B cell count for melanoma male responders
  at baseline (all sample/treatment types).

## Database schema

SQLite, three tables:

- **`subjects`** — `subject_id` (PK), `project`, `condition`, `age`, `sex`, `treatment`,
  `response`. One row per patient.
- **`samples`** — `sample_id` (PK), `subject_id` (FK → `subjects.subject_id`),
  `sample_type` (PBMC/WB), `time_from_treatment_start`. One row per sample.
- **`cell_counts`** — `sample_id` (FK → `samples.sample_id`), `population`, `count`,
  composite PK on `(sample_id, population)`. Long-format: one row per (sample, population)
  pair, five rows per sample (b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte).

`samples` is normalized 1:many off `subjects`; `cell_counts` is kept in long (tidy) format
rather than one wide row per sample so that adding a new population later requires no
schema change. `project` is stored directly on `subjects` as a plain column rather than a
separate lookup table, since the trial only has 3 distinct projects.

## Design notes

- **Relative frequency** is reported as a **percentage** (0–100), per the spec, computed
  per sample as `100 * count / total_count_for_that_sample`.
- **Significance testing** uses **Welch's t-test** (does not assume equal variance between
  groups) per population, with **FDR correction** across the 5 simultaneous tests (one per
  population) to control the false-discovery rate — with 5 tests at α=0.05, there's a
  meaningful chance of at least one false positive without this correction. Group sizes
  here are large, so the t-test's normality assumption is well supported by the Central
  Limit Theorem.

## Part 4 — quantitative answer

Considering melanoma males of all sample and treatment types, the average number of B
cells for responders at `time_from_treatment_start = 0` is **10206.15** (see
`avgb_cell.py`, also shown in the Part 4 dashboard tab).

## Dashboard link
https://teikoteknical.streamlit.app/