import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dual Fuel AR Dashboard",
    page_icon="📊",
    layout="wide",
)

# --- Login gate ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign in"):
        users = st.secrets["users"]
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# --- Dashboard (only runs after login) ---
conn = st.connection("snowflake")

st.title("Dual Fuel AR Dashboard, Weekly Trends")

# Query the gold view
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
        days_past_due           AS "Days Past Due"
    FROM ANALYTICS.GOLD.FCT_INVOICE_OPEN
    ORDER BY due_date ASC
""")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total AR", f"${df['Balance'].sum():,.2f}")
with col2:
    st.metric("Open Invoices", f"{len(df):,}")
with col3:
    st.metric("Customers", f"{df['Customer'].nunique():,}")
with col4:
    st.metric("Avg Days Past Due", f"{df['Days Past Due'].mean():.0f}")

st.divider()

# Filters — 4 columns
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
with filter_col1:
    dept_filter = st.multiselect("Department", options=sorted(df["Department"].dropna().unique()))
with filter_col2:
    bucket_filter = st.multiselect("Aging Bucket", options=["Not Yet Due", "Current (1-30)", "31-60 Days", "61-90 Days", "90+ Days"])
with filter_col3:
    property_filter = st.multiselect("Property / Project", options=sorted(df["Property / Project"].dropna().unique()))
with filter_col4:
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

# Display the table — compact
st.dataframe(
    filtered[["Customer", "Property / Project", "Invoice", "Balance", "Date"]].style.format({
        "Balance": "${:,.2f}",
        "Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else ""
    }),
    use_container_width=True,
    height=300,
    hide_index=True,
)

# Total row
st.markdown(f"**Total: ${filtered['Balance'].sum():,.2f}**")

st.divider()

# --- Weekly AR Trend Chart ---
st.subheader("AR Aging Trend — Weekly Snapshots")

snapshot_df = conn.query("""
    SELECT
        snapshot_date   AS "Week",
        aging_bucket    AS "Aging Bucket",
        aging_bucket_sort,
        total_outstanding AS "Amount"
    FROM ANALYTICS.GOLD.FCT_AR_WEEKLY_SNAPSHOT
    ORDER BY snapshot_date, aging_bucket_sort
""")

if len(snapshot_df) > 0:
    # Format week labels
    snapshot_df["Week Label"] = pd.to_datetime(snapshot_df["Week"]).dt.strftime("%m/%d/%Y")

    # Color mapping: Current=green, Watchlist=yellow, Aged=red
    color_scale = alt.Scale(
        domain=["Current", "Watchlist", "Aged"],
        range=["#27ae60", "#f1c40f", "#e74c3c"]
    )

    # Build the stacked bar chart
    chart = (
        alt.Chart(snapshot_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "Week Label:N",
                title="Week Ending",
                sort=alt.SortField(field="Week", order="ascending"),
                axis=alt.Axis(labelAngle=-45),
            ),
            y=alt.Y(
                "Amount:Q",
                title="AR ($)",
                axis=alt.Axis(format="$,.0f"),
            ),
            color=alt.Color(
                "Aging Bucket:N",
                scale=color_scale,
                legend=alt.Legend(title="Aging Bucket", orient="top"),
            ),
            order=alt.Order("aging_bucket_sort:Q"),
            tooltip=[
                alt.Tooltip("Week Label:N", title="Week"),
                alt.Tooltip("Aging Bucket:N"),
                alt.Tooltip("Amount:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=400)
    )

    # Add total labels on top of each bar
    totals = snapshot_df.groupby(["Week Label", "Week"], as_index=False)["Amount"].sum()
    totals["Label"] = totals["Amount"].apply(lambda x: f"${x/1000:,.0f}K")

    text = (
        alt.Chart(totals)
        .mark_text(dy=-10, fontSize=11, fontWeight="bold")
        .encode(
            x=alt.X(
                "Week Label:N",
                sort=alt.SortField(field="Week", order="ascending"),
            ),
            y=alt.Y("Amount:Q"),
            text="Label:N",
        )
    )

    st.altair_chart(chart + text, use_container_width=True)
else:
    st.info("No snapshot data yet. The first snapshot will appear after Friday at 5 PM.")
