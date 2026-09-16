#imports
import sqlite3
import pandas as pd
import pathlib

#Database
db_path = "cell_count.db"
csv_path = "cell-count.csv"

#Define Schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id   TEXT PRIMARY KEY,
    project      TEXT NOT NULL,
    condition    TEXT NOT NULL,
    age          INTEGER NOT NULL,
    sex          TEXT NOT NULL CHECK (sex IN ('M','F')),
    treatment    TEXT NOT NULL,
    response     TEXT CHECK (response IN ('yes','no'))
);

CREATE TABLE IF NOT EXISTS samples (
    sample_id                  TEXT PRIMARY KEY,
    subject_id                 TEXT NOT NULL REFERENCES subjects(subject_id),
    sample_type                TEXT NOT NULL CHECK (sample_type IN ('PBMC','WB')),
    time_from_treatment_start  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cell_counts (
    sample_id   TEXT NOT NULL REFERENCES samples(sample_id),
    population  TEXT NOT NULL CHECK (population IN
                    ('b_cell','cd8_t_cell','cd4_t_cell','nk_cell','monocyte')),
    count       INTEGER NOT NULL,
    PRIMARY KEY (sample_id, population)
);
"""

POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def main():
    # start fresh each run so `make pipeline` is idempotent
    pathlib.Path(db_path).unlink(missing_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)

    df = pd.read_csv(csv_path)

    # --- subjects: one row per unique subject ---
    subjects = (
        df[["subject", "project", "condition", "age", "sex", "treatment", "response"]]
        .drop_duplicates(subset="subject")
        .rename(columns={"subject": "subject_id"})
    )
    subjects.to_sql("subjects", conn, if_exists="append", index=False)

    # --- samples: one row per sample ---
    samples = df[["sample", "subject", "sample_type", "time_from_treatment_start"]].rename(
        columns={"sample": "sample_id", "subject": "subject_id"}
    )
    samples.to_sql("samples", conn, if_exists="append", index=False)

    # --- cell_counts: melt wide -> long
    cell_counts = df.melt(
        id_vars=["sample"],
        value_vars=POPULATIONS,
        var_name="population",
        value_name="count",
    ).rename(columns={"sample": "sample_id"})
    cell_counts.to_sql("cell_counts", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"Loaded {len(subjects)} subjects, {len(samples)} samples, "
          f"{len(cell_counts)} cell_count rows into {db_path}")


if __name__ == "__main__":
    main()