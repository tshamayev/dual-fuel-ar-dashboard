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
    # Centered login using markdown container
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
        billing_customer_name   AS "Customer",
        property_name           AS "Property / Project",
        invoice_number          AS "Invoice",
        outstanding_balance     AS "Balance",
        due_date                AS "Date",
        aging_bucket            AS "Aging Bucket",
        department_name         AS "Department",
        sa_type                 AS "SA Type",
        days_past_due           AS "Days Past Due",
        project_manager         AS "Project Manager"
    FROM ANALYTICS.GOLD.FCT_INVOICE_OPEN
    ORDER BY due_date ASC
""")

# Clean up department names
df["Department"] = df["Department"].str.replace(r"^DFC\s*-\s*", "", regex=True)

# Fill blank properties and PMs with dash for display
df["Property / Project"] = df["Property / Project"].fillna("—").replace("", "—")
df["Project Manager"] = df["Project Manager"].fillna("—").replace("", "—")

# === Updated Customer Name overrides (management transfers) ===
CUSTOMER_OVERRIDES = [
    ("35 East 10th St:HW Heater Installation", "AKAM Associates, Inc."),
    ("35 East 10th St", "AKAM Associates, Inc."),
    ("421 West 57th Street", "AKAM Associates, Inc."),
    ("345 East 69th St", "AKAM Associates, Inc."),
    ("860 Grand Concourse", "Argo Real Estate, LLC"),
    ("448 West 37th St.", "Argo Real Estate, LLC"),
    ("414 East 119th St", "Choice New York Management"),
    ("409 East 84th St.", "Choice New York Management"),
    ("3535 Kings College Place", "David Associates"),
    ("31-05 39th Ave", "David Associates"),
    ("61-05 39th Ave", "David Associates"),
    ("Camber - Bronx Park PH2 - 1985 Webster Ave (PH2)", "Dolphin Property Services LLC"),
    ("Camber - Remeeder Houses - 585 Blake Avenue", "Dolphin Property Services LLC"),
    ("Camber - Stevenson - 1850 Lafayette Ave", "Dolphin Property Services LLC"),
    ("Camber - Remeeder - 350 Sheffield Ave", "Dolphin Property Services LLC"),
    ("Camber - Target - 1971 Grand Ave, LLC", "Dolphin Property Services LLC"),
    ("2095 Honeywell Ave", "Dolphin Property Services LLC"),
    ("876 East 180th St", "Dolphin Property Services LLC"),
    ("1898 Belmont Ave", "Dolphin Property Services LLC"),
    ("1899 Belmont Ave", "Dolphin Property Services LLC"),
    ("1900 Belmont Ave", "Dolphin Property Services LLC"),
    ("1908 Belmont Ave", "Dolphin Property Services LLC"),
    ("2083 Mohegan Ave", "Dolphin Property Services LLC"),
    ("2088 Mohegan Ave", "Dolphin Property Services LLC"),
    ("2090 Mohegan Ave", "Dolphin Property Services LLC"),
    ("1892 Arthur Ave", "Dolphin Property Services LLC"),
    ("1133 Ogden Ave", "Dolphin Property Services LLC"),
    ("Morningside - 107 West 109th St", "Dolphin Property Services LLC"),
    ("287 Audubon Avenue", "Dolphin Property Services LLC"),
    ("Deschler - 1871 7th Ave (Adam Clayton Powell Jr)", "Dolphin Property Services LLC"),
    ("Johana - 106 West 144th St", "Dolphin Property Services LLC"),
    ("Morris Heights Mews - 47 West 175th St.", "Dolphin Property Services LLC"),
    ("Camber - 44 West 175th St.", "Dolphin Property Services LLC"),
    ("Morris Heights Mews - 1695 Grand Ave.", "Dolphin Property Services LLC"),
    ("Camber - Trinity - 2105 Daly Ave", "Dolphin Property Services LLC"),
    ("SHF - 44 West 175th St.", "Dolphin Property Services LLC"),
    ("340 East 93rd St.", "Douglas Elliman Property Management"),
    ("Sea Park North - 2828 West 28th Street", "Gilbane Development Company"),
    ("Sea Park East - 2980 West 28th street", "Gilbane Development Company"),
    ("Sea Park West- 2930 West 30th Street", "Gilbane Development Company"),
    ("2828 W 28th Street", "Gilbane Development Company"),
    ("2930 W 30th Street", "Gilbane Development Company"),
    ("2828 W 28th St", "Gilbane Development Company"),
    ("2930 W 30th St", "Gilbane Development Company"),
    ("2980 W 28th St", "Gilbane Development Company"),
    ("Linden Plaza Building #10", "Grenadier Realty Corp"),
    ("Linden Plaza Building #1", "Grenadier Realty Corp"),
    ("Linden Plaza Building #2", "Grenadier Realty Corp"),
    ("Linden Plaza Building #3", "Grenadier Realty Corp"),
    ("Linden Plaza Building #4", "Grenadier Realty Corp"),
    ("Linden Plaza Building #5", "Grenadier Realty Corp"),
    ("Linden Plaza Building #6", "Grenadier Realty Corp"),
    ("2165 Matthews Avenue", "John B. Lovett & Associates, Ltd."),
    ("MBD New Heights Apts. II (MPLP) - 1093 Jerome Avenue", "MBD Community Housing Corporation"),
    ("MBD New Heights Apts. II (MPLP) - 1095 Jerome Avenue", "MBD Community Housing Corporation"),
    ("MBD New Heights Apts. LP - 970 Anderson Avenue", "MBD Community Housing Corporation"),
    ("MBD New Heights Apts. LP - 1105 Tinton Avenue", "MBD Community Housing Corporation"),
    ("MBD New Heights Apts. LP - 1120 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Mid Bronx Plaza 1690-1700 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Rose Ellen Smith - 1131 West Farms Road", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1661 Southern Boulevard", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1675 Southern Boulevard", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1345 Southern Boulevard", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1816 Crotona Park East", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 909 East 173rd Street", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 960 East 173rd Street", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1174 West Farms Road", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 961 East 173rd Sreet", "MBD Community Housing Corporation"),
    ("MBD Mid Bronx Plaza - 1441 Boston Road", "MBD Community Housing Corporation"),
    ("MBD Rose Ellen Smith - 1711 Hoe Avenue", "MBD Community Housing Corporation"),
    ("MBD WE Mobley - 1714 Crotona Park East", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1160 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1415 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1434 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1438 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1665 Bryant Avenue", "MBD Community Housing Corporation"),
    ("MBD WE Mobley - 945 East 174th Street", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1014 Home Street", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1522 Vyse Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1536 Vyse Avenue", "MBD Community Housing Corporation"),
    ("MBD Silva Taylor - 1566 Vyse Avenue", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1346 Lyman Place", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1359 Lyman Place", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1360 Lyman Place", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1365 Lyman Place", "MBD Community Housing Corporation"),
    ("MBD Don L W LLC - 1366 Lyman Place", "MBD Community Housing Corporation"),
    ("MBD Don LW - 1389 Stebbins Avenue", "MBD Community Housing Corporation"),
    ("MBD DON LW - 1327 Southern Blvd", "MBD Community Housing Corporation"),
    ("474 West 238th St", "Norwax Associates Inc."),
    ("511 East 12th St", "Novum Properties"),
    ("239 West 139th Street", "St Marks Methodist Church"),
    ("804 West 180th St", "Synoptic Management Corp."),
    ("Camber - Seneca - 1314 Seneca Ave", "The Wavecrest Management Team, Ltd."),
    ("2403 Adam Clayton Powell Blvd", "The Wavecrest Management Team, Ltd."),
    ("2405 Adam Clayton Powell Blvd", "The Wavecrest Management Team, Ltd."),
    ("2109-2111 Amsterdam Ave", "The Wavecrest Management Team, Ltd."),
    ("99 Fort Washington Ave", "The Wavecrest Management Team, Ltd."),
    ("182 St Nicholas Ave", "The Wavecrest Management Team, Ltd."),
    ("1504 Amsterdam Ave", "The Wavecrest Management Team, Ltd."),
    ("110 West 139th St", "The Wavecrest Management Team, Ltd."),
    ("120 East 123rd St", "The Wavecrest Management Team, Ltd."),
    ("120 West 140th St", "The Wavecrest Management Team, Ltd."),
    ("136 West 139th St", "The Wavecrest Management Team, Ltd."),
    ("138 West 139th St", "The Wavecrest Management Team, Ltd."),
    ("151 West 142nd St", "The Wavecrest Management Team, Ltd."),
    ("173 West 140th St", "The Wavecrest Management Team, Ltd."),
    ("335 East 111th St", "The Wavecrest Management Team, Ltd."),
    ("450 West 164th St", "The Wavecrest Management Team, Ltd."),
    ("457 West 164th St", "The Wavecrest Management Team, Ltd."),
    ("500 West 164th St", "The Wavecrest Management Team, Ltd."),
    ("500 West 177th St", "The Wavecrest Management Team, Ltd."),
    ("501 West 176th St", "The Wavecrest Management Team, Ltd."),
    ("502 West 177th St", "The Wavecrest Management Team, Ltd."),
    ("503 West 177th St", "The Wavecrest Management Team, Ltd."),
    ("506 West 176th St", "The Wavecrest Management Team, Ltd."),
    ("506 West 177th St", "The Wavecrest Management Team, Ltd."),
    ("509 West 176th St", "The Wavecrest Management Team, Ltd."),
    ("510 West 176th St", "The Wavecrest Management Team, Ltd."),
    ("511 West 134th St", "The Wavecrest Management Team, Ltd."),
    ("514 West 134th St", "The Wavecrest Management Team, Ltd."),
    ("514 West 176th St", "The Wavecrest Management Team, Ltd."),
    ("515 West 134th St", "The Wavecrest Management Team, Ltd."),
    ("529 West 133rd St", "The Wavecrest Management Team, Ltd."),
    ("545 West 156th St", "The Wavecrest Management Team, Ltd."),
    ("117 West 90th St", "The Wavecrest Management Team, Ltd."),
    ("133 West 90th St", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1454 Grand Concourse Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1503-05 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1424-26 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1563 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1525-33 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1206 Westchester Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1410 Grand Concourse Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1512-14 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1550 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 373 E 183rd Street", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1610-16 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("301 W 46th Street", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1465-75-77 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1615-17 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1575 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1561 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 620 East 13th Street", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1530-32 Townsend Avenue", "The Wavecrest Management Team, Ltd."),
    ("1484 Inwood Avenue", "The Wavecrest Management Team, Ltd."),
    ("1563 Walton Ave", "The Wavecrest Management Team, Ltd."),
    ("1561 Walton Avenue", "The Wavecrest Management Team, Ltd."),
    ("SHF - 35 Marcy Place", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1615 St. John\'s Place", "The Wavecrest Management Team, Ltd."),
    ("SHF - 1484 Inwood Avenue", "The Wavecrest Management Team, Ltd."),
    ("35 Marcy Place", "The Wavecrest Management Team, Ltd."),
    ("SHF - 82 Rutgers Slip", "Grenadier Realty Corp."),
    ("140 Claremont Ave:Gas Conversion", "Total Management NYC LLC"),
    ("140 Claremont Ave", "Total Management NYC LLC"),
    ("371 West 123rd St", "Daisy Management"),
    ("PPSP - 221 Linden Blvd - A-B", "Twin Pines Management"),
    ("PPSP - 221 Linden Blvd - C-D", "Twin Pines Management"),
    ("PPSP - 91-95 East 18th St", "Twin Pines Management"),
    ("West Brighton Building #6", "Twin Pines Management"),
    ("PPSP - 280 East 21st St", "Twin Pines Management"),
    ("PPSP - 666 Ocean Ave.", "Twin Pines Management"),
    ("PPSP - 682 Ocean Ave.", "Twin Pines Management"),
    ("1140 Woodycrest Ave.", "Twin Pines Management"),
    ("28 Lamartine Terrace", "Twin Pines Management"),
    ("PPSP - 672 Ocean Ave", "Twin Pines Management"),
    ("2363 Southern Blvd.", "Twin Pines Management"),
    ("1105 Jerome Avenue", "Twin Pines Management"),
    ("280 East 161st St.", "Twin Pines Management"),
    ("50 St. Andrews Pl", "Twin Pines Management"),
    ("101 West 165th", "Twin Pines Management"),
    ("2199 Holland Avenue", "Garthchester Realty"),
    ("11 Park Ave.", "Garthchester Realty"),
    ("129 E 102nd St.", "All Area Realty Services"),
    ("129 East 102nd St - Boiler Replacement", "All Area Realty Services"),
    ("222 East 35th St", "Veritas Property Management"),
    ("105 East 29th St.", "Venture NY Property Management, LLC"),
    ("439 West 46th St", "Venture NY Property Management, LLC"),
    ("230 East 179th St.", "Jonas Bronck Housing Company Inc."),
]

def get_updated_customer(row):
    prop = str(row.get("Property / Project", "") or "").strip()
    cust = str(row.get("Customer", "") or "").strip()
    for pattern, new_cust in CUSTOMER_OVERRIDES:
        if pattern.lower() in prop.lower():
            return new_cust
    return cust

df["Updated Customer"] = df.apply(get_updated_customer, axis=1)


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
    filtered[["Customer", "Updated Customer", "Property / Project", "Project Manager", "Invoice", "Balance", "Date"]].style.format({
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

snapshot_raw = conn.query("""
    SELECT
        snapshot_date,
        aging_bucket,
        aging_bucket_sort,
        outstanding_balance,
        department_name,
        project_manager,
        property_name,
        billing_customer_name
    FROM ANALYTICS.GOLD.FCT_AR_INVOICE_SNAPSHOT
    ORDER BY snapshot_date, aging_bucket_sort
""")

# Rename columns to match dashboard conventions
snapshot_raw = snapshot_raw.rename(columns={
    "SNAPSHOT_DATE": "Week", "AGING_BUCKET": "Aging Bucket",
    "AGING_BUCKET_SORT": "aging_bucket_sort", "OUTSTANDING_BALANCE": "Amount",
    "DEPARTMENT_NAME": "Department", "PROJECT_MANAGER": "Project Manager",
    "PROPERTY_NAME": "Property / Project", "BILLING_CUSTOMER_NAME": "Customer",
})

if len(snapshot_raw) > 0:
    # Clean department names in snapshot too
    snapshot_raw["Department"] = snapshot_raw["Department"].str.replace(r"^DFC\s*-\s*", "", regex=True)

    # Apply same filters to snapshot data
    snap_filtered = snapshot_raw.copy()
    if dept_filter:
        snap_filtered = snap_filtered[snap_filtered["Department"].isin(dept_filter)]
    if property_filter:
        snap_filtered = snap_filtered[snap_filtered["Property / Project"].isin(property_filter)]
    if customer_search:
        snap_filtered = snap_filtered[snap_filtered["Customer"].str.contains(customer_search, case=False, na=False)]
    if pm_filter:
        snap_filtered = snap_filtered[snap_filtered["Project Manager"].isin(pm_filter)]

    # Aggregate filtered snapshot data
    snapshot_df = snap_filtered.groupby(["Week", "Aging Bucket", "aging_bucket_sort"], as_index=False)["Amount"].sum()
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
