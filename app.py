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
/* === Base theme overrides === */
[data-testid="stAppViewContainer"] {
    background-color: #000000;
}
[data-testid="stHeader"] {
    background-color: #000000;
}
[data-testid="stSidebar"] {
    background-color: #1A1A1A;
    border-right: 1px solid #333333;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF;
}

/* === Metric cards === */
[data-testid="stMetric"] {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-top: 3px solid #C30017;
    border-radius: 4px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] {
    color: #C0C0C0 !important;
}
[data-testid="stMetricLabel"] p {
    color: #C0C0C0 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* === Title styling === */
h1 {
    color: #FFFFFF !important;
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
    font-weight: 700 !important;
}
h2, h3 {
    color: #FFFFFF !important;
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
}

/* === Red accent divider === */
hr {
    border-color: #C30017 !important;
    border-width: 2px !important;
}

/* === Dataframe styling === */
[data-testid="stDataFrame"] {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 4px;
}

/* === Sidebar filter labels === */
[data-testid="stSidebar"] label {
    color: #C0C0C0 !important;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px;
}

/* === Sidebar multiselect and text inputs === */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] {
    margin-bottom: 8px;
}
[data-testid="stSidebar"] .stTextInput input {
    background-color: #333333;
    color: #FFFFFF;
    border: 1px solid #808080;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #C30017;
}

/* === Chart container === */
[data-testid="stVegaLiteChart"] {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 12px;
}

/* === General text === */
[data-testid="stMarkdownContainer"] p {
    color: #FFFFFF;
}

/* === Total row styling === */
.total-row {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-left: 4px solid #C30017;
    border-radius: 4px;
    padding: 12px 20px;
    margin-top: 8px;
}
.total-row p {
    color: #FFFFFF !important;
    font-size: 1.1rem !important;
    margin: 0 !important;
}

/* === Info box === */
[data-testid="stAlert"] {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    color: #C0C0C0;
}

/* === Hide Streamlit branding === */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* === Sidebar logo section === */
.sidebar-logo {
    text-align: center;
    padding: 12px 0 8px 0;
    border-bottom: 1px solid #333333;
    margin-bottom: 20px;
}
.sidebar-logo img {
    width: 50px;
    height: 50px;
}
.sidebar-title {
    color: #FFFFFF;
    font-size: 1.1rem;
    font-weight: 700;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 8px 0 2px 0;
}
.sidebar-subtitle {
    color: #C30017;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0;
}
.filter-header {
    color: #C30017 !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 16px !important;
    margin-bottom: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# --- Login gate ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.markdown("<br><br>", unsafe_allow_html=True)
        flame_path = Path(__file__).parent / "Flame.png"
        if flame_path.exists():
            flame_b64 = base64.b64encode(flame_path.read_bytes()).decode()
            st.markdown(
                f'<div style="text-align:center;margin-bottom:16px;">'
                f'<img src="data:image/png;base64,{flame_b64}" width="60"></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<h2 style="text-align:center;margin-bottom:4px;">Dual Fuel</h2>'
            '<p style="text-align:center;color:#C30017;font-size:0.8rem;'
            'letter-spacing:2px;text-transform:uppercase;margin-bottom:24px;">'
            'AR Dashboard</p>',
            unsafe_allow_html=True,
        )
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
        days_past_due           AS \"Days Past Due\"
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


# === MAIN CONTENT ===
st.markdown(
    '<h1 style="margin-bottom:4px;">AR Dashboard</h1>'
    '<p style="color:#808080;font-size:0.9rem;margin-bottom:24px;">'
    'Weekly Trends &amp; Open Invoice Tracking</p>',
    unsafe_allow_html=True,
)

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
    '<p style="color:#C0C0C0;font-size:0.8rem;text-transform:uppercase;'
    'letter-spacing:0.5px;margin-bottom:8px;">Open Invoices</p>',
    unsafe_allow_html=True,
)

st.dataframe(
    filtered[["Customer", "Property / Project", "Invoice", "Balance", "Date"]].style.format({
        "Balance": "${:,.2f}",
        "Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else ""
    }),
    use_container_width=True,
    height=300,
    hide_index=True,
)

st.markdown(
    f'<div class="total-row"><p><strong>Total: ${filtered["Balance"].sum():,.2f}</strong></p></div>',
    unsafe_allow_html=True,
)

st.divider()

# --- Weekly AR Trend Chart ---
st.markdown(
    '<p style="color:#C0C0C0;font-size:0.8rem;text-transform:uppercase;'
    'letter-spacing:0.5px;margin-bottom:4px;">AR Aging Trend</p>'
    '<h3 style="margin-top:0;">Weekly Snapshots</h3>',
    unsafe_allow_html=True,
)

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
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(
                "Week Label:N",
                title="Week Ending",
                sort=alt.SortField(field="Week", order="ascending"),
                axis=alt.Axis(labelAngle=-45, labelColor="#C0C0C0", titleColor="#808080"),
            ),
            y=alt.Y(
                "Amount:Q",
                title="AR ($)",
                axis=alt.Axis(format="$,.0f", labelColor="#C0C0C0", titleColor="#808080"),
            ),
            color=alt.Color(
                "Aging Bucket:N",
                scale=color_scale,
                legend=alt.Legend(title="Aging Bucket", orient="top", labelColor="#C0C0C0", titleColor="#808080"),
            ),
            order=alt.Order("aging_bucket_sort:Q"),
            tooltip=[
                alt.Tooltip("Week Label:N", title="Week"),
                alt.Tooltip("Aging Bucket:N"),
                alt.Tooltip("Amount:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=400)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#333333")
    )

    totals = snapshot_df.groupby(["Week Label", "Week"], as_index=False)["Amount"].sum()
    totals["Label"] = totals["Amount"].apply(lambda x: f"${x/1000:,.0f}K")

    text = (
        alt.Chart(totals)
        .mark_text(dy=-10, fontSize=11, fontWeight="bold", color="#FFFFFF")
        .encode(
            x=alt.X("Week Label:N", sort=alt.SortField(field="Week", order="ascending")),
            y=alt.Y("Amount:Q"),
            text="Label:N",
        )
    )

    st.altair_chart(chart + text, use_container_width=True)
else:
    st.info("No snapshot data yet. The first snapshot will appear after Friday at 5 PM.")

