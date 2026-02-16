"""
Local storage utility for persisting user state across sessions.
Uses streamlit-local-storage for client-side persistence.
"""
import json
import logging
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, date
from enum import Enum

import streamlit as st

logger = logging.getLogger(__name__)


class StorageKey(Enum):
    """Enumeration of local storage keys for type safety."""
    SEC_FILING = "sec_filing"
    START_DATE = "start_date"
    END_DATE = "end_date"
    USER_PREFERENCES = "user_preferences"
    CHART_SETTINGS = "chart_settings"
    FILTER_STATE = "filter_state"
    # Market Data page keys
    MARKETDATA_SELECTED_SOURCE = "marketdata_selected_source"
    MARKETDATA_SELECTED_COMPANY = "marketdata_selected_company"
    MARKETDATA_SELECTED_TAB = "marketdata_selected_tab"
    MARKETDATA_DATE_START = "marketdata_date_start"
    MARKETDATA_DATE_END = "marketdata_date_end"
    # Global company selection (used across all pages)
    COMPANY_SELECTED = "company_selected"


@dataclass
class UserFilterState:
    """User's filter selections."""
    sec_filing: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserFilterState':
        return cls(**data)


class LocalStorageManager:
    """
    Global utility for managing local storage operations.
    Provides safe get/set/update operations with type validation.
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._initialized = False
    
    def _get_from_st_state(self, key: str) -> Optional[Any]:
        """Retrieve value from streamlit session state."""
        storage_key = f"ls_{key}"
        if storage_key in st.session_state:
            return st.session_state[storage_key]
        return None
    
    def _set_to_st_state(self, key: str, value: Any) -> None:
        """Store value in streamlit session state."""
        storage_key = f"ls_{key}"
        st.session_state[storage_key] = value
        self._cache[key] = value
    
    def get(
        self, 
        key: StorageKey | str, 
        default: Any = None,
        validate_type: Optional[type] = None
    ) -> Any:
        """
        Safely retrieve data from local storage.
        
        Args:
            key: Storage key (enum or string)
            default: Default value if key not found
            validate_type: Optional type to validate against
            
        Returns:
            Stored value or default
        """
        key_str = key.value if isinstance(key, StorageKey) else key
        
        try:
            # Check cache first
            if key_str in self._cache:
                value = self._cache[key_str]
            else:
                value = self._get_from_st_state(key_str)
                if value is None:
                    return default
                self._cache[key_str] = value
            
            # Type validation
            if validate_type is not None and value is not None:
                if not isinstance(value, validate_type):
                    logger.warning(f"Type mismatch for key {key_str}: expected {validate_type}, got {type(value)}")
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error retrieving local storage key {key_str}: {e}")
            return default
    
    def set(
        self, 
        key: StorageKey | str, 
        value: Any,
        serializer: Optional[Callable[[Any], str]] = None
    ) -> bool:
        """
        Safely store data in local storage.
        
        Args:
            key: Storage key (enum or string)
            value: Value to store
            serializer: Optional custom serializer
            
        Returns:
            True if successful, False otherwise
        """
        key_str = key.value if isinstance(key, StorageKey) else key
        
        try:
            # Serialize if needed
            if serializer is not None:
                value = serializer(value)
            elif isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self._set_to_st_state(key_str, value)
            logger.debug(f"Stored value for key: {key_str}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing local storage key {key_str}: {e}")
            return False
    
    def update(
        self, 
        key: StorageKey | str, 
        updater: Callable[[Any], Any],
        default: Any = None
    ) -> bool:
        """
        Update existing value using a transformer function.
        
        Args:
            key: Storage key
            updater: Function that receives current value and returns new value
            default: Default value if key doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        current = self.get(key, default)
        new_value = updater(current)
        return self.set(key, new_value)
    
    def delete(self, key: StorageKey | str) -> bool:
        """
        Remove a key from local storage.
        
        Args:
            key: Storage key to remove
            
        Returns:
            True if successful, False otherwise
        """
        key_str = key.value if isinstance(key, StorageKey) else key
        
        try:
            storage_key = f"ls_{key_str}"
            if storage_key in st.session_state:
                del st.session_state[storage_key]
            if key_str in self._cache:
                del self._cache[key_str]
            return True
        except Exception as e:
            logger.error(f"Error deleting local storage key {key_str}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all local storage data."""
        try:
            keys_to_remove = [k for k in st.session_state.keys() if k.startswith("ls_")]
            for key in keys_to_remove:
                del st.session_state[key]
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing local storage: {e}")
            return False
    
    def get_filter_state(self) -> UserFilterState:
        """Get user's filter state from local storage."""
        data = self.get(StorageKey.FILTER_STATE, {})
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        return UserFilterState.from_dict(data)
    
    def save_filter_state(self, state: UserFilterState) -> bool:
        """Save user's filter state to local storage."""
        return self.set(StorageKey.FILTER_STATE, state.to_dict())
    
    def sync_to_session_state(self) -> None:
        """
        Sync local storage values to streamlit session state.
        Call this at app initialization.
        """
        filter_state = self.get_filter_state()
        
        # Map to session state with standard keys
        st.session_state.sec_filing = filter_state.sec_filing
        st.session_state.start_date = filter_state.start_date
        st.session_state.end_date = filter_state.end_date
        
        logger.debug("Synced local storage to session state")
    
    def sync_from_session_state(self) -> bool:
        """
        Save current session state to local storage.
        Call this when filters change.
        """
        state = UserFilterState(
            sec_filing=st.session_state.get("sec_filing"),
            start_date=st.session_state.get("start_date"),
            end_date=st.session_state.get("end_date"),
        )
        return self.save_filter_state(state)


# Global local storage instance
local_storage = LocalStorageManager()


# Convenience functions for common operations
def get_sec_filing() -> Optional[str]:
    """Get selected SEC filing from storage."""
    return local_storage.get(StorageKey.SEC_FILING)


def set_sec_filing(filing: str) -> bool:
    """Save selected SEC filing to storage."""
    return local_storage.set(StorageKey.SEC_FILING, filing)


def get_date_range() -> tuple[Optional[str], Optional[str]]:
    """Get date range from storage."""
    start = local_storage.get(StorageKey.START_DATE)
    end = local_storage.get(StorageKey.END_DATE)
    return start, end


def set_date_range(start: str, end: str) -> bool:
    """Save date range to storage."""
    success_start = local_storage.set(StorageKey.START_DATE, start)
    success_end = local_storage.set(StorageKey.END_DATE, end)
    return success_start and success_end


def init_local_storage():
    """Initialize local storage on app startup."""
    local_storage.sync_to_session_state()


# Market Data page convenience functions
def get_marketdata_source() -> Optional[str]:
    """Get selected data source for market data."""
    return local_storage.get(StorageKey.MARKETDATA_SELECTED_SOURCE)


def set_marketdata_source(source: str) -> bool:
    """Save selected data source for market data."""
    return local_storage.set(StorageKey.MARKETDATA_SELECTED_SOURCE, source)


def get_marketdata_company() -> Optional[str]:
    """Get selected company ticker for market data."""
    return local_storage.get(StorageKey.MARKETDATA_SELECTED_COMPANY)


def set_marketdata_company(ticker: str) -> bool:
    """Save selected company ticker for market data."""
    return local_storage.set(StorageKey.MARKETDATA_SELECTED_COMPANY, ticker)


def get_marketdata_tab() -> Optional[str]:
    """Get selected tab for market data."""
    return local_storage.get(StorageKey.MARKETDATA_SELECTED_TAB, "company_profile")


def set_marketdata_tab(tab: str) -> bool:
    """Save selected tab for market data."""
    return local_storage.set(StorageKey.MARKETDATA_SELECTED_TAB, tab)


def get_marketdata_date_range() -> tuple[Optional[str], Optional[str]]:
    """Get date range for market data."""
    start = local_storage.get(StorageKey.MARKETDATA_DATE_START)
    end = local_storage.get(StorageKey.MARKETDATA_DATE_END)
    return start, end


def set_marketdata_date_range(start: str, end: str) -> bool:
    """Save date range for market data."""
    success_start = local_storage.set(StorageKey.MARKETDATA_DATE_START, start)
    success_end = local_storage.set(StorageKey.MARKETDATA_DATE_END, end)
    return success_start and success_end


# Global company selection functions (used across all pages)
def get_selected_company() -> Optional[str]:
    """Get the globally selected company ticker (used across all pages)."""
    return local_storage.get(StorageKey.COMPANY_SELECTED)


def set_selected_company(ticker: str) -> bool:
    """Save the globally selected company ticker (used across all pages)."""
    # Also update marketdata company for backward compatibility
    set_marketdata_company(ticker)
    return local_storage.set(StorageKey.COMPANY_SELECTED, ticker)


def clear_selected_company() -> bool:
    """Clear the selected company."""
    return local_storage.delete(StorageKey.COMPANY_SELECTED)
