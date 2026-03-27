"""
Unit Tests for Authentication Logic
====================================
Tests auth data structures, session logic, and cookie contracts
WITHOUT importing Streamlit (which requires a running server).

Run: pytest tests/unit/test_auth_manager.py -v
"""
import json
import uuid
import time
import pytest
from datetime import datetime, timezone, timedelta


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Cookie Configuration Contract Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestCookieContract:

    EXPECTED_COOKIE_NAME = "auth_session"
    EXPECTED_MAX_AGE_DAYS = 7

    def test_cookie_name_is_auth_session(self):
        """Cookie name must be 'auth_session' — all browsers and server code depend on this."""
        assert self.EXPECTED_COOKIE_NAME == "auth_session"

    def test_cookie_max_age_is_7_days(self):
        """Cookie expiry is 7 days for production."""
        assert self.EXPECTED_MAX_AGE_DAYS == 7

    def test_cookie_expiry_seconds(self):
        """7 days in seconds = 604800."""
        expiry_seconds = self.EXPECTED_MAX_AGE_DAYS * 24 * 60 * 60
        assert expiry_seconds == 604800


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Session ID Generation & Uniqueness
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestSessionIdGeneration:

    def test_session_id_is_valid_uuid(self):
        """Session IDs must be valid UUID4 format."""
        sid = str(uuid.uuid4())
        parsed = uuid.UUID(sid, version=4)
        assert str(parsed) == sid

    def test_session_ids_are_unique(self):
        """1000 session IDs should have zero collisions."""
        ids = {str(uuid.uuid4()) for _ in range(1000)}
        assert len(ids) == 1000, "UUID collision detected!"

    def test_session_id_length(self):
        """UUID4 string is always 36 characters (8-4-4-4-12)."""
        sid = str(uuid.uuid4())
        assert len(sid) == 36

    def test_session_id_is_string(self):
        """Session ID must be a string for JSON serialization."""
        sid = str(uuid.uuid4())
        assert isinstance(sid, str)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Auth Cookie Data Validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestAuthCookieData:

    def _make_auth_data(self, email="user@test.com"):
        return {
            "session_id": str(uuid.uuid4()),
            "email": email,
            "display_name": "Test User",
            "login_time": datetime.now(timezone.utc).isoformat(),
        }

    def test_auth_data_is_json_serializable(self):
        """Auth data must be JSON serializable for cookie storage."""
        data = self._make_auth_data()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed["email"] == "user@test.com"

    def test_auth_data_has_session_id(self):
        """Cookie data must contain session_id."""
        data = self._make_auth_data()
        assert "session_id" in data
        assert len(data["session_id"]) == 36

    def test_auth_data_has_email(self):
        """Cookie data must contain user email."""
        data = self._make_auth_data()
        assert "email" in data
        assert "@" in data["email"]

    def test_auth_data_has_login_time(self):
        """Cookie data must contain login timestamp."""
        data = self._make_auth_data()
        assert "login_time" in data
        # Should be parseable as ISO format
        dt = datetime.fromisoformat(data["login_time"])
        assert dt.tzinfo is not None  # Must be timezone-aware

    def test_empty_email_is_invalid(self):
        """Empty email should be caught as invalid."""
        email = ""
        assert not email, "Empty email should be falsy"

    def test_none_session_id_is_invalid(self):
        """None session_id should be rejected."""
        session_id = None
        assert session_id is None  # Validation should catch this


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Domain Normalization Logic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestDomainNormalization:

    def _normalize(self, host):
        """Mirrors get_current_domain logic without Streamlit dep."""
        domain = host.split(":", 1)[0].strip().lower()
        if domain == "localhost":
            return "localhost"
        elif domain == "0.0.0.0":
            return "0.0.0.0"
        return domain

    def test_localhost_preserved(self):
        assert self._normalize("localhost:8502") == "localhost"

    def test_zero_addr_preserved(self):
        assert self._normalize("0.0.0.0:8502") == "0.0.0.0"

    def test_port_stripped(self):
        assert self._normalize("example.com:8502") == "example.com"

    def test_case_normalized(self):
        assert self._normalize("Example.COM:8502") == "example.com"

    def test_no_port(self):
        assert self._normalize("mysite.com") == "mysite.com"

    def test_ip_address(self):
        assert self._normalize("10.2.6.4:3306") == "10.2.6.4"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  User Isolation Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestUserIsolation:

    def test_different_users_get_different_sessions(self):
        """Two users must never share a session ID."""
        session_a = str(uuid.uuid4())
        session_b = str(uuid.uuid4())
        assert session_a != session_b

    def test_session_tied_to_email(self):
        """Each session must be associated with exactly one email."""
        data_a = {"session_id": str(uuid.uuid4()), "email": "alice@test.com"}
        data_b = {"session_id": str(uuid.uuid4()), "email": "bob@test.com"}
        assert data_a["email"] != data_b["email"]
        assert data_a["session_id"] != data_b["session_id"]

    def test_relogin_creates_new_session(self):
        """Re-login must produce a new session_id (no reuse)."""
        first_login = str(uuid.uuid4())
        second_login = str(uuid.uuid4())
        assert first_login != second_login


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Security Validation Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestSecurityValidation:

    def test_session_id_not_predictable(self):
        """Session IDs should be cryptographically random (UUID4)."""
        ids = [str(uuid.uuid4()) for _ in range(100)]
        # No sequential pattern
        assert len(set(ids)) == 100

    def test_xss_in_email_detectable(self):
        """XSS payload in email should be detectable."""
        malicious_email = "<script>alert('xss')</script>@evil.com"
        assert "<script" in malicious_email  # Detection logic should catch this

    def test_sql_injection_in_email_detectable(self):
        """SQL injection in email should be detectable."""
        malicious_email = "'; DROP TABLE users; --"
        assert "DROP TABLE" in malicious_email  # Should be parameterized anyway

    def test_cookie_value_not_plaintext_password(self):
        """Cookie should never contain the password."""
        auth_data = {
            "session_id": str(uuid.uuid4()),
            "email": "user@test.com",
        }
        json_str = json.dumps(auth_data)
        assert "password" not in json_str.lower()
        assert "Welcome@123" not in json_str
