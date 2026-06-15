"""Shared authentication helpers for the Dual Fuel AR Dashboard.

Adds a lightweight, tamper-proof "stay logged in" layer on top of the existing
username/password-in-secrets login.

How it works
------------
On a successful login we store a browser cookie containing a *signed* token:

    base64url(payload) + "." + hex(HMAC_SHA256(payload, secret))

where payload = {"u": <username>, "exp": <unix-expiry>}. The signature is an
HMAC-SHA256 over the payload using a server-side secret that never reaches the
browser (``st.secrets["cookie_auth"]["secret"]``), so the cookie cannot be
forged or modified by the client. The password itself is never stored anywhere
on the client.

Everything degrades gracefully: if the cookie component can't load, or no
``cookie_secret`` is configured, the helpers quietly no-op and the app falls
back to manual login on every visit. It never crashes the dashboard.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st

COOKIE_NAME = "df_ar_auth"        # name of the auth cookie in the browser
CONTROLLER_KEY = "cookies"        # session_state key used by CookieController
SESSION_DAYS = 7                  # how long a login lasts before re-auth


def cookie_secret():
    """Return the HMAC signing secret, or None if it isn't configured.

    NOTE: we use a custom [cookie_auth] secrets section, NOT [auth]. The [auth]
    section is reserved by Streamlit for its native OIDC login (st.login) — using
    it here would trigger Streamlit's auth/CORS/XSRF handling and can break the app.
    """
    try:
        return st.secrets["cookie_auth"]["secret"]
    except Exception:
        return None


def get_controller():
    """Return a CookieController, or None if the component can't be created.

    Wrapped in try/except so a missing or version-incompatible component can
    never take the whole dashboard down — we just lose the "stay logged in"
    convenience and fall back to manual login.
    """
    try:
        from streamlit_cookies_controller import CookieController
        return CookieController(key=CONTROLLER_KEY)
    except Exception:
        return None


def cookies_loaded() -> bool:
    """True once the cookie component has delivered the browser's cookies.

    On the very first script run of a fresh session the component hasn't
    reported back yet; it does so on the following (automatic) rerun.
    """
    return CONTROLLER_KEY in st.session_state


def _sign(payload: dict, secret: str) -> str:
    raw = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode()
    sig = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def _verify(token: str, secret: str):
    """Return the payload dict if the token is valid and unexpired, else None."""
    try:
        raw, sig = token.rsplit(".", 1)
        expected = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
        if float(payload.get("exp", 0)) < time.time():
            return None
        return payload
    except Exception:
        return None


def try_cookie_login(controller) -> bool:
    """Authenticate the session from a valid auth cookie, if present.

    Returns True if the session is authenticated after the call.
    """
    if st.session_state.get("authenticated"):
        return True
    secret = cookie_secret()
    if controller is None or not secret:
        return False
    try:
        token = controller.get(COOKIE_NAME)
    except Exception:
        token = None
    if not token:
        return False
    payload = _verify(token, secret)
    if payload:
        st.session_state.authenticated = True
        st.session_state.username = payload.get("u", "")
        return True
    return False


def issue_cookie(controller, username: str) -> None:
    """Set the signed auth cookie after a successful manual login (best-effort).

    The cookie is marked Secure (HTTPS only) and SameSite=Lax. Secure means it
    will not be stored over plain http:// (e.g. local `streamlit run` on
    localhost) — that only affects local persistence, not the deployed HTTPS app.
    """
    secret = cookie_secret()
    if controller is None or not secret:
        return
    exp = time.time() + SESSION_DAYS * 86400
    token = _sign({"u": username, "exp": exp}, secret)
    try:
        controller.set(
            COOKIE_NAME,
            token,
            expires=datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
            max_age=SESSION_DAYS * 86400,
            secure=True,
            same_site="lax",
        )
    except Exception:
        pass


def clear_cookie(controller) -> None:
    """Remove the auth cookie (best-effort)."""
    if controller is None:
        return
    try:
        controller.remove(COOKIE_NAME)
    except Exception:
        pass


def sign_out(controller) -> None:
    """Clear the cookie + session and rerun back to the login screen."""
    clear_cookie(controller)
    for key in ("authenticated", "username"):
        st.session_state.pop(key, None)
    st.rerun()
