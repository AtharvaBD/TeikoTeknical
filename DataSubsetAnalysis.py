#imports
import sqlite3
import pandas as pd
import yaml
 
with open("config.yml") as f:
    config = yaml.safe_load(f)
 
#Paths
DB_path = config["DB"]

def baseline_melanoma_miraclib_pbmc(conn):
    """All melanoma + PBMC + time_from_treatment_start = 0 samples from subjects treated with miraclib.
    Returns: sample, subject, project, response, sex
    """
    query = """
        SELECT
            s.sample_id AS sample,
            s.subject_id AS subject,
            sub.project,
            sub.response,
            sub.sex
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND s.time_from_treatment_start = 0;
    """
    return pd.read_sql_query(query, conn)

def baseline_breakdown(conn):
    """Breakdown of the baseline melanoma/PBMC/miraclib sample set by:
        - samples per project
        - subjects by responder/non-responder
        - subjects by sex
    Returns a dict of DataFrames: {"by_project", "by_response", "by_sex"}
    """
    df = baseline_melanoma_miraclib_pbmc(conn)
 
    by_project = (
        df.groupby("project")["sample"]
        .count()
        .reset_index()
        .rename(columns={"sample": "n_samples"})
    )
 
    subjects = df.drop_duplicates(subset="subject")
 
    by_response = (
        subjects.groupby("response")["subject"]
        .count()
        .reset_index()
        .rename(columns={"subject": "n_subjects"})
    )
 
    by_sex = (
        subjects.groupby("sex")["subject"]
        .count()
        .reset_index()
        .rename(columns={"subject": "n_subjects"})
    )
 
    return {"by_project": by_project, "by_response": by_response, "by_sex": by_sex}

if __name__ == "__main__":
    conn = sqlite3.connect(DB_path)
 
    baseline = baseline_melanoma_miraclib_pbmc(conn)
    print(f"Baseline melanoma/PBMC/miraclib samples: {len(baseline)}")
 
    breakdown = baseline_breakdown(conn)
    print("\nSamples per project:")
    print(breakdown["by_project"].to_string(index=False))
    print("\nSubjects by response:")
    print(breakdown["by_response"].to_string(index=False))
    print("\nSubjects by sex:")
    print(breakdown["by_sex"].to_string(index=False))
  
    conn.close()