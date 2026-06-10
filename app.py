import pandas as pd

import streamlit as st

import sqlite3

st.set_page_config(
    page_title="Religious Monitoring",
    layout="wide"
)

st.title(
    "Religious Intolerance Monitoring"
)

conn = sqlite3.connect(
    "monitoring.db"
)

df = pd.read_sql(
    "SELECT * FROM noticias",
    conn
)

conn.close()

# ==================
# METRICS
# ==================

total = len(df)

positivos = len(
    df[df["classe"] == 1]
)

negativos = len(
    df[df["classe"] == 0]
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total",
    total
)

c2.metric(
    "Intolerance",
    positivos
)

c3.metric(
    "No Intolerance",
    negativos
)

st.divider()

# ==================
# FILTER
# ==================

classe = st.selectbox(
    "Filter",
    [
        "All",
        "Intolerance",
        "No Intolerance"
    ]
)

if classe == "Intolerance":

    df = df[
        df["classe"] == 1
    ]

elif classe == "No Intolerance":

    df = df[
        df["classe"] == 0
    ]

# ==================
# TABLE
# ==================

st.dataframe(
    df,
    use_container_width=True
)