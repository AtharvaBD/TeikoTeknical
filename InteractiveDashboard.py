#imports
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml

from StatistialAnalysis import (
    cell_population_frequencies,
    responder_frequencies,
    responder_significance,
)

from DataSubsetAnalysis import (
    baseline_breakdown,
    baseline_melanoma_miraclib_pbmc,
)

#Paths
with open("config.yml") as f:
    config = yaml.safe_load(f)

DB_path = config["DB"]

#initilize page
st.set_page_config(page_title="Loblaw Bio - Cell Population Dashboard", layout="wide")

conn = sqlite3.connect(DB_path)
st.title("Immune Cell Population Dashboard")
st.caption("Miraclib clinical trial — melanoma responder analysis")

tab2, tab3, tab4 = st.tabs(
    ["Part 2 — Initial Analysis", "Part 3 — Statistical Analysis", "Part 4 — Data Subset Analysis"]
)

# Intial analysis
with tab2:
    st.header("Cell population frequency per sample")
 
    freq = cell_population_frequencies(conn)
 
    samples = sorted(freq["sample"].unique())
    selected_samples = st.multiselect(
        "Filter by sample (leave empty to show all)", samples, default=[]
    )
    view = freq[freq["sample"].isin(selected_samples)] if selected_samples else freq
 
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.caption(f"{len(view)} rows")
 
    if selected_samples:
        fig = px.bar(
            view,
            x="population",
            y="percentage",
            color="sample",
            barmode="group",
            title="Relative frequency by population",
        )
        st.plotly_chart(fig, use_container_width=True)

# Statistical Analysis
with tab3:
    st.header("Responders vs non-responders")
    st.caption("Melanoma · PBMC samples · miraclib treatment")
 
    resp_freq = responder_frequencies(conn)
 
    fig = px.box(
        resp_freq,
        x="population",
        y="percentage",
        color="response",
        points="all",
        category_orders={"response": ["no", "yes"]},
        labels={"percentage": "% of total cells", "response": "Response"},
        title="Cell population frequency: responders vs non-responders",
    )
    st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Significance testing (Welch's t-test, FDR-corrected)")
    significance = responder_significance(resp_freq)
 
    def highlight_significant(row):
        color = "background-color: #d4f7d4" if row["significant"] else ""
        return [color] * len(row)
 
    st.dataframe(
        significance.style.apply(highlight_significant, axis=1),
        use_container_width=True,
        hide_index=True,
    )
 
    sig_pops = significance[significance["significant"]]["population"].tolist()
    if sig_pops:
        st.success(f"Significant populations (FDR < 0.05): {', '.join(sig_pops)}")
    else:
        st.info("No populations reached significance after FDR correction.")

# Data Subset Analysis
with tab4:
    st.header("Baseline subset analysis")
    st.caption("Melanoma · PBMC · miraclib · time_from_treatment_start = 0")
 
    baseline = baseline_melanoma_miraclib_pbmc(conn)
    st.metric("Baseline samples", len(baseline))
 
    breakdown = baseline_breakdown(conn)
 
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Samples per project")
        st.dataframe(breakdown["by_project"], use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Subjects by response")
        st.dataframe(breakdown["by_response"], use_container_width=True, hide_index=True)
    with col3:
        st.subheader("Subjects by sex")
        st.dataframe(breakdown["by_sex"], use_container_width=True, hide_index=True)
 
