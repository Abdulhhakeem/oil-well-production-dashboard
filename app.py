"""
PETROVISION – Oilfield Production Intelligence Dashboard
Executive dashboard for oil & gas production monitoring.

Uses Python, Pandas, Streamlit and Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Liquid-glass premium theme — petroleum analytics
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0b1120 0%, #0f172a 45%, #111827 100%);
    background-attachment: fixed;
    color: #e8edf5;
}
[data-testid="stSidebar"] {
    background: rgba(11,17,32,0.92) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.06);
}
.stSubheader, .stMarkdown h2 {
    color: #fdf6e3;
    font-weight: 700;
    letter-spacing: 0.06em;
    border-left: 3.5px solid #f59e0b;
    padding-left: 0.9rem;
    padding-bottom: 0.35rem;
    margin-top: 2.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
[data-testid="metric-container"] {
    background: rgba(17,24,39,0.65) !important;
    backdrop-filter: blur(12px) saturate(120%);
    -webkit-backdrop-filter: blur(12px) saturate(120%);
    border: 1px solid rgba(13,148,136,0.25);
    border-top: 2.5px solid #f59e0b;
    border-radius: 1rem;
    padding: 1.1rem 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: transform .15s ease, box-shadow .15s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(245,158,11,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
}
[data-testid="metric-container"] > label { color: #94a3b8; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; }
[data-testid="metric-container"] > [data-testid="stMetricValue"] { color: #fdf6e3; font-weight: 800; font-size: 1.45rem; letter-spacing: -0.01em; }
[data-testid="stDataFrame"] thead th { background-color: #0f172a !important; color: #fdf6e3 !important; font-weight: 600; letter-spacing: 0.03em; border-bottom: 2px solid rgba(245,158,11,0.3) !important; }
[data-testid="stDataFrame"] tbody td { background-color: rgba(15,23,42,0.5) !important; color: #e8edf5 !important; border-bottom: 1px solid rgba(255,255,255,0.06) !important; }
.stCaption, .stMarkdown p { color: #94a3b8 !important; font-size: 0.82rem; }
.stSelectbox label, .stMultiselect label, .stRadio label { color: #fdf6e3 !important; font-weight: 500; }
/* Glass filter/sidebar cards */
.stSelectbox, .stMultiselect, .stRadio > div { background: rgba(17,24,39,0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.6rem; padding: 0.35rem 0.5rem; }
</style>
""", unsafe_allow_html=True)

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
# Petroleum imagery header
st.markdown("""
<div style="position:relative; border-radius:1rem; overflow:hidden; margin-bottom:1.25rem; box-shadow:0 10px 40px rgba(0,0,0,0.6);">
  <img src="https://images.unsplash.com/photo-1518770660439-4636500cff5f?w=1200&q=80&auto=format" style="width:100%; height:220px; object-fit:cover; filter:brightness(0.55) contrast(1.1);" alt="Offshore oil platform"/>
  <div style="position:absolute; inset:0; background:linear-gradient(90deg, rgba(11,17,32,0.85) 0%, rgba(11,17,32,0.4) 60%, rgba(11,17,32,0.75) 100%); display:flex; align-items:center; padding:0 2.5rem;">
    <div>
      <h2 style="margin:0; color:#fdf6e3; font-size:1.6rem; letter-spacing:0.06em; font-weight:700;">PETROVISION</h2>
      <p style="margin:0.2rem 0 0; color:#94a3b8; font-size:0.9rem;">Oilfield Production Intelligence &bull; Volve Field</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

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

# KPI row: 4 core production metrics — aligned card grid with consistent spacing
total_oil = filtered["Oil"].sum()
total_gas = filtered["Gas"].sum()
total_water = filtered["Water"].sum()
active_wells = filtered["Wellbore name"].nunique()
if total_oil > 0:
    wor = total_water / total_oil
else:
    wor = 0.0

cols = st.columns(4)
with cols[0]:
    st.metric("Total Oil Produced", f"{total_oil:,.0f} Sm³")
with cols[1]:
    st.metric("Total Gas Produced", f"{total_gas:,.0f} Sm³")
with cols[2]:
    st.metric("Total Water Produced", f"{total_water:,.0f} Sm³")
with cols[3]:
    st.metric("Active Wells", f"{active_wells}")

# Secondary indicator — WOR, consistent typography, restrained visual hierarchy
st.markdown("**Water-to-Oil Ratio**")
st.metric("WOR (Water / Oil)", f"{wor:.2f}", help="Higher values indicate increasing water cut.")


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
        line=dict(width=2.5, color="#f59e0b"),
        name=metric_choice,
    )
)
fig_trend.update_layout(
    title=f"Monthly {metric_choice} Production Trend",
    xaxis_title="Production Date",
    yaxis_title=f"{metric_choice} Produced (Sm³)",
    template="plotly_dark",
    height=450,
    hovermode="x unified",
)
st.plotly_chart(fig_trend, width="stretch")


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
        marker_color="#f59e0b",
    )
)
fig_wells.update_layout(
    title=f"{surveillance_metric} Production by Well",
    xaxis_title=f"Total {surveillance_metric} (Sm³)",
    yaxis_title="Wellbore Name",
    template="plotly_dark",
    height=500,
)
st.plotly_chart(fig_wells, width="stretch")


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
    st.dataframe(anomaly_df.style.format({
        "Value": "{:,.0f}",
        "Previous Value": "{:,.0f}",
        "Change (%)": "{:.1f}",
    }), width="stretch", height=300)
else:
    st.info("No anomalies detected in the selected period. Lower the threshold or broaden the date range to see more.")


# ─────────────────────────────────────────────────────────────────────────
# 6. Water Cut Analysis (Phase 2 — Feature 1)
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Water Cut Analysis")

# Filter valid observations (both Oil and Water present; not missing values)
valid_water = filtered[
    filtered["Oil"].notna() & filtered["Water"].notna() &
    (filtered["Oil"] + filtered["Water"] > 0)  # non-zero denominator
].copy()
valid_water["Water_Cut_pct"] = (valid_water["Water"] / (valid_water["Oil"] + valid_water["Water"])) * 100

# 6.1 KPI — Aggregate Water Cut for filtered dataset
aggregate_oil = valid_water["Oil"].sum()
aggregate_water = valid_water["Water"].sum()
if (aggregate_oil + aggregate_water) > 0:
    aggregate_wc = (aggregate_water / (aggregate_oil + aggregate_water)) * 100
else:
    aggregate_wc = float("nan")

kpi_cols = st.columns(3)
with kpi_cols[0]:
    st.metric(
        label="💧 Aggregate Water Cut",
        value=f"{aggregate_wc:.1f}%" if not (aggregate_wc != aggregate_wc) else "N/A",
        help="Water / (Oil + Water) × 100 across all valid observations in the selected filters.",
    )
with kpi_cols[1]:
    st.metric(
        label="📊 Valid Observations",
        value=str(len(valid_water)),
        help="Records with non-missing Oil and Water and non-zero denominator.",
    )
with kpi_cols[2]:
    # Average water cut across observations (not weighted by volume)
    avg_wc = valid_water["Water_Cut_pct"].mean() if len(valid_water) > 0 else float("nan")
    st.metric(
        label="📈 Average Water Cut",
        value=f"{avg_wc:.1f}%" if not (avg_wc != avg_wc) else "N/A",
        help="Simple arithmetic mean of monthly water-cut percentages.",
    )

st.caption("Flagged changes require review and do not establish an operational cause.")

# 6.2 Water Cut Trend Over Time — by well selection
st.markdown("**Water Cut Trend Over Time**")
trend_col = st.selectbox(
    "Well for trend (select one or view all):",
    options=["All Selected Wells"] + sorted(valid_water["Wellbore name"].unique()) if not valid_water.empty else ["No data"],
    index=0,
    key="wc_trend_well",
)

trend_df = valid_water.copy()
if trend_col != "All Selected Wells" and not valid_water.empty:
    trend_df = valid_water[valid_water["Wellbore name"] == trend_col]

trend_df = trend_df.sort_values("Date")

if not trend_df.empty:
    fig_wc = go.Figure()
    if trend_col == "All Selected Wells":
        for well in sorted(trend_df["Wellbore name"].unique()):
            well_trend = trend_df[trend_df["Wellbore name"] == well].sort_values("Date")
            fig_wc.add_trace(go.Scatter(
                x=well_trend["Date"], y=well_trend["Water_Cut_pct"],
                mode="lines+markers", name=well,
                line=dict(width=1.5),
            ))
    else:
        fig_wc.add_trace(go.Scatter(
            x=trend_df["Date"], y=trend_df["Water_Cut_pct"],
            mode="lines+markers", name=trend_col,
            line=dict(width=2, color="#2f769b"),
        ))
    fig_wc.update_layout(
        title="Monthly Water Cut (%)",
        xaxis_title="Production Date",
        yaxis_title="Water Cut (%)",
        yaxis=dict(range=[0, max(100, trend_df["Water_Cut_pct"].max() * 1.1 if not trend_df.empty else 100)]),
        template="plotly_dark",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_wc, width="stretch")
else:
    st.info("No valid water-cut observations for the selected filters.")

# 6.3 Well Comparison Chart — Water Cut by Well
st.markdown("**Well Comparison — Average Water Cut**")
if not valid_water.empty:
    well_wc = valid_water.groupby("Wellbore name")["Water_Cut_pct"].mean().sort_values(ascending=False)
    fig_wc_bar = go.Figure()
    fig_wc_bar.add_trace(go.Bar(
        x=well_wc.values,
        y=well_wc.index,
        orientation="h",
        marker_color="#0d9488",
    ))
    fig_wc_bar.update_layout(
        title="Average Water Cut by Well (%)",
        xaxis_title="Average Water Cut (%)",
        yaxis_title="Wellbore Name",
        template="plotly_dark",
        height=400,
    )
    st.plotly_chart(fig_wc_bar, width="stretch")
else:
    st.info("No data available for well comparison.")

# 6.4 Well Summary Table — sortable
st.markdown("**Well Summary — Water Cut**")
if not valid_water.empty:
    wc_summary = valid_water.groupby("Wellbore name").agg(
        Average_Water_Cut_pct=("Water_Cut_pct", "mean"),
        Valid_Observations=("Water_Cut_pct", "count"),
    ).round(2).reset_index()
    wc_summary = wc_summary.sort_values("Average_Water_Cut_pct", ascending=False)
    wc_summary.columns = ["Wellbore Name", "Average Water Cut (%)", "Valid Observations"]
    st.dataframe(wc_summary.style.format({
        "Average Water Cut (%)": "{:,.2f}",
    }), width="stretch", height=300)
else:
    st.info("No valid observations for water-cut summary.")


# ─────────────────────────────────────────────────────────────────────────
# 7. Gas-Oil Ratio (GOR) Analysis (Phase 2 — Feature 2)
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Gas-Oil Ratio (GOR) Analysis")

# Filter valid observations (both Gas and Oil present, Oil > 0 to avoid division by zero)
valid_gor = filtered[
    filtered["Gas"].notna() & filtered["Oil"].notna() & (filtered["Oil"] > 0)
].copy()
valid_gor["GOR"] = valid_gor["Gas"] / valid_gor["Oil"]

# 7.1 KPI — Aggregate GOR (total gas / total oil) for filtered dataset
aggregate_gas = valid_gor["Gas"].sum()
aggregate_oil_gor = valid_gor["Oil"].sum()
if aggregate_oil_gor > 0:
    aggregate_gor = aggregate_gas / aggregate_oil_gor
else:
    aggregate_gor = float("nan")

kpi_cols = st.columns(3)
with kpi_cols[0]:
    st.metric(
        label="⚡ Aggregate GOR (Total Gas / Total Oil)",
        value=f"{aggregate_gor:.2f}" if not (aggregate_gor != aggregate_gor) else "N/A",
        help="Total Gas / Total Oil in Sm³/Sm³ for valid observations in selected filters.",
    )
with kpi_cols[1]:
    st.metric(
        label="📊 Valid GOR Observations",
        value=str(len(valid_gor)),
        help="Records with non-missing Gas and Oil and Oil > 0.",
    )
with kpi_cols[2]:
    avg_gor = valid_gor["GOR"].mean() if len(valid_gor) > 0 else float("nan")
    st.metric(
        label="📈 Average Monthly GOR (Arithmetic Mean)",
        value=f"{avg_gor:.2f}" if not (avg_gor != avg_gor) else "N/A",
        help="Simple arithmetic mean of monthly GOR values (not weighted by volume).",
    )

st.caption("Flagged changes require review and do not establish an operational cause.")

# 7.2 GOR Trend Over Time
st.markdown("**GOR Trend Over Time**")
gor_trend_col = st.selectbox(
    "Well for GOR trend (select one or view all):",
    options=["All Selected Wells"] + sorted(valid_gor["Wellbore name"].unique()) if not valid_gor.empty else ["No data"],
    index=0,
    key="gor_trend_well",
)

gor_trend_df = valid_gor.copy()
if gor_trend_col != "All Selected Wells" and not valid_gor.empty:
    gor_trend_df = valid_gor[valid_gor["Wellbore name"] == gor_trend_col]

gor_trend_df = gor_trend_df.sort_values("Date")

if not gor_trend_df.empty:
    fig_gor = go.Figure()
    if gor_trend_col == "All Selected Wells":
        for well in sorted(gor_trend_df["Wellbore name"].unique()):
            well_trend = gor_trend_df[gor_trend_df["Wellbore name"] == well].sort_values("Date")
            fig_gor.add_trace(go.Scatter(
                x=well_trend["Date"], y=well_trend["GOR"],
                mode="lines+markers", name=well,
                line=dict(width=1.5),
            ))
    else:
        fig_gor.add_trace(go.Scatter(
            x=gor_trend_df["Date"], y=gor_trend_df["GOR"],
            mode="lines+markers", name=gor_trend_col,
            line=dict(width=2, color="#9e9ac8"),
        ))
    fig_gor.update_layout(
        title="Monthly Gas-Oil Ratio (Sm³/Sm³)",
        xaxis_title="Production Date",
        yaxis_title="GOR (Sm³/Sm³)",
        template="plotly_dark",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_gor, width="stretch")
else:
    st.info("No valid GOR observations for the selected filters.")

# 7.3 Well Comparison — Average GOR by Well
st.markdown("**Well Comparison — Average GOR (Sm³/Sm³)**")
if not valid_gor.empty:
    well_gor = valid_gor.groupby("Wellbore name")["GOR"].mean().sort_values(ascending=False)
    fig_gor_bar = go.Figure()
    fig_gor_bar.add_trace(go.Bar(
        x=well_gor.values,
        y=well_gor.index,
        orientation="h",
        marker_color="#f59e0b",
    ))
    fig_gor_bar.update_layout(
        title="Average GOR by Well (Sm³/Sm³)",
        xaxis_title="Average GOR (Sm³/Sm³)",
        yaxis_title="Wellbore Name",
        template="plotly_dark",
        height=400,
    )
    st.plotly_chart(fig_gor_bar, width="stretch")
else:
    st.info("No data available for GOR comparison.")

# 7.4 Well Summary Table — sortable
st.markdown("**Well Summary — GOR**")
if not valid_gor.empty:
    gor_summary = valid_gor.groupby("Wellbore name").agg(
        Average_GOR=("GOR", "mean"),
        Valid_Observations=("GOR", "count"),
    ).round(2).reset_index()
    gor_summary = gor_summary.sort_values("Average_GOR", ascending=False)
    gor_summary.columns = ["Wellbore Name", "Average GOR (Sm³/Sm³)", "Valid Observations"]
    st.dataframe(gor_summary.style.format({
        "Average GOR (Sm³/Sm³)": "{:,.2f}",
    }), width="stretch", height=300)
else:
    st.info("No valid observations for GOR summary.")


# ─────────────────────────────────────────────────────────────────────────
# 8. Well Performance Ranking (Phase 2 — Feature 3)
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Well Performance Ranking")

ranking_metric = st.selectbox(
    "Rank wells by:",
    options=["Total Oil (Sm³)", "Total Gas (Sm³)", "Total Water (Sm³)", "Average Monthly Oil (Sm³/month)"],
    index=0,
    help="Select a metric to rank selected wells. Average uses valid monthly observations only.",
)

# Build ranking table (respecting filters, using valid observations for averages)
ranking_rows = []
for well in sorted(filtered["Wellbore name"].unique()):
    well_data = filtered[filtered["Wellbore name"] == well].copy()
    ranking_rows.append({
        "Wellbore Name": well,
        "Total Oil (Sm³)": well_data["Oil"].sum(),
        "Total Gas (Sm³)": well_data["Gas"].sum(),
        "Total Water (Sm³)": well_data["Water"].sum(),
        "Average Monthly Oil (Sm³/month)": well_data["Oil"].mean() if not well_data.empty else float("nan"),
        "Valid Oil Obs": well_data["Oil"].notna().sum(),
        "Valid Gas Obs": well_data["Gas"].notna().sum(),
        "Valid Water Obs": well_data["Water"].notna().sum(),
    })

ranking_df = pd.DataFrame(ranking_rows)

# Sort by selected metric
sort_col = {
    "Total Oil (Sm³)": "Total Oil (Sm³)",
    "Total Gas (Sm³)": "Total Gas (Sm³)",
    "Total Water (Sm³)": "Total Water (Sm³)",
    "Average Monthly Oil (Sm³/month)": "Average Monthly Oil (Sm³/month)",
}[ranking_metric]
ranking_df = ranking_df.sort_values(sort_col, ascending=False).reset_index(drop=True)

# 8.1 Ranking Chart
metric_key = {
    "Total Oil (Sm³)": "Total Oil (Sm³)",
    "Total Gas (Sm³)": "Total Gas (Sm³)",
    "Total Water (Sm³)": "Total Water (Sm³)",
    "Average Monthly Oil (Sm³/month)": "Average Monthly Oil (Sm³/month)",
}[ranking_metric]

fig_rank = go.Figure()
fig_rank.add_trace(go.Bar(
    x=ranking_df[metric_key].values,
    y=ranking_df["Wellbore Name"],
    orientation="h",
    marker_color="#f59e0b",
))
fig_rank.update_layout(
    title=f"Well Performance Ranking — {ranking_metric}",
    xaxis_title=ranking_metric,
    yaxis_title="Wellbore Name",
    template="plotly_dark",
    height=max(300, 50 * len(ranking_df)),
)
st.plotly_chart(fig_rank, width="stretch")

# 8.2 Sortable Table
st.markdown("**Well Performance Table**")
st.dataframe(
    ranking_df.style.format({
        "Total Oil (Sm³)": "{:,.0f}",
        "Total Gas (Sm³)": "{:,.0f}",
        "Total Water (Sm³)": "{:,.0f}",
        "Average Monthly Oil (Sm³/month)": "{:,.2f}",
    }),
    width="stretch",
    height=300,
)

st.caption("Ranking reflects cumulative or average production only. No operational superiority is claimed from production volume alone. Missing months are not treated as zero.")


# ─────────────────────────────────────────────────────────────────────────
# 9. Individual Well Production Profiles (Phase 2 — Feature 4)
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Individual Well Production Profiles")

# Well selector — single well
well_selector = st.selectbox(
    "Select a well to profile:",
    options=sorted(filtered["Wellbore name"].unique()) if not filtered.empty else ["No data"],
    index=0,
    key="profile_well",
)

if well_selector != "No data" and not filtered.empty and well_selector in filtered["Wellbore name"].values:
    profile_df = filtered[filtered["Wellbore name"] == well_selector].copy()
    profile_df = profile_df.sort_values("Date")

    # Date range info for selected well
    first_date = profile_df["Date"].min() if not profile_df.empty else None
    last_date = profile_df["Date"].max() if not profile_df.empty else None
    available_months = profile_df["Date"].nunique() if not profile_df.empty else 0

    # 9.1 Well Statistics
    st.markdown("**Well Statistics**")
    stats_cols = st.columns(4)
    with stats_cols[0]:
        st.metric("First Production", first_date.strftime("%Y-%m") if first_date is not None else "N/A")
    with stats_cols[1]:
        st.metric("Last Production", last_date.strftime("%Y-%m") if last_date is not None else "N/A")
    with stats_cols[2]:
        st.metric("Valid Observations", f"Oil:{profile_df['Oil'].notna().sum()} | Gas:{profile_df['Gas'].notna().sum()} | Water:{profile_df['Water'].notna().sum()}")
    with stats_cols[3]:
        total_oil_p = profile_df["Oil"].sum()
        total_gas_p = profile_df["Gas"].sum()
        total_water_p = profile_df["Water"].sum()
        st.metric("Total Production", f"Oil:{total_oil_p:,.0f} | Gas:{total_gas_p:,.0f} | Water:{total_water_p:,.0f}")

    # 9.2 Production History Charts (Oil, Gas, Water)
    st.markdown("**Production History**")
    metrics = ["Oil", "Gas", "Water"]
    colors = {"Oil": "#2f769b", "Gas": "#9e9ac8", "Water": "#6baed6"}
    fig_prod = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=["Oil (Sm³)", "Gas (Sm³)", "Water (Sm³)"])
    for i, m in enumerate(metrics, 1):
        data = profile_df.sort_values("Date")
        fig_prod.add_trace(
            go.Scatter(x=data["Date"], y=data[m], mode="lines+markers", name=m, line=dict(width=2, color=colors[m]), showlegend=(i==1)),
            row=i, col=1,
        )
    fig_prod.update_layout(height=700, template="plotly_dark", hovermode="x unified", title_text=f"{well_selector} — Monthly Production")
    fig_prod.update_yaxes(title_text="Sm³")
    st.plotly_chart(fig_prod, width="stretch")

    # 9.3 Production Indicators (Water Cut, GOR)
    st.markdown("**Production Indicators**")
    profile_df["Water_Cut_pct"] = (profile_df["Water"] / (profile_df["Oil"] + profile_df["Water"])).replace([float("inf"), float("-inf")], float("nan")) * 100
    profile_df["GOR"] = profile_df.apply(lambda row: row["Gas"]/row["Oil"] if pd.notna(row["Oil"]) and row["Oil"]>0 and pd.notna(row["Gas"]) else float("nan"), axis=1)

    indicator_df = profile_df.sort_values("Date")[["Date", "Water_Cut_pct", "GOR"]].copy()
    indicator_df["Water_Cut_pct"] = indicator_df["Water_Cut_pct"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "")
    indicator_df["GOR"] = indicator_df["GOR"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    indicator_df["Date"] = indicator_df["Date"].dt.strftime("%Y-%m")

    fig_ind = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=["Water Cut (%)", "GOR (Sm³/Sm³)"])
    wc_data = profile_df.sort_values("Date")
    gor_data = profile_df.sort_values("Date")
    fig_ind.add_trace(go.Scatter(x=wc_data["Date"], y=wc_data["Water_Cut_pct"], mode="lines+markers", name="Water Cut %", line=dict(width=2, color="#2f769b")), row=1, col=1)
    fig_ind.add_trace(go.Scatter(x=gor_data["Date"], y=gor_data["GOR"], mode="lines+markers", name="GOR", line=dict(width=2, color="#6baed6")), row=2, col=1)
    fig_ind.update_layout(height=600, template="plotly_dark", hovermode="x unified", title_text=f"{well_selector} — Production Indicators")
    st.plotly_chart(fig_ind, width="stretch")

    # 9.4 Monthly Production Table
    st.markdown("**Monthly Production Table**")
    table_df = profile_df.sort_values("Date").copy()
    table_df["Water_Cut_pct"] = (table_df["Water"] / (table_df["Oil"] + table_df["Water"])).replace([float("inf"), float("-inf")], float("nan")) * 100
    table_df["GOR"] = table_df.apply(lambda row: row["Gas"]/row["Oil"] if pd.notna(row["Oil"]) and row["Oil"]>0 and pd.notna(row["Gas"]) else float("nan"), axis=1)
    display_table = table_df[["Date", "Oil", "Gas", "Water", "Water_Cut_pct", "GOR"]].copy()
    display_table["Date"] = display_table["Date"].dt.strftime("%Y-%m")
    # Format numeric columns with comma separators before converting to string
    display_table["Oil"] = display_table["Oil"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")
    display_table["Gas"] = display_table["Gas"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")
    display_table["Water"] = display_table["Water"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")
    # Convert numeric display columns to string so missing markers don't trigger TypeError
    display_table["Water_Cut_pct"] = display_table["Water_Cut_pct"].apply(lambda x: "—" if pd.isna(x) else f"{x:.1f}")
    display_table["GOR"] = display_table["GOR"].apply(lambda x: "—" if pd.isna(x) else f"{x:.2f}")
    st.dataframe(display_table, width="stretch", height=400)

    st.caption("Available observations shown; missing months are not interpolated. Zero production is shown as 0; unavailable (missing) is shown as blank. No operational cause is inferred from trends.")
else:
    st.info("Select a well from the dropdown to view its production profile.")


# ─────────────────────────────────────────────────────────────────────────
# 10. Production Decline Analysis (Phase 2 — Feature 5)
# ─────────────────────────────────────────────────────────────────────────
st.subheader("Production Decline Analysis")

# Continuity audit: find continuous sequences >= 12 months per well in filtered data
continuity_info = {}
for well in sorted(filtered["Wellbore name"].unique()) if not filtered.empty else []:
    well_df = filtered[filtered["Wellbore name"] == well].sort_values("Date").reset_index(drop=True)
    sequences = []
    if len(well_df) > 0:
        years = well_df["Date"].dt.year.values
        months = well_df["Date"].dt.month.values
        current_start_idx = 0
        for idx in range(1, len(well_df)):
            prev_date = pd.Timestamp(year=int(years[idx-1]), month=int(months[idx-1]), day=1)
            curr_date = pd.Timestamp(year=int(years[idx]), month=int(months[idx]), day=1)
            gap = (curr_date.year - prev_date.year) * 12 + (curr_date.month - prev_date.month)
            if gap > 1:
                sequences.append({
                    "start_idx": current_start_idx,
                    "end_idx": idx - 1,
                    "len": idx - current_start_idx,
                    "start": well_df.iloc[current_start_idx]["Date"],
                    "end": well_df.iloc[idx-1]["Date"],
                })
                current_start_idx = idx
        sequences.append({
            "start_idx": current_start_idx,
            "end_idx": len(well_df) - 1,
            "len": len(well_df) - current_start_idx,
            "start": well_df.iloc[current_start_idx]["Date"],
            "end": well_df.iloc[-1]["Date"],
        })
    continuity_info[well] = [s for s in sequences if s["len"] >= 12]

suitable_wells = {w: continuity_info[w] for w in continuity_info if continuity_info[w]}

if not suitable_wells:
    st.info("No continuous production sequences of 12+ months found in current filters. Decline analysis requires uninterrupted monthly records. Try broadening the date range.")
else:
    st.caption(f"Audit: {len(suitable_wells)} well(s) have continuous sequences ≥ 12 months in current filters.")
    options = []
    for w in sorted(suitable_wells):
        for s in suitable_wells[w]:
            options.append(f"{w} — {s['start'].strftime('%Y-%m')} to {s['end'].strftime('%Y-%m')} ({s['len']} months)")

    selected_option = st.selectbox("Select a continuous sequence for decline analysis:", options=options, index=0, key="decline_sequence")
    well_name = selected_option.split(" — ")[0]
    well_df = filtered[filtered["Wellbore name"] == well_name].sort_values("Date").reset_index(drop=True)

    sequence_info = None
    for s in suitable_wells[well_name]:
        if f"{s['start'].strftime('%Y-%m')} to {s['end'].strftime('%Y-%m')}" in selected_option:
            sequence_info = s
            break

    if sequence_info:
        start_idx = sequence_info["start_idx"]
        end_idx = sequence_info["end_idx"]
        seq_df = well_df.iloc[start_idx:end_idx+1].copy().reset_index(drop=True)

        st.markdown(f"**Selected: {well_name} — {sequence_info['start'].strftime('%Y-%m')} to {sequence_info['end'].strftime('%Y-%m')} ({sequence_info['len']} months)**")
        st.caption("No predictive forecasting is performed. Only descriptive statistics are shown.")

        first_oil = seq_df.iloc[0]["Oil"] if len(seq_df) > 0 else float("nan")
        last_oil = seq_df.iloc[-1]["Oil"] if len(seq_df) > 0 else float("nan")
        diff_oil = last_oil - first_oil if (not (first_oil != first_oil) and not (last_oil != last_oil)) else float("nan")
        pct_oil = ((last_oil / first_oil) - 1) * 100 if (not (first_oil != first_oil) and not (last_oil != last_oil) and first_oil != 0) else float("nan")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("First Month Oil (Sm³)", f"{first_oil:,.0f}" if not (first_oil != first_oil) else "N/A")
        with col_b:
            st.metric("Last Month Oil (Sm³)", f"{last_oil:,.0f}" if not (last_oil != last_oil) else "N/A")
        with col_c:
            st.metric("Production Change (%)", f"{pct_oil:.1f}%" if not (pct_oil != pct_oil) else "N/A", delta=f"{pct_oil:.1f}%" if not (pct_oil != pct_oil) else "N/A")

        for col in ["Oil", "Gas", "Water"]:
            seq_df[col] = pd.to_numeric(seq_df[col], errors="coerce")
        fig_seq = go.Figure()
        for col, label, clr in [("Oil", "Oil", "#2f769b"), ("Gas", "Gas", "#9e9ac8"), ("Water", "Water", "#6baed6")]:
            fig_seq.add_trace(go.Scatter(
                x=seq_df["Date"], y=seq_df[col], mode="lines+markers", name=label,
                line=dict(width=2, color=clr),
            ))
        fig_seq.update_layout(
            title=f"{well_name} — Continuous Sequence ({sequence_info['len']} months) — Monthly Production",
            xaxis_title="Production Date", yaxis_title="Produced (Sm³)",
            template="plotly_dark", height=400, hovermode="x unified",
        )
        st.plotly_chart(fig_seq, width="stretch")

        st.markdown("**Sequence Statistics**")
        stats_data = {
            "Metric": ["Oil (Sm³)", "Gas (Sm³)", "Water (Sm³)", "Months", "First Month", "Last Month"],
            "Value": [
                f"{seq_df['Oil'].sum():,.0f}",
                f"{seq_df['Gas'].sum():,.0f}" if 'Gas' in seq_df.columns else "N/A",
                f"{seq_df['Water'].sum():,.0f}" if 'Water' in seq_df.columns else "N/A",
                str(len(seq_df)),
                sequence_info["start"].strftime("%Y-%m"),
                sequence_info["end"].strftime("%Y-%m"),
            ],
        }
        st.table(pd.DataFrame(stats_data))

        st.caption("Analysis covers only the selected continuous sequence. No interpolation, no forecasting, and no reservoir/equipment cause is inferred. Gaps and missing months are excluded.")


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

st.dataframe(summary_report.style.format({
        "Total Oil (Sm³)": "{:,.0f}",
        "Total Gas (Sm³)": "{:,.0f}",
        "Total Water (Sm³)": "{:,.0f}",
    }), width="stretch")

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
