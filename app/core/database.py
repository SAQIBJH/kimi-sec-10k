"""
Database connector layer with connection pooling.
"""
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator, Callable
from functools import wraps
import threading

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .config import config

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class DatabaseQueryError(Exception):
    """Raised when a database query fails."""
    pass


class DatabaseManager:
    """
    Centralized database manager with connection pooling.
    Singleton pattern ensures single connection pool across the application.
    """
    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()
    
    # Phase 2: SQLAlchemy engine and session factory
    _engine: Any = None
    _session_factory: Any = None
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._config = config.database
        self._initialized = True
        self._local = threading.local()
        logger.info(f"DatabaseManager initialized for environment: {config.env.value}")
    
    def connect(self) -> None:
        """
        Initialize database connection pool with SSL and connection validation.
        """
        try:
            ssl_enabled = self._config.ssl_enabled
            # Get actual connect_args (triggers late-binding if needed)
            connect_args = self._config.connect_args
            
            if ssl_enabled:
                # Log the actual CA path being used (after late-binding)
                actual_ca = connect_args.get('ssl', {}).get('ca') if connect_args else None
                logger.info(f"SSL enabled — using CA: {actual_ca}")
            else:
                logger.debug("SSL disabled — connecting without SSL")

            self._engine = create_engine(
                self._config.connection_string,
                poolclass=QueuePool,
                pool_size=self._config.pool_size,
                max_overflow=self._config.max_overflow,
                pool_timeout=self._config.pool_timeout,
                pool_recycle=self._config.pool_recycle,
                echo=config.debug,
                connect_args=connect_args,
            )
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Test the connection immediately
            try:
                logger.info(f"Testing database connection to: {self._config.database} as {self._config.user}@{self._config.host}:{self._config.port}")
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info(f"✓ Database connection successful: {self._config.database}")
            except Exception as test_err:
                logger.error(f"Database connection test failed: {test_err}")
                logger.error(f"Connection details: host={self._config.host}, "
                           f"port={self._config.port}, database={self._config.database}, "
                           f"user={self._config.user}, ssl_enabled={self._config.ssl_enabled}")
                logger.error(f"Hint: User '{self._config.user}' may not have access to database '{self._config.database}'")
                logger.error(f"      Check grants with: SHOW GRANTS FOR '{self._config.user}'@'%';")
                raise DatabaseConnectionError(
                    f"Database connection test failed. Check credentials, network access, "
                    f"and SSL configuration. Error: {test_err}"
                )
        except DatabaseConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise DatabaseConnectionError(f"Database connection failed: {e}")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Ensures proper transaction handling and connection cleanup.
        """
        if self._engine is None:
            self.connect()
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise DatabaseQueryError(f"Query execution failed: {e}")
        finally:
            session.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of row dictionaries
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]
    
    def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute query returning single scalar value."""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.scalar()
    
    def execute_insert(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query and return affected rows.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Number of rows affected
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.rowcount
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


class MockSession:
    """Mock session for Phase 1 development."""
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def close(self):
        pass
    
    def execute(self, query, params=None):
        return MockResult()


class MockResult:
    """Mock result for Phase 1 development."""
    def scalar(self):
        return None
    
    def __iter__(self):
        return iter([])


# Global database manager instance
db_manager = DatabaseManager()


def with_db_session(func: Callable) -> Callable:
    """Decorator to inject database session into function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_manager.get_session() as session:
            kwargs['session'] = session
            return func(*args, **kwargs)
    return wrapper


def init_database():
    """Initialize database connection on application startup."""
    db_manager.connect()
