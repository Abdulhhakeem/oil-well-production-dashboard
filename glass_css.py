<style>
/* Deep navy/charcoal base with petroleum restraint */
.stApp {
    background: linear-gradient(180deg, #0b1120 0%, #0f172a 40%, #111827 100%);
    background-attachment: fixed;
    color: #e8edf5;
}
/* Liquid-glass KPI panel */
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
[data-testid="metric-container"] > label {
    color: #94a3b8;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
}
[data-testid="metric-container"] > [data-testid="stMetricValue"] {
    color: #fdf6e3;
    font-weight: 800;
    font-size: 1.45rem;
    letter-spacing: -0.01em;
}
/* Section headings — petroleum teal/amber accent bar */
.stSubheader, .stMarkdown h2 {
    color: #f0fdfa;
    font-weight: 700;
    letter-spacing: 0.06em;
    border-left: 3.5px solid #f59e0b;
    padding-left: 0.9rem;
    padding-bottom: 0.3rem;
    margin-top: 2.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
/* Sidebar glass */
[data-testid="stSidebar"] {
    background: rgba(11,17,32,0.92) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.06);
}
/* Tables — dark readable */
[data-testid="stDataFrame"] thead th {
    background-color: #0f172a !important;
    color: #fdf6e3 !important;
    font-weight: 600;
    letter-spacing: 0.03em;
    border-bottom: 2px solid rgba(245,158,11,0.3) !important;
}
[data-testid="stDataFrame"] tbody td {
    background-color: rgba(15,23,42,0.5) !important;
    color: #e8edf5 !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
/* Small text / captions */
.stCaption, .stMarkdown p {
    color: #94a3b8 !important;
    font-size: 0.82rem;
}
/* Select / radio labels */
.stSelectbox label, .stMultiselect label, .stRadio label {
    color: #fdf6e3 !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)
