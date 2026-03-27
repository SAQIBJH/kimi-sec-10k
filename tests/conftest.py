"""
Shared pytest fixtures for all test suites.
"""
import os
import sys
import pytest
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add app/ to sys.path so core.* imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


@pytest.fixture(scope="session")
def app_url():
    """Base URL of the running Streamlit app."""
    port = os.environ.get("TEST_PORT", "8502")
    return f"http://localhost:{port}"


@pytest.fixture(scope="session")
def test_credentials():
    """Test user credentials from .env."""
    return {
        "email": os.environ.get("ADMIN_EMAIL", "mohdsaeedafri@coresight.com"),
        "password": os.environ.get("ADMIN_PASSWORD", "Welcome@123"),
    }


@pytest.fixture(scope="session")
def db_config():
    """Database configuration for STG/LOCAL based on APP_ENV."""
    env = os.environ.get("APP_ENV", "LOCAL").lower()
    if env == "staging":
        return {
            "host": os.environ.get("STG_DB_HOST"),
            "port": int(os.environ.get("STG_DB_PORT", 3306)),
            "user": os.environ.get("STG_DB_USER"),
            "password": os.environ.get("STG_DB_PASS"),
            "database": os.environ.get("STG_DB_NAME"),
            "ssl_ca": os.environ.get("SSL_CA"),
        }
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASS"),
        "database": os.environ.get("DB_NAME"),
        "ssl_ca": None,
    }
