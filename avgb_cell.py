import sqlite3

db_path = "cell_count.db"

QUERY = """
    SELECT
        ROUND(AVG(cc.count), 2) AS avg_b_cells
    FROM cell_counts cc
    JOIN samples s ON cc.sample_id = s.sample_id
    JOIN subjects sub ON s.subject_id = sub.subject_id
    WHERE sub.condition = 'melanoma'
      AND sub.sex = 'M'
      AND sub.response = 'yes'
      AND s.time_from_treatment_start = 0
      AND cc.population = 'b_cell';
"""

if __name__ == "__main__":
    conn = sqlite3.connect(db_path)
    result = conn.execute(QUERY).fetchone()[0]
    conn.close()

    print(f"Average B cell count (melanoma, male, responders, t=0): {result:.2f}")