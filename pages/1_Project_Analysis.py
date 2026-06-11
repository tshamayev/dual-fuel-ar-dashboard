import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Project Analysis — Dual Fuel",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Reuse the same CSS from main app ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important; }
[data-testid="stAppViewContainer"] { background-color: #000000; }
[data-testid="stHeader"] { background-color: #000000; }
[data-testid="stSidebar"] { background-color: #0d0d12; border-right: 1px solid #1e1e2e; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #141422 0%, #1a1a2e 100%);
    border: 1px solid #2a2a3e; border-top: 3px solid #C30017;
    border-radius: 8px; padding: 20px 24px;
}
[data-testid="stMetricLabel"] p { color: #808090 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem !important; font-weight: 700 !important; }
h1, h2 { color: #FFFFFF !important; font-weight: 700 !important; }
h3 { color: #FFFFFF !important; font-weight: 600 !important; }
a.headerLink, h1 a, h2 a, h3 a { display: none !important; }
hr { border: none !important; height: 1px !important; background: linear-gradient(90deg, transparent, #C30017, transparent) !important; margin: 24px 0 !important; }
[data-testid="stDataFrame"] { background-color: #141422; border: 1px solid #2a2a3e; border-radius: 8px; overflow: hidden; }
[data-testid="stVegaLiteChart"] { background-color: #141422; border: 1px solid #2a2a3e; border-radius: 8px; padding: 16px; overflow: hidden; box-sizing: border-box; }
[data-testid="stVegaLiteChart"] > div { margin: 0 16px; }
[data-testid="stMarkdownContainer"] p { color: #e0e0e0; }
[data-testid="stSidebar"] label { color: #808090 !important; text-transform: uppercase; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.8px; }
.section-label { color: #808090 !important; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #e0e0e0; }
.sidebar-logo { text-align: center; padding: 16px 0 12px 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 24px; }
.sidebar-logo img { width: 44px; height: 44px; }
.sidebar-title { color: #FFFFFF; font-size: 1rem; font-weight: 700; margin: 10px 0 2px 0; }
.sidebar-subtitle { color: #C30017; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin: 0; }
.filter-header { color: #C30017 !important; font-size: 0.72rem !important; font-weight: 700 !important; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 8px !important; margin-bottom: 12px !important; }
</style>
""", unsafe_allow_html=True)


# --- Login gate (shared session state) ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in from the main AR Dashboard page.")
    st.stop()


# --- Data ---
conn = st.connection("snowflake")

df = conn.query("""
    SELECT
        project_id,
        project_number,
        project_name,
        project_status,
        project_manager,
        department_name,
        billing_customer_name,
        property_name,
        updated_contract_amount::FLOAT       AS updated_contract_amount,
        updated_cost_budget_amount::FLOAT    AS updated_cost_budget_amount,
        month_date,
        monthly_invoicing::FLOAT             AS monthly_invoicing,
        monthly_cost::FLOAT                  AS monthly_cost,
        monthly_labor_cost::FLOAT            AS monthly_labor_cost,
        monthly_material_cost::FLOAT         AS monthly_material_cost,
        monthly_equipment_cost::FLOAT        AS monthly_equipment_cost,
        monthly_subcontractor_cost::FLOAT    AS monthly_subcontractor_cost,
        monthly_overhead_cost::FLOAT         AS monthly_overhead_cost,
        monthly_other_cost::FLOAT            AS monthly_other_cost,
        cumulative_revenue::FLOAT            AS cumulative_revenue,
        cumulative_cost::FLOAT               AS cumulative_cost,
        pct_billed::FLOAT                    AS pct_billed,
        pct_cost::FLOAT                      AS pct_cost,
        overbilled_underbilled::FLOAT        AS overbilled_underbilled
    FROM ANALYTICS.GOLD.FCT_PROJECT_MONTHLY_ANALYSIS
    ORDER BY project_number, month_date
""", ttl=0)

# Rename columns for display
df.columns = [c.upper() for c in df.columns]
df = df.rename(columns={
    "PROJECT_ID": "Project ID", "PROJECT_NUMBER": "Project #",
    "PROJECT_NAME": "Project Name", "PROJECT_STATUS": "Status",
    "PROJECT_MANAGER": "PM", "DEPARTMENT_NAME": "Department",
    "BILLING_CUSTOMER_NAME": "Customer", "PROPERTY_NAME": "Property",
    "UPDATED_CONTRACT_AMOUNT": "Contract", "UPDATED_COST_BUDGET_AMOUNT": "Cost Budget",
    "MONTH_DATE": "Month", "MONTHLY_INVOICING": "Monthly Invoicing",
    "MONTHLY_COST": "Monthly Cost", "MONTHLY_LABOR_COST": "Labor",
    "MONTHLY_MATERIAL_COST": "Material", "MONTHLY_EQUIPMENT_COST": "Equipment",
    "MONTHLY_SUBCONTRACTOR_COST": "Subcontractor", "MONTHLY_OVERHEAD_COST": "Overhead",
    "MONTHLY_OTHER_COST": "Other", "CUMULATIVE_REVENUE": "Cumulative Revenue",
    "CUMULATIVE_COST": "Cumulative Cost", "PCT_BILLED": "% Billed",
    "PCT_COST": "% Cost", "OVERBILLED_UNDERBILLED": "Over/Under Billed",
})


# === SIDEBAR ===
with st.sidebar:
    import base64
    from pathlib import Path
    flame_path = Path(__file__).parent.parent / "Flame.png"
    if flame_path.exists():
        flame_b64 = base64.b64encode(flame_path.read_bytes()).decode()
        st.markdown(
            f'<div class="sidebar-logo">'
            f'<img src="data:image/png;base64,{flame_b64}">'
            f'<p class="sidebar-title">Dual Fuel</p>'
            f'<p class="sidebar-subtitle">Project Analysis</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Custom navigation links
    st.page_link("app.py", label="AR Dashboard", icon="📊")
    st.page_link("pages/1_Project_Analysis.py", label="Project Analysis", icon="📈")
    st.markdown("---")

    st.markdown('<p class="filter-header">Filters</p>', unsafe_allow_html=True)

    # Project selector — use "Number — Name" to distinguish duplicates
    project_lookup = df.drop_duplicates(subset=["Project ID"])[["Project #", "Project Name", "Project ID"]].dropna(subset=["Project #"])
    project_lookup["Label"] = project_lookup["Project #"].astype(str) + " — " + project_lookup["Project Name"].fillna("")
    project_options = sorted(project_lookup["Label"].unique())
    selected_label = st.selectbox("Project", options=["All"] + project_options)

    # Date range
    all_months = sorted(df["Month"].dropna().unique())
    date_range = st.select_slider(
        "Date Range",
        options=all_months,
        value=(all_months[0], all_months[-1]) if len(all_months) > 1 else (all_months[0], all_months[0]),
        format_func=lambda x: pd.to_datetime(x).strftime("%b %Y"),
    )

    # Monthly vs Cumulative toggle
    view_mode = st.radio("View Mode", ["Monthly", "Cumulative"], horizontal=True)


# Build display label column for matching
df["Project Label"] = df["Project #"].astype(str) + " — " + df["Project Name"].fillna("")

# Apply filters
filtered = df.copy()
selected_project = selected_label  # alias for readability
if selected_project != "All":
    filtered = filtered[filtered["Project Label"] == selected_project]
filtered = filtered[(filtered["Month"] >= date_range[0]) & (filtered["Month"] <= date_range[1])]


# === MAIN CONTENT ===
st.markdown('<p class="section-label">Project Analysis</p>', unsafe_allow_html=True)

if selected_project != "All":
    row = filtered.iloc[-1] if len(filtered) > 0 else None
    if row is not None:
        st.markdown(f"## Project {row['Project #']} — {row['Project Name']}")
        st.markdown(f"*{row['Customer']} | {row['Property']} | PM: {row['PM']}*")
    else:
        st.markdown(f"## {selected_project}")
else:
    st.markdown("## All Projects")

# --- Metrics ---
if len(filtered) > 0 and selected_project != "All":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contract", f"${filtered['Contract'].iloc[0]:,.0f}" if pd.notna(filtered['Contract'].iloc[0]) else "—")
    with col2:
        st.metric("Cost Budget", f"${filtered['Cost Budget'].iloc[0]:,.0f}" if pd.notna(filtered['Cost Budget'].iloc[0]) else "—")
    with col3:
        latest_pct_billed = filtered["% Billed"].iloc[-1]
        st.metric("% Billed", f"{latest_pct_billed * 100:.1f}%" if pd.notna(latest_pct_billed) else "—")
    with col4:
        latest_pct_cost = filtered["% Cost"].iloc[-1]
        st.metric("% Cost", f"{latest_pct_cost * 100:.1f}%" if pd.notna(latest_pct_cost) else "—")

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Total Revenue", f"${filtered['Cumulative Revenue'].iloc[-1]:,.0f}")
    with col6:
        st.metric("Total Cost", f"${filtered['Cumulative Cost'].iloc[-1]:,.0f}")

st.divider()

# --- Compact label formatter for chart bar labels ---
def compact(val):
    """3867195 → '3.9M', 150200 → '150.2K', 800 → '800'"""
    if pd.isna(val) or val == 0:
        return "0"
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"{val / 1_000:.1f}K"
    else:
        return f"{val:.0f}"

# --- Charts ---
if len(filtered) > 0:
    filtered["Month Label"] = pd.to_datetime(filtered["Month"]).dt.strftime("%b %Y")

    inv_col = "Cumulative Revenue" if view_mode == "Cumulative" else "Monthly Invoicing"
    cost_col = "Cumulative Cost" if view_mode == "Cumulative" else "Monthly Cost"

    # Aggregate if "All" projects — always sum monthly values, then compute cumulative
    if selected_project == "All":
        chart_data = filtered.groupby(["Month", "Month Label"], as_index=False).agg({
            "Monthly Invoicing": "sum", "Monthly Cost": "sum"
        }).sort_values("Month")
        chart_data["Cumulative Revenue"] = chart_data["Monthly Invoicing"].cumsum()
        chart_data["Cumulative Cost"] = chart_data["Monthly Cost"].cumsum()
    else:
        chart_data = filtered

    # --- Monthly Revenue Chart ---
    st.markdown('<p class="section-label">Revenue</p>', unsafe_allow_html=True)
    st.markdown(f"### {view_mode} Revenue")

    chart_data["Rev Label"] = chart_data[inv_col].apply(compact)

    inv_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#3b82f6")
        .encode(
            x=alt.X("Month Label:N", title="Month",
                     sort=alt.SortField(field="Month", order="ascending"),
                     axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10)),
            y=alt.Y(f"{inv_col}:Q", title="Amount ($)",
                     axis=alt.Axis(format="$,.0f", labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15)),
            tooltip=[
                alt.Tooltip("Month Label:N", title="Month"),
                alt.Tooltip(f"{inv_col}:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=300)
    )

    inv_text = (
        alt.Chart(chart_data)
        .mark_text(dy=-10, fontSize=10, fontWeight="bold", color="#FFFFFF")
        .encode(
            x=alt.X("Month Label:N", sort=alt.SortField(field="Month", order="ascending")),
            y=alt.Y(f"{inv_col}:Q"),
            text=alt.Text("Rev Label:N"),
        )
    )

    st.altair_chart(
        (inv_chart + inv_text).properties(padding={"top": 30, "right": 40, "left": 20}).configure_view(strokeWidth=0).configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e"),
        use_container_width=True,
    )

    st.divider()

    # --- Monthly Direct Cost Chart ---
    st.markdown('<p class="section-label">Direct Cost</p>', unsafe_allow_html=True)
    st.markdown(f"### {view_mode} Direct Cost")

    chart_data["Cost Label"] = chart_data[cost_col].apply(compact)

    cost_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#f59e0b")
        .encode(
            x=alt.X("Month Label:N", title="Month",
                     sort=alt.SortField(field="Month", order="ascending"),
                     axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10)),
            y=alt.Y(f"{cost_col}:Q", title="Amount ($)",
                     axis=alt.Axis(format="$,.0f", labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15)),
            tooltip=[
                alt.Tooltip("Month Label:N", title="Month"),
                alt.Tooltip(f"{cost_col}:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=300)
    )

    cost_text = (
        alt.Chart(chart_data)
        .mark_text(dy=-10, fontSize=10, fontWeight="bold", color="#FFFFFF")
        .encode(
            x=alt.X("Month Label:N", sort=alt.SortField(field="Month", order="ascending")),
            y=alt.Y(f"{cost_col}:Q"),
            text=alt.Text("Cost Label:N"),
        )
    )

    st.altair_chart(
        (cost_chart + cost_text).properties(padding={"top": 30, "right": 40, "left": 20}).configure_view(strokeWidth=0).configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e"),
        use_container_width=True,
    )

    st.divider()

    # --- Direct Monthly Profitability Chart ---
    st.markdown('<p class="section-label">Direct Profitability</p>', unsafe_allow_html=True)
    st.markdown(f"### Direct {view_mode} Profitability")

    profit_data = chart_data[["Month", "Month Label", inv_col, cost_col]].copy()
    profit_data["Direct Profit"] = profit_data[inv_col] - profit_data[cost_col]
    profit_data["Margin %"] = (
        (profit_data["Direct Profit"] / profit_data[inv_col] * 100)
        .where(profit_data[inv_col] != 0, 0)
        .round(1)
    )

    # Single green bar showing profit (revenue - cost)
    profit_data["Profit Label"] = profit_data["Direct Profit"].apply(compact)

    profit_bars = (
        alt.Chart(profit_data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#10b981")
        .encode(
            x=alt.X("Month Label:N", title="Month",
                     sort=alt.SortField(field="Month", order="ascending"),
                     axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10)),
            y=alt.Y("Direct Profit:Q", title="Profit ($)",
                     axis=alt.Axis(format="$,.0f", labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15)),
            tooltip=[
                alt.Tooltip("Month Label:N", title="Month"),
                alt.Tooltip(f"{inv_col}:Q", title="Revenue", format="$,.2f"),
                alt.Tooltip(f"{cost_col}:Q", title="Cost", format="$,.2f"),
                alt.Tooltip("Direct Profit:Q", title="Profit", format="$,.2f"),
                alt.Tooltip("Margin %:Q", title="Margin %", format=".1f"),
            ],
        )
        .properties(height=300)
    )

    profit_text = (
        alt.Chart(profit_data)
        .mark_text(dy=-10, fontSize=10, fontWeight="bold", color="#FFFFFF")
        .encode(
            x=alt.X("Month Label:N", sort=alt.SortField(field="Month", order="ascending")),
            y=alt.Y("Direct Profit:Q"),
            text=alt.Text("Profit Label:N"),
        )
    )

    st.altair_chart(
        (profit_bars + profit_text).properties(padding={"top": 30, "right": 40, "left": 20}).configure_view(strokeWidth=0).configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e"),
        use_container_width=True,
    )

    # Margin % line chart
    st.markdown("### Direct Margin %")

    margin_chart = (
        alt.Chart(profit_data)
        .mark_line(point=True, strokeWidth=2, color="#10b981")
        .encode(
            x=alt.X("Month Label:N", title="Month",
                     sort=alt.SortField(field="Month", order="ascending"),
                     axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10)),
            y=alt.Y("Margin %:Q", title="Margin %",
                     axis=alt.Axis(labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15)),
            tooltip=[
                alt.Tooltip("Month Label:N", title="Month"),
                alt.Tooltip("Margin %:Q", format=".1f"),
                alt.Tooltip("Direct Profit:Q", title="Direct Profit", format="$,.0f"),
            ],
        )
        .properties(height=250)
    )

    margin_text = (
        alt.Chart(profit_data)
        .mark_text(dy=-12, fontSize=10, fontWeight="bold", color="#10b981")
        .encode(
            x=alt.X("Month Label:N", sort=alt.SortField(field="Month", order="ascending")),
            y=alt.Y("Margin %:Q"),
            text=alt.Text("Margin %:Q", format=".1f"),
        )
    )

    st.altair_chart(
        (margin_chart + margin_text).properties(padding={"top": 25, "right": 40, "left": 20}).configure_view(strokeWidth=0).configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e"),
        use_container_width=True,
    )

    # Profitability KPIs (for single project view)
    if selected_project != "All" and len(chart_data) > 0:
        total_rev = chart_data[inv_col].iloc[-1] if view_mode == "Cumulative" else chart_data["Monthly Invoicing"].sum()
        total_cst = chart_data[cost_col].iloc[-1] if view_mode == "Cumulative" else chart_data["Monthly Cost"].sum()
        total_profit = total_rev - total_cst
        overall_margin = (total_profit / total_rev * 100) if total_rev != 0 else 0

        pcol1, pcol2, pcol3 = st.columns(3)
        with pcol1:
            st.metric("Total Revenue", f"${total_rev:,.0f}")
        with pcol2:
            st.metric("Total Cost", f"${total_cst:,.0f}")
        with pcol3:
            st.metric("Direct Margin", f"{overall_margin:.1f}%",
                       delta=f"${total_profit:,.0f}")

    st.divider()

    # --- % Billed vs % Cost Chart ---
    if selected_project != "All":
        st.markdown('<p class="section-label">WIP Analysis</p>', unsafe_allow_html=True)
        st.markdown("### % Billed vs % Cost")

        pct_data = filtered[["Month", "Month Label", "% Billed", "% Cost"]].copy()
        pct_data["% Billed"] = (pct_data["% Billed"] * 100).round(1)
        pct_data["% Cost"] = (pct_data["% Cost"] * 100).round(1)

        pct_melted = pct_data.melt(
            id_vars=["Month", "Month Label"],
            value_vars=["% Billed", "% Cost"],
            var_name="Metric",
            value_name="Percentage",
        )

        pct_chart = (
            alt.Chart(pct_melted)
            .mark_line(point=True, strokeWidth=2)
            .encode(
                x=alt.X("Month Label:N", title="Month",
                         sort=alt.SortField(field="Month", order="ascending"),
                         axis=alt.Axis(labelAngle=-45, labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=10)),
                y=alt.Y("Percentage:Q", title="%",
                         axis=alt.Axis(labelColor="#808090", titleColor="#FFFFFF", titleFontWeight="bold", titlePadding=15)),
                color=alt.Color("Metric:N",
                    scale=alt.Scale(domain=["% Billed", "% Cost"], range=["#3b82f6", "#f59e0b"]),
                    legend=alt.Legend(orient="top", labelColor="#c0c0c0", titleColor="#FFFFFF", titleFontWeight="bold", labelLimit=300, columnPadding=20)),
                tooltip=[
                    alt.Tooltip("Month Label:N", title="Month"),
                    alt.Tooltip("Metric:N"),
                    alt.Tooltip("Percentage:Q", format=".1f"),
                ],
            )
            .properties(height=300, padding={"top": 20, "right": 40, "left": 20})
        )

        st.altair_chart(
            pct_chart.configure_view(strokeWidth=0).configure_axis(gridColor="#1e1e2e", domainColor="#2a2a3e"),
            use_container_width=True,
        )

        st.divider()

        # --- Overbilled/Underbilled ---
        st.markdown('<p class="section-label">Billing Status</p>', unsafe_allow_html=True)
        st.markdown("### Overbilled / Underbilled")

        latest_ou = filtered["Over/Under Billed"].iloc[-1]
        if pd.notna(latest_ou):
            if latest_ou > 0:
                st.metric("Overbilled", f"${latest_ou:,.0f}")
            else:
                st.metric("Underbilled", f"${abs(latest_ou):,.0f}")

    # --- Data Table ---
    st.divider()
    st.markdown('<p class="section-label">Detail</p>', unsafe_allow_html=True)

    display_cols = ["Month Label", "Monthly Invoicing", "Monthly Cost", "Cumulative Revenue", "Cumulative Cost"]
    if selected_project != "All":
        display_cols = ["Month Label"] + ["Monthly Invoicing", "Cumulative Revenue", "Monthly Cost", "Cumulative Cost"]

    st.dataframe(
        filtered[display_cols].style.format({
            "Monthly Invoicing": "${:,.2f}",
            "Monthly Cost": "${:,.2f}",
            "Cumulative Revenue": "${:,.2f}",
            "Cumulative Cost": "${:,.2f}",
        }),
        use_container_width=True,
        height=300,
        hide_index=True,
    )

else:
    st.info("No data available for the selected filters.")
