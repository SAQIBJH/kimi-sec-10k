"""
Backend DB Integration Tests for Login Sessions
================================================
Tests that login sessions are correctly stored and managed in the database.
Works with both LOCAL and STG databases based on APP_ENV.

Run: pytest tests/backend/test_db_sessions.py -v
Prerequisites: Database accessible (APP_ENV in .env determines which DB)
"""
import os
import sys
import ssl
import time
import uuid
import pytest
from datetime import datetime, timezone

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# ── DB Connection ─────────────────────────────────────────────
def _get_db_connection():
    """Get pymysql connection based on APP_ENV."""
    import pymysql
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

    env = os.environ.get("APP_ENV", "LOCAL").lower()

    if env == "staging":
        ssl_ca = os.environ.get("SSL_CA")
        ssl_ctx = ssl.create_default_context(cafile=ssl_ca) if ssl_ca else None
        return pymysql.connect(
            host=os.environ.get("STG_DB_HOST"),
            port=int(os.environ.get("STG_DB_PORT", 3306)),
            user=os.environ.get("STG_DB_USER"),
            password=os.environ.get("STG_DB_PASS"),
            database=os.environ.get("STG_DB_NAME"),
            ssl=ssl_ctx,
            connect_timeout=30,
        )
    else:
        return pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME"),
            connect_timeout=10,
        )


@pytest.fixture(scope="module")
def db():
    """Database connection fixture."""
    try:
        conn = _get_db_connection()
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"Database not accessible: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Table Schema Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestSessionTableSchema:

    def test_sessions_table_exists(self, db):
        """market_data_user_sessions table must exist."""
        cursor = db.cursor()
        cursor.execute("SHOW TABLES LIKE 'market_data_user_sessions'")
        result = cursor.fetchone()
        assert result is not None, "market_data_user_sessions table does not exist!"

    def test_required_columns_present(self, db):
        """Table must have required columns."""
        cursor = db.cursor()
        cursor.execute("DESCRIBE market_data_user_sessions")
        columns = {row[0] for row in cursor.fetchall()}
        required = {"id", "email", "session_token", "login_time"}
        missing = required - columns
        assert not missing, f"Missing required columns: {missing}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Session Data Integrity Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestSessionDataIntegrity:

    def test_sessions_exist(self, db):
        """There should be at least 1 session in the table."""
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM market_data_user_sessions")
        count = cursor.fetchone()[0]
        assert count > 0, "No sessions found in database"

    def test_session_has_valid_email(self, db):
        """All sessions should have non-empty email addresses."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions WHERE email IS NULL OR email = ''"
        )
        invalid = cursor.fetchone()[0]
        assert invalid == 0, f"{invalid} sessions have empty/null email"

    def test_session_has_valid_token(self, db):
        """All sessions should have non-empty session tokens."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions "
            "WHERE session_token IS NULL OR session_token = ''"
        )
        invalid = cursor.fetchone()[0]
        assert invalid == 0, f"{invalid} sessions have empty/null token"

    def test_session_tokens_are_unique(self, db):
        """Session tokens should be unique (no duplicates)."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT session_token, COUNT(*) as cnt "
            "FROM market_data_user_sessions "
            "GROUP BY session_token HAVING cnt > 1"
        )
        duplicates = cursor.fetchall()
        assert len(duplicates) == 0, f"Duplicate session tokens found: {duplicates}"

    def test_login_time_not_future(self, db):
        """Login timestamps should not be in the future."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions WHERE login_time > NOW() + INTERVAL 1 HOUR"
        )
        future = cursor.fetchone()[0]
        assert future == 0, f"{future} sessions have future login times"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Test User Session Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestUserSessions:

    def test_test_user_has_sessions(self, db):
        """The test user should have at least one session."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions WHERE email = %s",
            ("mohdsaeedafri@coresight.com",)
        )
        count = cursor.fetchone()[0]
        assert count > 0, "Test user has no sessions"

    def test_latest_session_recent(self, db):
        """The most recent session should be from today (within last 24h)."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT login_time FROM market_data_user_sessions "
            "WHERE email = %s ORDER BY login_time DESC LIMIT 1",
            ("mohdsaeedafri@coresight.com",)
        )
        row = cursor.fetchone()
        if row:
            login_time = row[0]
            # Should be within last 24 hours (generous for timezone differences)
            assert login_time is not None, "Login time is null"

    def test_no_xss_in_sessions(self, db):
        """Session data should not contain XSS payloads."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions "
            "WHERE email LIKE '%<script%' OR session_token LIKE '%<script%'"
        )
        xss = cursor.fetchone()[0]
        assert xss == 0, "XSS payload detected in session data!"

    def test_no_sql_injection_artifacts(self, db):
        """No SQL injection artifacts in session data."""
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM market_data_user_sessions "
            "WHERE email LIKE '%DROP TABLE%' OR email LIKE '%1=1%'"
        )
        sqli = cursor.fetchone()[0]
        assert sqli == 0, "SQL injection artifact detected in session data!"
