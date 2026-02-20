"""
Local Storage Manager - Syncs session state with browser local storage
This module provides utilities to persist session state across page refreshes using streamlit-local-storage
"""
import streamlit as st
import json
import logging
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage

class LocalStorageManager:
    """Manages syncing between Streamlit session state and browser local storage"""
    
    STORAGE_KEY = "sip_app_state"  # Single key for entire app
    
    def __init__(self, page_name=None):
        """Initialize local storage manager
        
        Args:
            page_name: Page name to identify which page data to manage (e.g., 'market_data', 'home')
        """
        # Initialize with a unique key to avoid conflicts
        self.local_storage = LocalStorage(key=f"sip_local_storage_{page_name or 'default'}")
        self.page_name = page_name
        
    def load_from_local_storage(self):
        """Load state from local storage and sync to session state for this page"""
        try:
            # Get stored data from local storage using getItem
            stored_data = self.local_storage.getItem(self.STORAGE_KEY)
            
            if stored_data and stored_data != "null" and stored_data != "":
                # Parse JSON data if it's a string
                if isinstance(stored_data, str):
                    try:
                        all_pages_state = json.loads(stored_data)
                    except json.JSONDecodeError as e:
                        logging.warning(f"Invalid JSON in local storage: {stored_data}")
                        return False
                else:
                    all_pages_state = stored_data
                
                # Check if this page has data
                if isinstance(all_pages_state, dict) and self.page_name in all_pages_state:
                    page_data = all_pages_state[self.page_name]
                    
                    # page_data structure: { "base": {...}, "compare_retailers": {...}, "compare_sectors": {...}, "selected_tab_<page>": "..." }
                    if isinstance(page_data, dict):
                        loaded_count = 0
                        for key, value in page_data.items():
                            if key.startswith('selected_tab_'):
                                # Load tab selection
                                st.session_state[key] = value
                                loaded_count += 1
                            elif key.startswith('selected_ticker_'):
                                # Load ticker selection
                                st.session_state[key] = value
                                loaded_count += 1
                            elif key.startswith('date_range_'):
                                # Load date range
                                st.session_state[key] = value
                                loaded_count += 1
                            elif key.startswith('sort_order_'):
                                # Load sort order
                                st.session_state[key] = value
                                loaded_count += 1
                            elif isinstance(value, dict):
                                # Load tab filters (tab_name is the key like "base", "compare_retailers")
                                tab_name = key
                                session_key = f"filters_{self.page_name}_{tab_name}"
                                
                                # Deserialize all filter values
                                deserialized_filters = {k: self._deserialize_value(v) for k, v in value.items()}
                                
                                # Store in session state
                                st.session_state[session_key] = deserialized_filters
                                loaded_count += len(deserialized_filters)
                        
                        logging.info(f"Loaded {loaded_count} items for page '{self.page_name}' from local storage")
                        return True
                    else:
                        print(f"Page data is not a valid dict")
                else:
                    logging.info(f"No data for page '{self.page_name}' in local storage")
            else:
                logging.info(f"No data in local storage")
            
            return False
        except Exception as e:
            logging.warning(f"Failed to load from local storage: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return False
    
    def save_to_local_storage(self, page_name=None):
        """Save all filter data for this page to local storage in structured format
        
        Args:
            page_name: Override page name (optional, uses self.page_name if not provided)
        """
        page = page_name or self.page_name
        
        try:
            # Load existing data from localStorage (to preserve other pages' data)
            stored_data = self.local_storage.getItem(self.STORAGE_KEY)
            
            if stored_data and stored_data != "null" and stored_data != "":
                try:
                    all_pages_state = json.loads(stored_data) if isinstance(stored_data, str) else stored_data
                except:
                    all_pages_state = {}
            else:
                all_pages_state = {}
            
            if not isinstance(all_pages_state, dict):
                all_pages_state = {}
            
            # Collect all filter data for this page from session state
            # Structure: { "base": {...}, "compare_retailers": {...}, "compare_sectors": {...}, "selected_tab_<page>": "..." }
            page_data = {}
            
            # Look for tab selection state
            tab_selection_key = f"selected_tab_{page}"
            if tab_selection_key in st.session_state:
                page_data[tab_selection_key] = st.session_state[tab_selection_key]
            
            # Look for ticker selection state
            ticker_selection_key = f"selected_ticker_{page}"
            if ticker_selection_key in st.session_state:
                page_data[ticker_selection_key] = st.session_state[ticker_selection_key]
            
            # Look for all tab-specific date ranges
            for key in st.session_state.keys():
                if key.startswith(f'date_range_{page}_'):  # e.g., date_range_market_data_income_statement
                    page_data[key] = st.session_state[key]
            
            # Look for all tab-specific sort orders
            for key in st.session_state.keys():
                if key.startswith(f'sort_order_{page}_'):  # e.g., sort_order_market_data_income_statement
                    page_data[key] = st.session_state[key]
            
            # Look for general date range state (legacy support)
            date_range_key = f"date_range_{page}"
            if date_range_key in st.session_state:
                page_data[date_range_key] = st.session_state[date_range_key]
            
            # Look for general sort order state (legacy support)
            sort_order_key = f"sort_order_{page}"
            if sort_order_key in st.session_state:
                page_data[sort_order_key] = st.session_state[sort_order_key]
            
            # Look for all filters_<page>_<tab> keys in session state
            filter_prefix = f"filters_{page}_"
            
            for key in st.session_state.keys():
                if key.startswith(filter_prefix):
                    # Extract tab name from key (e.g., "filters_market_data_income_statement" -> "income_statement")
                    tab_name = key[len(filter_prefix):]
                    
                    # Get the filter data for this tab
                    tab_filters = st.session_state[key]
                    
                    if isinstance(tab_filters, dict) and self._is_serializable(tab_filters):
                        # Serialize each filter value
                        serialized_filters = {k: self._serialize_value(v) for k, v in tab_filters.items()}
                        page_data[tab_name] = serialized_filters
            
            if page_data:
                # Update the page data in the overall structure
                all_pages_state[page] = page_data
                
                # Convert to JSON and save
                json_data = json.dumps(all_pages_state)
                
                self.local_storage.setItem(self.STORAGE_KEY, json_data)
                logging.info(f"Successfully saved page '{page}' with {len(page_data)} items to local storage")
                
                # Also save using JavaScript as fallback
                save_to_local_storage_js(self.STORAGE_KEY, all_pages_state)
                return True
            else:
                return False
                
        except Exception as e:
            logging.warning(f"Failed to save to local storage: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            return False
    
    def clear_local_storage(self, page_name=None, tab_name=None):
        """Clear local storage for specific page/tab or entire storage
        
        Args:
            page_name: If provided, only clear this page's data
            tab_name: If provided (with page_name), only clear this specific tab's data
        """
        try:
            if page_name:
                # Load existing data
                stored_data = self.local_storage.getItem(self.STORAGE_KEY)
                if stored_data and stored_data != "null" and stored_data != "":
                    all_pages_state = json.loads(stored_data) if isinstance(stored_data, str) else stored_data
                    
                    if isinstance(all_pages_state, dict) and page_name in all_pages_state:
                        if tab_name:
                            # Clear specific tab
                            if tab_name in all_pages_state[page_name]:
                                del all_pages_state[page_name][tab_name]
                        else:
                            # Clear entire page
                            del all_pages_state[page_name]
                        
                        # Save back to localStorage
                        json_data = json.dumps(all_pages_state)
                        self.local_storage.setItem(self.STORAGE_KEY, json_data)
                        return True
            else:
                # Clear entire storage
                self.local_storage.removeItem(self.STORAGE_KEY)
                return True
        except Exception as e:
            logging.warning(f"Failed to clear local storage: {e}")
            return False
    
    def _serialize_value(self, value):
        """Serialize a value for storage"""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        elif isinstance(value, (list, dict)):
            return value  # JSON serializable
        else:
            return str(value)  # Convert to string as fallback
    
    def _deserialize_value(self, value):
        """Deserialize a value from storage"""
        return value  # For now, return as-is. Add custom deserialization if needed.
    
    def _is_serializable(self, obj):
        """Check if an object is JSON serializable"""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False


def save_to_local_storage_js(key, data):
    """Fallback JavaScript function to save data to localStorage"""
    js_code = f"""
    <script>
    try {{
        localStorage.setItem('{key}', JSON.stringify({json.dumps(data)}));
    }} catch (e) {{
        console.error('Failed to save to localStorage:', e);
    }}
    </script>
    """
    components.html(js_code, height=0, width=0)


# Convenience functions for Market Data page
def sync_market_data_state():
    """Sync market data page state between session and local storage"""
    manager = LocalStorageManager("market_data")
    
    # Load from local storage on page load
    manager.load_from_local_storage()
    
    # Set up automatic saving when state changes
    # This should be called after any state change in the UI
    return manager


def save_market_data_state():
    """Save current market data state to local storage"""
    manager = LocalStorageManager("market_data")
    return manager.save_to_local_storage()


def get_persistent_state(key, default=None):
    """Get a value from session state, with fallback to local storage"""
    if key in st.session_state:
        return st.session_state[key]
    
    # Try to load from local storage
    manager = LocalStorageManager("market_data")
    manager.load_from_local_storage()
    
    return st.session_state.get(key, default)


def set_persistent_state(key, value):
    """Set a value in session state and save to local storage"""
    st.session_state[key] = value
    save_market_data_state()


# =============================================================================
# Convenience functions for Earnings Calls page
# =============================================================================

_EC_KEYS = ("ec_company", "ec_year", "ec_quarter")


def load_earnings_calls_state():
    """Load earnings calls filter state from local storage into session state.

    Returns True if values were loaded, False otherwise.
    """
    manager = LocalStorageManager("earnings_calls")
    try:
        stored_data = manager.local_storage.getItem(manager.STORAGE_KEY)
        if stored_data and stored_data != "null" and stored_data != "":
            all_pages = json.loads(stored_data) if isinstance(stored_data, str) else stored_data
            if isinstance(all_pages, dict) and "earnings_calls" in all_pages:
                page_data = all_pages["earnings_calls"]
                if isinstance(page_data, dict):
                    for key in _EC_KEYS:
                        if key in page_data:
                            st.session_state[key] = page_data[key]
                    return True
    except Exception as e:
        logging.warning(f"Failed to load earnings calls state: {e}")
    return False


def save_earnings_calls_state():
    """Save current earnings calls filter state to local storage."""
    manager = LocalStorageManager("earnings_calls")
    try:
        stored_data = manager.local_storage.getItem(manager.STORAGE_KEY)
        if stored_data and stored_data != "null" and stored_data != "":
            try:
                all_pages = json.loads(stored_data) if isinstance(stored_data, str) else stored_data
            except Exception:
                all_pages = {}
        else:
            all_pages = {}

        if not isinstance(all_pages, dict):
            all_pages = {}

        page_data = {}
        for key in _EC_KEYS:
            if key in st.session_state:
                page_data[key] = st.session_state[key]

        if page_data:
            all_pages["earnings_calls"] = page_data
            json_data = json.dumps(all_pages)
            manager.local_storage.setItem(manager.STORAGE_KEY, json_data)
            save_to_local_storage_js(manager.STORAGE_KEY, all_pages)
            return True
    except Exception as e:
        logging.warning(f"Failed to save earnings calls state: {e}")
    return False