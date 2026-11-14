"""Peak Season Capacity Planner: Streamlit dashboard.

Run from the project folder with:  python -m streamlit run app.py

Reads the forecast saved by run_forecast.py and lets you
change the planning assumptions to see how headcount and shortfalls respond.
Operations data is synthetic (see README).
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src.capacity import headcount_needed

DB_PATH = Path(__file__).resolve().parent / "data" / "processed" / "forecaster.db"

st.set_page_config(page_title="Peak Season Capacity Planner", layout="wide")


@st.cache_data
def load_data():
    """Return the saved forecast table and the median historical UPH."""
    with sqlite3.connect(DB_PATH) as conn:
        forecast = pd.read_sql(
            "select * from forecast_peak_2025", conn, parse_dates=["date"]
        )
        uph = pd.read_sql("select uph from ops_synthetic", conn)["uph"]
    return forecast.set_index("date"), float(uph.median())


# ---------- Load data, with friendly errors ----------
if not DB_PATH.exists():
    st.error(
        "Database not found. Run 'python run_ingestion.py' first, "
        "then 'python run_forecast.py'."
    )
    st.stop()

try:
    forecast, default_uph = load_data()
except Exception:
    st.error(
        "The forecast table is missing. Run 'python run_forecast.py' to create it."
    )
    st.stop()

# ---------- Sidebar: planning assumptions ----------
st.sidebar.header("Planning assumptions")
buffer_pct = st.sidebar.slider("Forecast buffer (%)", 0, 30, 7)
absence_pct = st.sidebar.slider("Absence rate (%)", 0, 25, 10)
hours = st.sidebar.slider("Productive hours per associate", 6.0, 10.0, 8.0, 0.5)
target_uph = st.sidebar.number_input(
    "Target units per hour", min_value=50.0, max_value=150.0,
    value=round(default_uph, 1), step=1.0,
)

# ---------- Calculations ----------
df = forecast.copy()
df["planned_headcount"] = headcount_needed(
    df["forecast_parcels"] * (1 + buffer_pct / 100), target_uph, hours, absence_pct / 100
)
df["needed_headcount"] = headcount_needed(
    df["actual_parcels"], target_uph, hours, absence_pct / 100
)
df["gap"] = df["planned_headcount"] - df["needed_headcount"]

short = df["gap"] < 0
over = df.loc[~short, "gap"]

# ---------- Page ----------
st.title("Peak Season Capacity Planner")
st.caption(
    "Forecast parcels are converted to labour hours and then headcount. "
    "Operations data is synthetic; weather and bank holidays are real public data."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Days short-staffed", f"{int(short.sum())} of {len(df)}")
c2.metric("Worst shortfall", f"{int(abs(df['gap'].min())) if short.any() else 0} associates")
c3.metric("Avg over-plan (other days)", f"{over.mean():.1f}" if len(over) else "0.0")
c4.metric("Peak planned headcount", f"{int(df['planned_headcount'].max())}")

st.subheader("Parcels: forecast vs actual")
st.line_chart(
    df[["actual_parcels", "forecast_parcels"]].rename(
        columns={"actual_parcels": "Actual", "forecast_parcels": "Forecast"}
    )
)

st.subheader("Associates: planned vs needed")
st.line_chart(
    df[["needed_headcount", "planned_headcount"]].rename(
        columns={"needed_headcount": "Actually needed", "planned_headcount": "Planned from forecast"}
    )
)

with st.expander("Show daily data"):
    st.dataframe(
        df[["actual_parcels", "forecast_parcels", "planned_headcount", "needed_headcount", "gap"]].round(0)
    )
