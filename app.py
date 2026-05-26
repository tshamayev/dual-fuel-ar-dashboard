import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dual Fuel AR Dashboard",
    page_icon="📊",
    layout="wide",
)

# Connect to Snowflake using secrets
conn = st.connection("snowflake")

st.title("Accounts Receivable")

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

# Filters
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    dept_filter = st.multiselect("Department", options=sorted(df["Department"].dropna().unique()))
with filter_col2:
    bucket_filter = st.multiselect("Aging Bucket", options=["Not Yet Due", "Current (1-30)", "31-60 Days", "61-90 Days", "90+ Days"])
with filter_col3:
    customer_search = st.text_input("Search Customer")

# Apply filters
filtered = df.copy()
if dept_filter:
    filtered = filtered[filtered["Department"].isin(dept_filter)]
if bucket_filter:
    filtered = filtered[filtered["Aging Bucket"].isin(bucket_filter)]
if customer_search:
    filtered = filtered[filtered["Customer"].str.contains(customer_search, case=False, na=False)]

# Display the table
st.dataframe(
    filtered[["Customer", "Property / Project", "Invoice", "Balance", "Date"]].style.format({
        "Balance": "${:,.2f}",
        "Date": lambda x: pd.to_datetime(x).strftime("%m/%d/%Y") if pd.notna(x) else ""
    }),
    use_container_width=True,
    height=600,
    hide_index=True,
)

# Total row
st.markdown(f"**Total: ${filtered['Balance'].sum():,.2f}**")
