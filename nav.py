"""Shared sidebar header: logo + navigation + session controls.

Single source of truth for the sidebar across every page, so the navigation
link list can never drift between app.py and the pages/ files. Call this inside
a `with st.sidebar:` block; each page then adds its own filters below it.
"""
import base64
from pathlib import Path

import streamlit as st

import auth

# nav.py lives at the repo root, alongside Flame.png — so this resolves
# correctly whether the caller is app.py (root) or a file in pages/.
_FLAME_PATH = Path(__file__).parent / "Flame.png"


def render_sidebar_header(controller, subtitle="AR Dashboard"):
    """Render the Dual Fuel logo, the page navigation, and session controls.

    Args:
        controller: the cookie controller (used by the Sign out button).
        subtitle:   the red label shown under the logo for the current page.
    """
    if _FLAME_PATH.exists():
        flame_b64 = base64.b64encode(_FLAME_PATH.read_bytes()).decode()
        st.markdown(
            f'<div class="sidebar-logo">'
            f'<img src="data:image/png;base64,{flame_b64}">'
            f'<p class="sidebar-title">Dual Fuel</p>'
            f'<p class="sidebar-subtitle">{subtitle}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Navigation — the ONE place these links are defined for all pages.
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
