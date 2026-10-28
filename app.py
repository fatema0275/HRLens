import os
import glob
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# PAGE CONFIG

st.set_page_config(
    page_title="HR Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
/* ── Fonts & page background ── */
html, body, [class*="css"], .stApp {
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    background-color: #F3F2F1 !important;
    color: #252423 !important;
}
[data-testid="stAppViewContainer"] { background-color: #F3F2F1 !important; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }

/* ── Tight page padding ── */
.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}

/* ── Report header bar ── */
.rpt-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 4px 10px 4px;
    border-bottom: 2px solid #E1DFDD;
    margin-bottom: 12px;
}
.rpt-title {
    font-size: 22px;
    font-weight: 600;
    color: #252423;
    margin: 0;
}
.rpt-meta {
    font-size: 12px;
    color: #605E5C;
}

/* ── White tile ── */
.pbi-tile {
    background: #FFFFFF;
    border: 1px solid #E1DFDD;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 14px 16px 10px 16px;
    margin-bottom: 10px;
    height: 100%;
}
.tile-title {
    font-size: 14px;
    font-weight: 600;
    color: #252423;
    margin: 0 0 8px 0;
    line-height: 1.3;
}

/* ── KPI tile ── */
.kpi-tile {
    background: #FFFFFF;
    border: 1px solid #E1DFDD;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 16px 18px 14px 18px;
    height: 100%;
}
.kpi-label {
    font-size: 12px;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #605E5C;
    margin: 0 0 6px 0;
}
.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: #252423;
    line-height: 1;
    margin: 0 0 6px 0;
}
.kpi-sub {
    font-size: 12px;
    color: #605E5C;
    margin: 0;
}
.kpi-up   { color: #107C10; font-weight: 600; }
.kpi-down { color: #D64550; font-weight: 600; }

/* ── Sidebar slicer pane ── */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E1DFDD !important;
}
section[data-testid="stSidebar"] * { color: #252423 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label p,
section[data-testid="stSidebar"] .stMultiSelect label p {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #605E5C !important;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background: #F3F2F1 !important;
    border: 1px solid #E1DFDD !important;
    border-radius: 2px !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] button {
    background: #FFFFFF !important;
    border: 1px solid #E1DFDD !important;
    color: #252423 !important;
    border-radius: 2px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 6px 12px !important;
}
section[data-testid="stSidebar"] button:hover {
    background: #F3F2F1 !important;
    border-color: #605E5C !important;
}
/* ── Streamlit tab styling ── */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #605E5C !important;
    border-radius: 0 !important;
    padding: 8px 18px !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #118DFF !important;
    border-bottom: 2px solid #118DFF !important;
}
/* ── No-data warning ── */
.no-data {
    text-align: center;
    padding: 40px;
    color: #605E5C;
    font-size: 14px;
    background: #FFFFFF;
    border: 1px solid #E1DFDD;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# POWER BI PALETTE & PLOTLY TEMPLATE
# ─────────────────────────────────────────────
PBI_BLUE    = "#118DFF"
PBI_NAVY    = "#12239E"
PBI_ORANGE  = "#E66C37"
PBI_PURPLE  = "#6B007B"
PBI_PINK    = "#E044A7"
PBI_VIOLET  = "#744EC2"
PBI_GOLD    = "#D9B300"
PBI_RED     = "#D64550"

PBI_PALETTE = [PBI_BLUE, PBI_ORANGE, PBI_NAVY, PBI_VIOLET, PBI_GOLD, PBI_RED, PBI_PINK, PBI_PURPLE]

# Retained = blue, Attrition = orange/red — consistent everywhere
COLOR_RETAIN  = PBI_BLUE
COLOR_ATTRIT  = PBI_ORANGE

CHART_CFG  = {"displayModeBar": False}
GRID_COLOR = "#EDEBE9"

def _base_layout(height=300, show_legend=False, legend_top=True):
    leg = dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=12, color="#252423"),
        bgcolor="rgba(0,0,0,0)",
    ) if legend_top else dict(font=dict(size=12, color="#252423"))
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", size=12, color="#252423"),
        margin=dict(t=10, b=40, l=10, r=10),
        showlegend=show_legend,
        legend=leg,
        xaxis=dict(
            showgrid=False, zeroline=False,
            linecolor="#E1DFDD", tickfont=dict(size=12, color="#252423"),
            title_font=dict(size=12, color="#252423"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
            linecolor="rgba(0,0,0,0)", tickfont=dict(size=12, color="#252423"),
            title_font=dict(size=12, color="#252423"),
        ),
        hoverlabel=dict(
            bgcolor="#252423", font_color="#FFFFFF",
            font_size=12, font_family="Segoe UI, sans-serif",
            bordercolor="#252423",
        ),
    )

# ─────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────
def tile_open(title=""):
    t = f'<p class="tile-title">{title}</p>' if title else ""
    st.markdown(f'<div class="pbi-tile">{t}', unsafe_allow_html=True)

def tile_close():
    st.markdown("</div>", unsafe_allow_html=True)

def kpi_tile(label, value, sub="", delta_class=""):
    sub_html = f'<p class="kpi-sub {delta_class}">{sub}</p>' if sub else ""
    st.markdown(f"""
    <div class="kpi-tile">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def no_data():
    st.markdown('<div class="no-data">No data for the selected filters.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_raw():
    candidates = [
        "data/WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "data/ibm_hr_attrition.csv",
        "data/HR-Employee-Attrition.csv",
        "data/employees.csv",
    ]
    for p in candidates:
        if os.path.exists(p):
            return pd.read_csv(p)
    csvs = glob.glob("data/*.csv")
    return pd.read_csv(csvs[0]) if csvs else None

raw = load_raw()
if raw is None:
    st.error("No CSV dataset found in data/. Please add the IBM HR Attrition CSV.")
    st.stop()

# Normalise Attrition to bool
raw = raw.copy()
raw["_left"] = raw["Attrition"].str.strip().str.lower() == "yes"

# Precompute age groups
_bins   = [17, 24, 34, 44, 54, 100]
_labels = ["18-24", "25-34", "35-44", "45-54", "55+"]
raw["AgeGroup"] = pd.cut(raw["Age"], bins=_bins, labels=_labels)

TOTAL_ROWS = len(raw)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def reset_filters():
    for k in ("f_dept","f_gender","f_role","f_ot","f_age"):
        if k in st.session_state:
            del st.session_state[k]

with st.sidebar:
    st.markdown("<p style='font-size:11px;font-weight:600;color:#605E5C;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>Filters</p>", unsafe_allow_html=True)

    dept_opts  = sorted(raw["Department"].dropna().unique().tolist())
    gender_opts = sorted(raw["Gender"].dropna().unique().tolist())
    role_opts  = sorted(raw["JobRole"].dropna().unique().tolist())
    ot_opts    = sorted(raw["OverTime"].dropna().unique().tolist())

    f_dept   = st.multiselect("Department",   dept_opts,  key="f_dept")
    f_gender = st.multiselect("Gender",       gender_opts,key="f_gender")
    f_role   = st.multiselect("Job Role",     role_opts,  key="f_role")
    f_ot     = st.multiselect("Overtime",     ot_opts,    key="f_ot")

    age_min, age_max = int(raw["Age"].min()), int(raw["Age"].max())
    f_age = st.slider("Age range", age_min, age_max, (age_min, age_max), key="f_age")

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    st.button("Clear filters", on_click=reset_filters, use_container_width=True)

# Apply filters
df = raw.copy()
if f_dept:   df = df[df["Department"].isin(f_dept)]
if f_gender: df = df[df["Gender"].isin(f_gender)]
if f_role:   df = df[df["JobRole"].isin(f_role)]
if f_ot:     df = df[df["OverTime"].isin(f_ot)]
df = df[(df["Age"] >= f_age[0]) & (df["Age"] <= f_age[1])]

N = len(df)

# ─────────────────────────────────────────────
# REPORT HEADER BAR
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="rpt-header">
    <span class="rpt-title">HR Analytics</span>
    <span class="rpt-meta">{N:,} of {TOTAL_ROWS:,} records &nbsp;|&nbsp; IBM HR Attrition dataset</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EMPTY GUARD
# ─────────────────────────────────────────────
if N == 0:
    no_data()
    st.stop()

# ─────────────────────────────────────────────
# COMPUTED AGGREGATES (cached per filter combo)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def compute_kpis(df_hash):
    return None  # placeholder — we compute inline (df changes with filters so cache not useful per-call)

n_left     = int(df["_left"].sum())
n_active   = N - n_left
att_rate   = n_left / N * 100
avg_income = df["MonthlyIncome"].mean()
avg_tenure = df["YearsAtCompany"].mean()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_ov, tab_att, tab_comp = st.tabs(["Overview", "Attrition Drivers", "Compensation & Tenure"])

###############################################################################
# TAB 1 — OVERVIEW
###############################################################################
with tab_ov:

    # ── Row 0: 5 KPI tiles ──────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_tile("Total Employees", f"{N:,}", f"{TOTAL_ROWS:,} in full dataset")
    with c2: kpi_tile("Active",          f"{n_active:,}", f"{100-att_rate:.1f}% retained")
    with c3: kpi_tile("Attrition Rate",  f"{att_rate:.1f}%", f"{n_left:,} left", "kpi-down" if att_rate > 15 else "kpi-up")
    with c4: kpi_tile("Avg Monthly Income", f"${avg_income:,.0f}", f"across all roles")
    with c5: kpi_tile("Avg Tenure",      f"{avg_tenure:.1f} yrs", f"years at company")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Row 1: Donut | Dept bar | Attrition rate by job role ────────────────
    r1c1, r1c2, r1c3 = st.columns([1, 1.4, 1.6])

    # Donut – attrition split
    with r1c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Split</p>', unsafe_allow_html=True)
            donut_data = pd.DataFrame({
                "Status": ["Retained", "Left"],
                "Count":  [n_active, n_left],
            })
            fig = go.Figure(go.Pie(
                labels=donut_data["Status"], values=donut_data["Count"],
                hole=0.62,
                marker_colors=[COLOR_RETAIN, COLOR_ATTRIT],
                textinfo="percent", textfont_size=13,
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            ))
            fig.add_annotation(
                text=f"<b>{att_rate:.1f}%</b><br>attrition",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#252423", family="Segoe UI"),
            )
            layout = _base_layout(height=270)
            layout["margin"] = dict(t=5, b=5, l=5, r=5)
            layout["showlegend"] = True
            layout["legend"] = dict(
                orientation="h", yanchor="bottom", y=-0.12,
                xanchor="center", x=0.5,
                font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
            )
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Horizontal bar – headcount by dept
    with r1c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Headcount by Department</p>', unsafe_allow_html=True)
            dept_df = (
                df.groupby("Department", observed=True)
                  .size().reset_index(name="Count")
                  .sort_values("Count", ascending=True)
            )
            if dept_df.empty:
                no_data()
            else:
                fig = px.bar(
                    dept_df, y="Department", x="Count", orientation="h",
                    text="Count",
                    color_discrete_sequence=[PBI_BLUE],
                )
                fig.update_traces(
                    textposition="outside", textfont_size=12,
                    marker_line_width=0, cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Headcount: %{x:,}<extra></extra>",
                )
                layout = _base_layout(height=270)
                layout["xaxis"]["showgrid"] = True
                layout["xaxis"]["gridcolor"] = GRID_COLOR
                layout["yaxis"]["showgrid"] = False
                layout["margin"] = dict(t=5, b=5, l=5, r=60)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Column chart – attrition rate % by job role
    with r1c3:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Rate by Job Role</p>', unsafe_allow_html=True)
            role_att = (
                df.groupby("JobRole", observed=True)
                  .agg(Total=("_left","count"), Left=("_left","sum"))
                  .assign(Rate=lambda x: x["Left"]/x["Total"]*100)
                  .reset_index()
                  .sort_values("Rate", ascending=False)
            )
            if role_att.empty:
                no_data()
            else:
                fig = px.bar(
                    role_att, x="JobRole", y="Rate",
                    text=role_att["Rate"].map(lambda v: f"{v:.1f}%"),
                    color_discrete_sequence=[COLOR_ATTRIT],
                )
                fig.update_traces(
                    textposition="outside", textfont_size=12,
                    marker_line_width=0, cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Attrition: %{y:.1f}%<extra></extra>",
                )
                fig.update_xaxes(tickangle=-35, tickfont_size=11)
                layout = _base_layout(height=270)
                layout["yaxis"]["ticksuffix"] = "%"
                layout["margin"] = dict(t=5, b=60, l=10, r=10)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Row 2: Stacked 100% bar (gender + overtime) | Age histogram ─────────
    r2c1, r2c2 = st.columns([1, 1.3])

    with r2c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition by Gender & Overtime</p>', unsafe_allow_html=True)
            # Two grouped 100% bars side by side using subplots
            def pct_breakdown(col):
                grp = (
                    df.groupby([col, "_left"], observed=True)
                      .size().reset_index(name="n")
                )
                tot = grp.groupby(col, observed=True)["n"].transform("sum")
                grp["pct"] = grp["n"] / tot * 100
                return grp

            g_df = pct_breakdown("Gender")
            o_df = pct_breakdown("OverTime")

            fig = make_subplots(rows=1, cols=2, subplot_titles=["Gender", "OverTime"],
                                shared_yaxes=False)

            for left_val, color, name in [(False, COLOR_RETAIN, "Retained"), (True, COLOR_ATTRIT, "Left")]:
                # Gender
                sub = g_df[g_df["_left"] == left_val]
                fig.add_trace(go.Bar(
                    x=sub["Gender"], y=sub["pct"], name=name,
                    marker_color=color, showlegend=(left_val is False or True),
                    hovertemplate="<b>%{x}</b><br>" + name + ": %{y:.1f}%<extra></extra>",
                    text=sub["pct"].map(lambda v: f"{v:.0f}%"),
                    textposition="inside", textfont_size=12,
                ), row=1, col=1)
                # OverTime
                sub2 = o_df[o_df["_left"] == left_val]
                fig.add_trace(go.Bar(
                    x=sub2["OverTime"], y=sub2["pct"], name=name,
                    marker_color=color, showlegend=False,
                    hovertemplate="<b>%{x}</b><br>" + name + ": %{y:.1f}%<extra></extra>",
                    text=sub2["pct"].map(lambda v: f"{v:.0f}%"),
                    textposition="inside", textfont_size=12,
                ), row=1, col=2)

            fig.update_layout(
                barmode="stack",
                height=290,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Segoe UI, sans-serif", size=12, color="#252423"),
                margin=dict(t=28, b=10, l=5, r=5),
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.06,
                    xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                ),
                yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                           ticksuffix="%", tickfont_size=12),
                yaxis2=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                            ticksuffix="%", tickfont_size=12),
                hoverlabel=dict(bgcolor="#252423", font_color="#FFFFFF",
                                font_size=12, font_family="Segoe UI, sans-serif"),
            )
            for ann in fig.layout.annotations:
                ann.font.size = 12
                ann.font.color = "#252423"
            st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    with r2c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Age Distribution by Attrition</p>', unsafe_allow_html=True)
            df_age = df.copy()
            df_age["Status"] = df_age["_left"].map({True: "Left", False: "Retained"})
            if df_age.empty:
                no_data()
            else:
                fig = px.histogram(
                    df_age, x="Age", color="Status", nbins=20,
                    color_discrete_map={"Retained": COLOR_RETAIN, "Left": COLOR_ATTRIT},
                    barmode="overlay", opacity=0.85,
                )
                fig.update_traces(
                    marker_line_width=0,
                    hovertemplate="Age: %{x}<br>Count: %{y}<extra></extra>",
                )
                layout = _base_layout(height=290, show_legend=True)
                layout["legend"] = dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                )
                layout["margin"] = dict(t=5, b=10, l=5, r=5)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)


###############################################################################
# TAB 2 — ATTRITION DRIVERS
###############################################################################
with tab_att:

    r1c1, r1c2 = st.columns(2)

    # Heatmap: attrition rate by Department × Job Satisfaction
    with r1c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Rate: Department × Job Satisfaction</p>', unsafe_allow_html=True)
            sat_map = {1: "1-Low", 2: "2-Medium", 3: "3-High", 4: "4-Very High"}
            heat_df = df.copy()
            heat_df["Satisfaction"] = heat_df["JobSatisfaction"].map(sat_map)
            pivot = (
                heat_df.groupby(["Department", "Satisfaction"], observed=True)
                .agg(Rate=("_left", "mean"))
                .reset_index()
                .pivot(index="Department", columns="Satisfaction", values="Rate")
                .fillna(0) * 100
            )
            # keep sorted columns
            col_order = [c for c in ["1-Low","2-Medium","3-High","4-Very High"] if c in pivot.columns]
            pivot = pivot[col_order]
            if pivot.empty:
                no_data()
            else:
                fig = go.Figure(go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns.tolist(),
                    y=pivot.index.tolist(),
                    colorscale=[[0,"#EBF5FB"],[0.5,"#118DFF"],[1,"#D64550"]],
                    text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
                    texttemplate="%{text}",
                    textfont=dict(size=12, color="#252423"),
                    hovertemplate="Dept: %{y}<br>Satisfaction: %{x}<br>Attrition: %{z:.1f}%<extra></extra>",
                    showscale=True,
                    colorbar=dict(tickfont_size=11, thickness=12, len=0.8),
                ))
                layout = _base_layout(height=280)
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                layout["xaxis"]["showgrid"] = False
                layout["yaxis"]["showgrid"] = False
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Scatter: Monthly Income vs Age, colored by Attrition
    with r1c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Monthly Income vs Age (colored by Attrition)</p>', unsafe_allow_html=True)
            sc_df = df.copy()
            sc_df["Status"] = sc_df["_left"].map({True: "Left", False: "Retained"})
            if sc_df.empty:
                no_data()
            else:
                import numpy as np
                fig = go.Figure()
                for status, color, mask in [
                    ("Retained", COLOR_RETAIN, ~sc_df["_left"]),
                    ("Left",     COLOR_ATTRIT, sc_df["_left"]),
                ]:
                    sub = sc_df[mask]
                    fig.add_trace(go.Scatter(
                        x=sub["Age"], y=sub["MonthlyIncome"],
                        mode="markers", name=status,
                        marker=dict(color=color, size=5, opacity=0.6, line_width=0),
                        hovertemplate="Age: %{x}<br>Income: $%{y:,.0f}<extra></extra>",
                    ))
                # Add overall linear trendline via numpy polyfit
                _x = sc_df["Age"].values
                _y = sc_df["MonthlyIncome"].values
                _m, _b = np.polyfit(_x, _y, 1)
                _xs = np.array([_x.min(), _x.max()])
                fig.add_trace(go.Scatter(
                    x=_xs, y=_m * _xs + _b,
                    mode="lines", name="Trend",
                    line=dict(color="#252423", width=1.5, dash="dot"),
                    hoverinfo="skip", showlegend=True,
                ))
                layout = _base_layout(height=280, show_legend=True)
                layout["legend"] = dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                )
                layout["yaxis"]["tickprefix"] = "$"
                layout["yaxis"]["tickformat"] = ",.0f"
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    # Line: attrition rate by Years at Company
    with r2c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Rate by Years at Company</p>', unsafe_allow_html=True)
            yac_df = (
                df.groupby("YearsAtCompany", observed=True)
                  .agg(Total=("_left","count"), Left=("_left","sum"))
                  .assign(Rate=lambda x: x["Left"]/x["Total"]*100)
                  .reset_index()
                  .sort_values("YearsAtCompany")
            )
            # smooth with rolling mean for readability
            yac_df["RateSmooth"] = yac_df["Rate"].rolling(3, center=True, min_periods=1).mean()
            if yac_df.empty:
                no_data()
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=yac_df["YearsAtCompany"], y=yac_df["RateSmooth"],
                    mode="lines+markers",
                    line=dict(color=COLOR_ATTRIT, width=2.5),
                    marker=dict(size=5, color=COLOR_ATTRIT),
                    hovertemplate="Year: %{x}<br>Attrition: %{y:.1f}%<extra></extra>",
                    name="Attrition rate",
                ))
                layout = _base_layout(height=280)
                layout["yaxis"]["ticksuffix"] = "%"
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                layout["xaxis"]["title"] = "Years at Company"
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Grouped bar: attrition rate by Business Travel × OverTime
    with r2c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Rate by Business Travel & Overtime</p>', unsafe_allow_html=True)
            def att_by(col):
                return (
                    df.groupby(col, observed=True)
                      .agg(Total=("_left","count"), Left=("_left","sum"))
                      .assign(Rate=lambda x: x["Left"]/x["Total"]*100)
                      .reset_index()
                      .rename(columns={col:"Category"})
                      .assign(Group=col)
                )
            bt = att_by("BusinessTravel")
            ot = att_by("OverTime")
            combo = pd.concat([bt, ot], ignore_index=True)
            if combo.empty:
                no_data()
            else:
                colors = [PBI_NAVY, PBI_VIOLET, PBI_ORANGE, PBI_RED]
                fig = px.bar(
                    combo, x="Category", y="Rate",
                    color="Group", barmode="group",
                    text=combo["Rate"].map(lambda v: f"{v:.1f}%"),
                    color_discrete_sequence=colors,
                )
                fig.update_traces(
                    textposition="outside", textfont_size=12,
                    marker_line_width=0, cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Attrition: %{y:.1f}%<extra></extra>",
                )
                layout = _base_layout(height=280, show_legend=True)
                layout["yaxis"]["ticksuffix"] = "%"
                layout["margin"] = dict(t=5, b=20, l=10, r=10)
                layout["legend"] = dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                )
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Full-width: Age Group attrition rate
    with st.container():
        st.markdown('<div class="pbi-tile"><p class="tile-title">Attrition Rate by Age Group</p>', unsafe_allow_html=True)
        age_grp = (
            df.groupby("AgeGroup", observed=False)
              .agg(Total=("_left","count"), Left=("_left","sum"))
              .assign(Rate=lambda x: x["Left"]/x["Total"].replace(0, pd.NA)*100)
              .reset_index()
              .dropna(subset=["Rate"])
        )
        if age_grp.empty:
            no_data()
        else:
            fig = px.bar(
                age_grp, x="AgeGroup", y="Rate",
                text=age_grp["Rate"].map(lambda v: f"{v:.1f}%"),
                color="Rate",
                color_continuous_scale=[[0,"#118DFF"],[0.5,"#E66C37"],[1,"#D64550"]],
            )
            fig.update_traces(
                textposition="outside", textfont_size=12,
                marker_line_width=0, cliponaxis=False,
                hovertemplate="Age group: %{x}<br>Attrition: %{y:.1f}%<extra></extra>",
            )
            fig.update_coloraxes(showscale=False)
            layout = _base_layout(height=240)
            layout["yaxis"]["ticksuffix"] = "%"
            layout["margin"] = dict(t=5, b=10, l=10, r=10)
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
        st.markdown("</div>", unsafe_allow_html=True)


###############################################################################
# TAB 3 — COMPENSATION & TENURE
###############################################################################
with tab_comp:

    r1c1, r1c2 = st.columns(2)

    # Box plot: Monthly Income by Job Role split by Attrition
    with r1c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Monthly Income by Job Role & Attrition</p>', unsafe_allow_html=True)
            box_df = df.copy()
            box_df["Status"] = box_df["_left"].map({True: "Left", False: "Retained"})
            if box_df.empty:
                no_data()
            else:
                role_order = (
                    box_df.groupby("JobRole")["MonthlyIncome"].median()
                         .sort_values().index.tolist()
                )
                fig = px.box(
                    box_df, x="MonthlyIncome", y="JobRole",
                    color="Status", orientation="h",
                    color_discrete_map={"Retained": COLOR_RETAIN, "Left": COLOR_ATTRIT},
                    category_orders={"JobRole": role_order},
                )
                fig.update_traces(
                    marker_size=3, line_width=1.5,
                    hovertemplate="Role: %{y}<br>Income: $%{x:,.0f}<extra></extra>",
                )
                layout = _base_layout(height=320, show_legend=True)
                layout["xaxis"]["tickprefix"] = "$"
                layout["xaxis"]["tickformat"] = ",.0f"
                layout["xaxis"]["showgrid"] = True
                layout["xaxis"]["gridcolor"] = GRID_COLOR
                layout["yaxis"]["showgrid"] = False
                layout["legend"] = dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                )
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Bubble: Years at Company vs Monthly Income, size = TotalWorkingYears
    with r1c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Tenure vs Income (size = Total Working Years)</p>', unsafe_allow_html=True)
            bub_df = df.copy()
            bub_df["Status"] = bub_df["_left"].map({True: "Left", False: "Retained"})
            if bub_df.empty:
                no_data()
            else:
                fig = px.scatter(
                    bub_df,
                    x="YearsAtCompany", y="MonthlyIncome",
                    size="TotalWorkingYears", color="Status",
                    color_discrete_map={"Retained": COLOR_RETAIN, "Left": COLOR_ATTRIT},
                    opacity=0.65, size_max=18,
                )
                fig.update_traces(
                    marker_line_width=0,
                    hovertemplate=(
                        "Years at Co: %{x}<br>"
                        "Income: $%{y:,.0f}<br>"
                        "Total Exp: %{marker.size} yrs<extra></extra>"
                    ),
                )
                layout = _base_layout(height=320, show_legend=True)
                layout["yaxis"]["tickprefix"] = "$"
                layout["yaxis"]["tickformat"] = ",.0f"
                layout["legend"] = dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
                )
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                layout["xaxis"]["title"] = "Years at Company"
                layout["yaxis"]["title"] = "Monthly Income"
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns([1.6, 1])

    # Treemap: headcount by Department > Job Role
    with r2c1:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Headcount: Department › Job Role</p>', unsafe_allow_html=True)
            tree_df = (
                df.groupby(["Department", "JobRole"], observed=True)
                  .size().reset_index(name="Count")
            )
            if tree_df.empty:
                no_data()
            else:
                tree_df.insert(0, "All", "All")
                fig = px.treemap(
                    tree_df, path=["All","Department","JobRole"], values="Count",
                    color="Department",
                    color_discrete_sequence=PBI_PALETTE,
                )
                fig.update_traces(
                    textfont_size=13,
                    hovertemplate="<b>%{label}</b><br>Headcount: %{value:,}<extra></extra>",
                    marker_line_width=1,
                    marker_line_color="#FFFFFF",
                )
                layout = _base_layout(height=320)
                layout["margin"] = dict(t=5, b=5, l=5, r=5)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    # Box plot: Distance From Home by Attrition
    with r2c2:
        with st.container():
            st.markdown('<div class="pbi-tile"><p class="tile-title">Distance From Home by Attrition</p>', unsafe_allow_html=True)
            dist_df = df.copy()
            dist_df["Status"] = dist_df["_left"].map({True: "Left", False: "Retained"})
            if dist_df.empty:
                no_data()
            else:
                fig = px.box(
                    dist_df, x="Status", y="DistanceFromHome",
                    color="Status",
                    color_discrete_map={"Retained": COLOR_RETAIN, "Left": COLOR_ATTRIT},
                    points="outliers",
                )
                fig.update_traces(
                    marker_size=3, line_width=1.5,
                    hovertemplate="Status: %{x}<br>Distance: %{y} km<extra></extra>",
                )
                layout = _base_layout(height=320)
                layout["yaxis"]["title"] = "Distance From Home (km)"
                layout["xaxis"]["showgrid"] = False
                layout["margin"] = dict(t=5, b=10, l=10, r=10)
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Full-width: Avg Income by Department (sorted bar)
    with st.container():
        st.markdown('<div class="pbi-tile"><p class="tile-title">Average Monthly Income by Department & Job Role</p>', unsafe_allow_html=True)
        inc_df = (
            df.groupby(["Department", "JobRole"], observed=True)
              .agg(AvgIncome=("MonthlyIncome","mean"))
              .reset_index()
              .sort_values(["Department","AvgIncome"], ascending=[True, False])
        )
        if inc_df.empty:
            no_data()
        else:
            fig = px.bar(
                inc_df, x="JobRole", y="AvgIncome",
                color="Department",
                color_discrete_sequence=PBI_PALETTE,
                text=inc_df["AvgIncome"].map(lambda v: f"${v:,.0f}"),
                barmode="group",
            )
            fig.update_traces(
                textposition="outside", textfont_size=11,
                marker_line_width=0, cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>Avg Income: $%{y:,.0f}<extra></extra>",
            )
            fig.update_xaxes(tickangle=-30)
            layout = _base_layout(height=280, show_legend=True)
            layout["yaxis"]["tickprefix"] = "$"
            layout["yaxis"]["tickformat"] = ",.0f"
            layout["legend"] = dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=12, color="#252423"), bgcolor="rgba(0,0,0,0)",
            )
            layout["margin"] = dict(t=5, b=50, l=10, r=10)
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
        st.markdown("</div>", unsafe_allow_html=True)
