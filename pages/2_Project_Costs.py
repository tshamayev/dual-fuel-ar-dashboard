import streamlit as st
import pandas as pd
import os
import sys

# Make the repo root importable so `import auth` works from the pages/ folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth

st.set_page_config(
    page_title="Project Costs — Dual Fuel",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Reuse the same CSS from the other pages ---
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
span[data-testid="stIconMaterial"], [data-testid="stIconMaterial"], .material-icons, .material-icons-outlined, .material-symbols-outlined, .material-symbols-rounded { font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important; }
iframe[title="streamlit_cookies_controller.cookie_controller"] { display: none !important; height: 0 !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[class*="viewerBadge"] { display: none !important; }
button[title="Manage app"], [data-testid="manageAppButton"] { display: none !important; }
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
[data-testid="stButton"] button { background-color: #C30017 !important; color: #FFFFFF !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; }
[data-testid="stButton"] button:hover { background-color: #D30011 !important; }
.cost-tree { border: 1px solid #2a2a3e; border-radius: 8px; background:#0f0f17; padding: 4px 0; }
.cost-tree summary { cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items:center; gap: 12px; padding: 7px 12px; color: #e0e0e0; border-top: 1px solid #16161f; }
.cost-tree details.lvl1 > summary { color:#fff; font-weight:700; font-size:0.95rem; }
.cost-tree summary::-webkit-details-marker { display:none; }
.cost-tree summary::before { content:"▸"; color:#C30017; font-size:0.8rem; }
.cost-tree details[open] > summary::before { content:"▾"; }
.cost-tree details details > summary { padding-left: 28px; }
.cost-tree details details details > summary { padding-left: 44px; }
.cost-tree details details details details > summary { padding-left: 60px; }
.cost-tree summary:hover { background:#141422; }
.cost-tree .lbl { flex:1; }
.cost-tree .amt { font-size:0.78rem; color:#808090; white-space:nowrap; }
.cost-tree .amt.comm { color:#f1c40f; }
.cost-tree .amt.act { color:#27ae60; }
.cost-tree .line { display:flex; justify-content:space-between; gap:12px; padding:5px 12px 5px 76px; border-top:1px solid #14141c; font-size:0.82rem; }
.cost-tree .line-ref { color:#8a8a99; min-width:88px; }
.cost-tree .line-item { flex:1; color:#cfcfd6; }
.cost-tree .line-amt { white-space:nowrap; font-variant-numeric:tabular-nums; }
.cost-tree .line-amt.comm { color:#f1c40f; }
.cost-tree .line-amt.act { color:#27ae60; }
</style>
""", unsafe_allow_html=True)


# --- Login gate (shared session state + cookie auto-login) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

controller = auth.get_controller()
auth.try_cookie_login(controller)

if not st.session_state.authenticated:
    if controller is not None and not auth.cookies_loaded():
        st.stop()
    st.switch_page("app.py")


# --- Data ---
conn = st.connection("snowflake")

# Cost-by-type (the Finance -> Costs table)
cost = conn.query("""
    SELECT project_id, project_number, project_name, project_status, project_manager,
           cost_type,
           starting_budget::FLOAT       AS starting_budget,
           change_order_budget::FLOAT   AS change_orders,
           updated_budget::FLOAT        AS updated_budget,
           committed_cost::FLOAT        AS committed,
           actual_cost::FLOAT           AS actual,
           pct_used::FLOAT              AS pct_used,
           updated_vs_starting_pct::FLOAT AS updated_vs_starting
    FROM ANALYTICS.GOLD.FCT_PROJECT_COST_BY_TYPE
""", ttl=3600)  # cache 1 hour; "Refresh data" forces a fresh pull
cost.columns = [c.lower() for c in cost.columns]

# Project-level KPIs / header (from the WIP gold view the dashboard already reads)
wip = conn.query("""
    SELECT project_id, project_number, project_name, project_status, project_manager,
           department_name, billing_customer_name, property_name,
           updated_contract_amount::FLOAT   AS contract,
           updated_cost_budget_amount::FLOAT AS cost_budget,
           actual_total_cost::FLOAT          AS actual_total_cost,
           total_billed_amount::FLOAT        AS revenue_billed,
           open_ar_amount::FLOAT             AS open_ar,
           overbilled_underbilled_amount::FLOAT AS over_under_billed,
           pct_billed::FLOAT                 AS pct_billed
    FROM ANALYTICS.GOLD.FCT_WIP_STATUS
""", ttl=3600)
wip.columns = [c.lower() for c in wip.columns]


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
            f'<p class="sidebar-subtitle">Project Costs</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.page_link("app.py", label="AR Dashboard", icon="📊")
    st.page_link("pages/1_Project_Analysis.py", label="Project Analysis", icon="📈")
    st.page_link("pages/2_Project_Costs.py", label="Project Costs", icon="💰")

    _user = st.session_state.get("username", "")
    if _user:
        st.caption(f"Signed in as {_user}")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if st.button("Sign out", use_container_width=True):
        auth.sign_out(controller)

    st.markdown("---")
    st.markdown('<p class="filter-header">Filters</p>', unsafe_allow_html=True)

    # Project selector — "number — name", sorted
    proj = wip.dropna(subset=["project_number"]).copy()
    proj["label"] = proj["project_number"].astype(str) + " — " + proj["project_name"].fillna("")
    options = sorted(proj["label"].unique())
    default_idx = next((i for i, o in enumerate(options) if o.startswith("2824")), 0)
    selected_label = st.selectbox("Project", options=options, index=default_idx if options else 0)


# Resolve selected project
sel = proj[proj["label"] == selected_label]
if sel.empty:
    st.info("No project selected.")
    st.stop()
sel = sel.iloc[0]
pid = sel["project_id"]
pnum = sel["project_number"]

cost_p = cost[cost["project_id"] == pid].copy()


# === MAIN CONTENT ===
st.markdown('<p class="section-label" style="margin-top:8px;">Project · Finance</p>', unsafe_allow_html=True)
st.markdown(f"## {pnum} — {sel['project_name']}")
st.markdown(
    f"*{sel.get('billing_customer_name') or '—'} | {sel.get('property_name') or '—'} | "
    f"PM: {sel.get('project_manager') or '—'} | {sel.get('project_status') or '—'} | "
    f"Dept: {sel.get('department_name') or '—'}*"
)

# --- Billing KPIs ---
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Open AR", f"${sel['open_ar']:,.2f}" if pd.notna(sel['open_ar']) else "—")
with k2:
    st.metric("Revenue Billed to Date", f"${sel['revenue_billed']:,.2f}" if pd.notna(sel['revenue_billed']) else "—")
with k3:
    oub = sel['over_under_billed']
    label = "Over Billed (WIP)" if pd.notna(oub) and oub >= 0 else "Under Billed (WIP)"
    st.metric(label, f"${abs(oub):,.2f}" if pd.notna(oub) else "—")

st.divider()

# --- Costs by cost type ---
st.markdown('<p class="section-label">Costs by Cost Type</p>', unsafe_allow_html=True)

order = ["Labor", "Equipment", "Material", "Other", "Subcontractor", "Overhead", "Unspecified"]
cost_p["__o"] = cost_p["cost_type"].apply(lambda x: order.index(x) if x in order else 99)
cost_p = cost_p.sort_values("__o")

show_cols = ["cost_type", "starting_budget", "change_orders", "updated_budget",
             "committed", "actual", "pct_used", "updated_vs_starting"]
table = cost_p[show_cols].copy()

# Total row
total = {
    "cost_type": "Total",
    "starting_budget": table["starting_budget"].sum(),
    "change_orders": table["change_orders"].sum(),
    "updated_budget": table["updated_budget"].sum(),
    "committed": table["committed"].sum(),
    "actual": table["actual"].sum(),
}
total["pct_used"] = (total["actual"] / total["updated_budget"] * 100) if total["updated_budget"] else None
total["updated_vs_starting"] = (total["change_orders"] / total["starting_budget"] * 100) if total["starting_budget"] else None
table = pd.concat([table, pd.DataFrame([total])], ignore_index=True)

table = table.rename(columns={
    "cost_type": "Cost Type", "starting_budget": "Starting Budget", "change_orders": "Change Orders",
    "updated_budget": "Updated Budget", "committed": "Committed Costs", "actual": "Actual Costs",
    "pct_used": "% Used", "updated_vs_starting": "Updated vs Starting",
})

st.dataframe(
    table.style.format({
        "Starting Budget": "${:,.2f}", "Change Orders": "${:,.2f}", "Updated Budget": "${:,.2f}",
        "Committed Costs": "${:,.2f}", "Actual Costs": "${:,.2f}",
        "% Used": lambda v: f"{v:,.1f}%" if pd.notna(v) else "—",
        "Updated vs Starting": lambda v: f"{v:,.1f}%" if pd.notna(v) else "—",
    }),
    use_container_width=True, hide_index=True,
)
st.divider()

# --- Drill-down tree: Cost Type > Phase > Department > Cost Code > line items ---
st.markdown('<p class="section-label">Drill-down — Cost Type ▸ Phase ▸ Department ▸ Cost Code ▸ Items</p>', unsafe_allow_html=True)

detail = conn.query(f"""
    SELECT cost_type, phase, department, cost_code, source, ref, item,
           committed_amount::FLOAT AS committed_amount,
           actual_amount::FLOAT    AS actual_amount
    FROM ANALYTICS.GOLD.FCT_PROJECT_COST_DETAIL
    WHERE project_id = '{pid}'
""", ttl=3600)
detail.columns = [c.lower() for c in detail.columns]

if detail.empty:
    st.info("No cost detail for this project yet.")
else:
    import html as _html

    def _money(v):
        return f"${v:,.0f}" if v else "—"

    def _sumlabel(comm, act):
        bits = []
        if comm:
            bits.append(f'<span class="amt comm">Committed {_money(comm)}</span>')
        if act:
            bits.append(f'<span class="amt act">Actual {_money(act)}</span>')
        return " ".join(bits) if bits else '<span class="amt">—</span>'

    ORD = ["Labor", "Equipment", "Material", "Other", "Subcontractor", "Overhead", "Unspecified"]
    parts = ['<div class="cost-tree">']
    for ct, ctdf in sorted(detail.groupby("cost_type"), key=lambda kv: ORD.index(kv[0]) if kv[0] in ORD else 99):
        parts.append(f'<details class="lvl1"><summary><span class="lbl">{_html.escape(str(ct))}</span>'
                     f'{_sumlabel(ctdf.committed_amount.sum(), ctdf.actual_amount.sum())}</summary>')
        for ph, phdf in sorted(ctdf.groupby("phase")):
            parts.append(f'<details><summary><span class="lbl">{_html.escape(str(ph))}</span>'
                         f'{_sumlabel(phdf.committed_amount.sum(), phdf.actual_amount.sum())}</summary>')
            for dep, depdf in sorted(phdf.groupby("department")):
                parts.append(f'<details><summary><span class="lbl">{_html.escape(str(dep))}</span>'
                             f'{_sumlabel(depdf.committed_amount.sum(), depdf.actual_amount.sum())}</summary>')
                for cc, ccdf in sorted(depdf.groupby("cost_code")):
                    parts.append(f'<details><summary><span class="lbl">{_html.escape(str(cc))}</span>'
                                 f'{_sumlabel(ccdf.committed_amount.sum(), ccdf.actual_amount.sum())}</summary>')
                    leaf = (ccdf.groupby(["source", "ref", "item"], as_index=False)
                                .agg(committed=("committed_amount", "sum"), actual=("actual_amount", "sum")))
                    leaf["amt"] = leaf["committed"] + leaf["actual"]
                    leaf = leaf.sort_values("amt", ascending=False)
                    for r in leaf.head(100).itertuples():
                        amt = r.committed if r.committed else r.actual
                        cls = "comm" if r.committed else "act"
                        parts.append(f'<div class="line"><span class="line-ref">{_html.escape(str(r.ref))}</span>'
                                     f'<span class="line-item">{_html.escape(str(r.item))}</span>'
                                     f'<span class="line-amt {cls}">{_money(amt)}</span></div>')
                    if len(leaf) > 100:
                        parts.append(f'<div class="line"><span class="line-item">+{len(leaf) - 100} more line items…</span></div>')
                    parts.append('</details>')
                parts.append('</details>')
            parts.append('</details>')
        parts.append('</details>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

st.caption("Amber = Committed · Green = Actual — click any row to drill in.")
