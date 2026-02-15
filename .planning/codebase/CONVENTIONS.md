# Code Conventions

## Python Style

### Type Hints
- Use type hints for all function signatures and return types
- Example: `def get_company_by_ticker(ticker: str) -> Optional[Company]:`

### Docstrings
- Use Google-style docstrings for all public functions
- Include Args, Returns, and Raises sections

### Dataclasses
- Use `@dataclass` for all data models
- Include type annotations for all fields
- Use properties for computed fields

### Static Methods
- Repository methods should be `@staticmethod`
- No instance state needed for data access

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions/Variables | snake_case | `get_companies()` |
| Classes | PascalCase | `CompanyRepository` |
| Constants | UPPER_CASE | `LINE_ITEMS` |
| Private | _leading_underscore | `_parse_json()` |

## Import Order

```python
# 1. Standard library imports
import os
from typing import List, Optional
from datetime import date

# 2. Third-party imports
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 3. Local imports (absolute from app root)
from core.database import db_manager
from data.models import Company
from components.styles import COLORS
```

## Component Patterns

### Streamlit Page Structure
```python
import streamlit as st

# MUST be first Streamlit command
st.set_page_config(
    page_title="Page Title",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Immediately hide sidebar
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

# Initialize
from utils.local_storage import init_local_storage
from core.database import init_database
init_local_storage()
init_database()

# Render styles
from components.styles import render_styles
render_styles()

# Set layout
set_page_layout(...)

# Render shared header
from components.navigation import render_header, render_coresight_footer
render_header(full_width=True)

# Render page content
from pages.your_page import render_page
render_page()

# Render footer
render_coresight_footer(full_width=True, stick_to_bottom=True)
```

## Database Patterns

### Repository Pattern
```python
class CompanyRepository:
    @staticmethod
    def get_company_by_ticker(ticker: str) -> Optional[Company]:
        query = """SELECT ... FROM table WHERE ticker = :ticker"""
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None
        return Company(...)
```

### Query Parameters
- Always use parameterized queries with `:param` syntax
- Never use f-strings for SQL queries

### Error Handling
- Repository layer catches exceptions and returns None or empty list
- Business logic layer handles None checks

## Design System

### Colors (from components/styles.py)
- Primary: `#0066CC`
- Success: `#28A745`
- Danger: `#DC3545`
- Warning: `#FFC107`
- Coresight Red: `#d62e2f`
- Dark Text: `#323232`
- Border Gray: `#cbcaca`

### Typography
- Font Family: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Base Size: `1rem` (16px)

### Spacing
- Based on 8px grid
- Space 1: 0.25rem (4px)
- Space 2: 0.5rem (8px)
- Space 4: 1rem (16px)

## File Organization

```python
"""
Module docstring describing purpose.
"""
# 1. Standard library imports
# 2. Third-party imports
# 3. Local imports

# Constants
# Classes
# Functions
```

## Error Handling

- Use custom exceptions sparingly
- Return Optional[T] for functions that may not find data
- Log errors at the appropriate level
- Don't expose internal errors to UI

## Testing

Currently minimal testing. Recommended:
- Unit tests for repository methods
- Integration tests for database queries
- Component tests for UI logic
