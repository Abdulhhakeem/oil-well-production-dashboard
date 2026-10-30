"""
PETROVISION – Oilfield Production Intelligence Dashboard
Executive dashboard for oil & gas production monitoring.

Uses Python, Pandas, Streamlit and Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sys
sys.path.append("src")
from loader import load_data

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PETROVISION",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "data/Volve production data.xlsx"
SHEET_NAME = "Monthly Production Data"

# Anomaly threshold: flag months where production changes by more than this %.
ANOMALY_THRESHOLD_PCT = 25.0

# Helper to replace positive and negative infinity with NaN
def inf_to_nan(series):
    return series.replace(float("inf"), float("nan")).replace(float("-inf"), float("nan"))


# ──────────────────────────────────────────────────────────────
# Load data (cached)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_cached_data():
    """Load and clean the production dataset."""
    df = load_data(DATA_PATH, SHEET_NAME)
    # Build a proper date column for time-series work
    df = df[df["Wellbore name"].notna()].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df = df.dropna(subset=["Year", "Month"]).copy()
    df["Date"] = pd.to_datetime(
        {"year": df["Year"].astype(int), "month": df["Month"].astype(int), "day": 1}
    )
    # Sort wells alphabetically for consistent UI
    df["Wellbore name"] = df["Wellbore name"].astype(str)
    return df


# ──────────────────────────────────────────────────────────────
# Title
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style='margin-bottom: 0.25rem;'>
        🛢️ PETROVISION — Oilfield Production Intelligence Dashboard
    </h1>
    <p style='color: #666; font-size: 0.9rem; margin-top: 0;'>
        Volve Field • Monthly Production Data
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ──────────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────────
df = load_cached_data()

# Ensure numeric columns are clean
for col in ["Oil", "Gas", "Water"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# ──────────────────────────────────────────────────────────────
# Sidebar controls
# ──────────────────────────────────────────────────────────────
st.sidebar.header("PETROVISION Filter")

well_names = sorted(df["Wellbore name"].unique())
selected_wells = st.sidebar.multiselect(
    "📋 Well(s)",
    options=well_names,
    default=well_names,
    help="Select one or more wells to include in the analysis.",
)

# Date range filter
min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input(
    "📅 Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Apply filters
filtered = df[df["Wellbore name"].isin(selected_wells)].copy()
if len(date_range) == 2:
    filtered = filtered[(filtered["Date"] >= pd.Timestamp(date_range[0])) &
                        (filtered["Date"] <= pd.Timestamp(date_range[1]))]

st.sidebar.markdown("---")
st.sidebar.info(
    "Calculations:\n"
    "- **Oil/Gas/Water** — total cumulative produced volume in Sm³.\n"
    "- **Anomaly** — monthly change exceeding ±25% (flagged for review only, no root-cause assumed)."
)


# ──────────────────────────────────────────────────────────────
# 1. Executive Summary — KPI Cards
# ──────────────────────────────────────────────────────────────
st.subheader("Executive Summary")

total_oil = filtered["Oil"].sum()
total_gas = filtered["Gas"].sum()
total_water = filtered["Water"].sum()

# Active wells count
active_wells = filtered["Wellbore name"].nunique()

cols = st.columns(4)
with cols[0]:
    st.metric(
        label="💧 Total Oil Produced",
        value=f"{total_oil:,.0f} Sm³",
        help="Cumulative oil produced across all selected wells in the chosen period.",
    )
with cols[1]:
    st.metric(
        label="🔥 Total Gas Produced",
        value=f"{total_gas:,.0f} Sm³",
        help="Cumulative gas produced across all selected wells in the chosen period.",
    )
with cols[2]:
    st.metric(
        label="🌊 Total Water Produced",
        value=f"{total_water:,.0f} Sm³",
        help="Cumulative water cut produced across all selected wells in the chosen period.",
    )
with cols[3]:
    st.metric(
        label="📈 Active Wells",
        value=active_wells,
        help="Number of distinct wells with production records in the selected period.",
    )

# Water-to-Oil ratio (WOR) — a meaningful ratio in oil production
if total_oil > 0:
    wor = total_water / total_oil
else:
    wor = 0.0
st.metric(
    label="⚖️ Water-to-Oil Ratio (WOR)",
    value=f"{wor:.2f}",
    help="Total water produced divided by total oil produced — higher values indicate increasing water cut.",
)


# ──────────────────────────────────────────────────────────────
# 2. Production Trends Over Time
# ──────────────────────────────────────────────────────────────
st.subheader("Production Trends Over Time")

metric_choice = st.radio(
    "Select metric to chart:",
    options=["Oil", "Gas", "Water"],
    horizontal=True,
    help="Switch between liquid and gas production trends over time.",
    index=0,
    key="trend_metric",
)

# Aggregate monthly across selected wells
monthly = (
    filtered.groupby("Date")[metric_choice]
    .sum()
    .resample("MS")
    .sum()
    .reset_index()
)

fig_trend = go.Figure()
fig_trend.add_trace(
    go.Scatter(
        x=monthly["Date"],
        y=monthly[metric_choice],
        mode="lines+markers",
        line=dict(width=2),
        name=metric_choice,
    )
)
fig_trend.update_layout(
    title=f"Monthly {metric_choice} Production Trend",
    xaxis_title="Production Date",
    yaxis_title=f"{metric_choice} Produced (Sm³)",
    template="plotly_white",
    height=450,
    hovermode="x unified",
)
st.plotly_chart(fig_trend, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 3. Well Surveillance — Production Comparison
# ──────────────────────────────────────────────────────────────
st.subheader("Well Surveillance — Production Comparison")

surveillance_metric = st.radio(
    "Comparison metric:",
    options=["Oil", "Gas", "Water"],
    horizontal=True,
    key="surveillance_metric",
)

# Aggregate per well
well_metrics = filtered.groupby("Wellbore name")[surveillance_metric].sum().sort_values(ascending=False)

fig_wells = go.Figure()
fig_wells.add_trace(
    go.Bar(
        x=well_metrics.values,
        y=well_metrics.index,
        orientation="h",
        marker_color="#2f769b",
    )
)
fig_wells.update_layout(
    title=f"{surveillance_metric} Production by Well",
    xaxis_title=f"Total {surveillance_metric} (Sm³)",
    yaxis_title="Wellbore Name",
    template="plotly_white",
    height=500,
)
st.plotly_chart(fig_wells, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 4. Anomaly Flagging
# ──────────────────────────────────────────────────────────────
st.subheader("Anomaly Flagging")

anomaly_col = st.selectbox(
    "Metric to analyse for anomalies:",
    options=["Oil", "Gas", "Water"],
    index=0,
    help="Flag months where production changes by more than ±25% month-over-month.",
)

# Calculate month-over-month percentage change per well, then find anomalies
anomaly_records = []
for well, well_df in filtered.groupby("Wellbore name"):
    well_df = well_df.sort_values("Date").copy()
    well_df["pct_change"] = inf_to_nan(well_df[anomaly_col].pct_change()) * 100
    anomalies = well_df[
        (well_df["pct_change"].abs() > ANOMALY_THRESHOLD_PCT) &
        (well_df["pct_change"].notna())
    ]
    for _, row in anomalies.iterrows():
        anomaly_records.append({
            "Well": well,
            "Date": row["Date"].strftime("%Y-%m"),
            "Value": row[anomaly_col],
            "Previous Value": well_df.loc[row.name, anomaly_col],
            "Change (%)": round(row["pct_change"], 1),
        })

if anomaly_records:
    anomaly_df = pd.DataFrame(anomaly_records).sort_values("Change (%)", key=lambda x: x.abs(), ascending=False)
    st.caption(f"Flagged {len(anomaly_df)} anomaly records (change > ±{ANOMALY_THRESHOLD_PCT}%, for review only — no operational cause assumed).")
    st.dataframe(anomaly_df, use_container_width=True, height=300)
else:
    st.info("No anomalies detected in the selected period. Lower the threshold or broaden the date range to see more.")


# ─────────────────────────────────────────────────────────────────────────
# 5. Downloadable Production Summary Report
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Downloadable Production Summary Report")

# Build the summary report
summary_rows = []
for well in sorted(filtered["Wellbore name"].unique()):
    well_data = filtered[filtered["Wellbore name"] == well]
    summary_rows.append({
        "Wellbore Name": well,
        "Total Oil (Sm³)": well_data["Oil"].sum(),
        "Total Gas (Sm³)": well_data["Gas"].sum(),
        "Total Water (Sm³)": well_data["Water"].sum(),
        "First Production": well_data["Date"].min().strftime("%Y-%m") if not well_data.empty else "",
        "Last Production": well_data["Date"].max().strftime("%Y-%m") if not well_data.empty else "",
        "Months On Stream": well_data["Date"].nunique(),
    })

summary_report = pd.DataFrame(summary_rows)

st.dataframe(summary_report, use_container_width=True)

csv = summary_report.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Summary Report (CSV)",
    data=csv,
    file_name="petrovision_production_summary.csv",
    mime="text/csv",
    key="download-csv",
)

st.divider()
st.caption(
    "PETROVISION — Oilfield Production Intelligence Dashboard. "
    "Data source: Volve Field monthly production dataset. "
    "Calculations shown here are indicative and should be validated before operational decisions."
)
