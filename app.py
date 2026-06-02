import streamlit as st
import pandas as pd
import altair as alt
import base64
from pathlib import Path

# --- Page config ---
st.set_page_config(
    page_title="Dual Fuel AR Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dual Fuel Brand CSS ---
st.markdown("""
<style>
/* === Import font === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === Base === */
*, html, body, [class*="css"] {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background-color: #000000;
}
[data-testid="stHeader"] {
    background-color: #000000;
}

/* === Sidebar === */
[data-testid="stSidebar"] {
    background-color: #0d0d12;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #e0e0e0;
}

/* === Metric cards === */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #141422 0%, #1a1a2e 100%);
    border: 1px solid #2a2a3e;
    border-top: 3px solid #C30017;
    border-radius: 8px;
    padding: 20px 24px;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: #C30017;
}
[data-testid="stMetricLabel"] p {
    color: #808090 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* === Headings === */
h1 { color: #FFFFFF !important; font-weight: 700 !important; }
h2 { color: #FFFFFF !important; font-weight: 700 !important; }
h3 { color: #FFFFFF !important; font-weight: 600 !important; }

/* === Hide anchor links on headings === */
a.headerLink { display: none !important; }
h1 a, h2 a, h3 a { display: none !important; }
[data-testid="stMarkdownContainer"] h2 a { display: none !important; }

/* === Dividers === */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #C30017, transparent) !important;
    margin: 24px 0 !important;
}

/* === Dataframe === */
[data-testid="stDataFrame"] {
    background-color: #141422;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    overflow: hidden;
}

/* === Sidebar labels === */
[data-testid="stSidebar"] label {
    color: #808090 !important;
    text-transform: uppercase;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px;
}

/* === Sidebar inputs === */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] {
    margin-bottom: 4px;
}

/* === Chart container === */
[data-testid="stVegaLiteChart"] {
    background-color: #141422;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    padding: 16px;
    overflow: hidden;
}

/* === General text === */
[data-testid="stMarkdownContainer"] p {
    color: #e0e0e0;
}

/* === Total row === */
.total-row {
    background: linear-gradient(135deg, #141422 0%, #1a1a2e 100%);
    border: 1px solid #2a2a3e;
    border-left: 4px solid #C30017;
    border-radius: 8px;
    padding: 14px 24px;
    margin-top: 10px;
}
.total-row p {
    color: #FFFFFF !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* === Info box === */
[data-testid="stAlert"] {
    background-color: #141422;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    color: #808090;
}

/* === Hide Streamlit branding === */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {visibility: hidden;}

/* === Sidebar logo === */
.sidebar-logo {
    text-align: center;
    padding: 16px 0 12px 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 24px;
}
.sidebar-logo img { width: 44px; height: 44px; }
.sidebar-title {
    color: #FFFFFF;
    font-size: 1rem;
    font-weight: 700;
    margin: 10px 0 2px 0;
    letter-spacing: 0.5px;
}
.sidebar-subtitle {
    color: #C30017;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 0;
}
.filter-header {
    color: #C30017 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 8px !important;
    margin-bottom: 12px !important;
}

/* === Section labels === */
.section-label {
    color: #808090 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px !important;
}

/* === Login page === */
.login-wrap {
    text-align: center;
    max-width: 380px;
    margin: 0 auto;
    padding-top: 60px;
}
.login-wrap img { margin-bottom: 16px; }
.login-title {
    color: #FFFFFF;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    text-align: center;
}
.login-sub {
    color: #C30017;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0 0 32px 0;
    text-align: center;
}

/* === Button styling === */
[data-testid="stButton"] button {
    background-color: #C30017 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    padding: 10px 24px !important;
    transition: background-color 0.2s;
}
[data-testid="stButton"] button:hover {
    background-color: #D30011 !important;
}
</style>
""", unsafe_allow_html=True)


# --- Login gate ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    flame_path = Path(__file__).parent / "Flame.png"
    flame_html = ""
    if flame_path.exists():
        flame_b64 = base64.b64encode(flame_path.read_bytes()).decode()
        flame_html = f'<img src="data:image/png;base64,{flame_b64}" width="56">'

    st.markdown(
        f'<div class="login-wrap">'
        f'{flame_html}'
        f'<p class="login-title">Dual Fuel</p>'
        f'<p class="login-sub">AR Dashboard</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Sign in", use_container_width=True):
            users = st.secrets["users"]
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()


# --- Dashboard (only runs after login) ---
conn = st.connection("snowflake")

df = conn.query("""
    SELECT
        billing_customer_name   AS \"Customer\",
        property_name           AS \"Property / Project\",
        invoice_number          AS \"Invoice\",
        outstanding_balance     AS \"Balance\",
        due_date                AS \"Date\",
        aging_bucket            AS \"Aging Bucket\",
        department_name         AS \"Department\",
        sa_type                 AS \"SA Type\",
        days_past_due           AS \"Days Past Due\",
        project_manager         AS \"Project Manager\"
    FROM ANALYTICS.GOLD.FCT_INVOICE_OPEN
    ORDER BY due_date ASC
""")

# Clean up department names
df["Department"] = df["Department"].str.replace(r"^DFC\s*-\s*", "", regex=True)


# === SIDEBAR ===
with st.sidebar:
    flame_path = Path(__file__).parent / "Flame.png"
    if flame_path.exists():
        flame_b64 = base64.b64encode(flame_path.read_bytes()).decode()
        st.markdown(
            f'<div class="sidebar-logo">'
            f'<img src="data:image/png;base64,{flame_b64}">'
            f'<p class="sidebar-title">Dual Fuel</p>'
            f'<p class="sidebar-subtitle">AR Dashboard</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<p class="filter-header">Filters</p>', unsafe_allow_html=True)

    dept_filter = st.multiselect(
        "Department",
        options=sorted(df["Department"].dropna().unique()),
    )
    bucket_filter = st.multiselect(
        "Aging Bucket",
        options=["Not Yet Due", "Current (1-30)", "31-60 Days", "61-90 Days", "90+ Days"],
    )
    property_filter = st.multiselect(
        "Property / Project",
        options=sorted(df["Property / Project"].dropna().unique()),
    )
    customer_search = st.text_input("Search Customer")
    pm_filter = st.multiselect(
        "Project Manager",
        options=sorted(df["Project Manager"].dropna().loc[df["Project Manager"] != ""].unique()),
    )


# Apply filters
filtered = df.copy()
if dept_filter:
    filtered = filtered[filtered["Department"].isin(dept_filter)]
if bucket_filter:
    filtered = filtered[filtered["Aging Bucket"].isin(bucket_filter)]
if property_filter:
    filtered = filtered[filtered["Property / Project"].isin(property_filter)]
if customer_search:
    filtered = filtered[filtered["Customer"].str.contains(customer_search, case=False, na=False)]
if pm_filter:
    filtered = filtered[filtered["Project Manager"].isin(pm_filter)]


# === MAIN CONTENT ===
st.markdown(
    '<p class="section-label" style="margin-top:8px;">Overview</p>',
    unsafe_allow_html=True,
)
st.markdown("## AR Dashboard")

# --- Metric cards ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total AR", f"${filtered['Balance'].sum():,.2f}")
with col2:
    st.metric("Open Invoices", f"{len(filtered):,}")
with col3:
    st.metric("Customers", f"{filtered['Customer'].nunique():,}")
with col4:
    avg_dpd = filtered['Days Past Due'].mean()
    st.metric("Avg Days Past Due", f"{avg_dpd:.0f}" if pd.notna(avg_dpd) else "—")

st.divider()

# --- Data table ---
st.markdown(
    '<p class="section-label">Open Invoices</p>',
    unsafe_allow_html=True,
)

st.dataframe(
    filtered[["Customer", "Property / Project", "Project Manager", "Invoice", "Balance", "Date"]].style.format({
        "Balance": "${:,.2f}",
        "Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else ""
    }),
    use_container_width=True,
    height=300,
    hide_index=True,
)

st.markdown(
    f'<div class="total-row"><p>Total: ${filtered["Balance"].sum():,.2f}</p></div>',
    unsafe_allow_html=True,
)

st.divider()

# --- Weekly AR Trend Chart ---
st.markdown(
    '<p class="section-label">AR Aging Trend</p>',
    unsafe_allow_html=True,
)
st.markdown("### Weekly Snapshots")

snapshot_df = conn.query("""
    SELECT
        snapshot_date   AS \"Week\",
        aging_bucket    AS \"Aging Bucket\",
        aging_bucket_sort,
        total_outstanding AS \"Amount\"
    FROM ANALYTICS.GOLD.FCT_AR_WEEKLY_SNAPSHOT
    ORDER BY snapshot_date, aging_bucket_sort
""")

if len(snapshot_df) > 0:
    snapshot_df["Week Label"] = pd.to_datetime(snapshot_df["Week"]).dt.strftime("%m/%d/%Y")

    color_scale = alt.Scale(
        domain=["Current", "Watchlist", "Aged"],
        range=["#27ae60", "#f1c40f", "#C30017"]
    )

    chart = (
        alt.Chart(snapshot_df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Week Label:N",
                title="Week Ending",
                sort=alt.SortField(field="Week", order="ascending"),
                axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#808090"),
            ),
            y=alt.Y(
                "Amount:Q",
                title="AR ($)",
                axis=alt.Axis(format="$,.0f", labelColor="#808090", titleColor="#808090"),
            ),
            color=alt.Color(
                "Aging Bucket:N",
                scale=color_scale,
                legend=alt.Legend(title="Aging Bucket", orient="top", labelColor="#c0c0c0", titleColor="#808090"),
            ),
            order=alt.Order("aging_bucket_sort:Q"),
            tooltip=[
                alt.Tooltip("Week Label:N", title="Week"),
                alt.Tooltip("Aging Bucket:N"),
                alt.Tooltip("Amount:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=380)
    )

    totals = snapshot_df.groupby(["Week Label", "Week"], as_index=False)["Amount"].sum()
    totals["Label"] = totals["Amount"].apply(lambda x: f"${x/1000:,.0f}K")

    text = (
        alt.Chart(totals)
        .mark_text(dy=-12, fontSize=12, fontWeight="bold", color="#FFFFFF")
        .encode(
            x=alt.X("Week Label:N", sort=alt.SortField(field="Week", order="ascending")),
            y=alt.Y("Amount:Q"),
            text="Label:N",
        )
    )

    combined = (
        (chart + text)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e")
    )
    st.altair_chart(combined, use_container_width=True)
else:
    st.info("No snapshot data yet. The first snapshot will appear after Friday at 5 PM.")

