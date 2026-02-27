"""
Configuration module for environment-based settings.
Supports local development and production deployments.

Key fix:
- If SSL is enabled but SSL_CA is missing at import time (common in Streamlit),
  we late-bind the CA path by calling core.ssl_setup.ensure_ca_cert() inside
  DatabaseConfig.connect_args.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file in development
load_dotenv()

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Application environments."""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str
    port: int
    database: str
    user: str
    password: str

    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800

    ssl_enabled: bool = False
    ssl_ca: Optional[str] = None

    @property
    def connection_string(self) -> str:
        """
        Generate MySQL connection string for SQLAlchemy.
        NOTE: Do NOT print/log this string (contains password).
        """
        # If your DB name can contain special chars, URL-encode it. Keeping simple here.
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def connect_args(self) -> dict:
        """
        Return SSL connect_args for SQLAlchemy if SSL is enabled.
        IMPORTANT: Late-bind CA path here to avoid Streamlit import-order issues.

        If ssl_enabled=True and ssl_ca is missing, we call ensure_ca_cert() which:
        - downloads the CA if needed
        - sets os.environ["SSL_CA"]
        - returns the absolute path
        """
        if not self.ssl_enabled:
            return {}

        # First check if SSL_CA was set in environment (by ensure_ca_cert or otherwise)
        ca_from_env = os.getenv("SSL_CA", "").strip()
        if ca_from_env:
            # Update our cached value
            self.ssl_ca = ca_from_env
            return {"ssl": {"ca": ca_from_env}}

        # Check if we already have a cached value
        ca_path = (self.ssl_ca or "").strip() if isinstance(self.ssl_ca, str) else None

        # Late-bind if missing (common when config is imported before main.py calls ensure_ca_cert())
        if not ca_path:
            try:
                from core.ssl_setup import ensure_ca_cert  # local import to avoid circulars
                ca_path = ensure_ca_cert()
                self.ssl_ca = ca_path  # update cached config instance
                logger.info(f"[CONFIG] Late-bound SSL_CA via ensure_ca_cert(): {ca_path}")
            except Exception as e:
                # Do not crash here; DB layer will raise a clearer error if SSL actually required.
                logger.warning(f"[CONFIG] SSL enabled but CA could not be resolved: {e}")
                ca_path = None

        if ca_path:
            # pymysql expects connect_args={"ssl": {"ca": "..."}}
            return {"ssl": {"ca": ca_path}}

        # If still None, warn and return empty args
        logger.warning("[CONFIG] SSL enabled but no CA certificate available")
        return {}


@dataclass
class AppConfig:
    """Application configuration."""
    env: Environment
    debug: bool
    database: DatabaseConfig
    secret_key: str
    session_timeout: int = 3600

    # Feature flags
    enable_caching: bool = True
    cache_ttl: int = 300

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    # Navigation mode: 'new' = open in new tab, 'same' = load in same tab
    navigation_mode: str = "same"


def _as_bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    Falls back to sensible defaults for local development.
    """
    env_str = os.getenv("APP_ENV", "local").strip().lower()
    try:
        env = Environment(env_str)
    except Exception:
        env = Environment.LOCAL

    pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # SSL is only considered in staging/production in this template
    if env in (Environment.STAGING, Environment.PRODUCTION):
        ssl_enabled = _as_bool(os.getenv("ENABLE_SSL", "false"), default=False)

        # If SSL enabled, read SSL_CA from env *if present*.
        # If it's missing, DatabaseConfig.connect_args will late-bind it.
        ssl_ca = os.getenv("SSL_CA") if ssl_enabled else None

        # Prefer STG_DB_* for staging, PROD_DB_* for prod; fall back to DB_*.
        if env == Environment.STAGING:
            host = os.getenv("STG_DB_HOST", os.getenv("DB_HOST", "localhost"))
            port = int(os.getenv("STG_DB_PORT", os.getenv("DB_PORT", "3306")))
            database = os.getenv("STG_DB_NAME", os.getenv("DB_NAME", "secfiling"))
            user = os.getenv("STG_DB_USER", os.getenv("DB_USER", "root"))
            password = os.getenv("STG_DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
        else:  # PRODUCTION
            host = os.getenv("PROD_DB_HOST", os.getenv("DB_HOST", "localhost"))
            port = int(os.getenv("PROD_DB_PORT", os.getenv("DB_PORT", "3306")))
            database = os.getenv("PROD_DB_NAME", os.getenv("DB_NAME", "secfiling"))
            user = os.getenv("PROD_DB_USER", os.getenv("DB_USER", "root"))
            password = os.getenv("PROD_DB_PASSWORD", os.getenv("DB_PASSWORD", ""))

        db_config = DatabaseConfig(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            pool_size=pool_size,
            max_overflow=max_overflow,
            ssl_enabled=ssl_enabled,
            ssl_ca=ssl_ca,
        )
    else:
        # Local: default SSL off unless you explicitly enable it
        ssl_enabled = _as_bool(os.getenv("ENABLE_SSL", "false"), default=False)
        ssl_ca = os.getenv("SSL_CA") if ssl_enabled else None

        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "secfiling"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "admin"),
            pool_size=pool_size,
            max_overflow=max_overflow,
            ssl_enabled=ssl_enabled,
            ssl_ca=ssl_ca,
        )

    debug = _as_bool(os.getenv("DEBUG", "true"), default=True)
    if env == Environment.PRODUCTION:
        debug = _as_bool(os.getenv("DEBUG", "false"), default=False)

    cfg = AppConfig(
        env=env,
        debug=debug,
        database=db_config,
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
        enable_caching=_as_bool(os.getenv("ENABLE_CACHING", "true"), default=True),
        cache_ttl=int(os.getenv("CACHE_TTL", "300")),
        default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("MAX_PAGE_SIZE", "100")),
        navigation_mode=os.getenv("NAVIGATION_MODE", "same").strip().lower(),
    )

    # Safe logging (no passwords)
    logger.info(
        f"[CONFIG] env={cfg.env.value} debug={cfg.debug} "
        f"db_host={cfg.database.host} db_port={cfg.database.port} "
        f"db_name={cfg.database.database} db_user={cfg.database.user} "
        f"ssl_enabled={cfg.database.ssl_enabled} ssl_ca={'<set>' if cfg.database.ssl_ca else None}"
    )

    return cfg


# Global configuration instance (import-safe)
config = load_config()
