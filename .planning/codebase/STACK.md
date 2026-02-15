# Technology Stack

## Core Framework
- **Streamlit** >= 1.54.0 - Primary UI framework for data apps
- **Python** >= 3.13 - Runtime language

## Database Layer
- **MySQL** 8.0+ - Primary database
- **SQLAlchemy** >= 2.0.46 - ORM and connection pooling
- **PyMySQL** >= 1.1.0 - MySQL driver
- **cryptography** >= 46.0.0 - MySQL SSL support

## Data Processing
- **Pandas** >= 2.3.0 - Data manipulation and analysis
- **NumPy** >= 2.4.0 - Numerical computing

## Visualization
- **Plotly** >= 6.5.0 - Interactive charts and visualizations

## External APIs
- **forex-python** >= 1.8 - Currency conversion
- **Alpha Vantage** - Financial data API (via SQL import)

## Utilities
- **python-dotenv** >= 1.2.0 - Environment configuration

## Optional Enhancements (Not Currently Used)
- streamlit-aggrid >= 0.3.4 - Advanced data grids
- streamlit-option-menu >= 0.3.6 - Enhanced navigation

## Key Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >= 1.54.0 | Web UI framework |
| sqlalchemy | >= 2.0.46 | Database ORM |
| pymysql | >= 1.1.0 | MySQL driver |
| pandas | >= 2.3.0 | Data processing |
| numpy | >= 2.4.0 | Numerical ops |
| plotly | >= 6.5.0 | Visualization |
| forex-python | >= 1.8 | Currency conversion |
| python-dotenv | >= 1.2.0 | Config management |
| cryptography | >= 46.0.0 | SSL support |

## Runtime Requirements
- Python >= 3.13
- MySQL 8.0+ with existing secfiling database
- Node.js (for GSD tooling)
