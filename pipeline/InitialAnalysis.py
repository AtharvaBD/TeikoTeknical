#import
import sqlite3
import pandas as pd

#Paths
db_path = "cell_count.db"

def cell_population_frequencies(conn):
    """Part 2: relative frequency of each cell population in each sample.
 
    Returns one row per (sample, population) with columns:
        sample, total_count, population, count, percentage
    """
    query = """
        SELECT
            sample_id AS sample,
            SUM(count) OVER (PARTITION BY sample_id) AS total_count,
            population,
            count,
            ROUND(100.0 * count / SUM(count) OVER (PARTITION BY sample_id), 4)
                AS percentage
        FROM cell_counts
        ORDER BY sample_id, population;
    """
    return pd.read_sql_query(query, conn)
 
 
if __name__ == "__main__":
    conn = sqlite3.connect(db_path)
    freq = cell_population_frequencies(conn)
    print(freq.head(10))
    print(f"\nTotal rows: {len(freq)}")
    conn.close()