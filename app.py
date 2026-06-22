import streamlit as st
import pandas as pd
import altair as alt
import base64
from pathlib import Path

import auth

# --- Page config ---
st.set_page_config(
    page_title="AR Dashboard — Dual Fuel",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide default sidebar nav (we use custom st.page_link instead)
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

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
    box-sizing: border-box;
    display: flex;
    justify-content: center;
}
/* Center the chart inside its bordered box (the old `margin: 0 16px` stacked
   on top of the container padding and pushed the chart off-center). */
[data-testid="stVegaLiteChart"] > div {
    margin: 0 auto;
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
/* Hide the Community Cloud status/badge chrome (best-effort). Note: the
   bottom-right "Manage app" button is only visible to people with write access
   to the GitHub repo, so anonymous viewers never see or can use it. */
[data-testid="stStatusWidget"] { display: none !important; }
[class*="viewerBadge"] { display: none !important; }
button[title="Manage app"], [data-testid="manageAppButton"] { display: none !important; }
/* Hide the (invisible) cookie-controller component iframe so it takes no space */
iframe[title="streamlit_cookies_controller.cookie_controller"] {
    display: none !important;
    height: 0 !important;
}

/* === Restore Material icon font ===
   The global `* { font-family: Inter !important }` rule above also lands on
   Streamlit's Material icons, which makes the sidebar collapse control render
   its ligature name ("keyboard_double_arrow_left") as literal text. Re-assert
   the icon font on icon elements so the arrow shows correctly. */
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
.material-icons, .material-icons-outlined,
.material-symbols-outlined, .material-symbols-rounded {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}

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


# --- Auth state + cookie-based auto-login ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Cookie controller renders on every run (login + dashboard) so we can both
# read the "stay logged in" cookie and clear it on sign-out. Falls back to None
# if the component can't load — the app still works, just without persistence.
controller = auth.get_controller()
auth.try_cookie_login(controller)

# Write the persistent-login cookie on the run right AFTER a successful login —
# i.e. a run that renders to completion and isn't aborted by st.rerun(). If we
# set it in the same run as the rerun, the component's cookie write is dropped
# and nothing persists across refreshes.
if st.session_state.authenticated and st.session_state.pop("_issue_cookie", False):
    auth.issue_cookie(controller, st.session_state.get("username", ""))

if not st.session_state.authenticated:
    # On the login screen, hide the (empty, non-functional) sidebar and its
    # collapse/expand control so it reads as a clean login page.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stAppViewContainer"] > section:first-child { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
        f'<p class="login-sub">Sign In</p>'
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
                st.session_state.username = username
                st.session_state["_issue_cookie"] = True
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()


# --- Dashboard (only runs after login) ---
conn = st.connection("snowflake")

df = conn.query("""
    SELECT
        billing_customer_name   AS "Customer",
        COALESCE(NULLIF(property_name, ''), NULLIF(project_name, '')) AS "Property / Project",
        invoice_number          AS "Invoice",
        outstanding_balance::FLOAT AS "Balance",
        invoice_date            AS "Invoice Date",
        due_date                AS "Due Date",
        aging_bucket            AS "Aging Bucket",
        department_name         AS "Department",
        sa_type                 AS "SA Type",
        sa_number               AS "SA Number",
        job_number              AS "Job Number",
        days_past_due           AS "Days Past Due",
        project_manager         AS "Project Manager"
    FROM ANALYTICS.GOLD.FCT_INVOICE_OPEN
    ORDER BY due_date ASC
""", ttl=3600)  # cache 1 hour; "Refresh data" forces a fresh pull

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

# === SA/MA classification — valid SA/MA = has agreement number, NO job number (recurring billing) ===
df["SA/MA"] = df["SA Number"].str[:2].where(
    (df["SA Number"].str[:2].isin(["SA", "MA"])) & ((df["Job Number"].isna()) | (df["Job Number"] == "")),
    ""
)
# Agreement match key for unique property counting (customer | property)
df["Agreement Key"] = df["Customer"].fillna("") + " | " + df["Property / Project"].fillna("")

# === Collector Assignment (based on billing customer or updated customer) ===
COLLECTOR_MAP = {
    "Notias Construction": "John Viado", "Gilbane APEX": "John Viado",
    "ETC Companies LLC": "John Viado", "The Wavecrest Management Team, Ltd.": "John Viado",
    "Grenadier Realty Corp": "John Viado", "AKAM Associates, Inc.": "John Viado",
    "AMK Contracting Corp": "John Viado", "CSA Preservation HTC LLC": "John Viado",
    "Dolphin Property Services LLC": "John Viado", "MBD Community Housing Corporation": "John Viado",
    "C&C Apartment Management LLC": "John Viado",
    "Diego Beekman Mutual Housing Association, HDFC": "John Viado",
    "Maxwell Kates": "John Viado", "Levine Builders": "John Viado",
    "Twin Pines Management": "John Viado", "Century Management Services, Inc.": "John Viado",
    "Gilbane Development Company": "John Viado", "Yeshiva University": "John Viado",
    "Argo Real Estate, LLC": "John Viado", "Dalan Management": "John Viado",
    "Fairstead Management": "John Viado", "Orsid New York": "John Viado",
    "Shinda Management Corp.": "John Viado", "MD2 Property Group, LLC": "John Viado",
    "East Harlem Council for Human Svcs, Inc": "John Viado",
    "Wilshire Pacific Builders, LLC": "John Viado", "Canvas Property Group": "John Viado",
    "CBRE Property Management": "John Viado", "Sugar Hill Capital Partners LLC": "John Viado",
    "SW Management": "John Viado", "Settlement Housing Fund": "John Viado",
    "Volmar Construction": "John Viado", "126-8 Fifth Ave, LLC": "John Viado",
    "Hudsoncrest Properties": "John Viado", "Pact Renaissance Collaborative": "John Viado",
    "Orsid Realty1": "John Viado", "Bennett Towers Apartment Inc": "John Viado",
    "Carbon Quest, Inc.": "John Viado", "Allied Partners": "John Viado",
    "419 Builders LLC": "John Viado", "Pinnacle City Living": "John Viado",
    "TEG Bronx Park LLC": "John Viado", "Camber Property Group": "John Viado",
    "Willdan Lighting & Electrical Inc": "John Viado", "B&D Heating LLC": "John Viado",
    "4 East 80th LLC": "John Viado", "Guaranteed Home Improvement LLC": "John Viado",
    "Terris Realty LLC": "Ryann Rayo", "ELH Mgmt, LLC": "Ryann Rayo",
    "Related Properties": "Ryann Rayo", "Community Realty Management": "Ryann Rayo",
    "TB Construction Services LLC": "Ryann Rayo", "Finger Management": "Ryann Rayo",
    "New Bedford Management": "Ryann Rayo", "ABC Management": "Ryann Rayo",
    "Lemle & Wolff Construction Corp": "Ryann Rayo",
    "Clinton Housing Development Co.": "Ryann Rayo", "Robert E. Hill, Inc.": "Ryann Rayo",
    "699-711 BKLYN Realty LLC": "Ryann Rayo", "David Associates": "Ryann Rayo",
    "Tristar Management": "Ryann Rayo", "Andrews Organization": "Ryann Rayo",
    "Clinton Management": "Ryann Rayo", "Stonebridge Realty Management": "Ryann Rayo",
    "Kraus Management": "Ryann Rayo", "C Gershon Company, Inc": "Ryann Rayo",
    "Winn Residential": "Ryann Rayo", "Total Management NYC LLC": "Ryann Rayo",
    "ABC Restoration Inc.": "Ryann Rayo",
    "Hunter Roberts Construction Group, LLC": "Ryann Rayo",
    "Midas Management": "Ryann Rayo", "All Area Realty Services": "Ryann Rayo",
    "Columbus Property Mangement": "Ryann Rayo", "Jonathan Rose Companies": "Ryann Rayo",
    "Douglas Elliman Property Management": "Ryann Rayo",
    "Jonas Bronck Housing Company Inc.": "Ryann Rayo", "Tri-Hill Management": "Ryann Rayo",
    "Hazelton Capital Group": "Ryann Rayo", "Zeta Charter Schools, Inc.": "Ryann Rayo",
    "Daisy Management": "Ryann Rayo", "Martino Mangement & Consulting": "Ryann Rayo",
    "Big Apple Management": "Ryann Rayo", "Plaza Management": "Ryann Rayo",
    "First Service Residential": "Ryann Rayo", "Leiter Management": "Ryann Rayo",
    "Belveron Partners": "Ryann Rayo", "SKS Entreprises LLC": "Ryann Rayo",
    "Halstead Management Co": "Ryann Rayo", "Alwest Management": "Ryann Rayo",
    "Concord Management of NY": "Ryann Rayo", "Charles Greenthal Management": "Ryann Rayo",
    "Harborview Properties": "Ryann Rayo", "Aguilar Gardens Inc.": "Ryann Rayo",
    "Phillibert Estate Corp": "Ryann Rayo", "Total Realty Associates, Inc.": "Ryann Rayo",
    "Scalzo Property Management": "Ryann Rayo", "Pride Property Management": "Ryann Rayo",
    "White Management": "Ryann Rayo", "108 West 78th St Owners Corp": "Ryann Rayo",
    "MGT Property Group": "Ryann Rayo", "Taconic Investment Partners": "Ryann Rayo",
    "Emcor": "Ryann Rayo", "Luxstone Partners": "Ryann Rayo",
    "DynaMax Realty Inc": "Ryann Rayo", "Anker Management": "Ryann Rayo",
    "Ritz South Management": "Ryann Rayo", "SHP Management": "Ryann Rayo",
    "1003-05 East 174 Street HDFC": "Ryann Rayo", "The Bisceglia Group": "Ryann Rayo",
    "John B. Lovett & Associates, Ltd.": "Ryann Rayo", "Lori-Zee Corp": "Ryann Rayo",
    "The Sherwin-Williams Company": "Ryann Rayo", "Safety Facility Services": "Ryann Rayo",
    "Panasia Estate Inc": "Ryann Rayo", "Windsor Management Corp": "Ryann Rayo",
    "Metro Management": "Ryann Rayo", "BOTA Property Management LLC": "Ryann Rayo",
    "796-798 Ninth Successor LLC": "Ryann Rayo",
    "RockBridge Property Mngt LLC": "Ryann Rayo",
    "Dual Fuel - Installations": "Ryann Rayo",
    "Fordham United Methodist Church": "Ryann Rayo", "Spigro Management": "Ryann Rayo",
    "Synoptic Management Corp.": "Ryann Rayo", "Casa Cipriani New York": "Ryann Rayo",
    "Neptune Mechanical": "Rechell Jongco", "River City Builders LLC": "Rechell Jongco",
    "Akelius Real Estate Mangement LLC": "Rechell Jongco",
    "Faria Management": "Rechell Jongco",
    "Indoor Air Quality Champs, Inc.": "Rechell Jongco",
    "Calgi Construction": "Rechell Jongco",
    "NY Foundation for Senior Citizens, Inc.": "Rechell Jongco",
    "Renewal Chateau JV": "Rechell Jongco", "Denali Management": "Rechell Jongco",
    "Stillman Management": "Rechell Jongco",
    "Montrose Management Associates, Inc.": "Rechell Jongco",
    "Ferrara Management": "Rechell Jongco",
    "Monadnock Construction, Inc.": "Rechell Jongco",
    "Gramatan Management, Inc.": "Rechell Jongco",
    "Memphis Downtown Condominiums": "Rechell Jongco",
    "Green Cedar Management": "Rechell Jongco",
    "Venture NY Property Management, LLC": "Rechell Jongco",
    "Community Housing Management Corp": "Rechell Jongco",
    "OTB Management": "Rechell Jongco", "Garthchester Realty": "Rechell Jongco",
    "Apex ETC JV": "Rechell Jongco", "Platzner International Group": "Rechell Jongco",
    "Grenadier Realty Corp.": "Rechell Jongco",
    "Harlem Property Management": "Rechell Jongco",
    "City of Mount Vernon, NY": "Rechell Jongco",
    "South Glo Properties": "Rechell Jongco",
    "St Marks Methodist Church": "Rechell Jongco", "BCD Owner LLC": "Rechell Jongco",
    "Nina Dunn": "Rechell Jongco", "Genesis Companies": "Rechell Jongco",
    "Choice New York Management": "Rechell Jongco",
    "Solstice Residential Group, LLC": "Rechell Jongco",
    "Sandberg Management": "Rechell Jongco",
    "Camelot Realty Group": "Rechell Jongco",
    "Langsam Property Managment": "Rechell Jongco",
    "Village of Larchmont": "Rechell Jongco", "City Urban Realty": "Rechell Jongco",
    "Esra Management LLC": "Rechell Jongco",
    "Rapoport Construction Corp": "Rechell Jongco",
    "Veritas Property Management": "Rechell Jongco",
    "M&L Milevoi Realty": "Rechell Jongco",
    "Scarsdale Home Improvements": "Rechell Jongco",
    "Kalel Companies": "Rechell Jongco", "Apex Management Group": "Rechell Jongco",
    "Ivy Property Management": "Rechell Jongco",
    "JCC Mid Westchester": "Rechell Jongco", "Ventura Land Corp": "Rechell Jongco",
    "ABC Tank Repair & Lining Inc": "Rechell Jongco", "CDM Smith": "Rechell Jongco",
    "MDG": "Rechell Jongco", "SKS Enterprises": "Rechell Jongco",
    "Elite Management LLC": "Rechell Jongco", "Lineland Management": "Rechell Jongco",
    "MBD New Heights Apts. LP": "Rechell Jongco", "CKC Associates LLC": "Rechell Jongco",
    "SAP Construction LLC": "Rechell Jongco", "Sassouni Management": "Rechell Jongco",
    "Sheridan Properties": "Rechell Jongco",
    "St. John's Espiscopal Hospital": "Rechell Jongco",
    "Noam Management Group": "Rechell Jongco",
    "VPH Management Services LLC": "Rechell Jongco",
    "Librett Real Estate Group": "Rechell Jongco",
    "Lolo Montague, LLC": "Rechell Jongco",
    "Blue Woods Management": "Rechell Jongco",
    "Archer Property Management": "Rechell Jongco",
    "Aram Gadarigian": "Rechell Jongco", "Novum Properties": "Rechell Jongco",
    "47 Fort Washington Ave HDFC": "Rechell Jongco",
    "Markers Capital Partners": "Rechell Jongco",
    "Homeowner association of 110 Neptune": "Rechell Jongco",
    "Empire State Equities": "Rechell Jongco",
    "Orbach Afforable Housing Solutions": "Rechell Jongco",
    "Infinity Contracting Services": "Rechell Jongco",
    "Pine Management, Inc.": "Rechell Jongco", "Maria Schwartz": "Rechell Jongco",
    "Famurb Company LLC": "Rechell Jongco", "Fantis Foods, Inc.": "Rechell Jongco",
    "Or Trabelsi": "Rechell Jongco", "QN Realty LLC": "Rechell Jongco",
    "E & G Management": "Rechell Jongco", "Brodsky": "Rechell Jongco",
    "CG West 181st Street": "Rechell Jongco",
    "Medallion Real Estate LLC": "Rechell Jongco",
    "New Aim Realty": "Rechell Jongco",
    "L & M Development Partners": "Rechell Jongco",
    "Cornell Pace Inc": "Rechell Jongco",
    "Solar Realty Management": "Rechell Jongco",
    "Park Avenue South Managment": "Rechell Jongco",
    "Atlantic Commons": "Rechell Jongco", "Roni Jesselson": "Rechell Jongco",
    "Sand Managements": "Rechell Jongco", "The Moinian Group": "Rechell Jongco",
    "Je Partners Group LLC": "Rechell Jongco",
    "Don Gringer": "Rechell Jongco", "Annal Management Co., Ltd": "Rechell Jongco",
    "The Ader Group": "Rechell Jongco",
    "Jenkins Portfolio Companies LLC": "Rechell Jongco",
    "JLP Metro Management": "Rechell Jongco",
    "Magen David Yeshiva": "Rechell Jongco", "Breukelen One LLC": "Rechell Jongco",
    "Rich Energy Solutions": "Rechell Jongco",
    "Locust Cove Management": "Rechell Jongco",
    "Caprice Management Corp": "Rechell Jongco",
    "Norwax Associates Inc.": "Rechell Jongco",
    "Medallion Real Estate LLC": "Rechell Jongco",
}

def get_collector(row):
    # Check updated customer first, then original customer
    updated = str(row.get("Updated Customer", "") or "").strip()
    original = str(row.get("Customer", "") or "").strip()
    return COLLECTOR_MAP.get(updated, COLLECTOR_MAP.get(original, "")
)

df["Collector"] = df.apply(get_collector, axis=1)


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

    # Custom navigation links (replaces default sidebar nav)
    st.page_link("app.py", label="AR Dashboard", icon="📊")
    st.page_link("pages/1_Project_Analysis.py", label="Project Analysis", icon="📈")
    st.page_link("pages/2_Project_Costs.py", label="Project Costs", icon="💰")

    # Session controls
    _user = st.session_state.get("username", "")
    if _user:
        st.caption(f"Signed in as {_user}")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()  # force the next queries to re-hit Snowflake
        st.rerun()
    if st.button("Sign out", use_container_width=True):
        auth.sign_out(controller)

    st.markdown("---")

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
    sa_ma_filter = st.multiselect(
        "SA / MA",
        options=["SA", "MA"],
    )
    collector_filter = st.multiselect(
        "Collector",
        options=sorted(df["Collector"].loc[df["Collector"] != ""].unique()),
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
if sa_ma_filter:
    filtered = filtered[filtered["SA/MA"].isin(sa_ma_filter)]
if collector_filter:
    filtered = filtered[filtered["Collector"].isin(collector_filter)]


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

sa_col1, sa_col2 = st.columns(2)
with sa_col1:
    ma_count = filtered.loc[filtered["SA/MA"] == "MA", "Agreement Key"].nunique()
    st.metric("MA", f"{ma_count}")
with sa_col2:
    sa_count = filtered.loc[filtered["SA/MA"] == "SA", "Agreement Key"].nunique()
    st.metric("SA", f"{sa_count}")

st.divider()

# --- Data table ---
st.markdown(
    '<p class="section-label">Open Invoices</p>',
    unsafe_allow_html=True,
)

st.dataframe(
    filtered[["Customer", "Updated Customer", "Collector", "Property / Project", "Project Manager", "SA/MA", "Invoice", "Balance", "Invoice Date", "Due Date"]].style.format({
        "Balance": "${:,.2f}",
        "Invoice Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else "",
        "Due Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else ""
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
        outstanding_balance::FLOAT AS outstanding_balance,
        department_name,
        project_manager,
        property_name,
        billing_customer_name
    FROM ANALYTICS.GOLD.FCT_AR_INVOICE_SNAPSHOT
    ORDER BY snapshot_date, aging_bucket_sort
""", ttl=3600)  # cache 1 hour; "Refresh data" forces a fresh pull

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
                axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10),
            ),
            y=alt.Y(
                "Amount:Q",
                title="AR ($)",
                axis=alt.Axis(format="$,.0f", labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15),
            ),
            color=alt.Color(
                "Aging Bucket:N",
                scale=color_scale,
                legend=alt.Legend(title="Aging Bucket", orient="top", labelColor="#c0c0c0", titleColor="#FFFFFF", titleFontWeight="bold", labelLimit=300, columnPadding=20),
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
        .properties(padding={"top": 30, "right": 20, "left": 20, "bottom": 5})
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e")
    )
    st.altair_chart(combined, use_container_width=True)
else:
    st.info("No snapshot data yet. The first snapshot will appear after Friday at 5 PM.")
# end of app.py
