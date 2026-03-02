"""
Authentication Manager - Session Token Pattern
- Login: Store in DB + Cookie
- Auth check: Cookie only (fast)
- DB used for audit, not validation
"""
import os
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from time import sleep
from typing import Optional, Dict, Any
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController

from core.database import db_manager

load_dotenv()
logger = logging.getLogger(__name__)

# Cookie settings
COOKIE_NAME = "auth_session"
COOKIE_MAX_AGE_DAYS = 7


def get_current_domain(default: Optional[str] = None) -> str:
    """Best-effort current host → cookie domain (normalized)."""
    try:
        host = st.context.headers.get("host", "")
 
        if not host:
            try:
                from streamlit.web.server.websocket_headers import _get_websocket_headers
                ws = _get_websocket_headers() or {}
                host = ws.get("host") or ws.get("Host") or ""
            except ImportError:
                pass
 
        # Extract only the domain part (ignore port if present)
        domain = host.split(":", 1)[0].strip().lower()
 
        # --- Normalize allowed domains ---
        if domain == "localhost":
            return "localhost"
        elif domain == "0.0.0.0":
            return "0.0.0.0"
        elif domain.endswith(".coresight.com"):
            return ".coresight.com"
 
        # Fallback
        return default or ""
    except Exception:
        return default or ""


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    success: bool
    session_id: Optional[str] = None
    user_email: Optional[str] = None
    error_message: Optional[str] = None


class AuthManager:
    """Manages user authentication with session token pattern."""
    
    def _get_controller(self) -> CookieController:
        """Get a fresh CookieController for the current Streamlit session.
        Must NOT be cached as a class attribute — each session needs its own."""
        return CookieController(key="auth_cookies")
    
    # =========================================================================
    # LOGIN FLOW
    # =========================================================================
    
    def login(self, user_email: str, user_nicename: str, 
              user_display_name: str, token: str) -> AuthResult:
        """
        Complete login flow:
        1. Generate session_id
        2. Store in database (audit trail)
        3. Store session_id in cookie
        4. Set session state
        """
        try:
            # Generate cryptographically secure session ID
            session_id = self._generate_session_id()
            
            # Store in database (for audit, can be disabled if DB down)
            self._store_session_in_db(
                user_email=user_email,
                user_nicename=user_nicename,
                user_display_name=user_display_name,
                token=token
            )
            
            # Prepare auth data for cookie
            auth_data = {
                "session_id": session_id,
                "user_email": user_email,
                "user_display_name": user_display_name,
                "login_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store in cookie
            if not self._set_cookie(auth_data):
                return AuthResult(
                    success=False, 
                    error_message="Failed to create session"
                )
            
            # Set session state for current request
            st.session_state.auth_data = auth_data
            st.session_state.authenticated = True
            
            logger.info(f"Login successful: {user_email}, session: {session_id}")
            
            return AuthResult(
                success=True,
                session_id=session_id,
                user_email=user_email
            )
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return AuthResult(
                success=False, 
                error_message="Login failed. Please try again."
            )
    
    def _generate_session_id(self) -> str:
        """Generate secure random session ID."""
        return uuid.uuid4().hex  # 32 character hex string
    
    def _store_session_in_db(self,  user_email: str,
                             user_nicename: str, user_display_name: str,
                             token: str) -> bool:
        """
        Store session in database for audit trail.
        Non-blocking: Login succeeds even if DB fails.
        """
        try:
            query = """
            INSERT INTO market_data_user_sessions 
                (user_email, user_nicename, user_display_name, token, 
                 login_at, last_activity)
            VALUES 
                (:user_email, :user_nicename, :user_display_name, :token,
                 NOW(), NOW())
            """
            
            db_manager.execute_insert(query, {
                "user_email": user_email,
                "user_nicename": user_nicename,
                "user_display_name": user_display_name,
                "token": token
            })
            
            logger.debug(f"Session stored in DB for user: {user_email}")
            return True
            
        except Exception as e:
            # Log but don't fail login - cookie is source of truth
            logger.warning(f"DB storage failed (non-critical): {e}")
            return False
    
    def _set_cookie(self, auth_data: Dict[str, Any]) -> bool:
        """Set auth cookie with session data."""
        try:
            cookie_value = json.dumps(auth_data, separators=(',', ':'))
            
            expires_dt = datetime.now(timezone.utc) + timedelta(days=COOKIE_MAX_AGE_DAYS)
            domain = get_current_domain()
            
            cookie_params = {
                'expires': expires_dt,
                'path': '/',
                'domain': domain,
            }
            
            controller = self._get_controller()
            controller.set(COOKIE_NAME, cookie_value, **cookie_params)
            # Allow the frontend time to process the Set-Cookie command
            # before any page navigation (CookieController is async)
            sleep(1.5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cookie: {e}")
            return False
    
    # =========================================================================
    # AUTH CHECK (NO DB CALL - FAST)
    # =========================================================================
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.
        FAST: Only checks cookie, no database call.
        """
        # Fast path: already in session state
        if st.session_state.get("authenticated") and st.session_state.get("auth_data"):
            return True
        
        # Check cookie
        auth_data = self._get_cookie()
        if auth_data and auth_data.get("session_id"):
            # Valid session in cookie
            st.session_state.auth_data = auth_data
            st.session_state.authenticated = True
            return True
        
        return False
    
    def require_auth(self, redirect_to: str = "login") -> Optional[Dict[str, Any]]:
        """
        Require authentication for protected pages.
        Uses st.rerun() retry to handle async CookieController mount on refresh.
        SECURITY: st.stop() is called after redirect/rerun as a safety net
                  to guarantee execution NEVER continues past this point.
        
        DEBUG MODE: Auth is bypassed when APP_ENV=LOCAL and DEBUG=true
        """
        # DEBUG MODE BYPASS: Allow access without auth in local debug mode
        app_env = os.getenv("APP_ENV", "").upper()
        debug_mode = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        if app_env == "LOCAL" and debug_mode:
            # Set mock auth data for testing
            if not st.session_state.get("authenticated"):
                st.session_state.auth_data = {
                    "session_id": "local-debug-session",
                    "user_email": "local@test.com",
                    "user_display_name": "Local Test User",
                    "login_at": datetime.now(timezone.utc).isoformat()
                }
                st.session_state.authenticated = True
            return st.session_state.get("auth_data")
        
        # Initialize retry counter on first run
        if "_auth_retry_count" not in st.session_state:
            st.session_state._auth_retry_count = 0
        
        # Fast path: already authenticated in session state
        if self.is_authenticated():
            st.session_state._auth_retry_count = 0
            return st.session_state.get("auth_data")
        
        # Cookie not available yet — CookieController may still be mounting.
        # Retry by calling st.rerun() to give the frontend another render cycle.
        # sleep() gives the frontend time to mount the component before retrying.
        if st.session_state._auth_retry_count < 5:
            st.session_state._auth_retry_count += 1
            sleep(1.0)
            st.rerun()
            st.stop()  # Safety net: guarantee execution halts
            return None
        
        # Max retries exhausted — cookie truly not available, redirect to login
        st.session_state._auth_retry_count = 0
        if "auth_data" in st.session_state:
            del st.session_state["auth_data"]
        if "authenticated" in st.session_state:
            del st.session_state["authenticated"]
        st.switch_page(f"pages/{redirect_to}.py")
        st.stop()  # Safety net: guarantee execution halts even if switch_page fails
        return None
    
    def _get_cookie(self) -> Optional[Dict[str, Any]]:
        """Read and parse auth cookie."""
        try:
            controller = self._get_controller()
            cookie_value = controller.get(COOKIE_NAME)
            
            if not cookie_value:
                return None
            
            if isinstance(cookie_value, str):
                return json.loads(cookie_value)
            
            return cookie_value
            
        except Exception as e:
            logger.warning(f"Failed to read cookie: {e}")
            return None
    
    # =========================================================================
    # USER INFO GETTERS
    # =========================================================================
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged-in user email."""
        auth_data = st.session_state.get("auth_data")
        return auth_data.get("user_email") if auth_data else None
    
    def get_session_id(self) -> Optional[str]:
        """Get current session ID."""
        auth_data = st.session_state.get("auth_data")
        return auth_data.get("session_id") if auth_data else None
    
    def get_auth_data(self) -> Optional[Dict[str, Any]]:
        """Get full auth data from session."""
        return st.session_state.get("auth_data")
    
    # =========================================================================
    # LOGOUT
    # =========================================================================
    
    def logout(self):
        """Logout user - clear cookie and session."""
        try:
            # Remove cookie — sleep BEFORE remove so CookieController has
            # time to mount on fresh page loads (?action=logout); the
            # component is async and remove() silently fails if called early.
            try:
                domain = get_current_domain()
                controller = self._get_controller()
                sleep(2.0)
                controller.remove(COOKIE_NAME, path="/", domain=domain or None)
                sleep(0.5)  # Allow frontend to process the removal
                logger.info(f"Cookie removed with domain: {domain}")
            except Exception as e:
                logger.warning(f"Cookie clear warning: {e}")
            
            # Clear session state
            keys_to_remove = ["auth_data", "authenticated"]
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            sleep(0.5)
            logger.info("User logged out")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
        
        # # Small delay before redirect (same as auth_utils)
        # sleep(0.5)
        
        # # Redirect to login
        # st.switch_page("pages/login.py")


# =========================================================================
# GLOBAL INSTANCE (Singleton Pattern)
# =========================================================================

_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create AuthManager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# =========================================================================
# CONVENIENCE FUNCTIONS (Module-level)
# =========================================================================

def login_user(user_email: str, user_nicename: str, 
               user_display_name: str, token: str) -> AuthResult:
    """Module-level login function."""
    return get_auth_manager().login(user_email, user_nicename, user_display_name, token)


def require_auth(redirect_to: str = "login") -> Optional[Dict[str, Any]]:
    """Module-level auth check for protected pages."""
    return get_auth_manager().require_auth(redirect_to)


def is_authenticated() -> bool:
    """Module-level auth check."""
    return get_auth_manager().is_authenticated()


def logout():
    """Module-level logout."""
    return get_auth_manager().logout()


def get_current_user() -> Optional[str]:
    """Module-level getter for current user."""
    return get_auth_manager().get_current_user()


def get_session_id() -> Optional[str]:
    """Module-level getter for session ID."""
    return get_auth_manager().get_session_id()
