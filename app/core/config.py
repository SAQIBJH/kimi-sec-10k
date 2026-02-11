"""
Configuration module for environment-based settings.
Supports local development and production deployments.
"""
import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
# Load environment variables from .env file in development
load_dotenv()

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
    
    @property
    def connection_string(self) -> str:
        """Generate MySQL connection string."""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


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


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    Falls back to sensible defaults for local development.
    """
    env = Environment(os.getenv("APP_ENV", "local"))
    
    # Database configuration
    db_config = DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "secfiling"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "admin"),
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    )
    
    return AppConfig(
        env=env,
        debug=os.getenv("DEBUG", "true").lower() == "true" if env != Environment.PRODUCTION else False,
        database=db_config,
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
        enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
        cache_ttl=int(os.getenv("CACHE_TTL", "300")),
        default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("MAX_PAGE_SIZE", "100")),
    )


# Global configuration instance
config = load_config()
