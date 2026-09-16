#imports
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

#Paths
db_path = "cell_count.db"


def cell_population_frequencies(conn):
    """relative frequency of each cell population in each sample and population. with columns:
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


def responder_frequencies(conn):
    """relative frequencies for melanoma PBMC miraclib samples,
    labeled by responder/non-responder in each sample and population with columns:
        sample, population, percentage, response
    """

    #Get the frequencies
    freq = cell_population_frequencies(conn)

    #Perform the query for melanoma + miraclib + PBMC, removing null responses
    meta_query = """
        SELECT
            s.sample_id AS sample,
            sub.response
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND sub.response IS NOT NULL;
    """
    meta = pd.read_sql_query(meta_query, conn)

    # Merge the response and frequency data of each population /
    merged = freq.merge(meta, on="sample", how="inner")
    return merged[["sample", "population", "percentage", "response"]]


def plot_responder_boxplots(df, out_path = "Boxplots.png"):

    # One boxplot per population, responders vs non-responders.
    populations = sorted(df["population"].unique())
    fig, axes = plt.subplots(1, len(populations), figsize=(4 * len(populations), 5), sharey=False)

    for ax, pop in zip(axes, populations):
        sub = df[df["population"] == pop]
        data = [sub[sub["response"] == "no"]["percentage"], sub[sub["response"] == "yes"]["percentage"]]
        ax.boxplot(data, tick_labels=["non-responder", "responder"])
        ax.set_title(pop)
        ax.set_ylabel("% of total cells")

    fig.suptitle("Cell population frequency: responders vs non-responders\n(melanoma, PBMC, miraclib)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def responder_significance(df):
    """Perform a T-test per population, responder vs non-responder. 
        Returns one row per population with columns:
        population, n_responder, n_non_responder, mean_responder,
        mean_non_responder, t_statistic, p_value
    """
 
    rows = []
    for pop in sorted(df["population"].unique()):
        sub = df[df["population"] == pop]
        resp = sub[sub["response"] == "yes"]["percentage"]
        non_resp = sub[sub["response"] == "no"]["percentage"]
 
        # Welch's t-test: doesn't assume equal variance between groups
        stat, p = ttest_ind(resp, non_resp, equal_var=False)
 
        rows.append({
            "population": pop,
            "n_responder": len(resp),
            "n_non_responder": len(non_resp),
            "mean_responder": round(resp.mean(), 4),
            "mean_non_responder": round(non_resp.mean(), 4),
            "t_statistic": round(stat, 4),
            "p_value": p,
        })
 
    result = pd.DataFrame(rows)
    result["p_value_adj"] = multipletests(result["p_value"], method="fdr_bh")[1]
    result["significant"] = result["p_value_adj"] < 0.05
    return result.sort_values("p_value_adj")
 
 
if __name__ == "__main__":
    conn = sqlite3.connect(db_path)

    #Overall frequency table
    freq = cell_population_frequencies(conn)
    print(freq.head(10))
    print(f"\nTotal rows: {len(freq)}")

    #responder vs non-responder analysis (melanoma, PBMC, miraclib)
    resp_freq = responder_frequencies(conn)
    print(f"\nResponder/non-responder rows: {len(resp_freq)}")

    boxplot_path = plot_responder_boxplots(resp_freq)
    print(f"\nBoxplots saved to: {boxplot_path}")

    significance = responder_significance(resp_freq)
    print("\nSignificance testing (responder vs non-responder):")
    print(significance.to_string(index=False))

    conn.close()