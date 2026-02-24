#!/usr/bin/env python3
"""
Login Page - Coresight Research
SIP Login with JWT authentication.
"""
import os
import json
import logging
import requests
import traceback
from time import sleep, perf_counter
from datetime import datetime, timedelta, timezone
from typing import Union, Tuple
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Import new auth manager
from core.auth_manager import login_user, AuthResult

# Import UI components (minimal)
from components.styles import hide_sidebar

# Must be called immediately after imports
hide_sidebar()

# ===========================
# Bootstrap / Config
# ===========================
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
)
log = logging.getLogger("sip-login")

AUTH_URL = os.getenv("AUTH_URL", "").strip()
AUTH_URL_PAID = os.getenv("AUTH_URL_PAID", "").strip()

log.info("=== SIP Login starting ===")


# ===========================
# Small utils
# ===========================
def _exc() -> str:
    return "".join(traceback.format_exc(limit=2))

def _mask(s: str, keep=4) -> str:
    if not s:
        return ""
    if len(s) <= keep:
        return "*" * len(s)
    return s[:keep] + "..." + "*" * (max(0, len(s) - keep - 3))

def _mask_bearer(hdrs: dict) -> dict:
    if not isinstance(hdrs, dict):
        return {}
    out = dict(hdrs)
    val = out.get("Authorization")
    if isinstance(val, str) and val.lower().startswith("bearer "):
        out["Authorization"] = "Bearer " + _mask(val.split(" ", 1)[1], keep=6)
    return out

def _as_str_or_empty(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return str(x)

def sanitize_username(u) -> str:
    if u is None:
        return ""
    return u.strip() if isinstance(u, str) else str(u)

def sanitize_password(p: Union[str, bytes, None]) -> str:
    if p is None:
        return ""
    if isinstance(p, bytes):
        return p.decode("utf-8", errors="replace")
    return str(p)

def _has_quote(s: str) -> bool:
    return isinstance(s, str) and ("'" in s or '"' in s)


# ===========================
# URL Helpers
# ===========================
def _strip_trailing(s: str, suffix: str) -> str:
    return s[:-len(suffix)] if s and s.endswith(suffix) else s

def _no_trailing_slash(url: str) -> str:
    if not url:
        return url
    return url[:-1] if url.endswith("/") else url

def _wpjson_base(api_url: str):
    if not api_url:
        log.debug("_wpjson_base: empty api_url -> None")
        return None
    url = _no_trailing_slash(api_url)
    lower = url.lower()

    token_suffix = "/jwt-auth/v1/token"
    if lower.endswith(token_suffix):
        base = _strip_trailing(url, token_suffix)
        out = _no_trailing_slash(base + "/wp-json") if "/wp-json" not in base.lower() else _no_trailing_slash(base)
        return out

    if "/wp-json" in lower:
        parts = url.split("/wp-json")
        out = _no_trailing_slash(parts[0] + "/wp-json")
        return out

    out = _no_trailing_slash(url + "/wp-json")
    return out

def _auth_endpoint():
    base_paid = _wpjson_base(AUTH_URL_PAID) if AUTH_URL_PAID else None
    if base_paid:
        url = f"{base_paid}/jwt-auth/v1/token"
        log.info(f"JWT endpoint (from AUTH_URL_PAID): {url}")
        return url

    base_auth = _wpjson_base(AUTH_URL) if AUTH_URL else None
    if base_auth:
        url = f"{base_auth}/jwt-auth/v1/token"
        log.info(f"JWT endpoint (from AUTH_URL): {url}")
        return url

    log.error("JWT endpoint could not be derived. Set AUTH_URL_PAID or AUTH_URL in .env.")
    return None


# ===========================
# JSON & FORM body builders
# ===========================
def _build_wire_json(payload: dict) -> Tuple[str, str]:
    raw_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    wire_json = raw_json.replace('\\"', '\\u0022').replace("'", "\\u0027")
    return raw_json, wire_json

def _escape_for_unslash(value: str) -> str:
    if value is None:
        return ""
    v = value.replace("\\", "\\\\")
    v = v.replace('"', '\\"').replace("'", "\\'")
    return v


# ===========================
# AUTH senders
# ===========================
def _send_json_wire(token_url: str, payload: dict, timeout: int = 12):
    headers = {
        "Accept": "application/json, */*;q=0.5",
        "User-Agent": "SIPLogin/3.4 (+https://coresight.com)",
        "Content-Type": "application/json; charset=utf-8",
    }
    raw_json, wire_json = _build_wire_json(payload)
    st.session_state["__auth_json_preview_raw__"] = raw_json
    st.session_state["__auth_json_preview_wire__"] = wire_json

    resp = requests.post(token_url, data=wire_json, headers=headers, timeout=timeout, allow_redirects=False)
    log.info(f"[AUTH][JSON-WIRE] status={resp.status_code}")
    return resp, "json-wire"

def _send_json_raw(token_url: str, payload: dict, timeout: int = 12):
    headers = {
        "Accept": "application/json, */*;q=0.5",
        "User-Agent": "SIPLogin/3.4 (+https://coresights.com)",
    }
    resp = requests.post(token_url, json=payload, headers=headers, timeout=timeout, allow_redirects=False)
    return resp, "json-raw"

def _send_form(token_url: str, payload: dict, timeout: int = 12):
    headers = {
        "Accept": "application/json, */*;q=0.5",
        "User-Agent": "SIPLogin/3.4 (+https://coresight.com)",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    resp = requests.post(token_url, data=payload, headers=headers, timeout=timeout, allow_redirects=False)
    return resp, "form"

def _parse_error(resp: requests.Response):
    code = msg = None
    try:
        j = resp.json()
        code = (j.get("code") or "").strip()
        msg = j.get("message")
    except Exception:
        pass
    return code, msg


# ===========================
# Authenticate (A→B→C, then D with backslash-escape)
# ===========================
def authenticate_user(username, password):
    token_url = _auth_endpoint()
    if not token_url:
        return None

    username = sanitize_username(_as_str_or_empty(username))
    password = sanitize_password(_as_str_or_empty(password))
    if not username or not password:
        st.error("Please enter both email and password.")
        return None

    payload = {"username": username, "password": password}

    log.warning(f"[DEBUG][AUTH] POST {token_url} | username={username} | pw_len={len(password)} has_quote={_has_quote(password)}")

    try:
        # A) JSON wire
        resp, mode = _send_json_wire(token_url, payload, timeout=12)
        if resp is not None and resp.status_code == 200:
            return _handle_success(resp, mode)
        _log_err(resp, mode)

        # B) JSON raw
        respB, modeB = _send_json_raw(token_url, payload, timeout=12)
        if respB is not None and respB.status_code == 200:
            return _handle_success(respB, modeB)
        _log_err(respB, modeB)

        # C) FORM
        respC, modeC = _send_form(token_url, payload, timeout=12)
        if respC is not None and respC.status_code == 200:
            return _handle_success(respC, modeC)
        _log_err(respC, modeC)

        # D) Backslash-escape password value, then retry A→B→C
        if _has_quote(password):
            escaped_pw = _escape_for_unslash(password)
            log.warning("[DEBUG][AUTH] Retrying with backslash-escaped password value (hidden)")
            payload2 = {"username": username, "password": escaped_pw}

            respD1, modeD1 = _send_json_wire(token_url, payload2, timeout=12)
            if respD1 is not None and respD1.status_code == 200:
                return _handle_success(respD1, modeD1)
            _log_err(respD1, modeD1)

            respD2, modeD2 = _send_json_raw(token_url, payload2, timeout=12)
            if respD2 is not None and respD2.status_code == 200:
                return _handle_success(respD2, modeD2)
            _log_err(respD2, modeD2)

            respD3, modeD3 = _send_form(token_url, payload2, timeout=12)
            if respD3 is not None and respD3.status_code == 200:
                return _handle_success(respD3, modeD3)
            _log_err(respD3, modeD3)

    except requests.RequestException as e:
        log.error(f"[AUTH] Request error: {e} | { _exc() }")
        return None
    except Exception as e:
        log.error(f"[AUTH] Unexpected error: {e} | { _exc() }")
        return None

def _handle_success(resp: requests.Response, mode: str):
    try:
        data = resp.json()
    except Exception:
        log.error(f"[AUTH] 200 but non-JSON payload ({mode}).")
        return None
    tok = data.get("token")
    if tok:
        log.info(f"[AUTH] token={_mask(tok, keep=6)} user_email={data.get('user_email')}")
    else:
        log.warning(f"[AUTH] 200 but missing token key ({mode}).")
    return data

def _log_err(resp: requests.Response, mode: str):
    if resp is None:
        log.error(f"[AUTH] No response from token endpoint ({mode}).")
        return
    try:
        code, msg = _parse_error(resp)
        if code or msg:
            log.warning(f"[AUTH] JWT error ({mode}) {resp.status_code}: code={code} msg={msg}")
        else:
            snippet = (resp.text or "")[:300].replace("\n", " ")
            log.warning(f"[AUTH] Failure ({mode}) {resp.status_code}: {snippet}")
    except Exception:
        snippet = (getattr(resp, "text", "") or "")[:300].replace("\n", " ")
        log.warning(f"[AUTH] Failure ({mode}) {getattr(resp, 'status_code', 'n/a')}: {snippet}")


# ===========================
# LAYOUT CSS FILE PATH
# ===========================
LAYOUT_CSS_FILE = "login_layout.css"

APP_DIR = Path(__file__).parent.parent

def load_html_component(filename: str) -> str:
    """Load HTML component from components directory."""
    components_dir = APP_DIR / "components"
    file_path = components_dir / filename
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        log.error(f"Error loading {filename}: {e}")
        return ""


# ===========================
# Main UI Function
# ===========================
def main():
    """Main render function - with external header/footer components."""
    
    # Load and apply layout CSS first
    layout_css = load_html_component(LAYOUT_CSS_FILE)
    if layout_css:
        if not layout_css.strip().startswith('<style>'):
            layout_css = f"<style>{layout_css}</style>"
        st.markdown(layout_css, unsafe_allow_html=True)
    
    # Load and render Header (at top, fixed position)
    header_html = load_html_component("login_header.html")
    if header_html:
        st.markdown(header_html, unsafe_allow_html=True)
    
    # Spacer to push content below fixed header
    st.markdown("<div style='height: 78px;'></div>", unsafe_allow_html=True)
    
    # Content wrapper for consistent layout
    st.markdown('<div class="content-wrapper login-content">', unsafe_allow_html=True)
    
    # Use columns to center the form (left spacer | form | right spacer)
    left_spacer, center_col, right_spacer = st.columns([2, 5, 2])
    
    with center_col:
        # Add some top spacing for visual balance
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Welcome text
        st.markdown(
            "<h4 style='font-family:sans-serif,Inter; color: #323232; font-size: 24px; font-weight: 600; padding: 0; margin: 0; '> "
            "Welcome to the Coresight Research</h4>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h1 style='font-family:sans-serif,Inter; font-size: 28px; font-weight: 700; "
            "color: #323232; margin-bottom: 24px; line-height: 1.2;'>"
            "Coresight Market Data Portal</h1>",
            unsafe_allow_html=True
        )
        
        # ===========================
        # Login Form
        # ===========================
        # Custom CSS for the form elements
        st.markdown("""
            <style>
            /* Hide Streamlit header action elements (link icon) */
            [data-testid="stHeaderActionElements"] {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Red login button - FULL WIDTH */
            div[data-testid="stVerticalBlock"] div[data-testid="stElementContainer"] {
                width: 100% !important;
            }
            
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] {
                width: 100% !important;
            }
            
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button,
            div[data-testid="stVerticalBlock"] button[data-testid="stBaseButton-secondary"],
            div[data-testid="stVerticalBlock"] button[kind="secondary"] {
                background-color: #d32f2f !important;
                color: white !important;
                width: 100% !important;
                min-width: 100% !important;
                max-width: 100% !important;
                height: 44px !important;
                font-size: 16px !important;
                border-radius: 4px !important;
                border: none !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
                margin-top: 8px !important;
            }
            
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button:hover,
            div[data-testid="stVerticalBlock"] button[data-testid="stBaseButton-secondary"]:hover {
                background-color: #b71c1c !important;
            }
            
            /* Center button text when disabled (authenticating) */
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button:disabled > div {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 10px !important;
                width: 100% !important;
            }
            
            /* Spinner before "Authenticating..." text */
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button:disabled > div::before {
                content: "";
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top-color: #ffffff;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                flex-shrink: 0;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Input fields styling */
            div[data-testid="stTextInput"] > div > div > input {
                border-radius: 4px !important;
                border: 1px solid #ccc !important;
                padding: 10px 12px !important;
                font-size: 15px !important;
                height: 42px !important;
            }
            
            /* Label styling */
            div[data-testid="stTextInput"] label {
                font-size: 13px !important;
                color: #555 !important;
                margin-bottom: 4px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Use session state to track loading
        if "is_authenticating" not in st.session_state:
            st.session_state.is_authenticating = False
        if "auth_error" not in st.session_state:
            st.session_state.auth_error = None
        
        username = st.text_input("Email or Username")
        password = st.text_input("Password", type="password")
        
        # Show button with loader text when authenticating
        button_label = "Authenticating..." if st.session_state.is_authenticating else "Login"
        
        # Disable button during authentication
        login_button = st.button(
            button_label, 
            key="login_button",
            disabled=st.session_state.is_authenticating
        )
        
        # Show error message if exists (and clear it)
        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None
            
        # Perform authentication when in authenticating state (no spinner, just button text)
        if st.session_state.is_authenticating:
            token_data = authenticate_user(username, password)
            
            if token_data:
                user_email = token_data.get("user_email")
                token = token_data.get("token")
                log.info(f"[LOGIN] JWT success user_email={user_email}")

                if not (user_email and token):
                    log.error(f"[LOGIN] Unexpected token payload keys={list(token_data.keys())}")
                    st.session_state.is_authenticating = False
                    st.session_state.auth_error = "Invalid response from server."
                    st.rerun()

                # Create session (DB + Cookie)
                result = login_user(
                    user_email=user_email,
                    user_nicename=token_data.get("user_nicename"),
                    user_display_name=token_data.get("user_display_name"),
                    token=token
                )
                
                if result.success:
                    log.info(f"[LOGIN] App session created session_id={result.session_id}")
                    st.session_state.is_authenticating = False
                    st.success("Logged in successfully!")
                    sleep(0.5)
                    log.info("[LOGIN] Redirect → pages/home.py")
                    st.switch_page("pages/home.py")
                else:
                    st.session_state.is_authenticating = False
                    st.session_state.auth_error = result.error_message or "Login failed. Please try again."
                    st.rerun()
            else:
                st.session_state.is_authenticating = False
                log.warning("[LOGIN] Authentication failed (JWT error or incorrect credentials).")
                st.session_state.auth_error = "Incorrect username or password."
                st.rerun()
    
    # ===========================
    # Login Flow
    # ===========================
    if login_button and not st.session_state.is_authenticating:
        log.info(f"[LOGIN] Clicked | username={username!r} | pw_len={len(password)}")
        
        # Set authenticating state and rerun to show loader
        st.session_state.is_authenticating = True
        st.rerun()
    
    # Close content wrapper
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    # Load and render Footer (at bottom, no extra space)
    footer_html = load_html_component("login_footer.html")
    if footer_html:
        st.markdown(footer_html, unsafe_allow_html=True)


# Run main
if __name__ == "__main__":
    main()
