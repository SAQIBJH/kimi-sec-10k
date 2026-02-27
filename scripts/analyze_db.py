"""Analyze STG database performance for income statement queries."""
import pymysql
import os
import time
from dotenv import load_dotenv
load_dotenv()

conn = pymysql.connect(
    host=os.getenv('STG_DB_HOST'),
    port=int(os.getenv('STG_DB_PORT', 3306)),
    user=os.getenv('STG_DB_USER'),
    password=os.getenv('STG_DB_PASSWORD'),
    database=os.getenv('STG_DB_NAME'),
    ssl={'ca': os.getenv('SSL_CA')}
)
cursor = conn.cursor()

print('=== EXPLAIN: get_income_statement_data ===')
cursor.execute("""EXPLAIN SELECT DISTINCT fiscal_date_ending, total_revenue, cost_of_revenue,
                   gross_profit, selling_general_and_administrative, research_and_development,
                   depreciation_and_amortization, operating_income, interest_expense,
                   interest_income, net_income, reported_currency
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF'
              AND fiscal_date_ending BETWEEN '2020-01-01' AND '2025-12-31'
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC""")
for row in cursor.fetchall():
    print(row)

print('\n=== EXPLAIN: get_date_range ===')
cursor.execute("""EXPLAIN SELECT MIN(fiscal_date_ending) as min_date, MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF' AND report_type = 'annual'""")
for row in cursor.fetchall():
    print(row)

print('\n=== EXPLAIN: get_available_dates ===')
cursor.execute("""EXPLAIN SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF' AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC""")
for row in cursor.fetchall():
    print(row)

print('\n=== EXPLAIN: get_companies (heavy dropdown) ===')
cursor.execute("""EXPLAIN SELECT
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            WHERE c.ticker IS NOT NULL
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_income_statement)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_balance_sheet)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_cash_flow)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_company_overview)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_earnings_call_transcripts)
            ORDER BY display_name""")
for row in cursor.fetchall():
    print(row)

print('\n=== coreiq_companies INDEXES ===')
cursor.execute('SHOW INDEX FROM coreiq_companies')
for row in cursor.fetchall():
    print(row)

# Now time the actual queries
print('\n\n========== TIMING BENCHMARKS ==========')

queries = {
    'get_income_statement_data': """SELECT DISTINCT fiscal_date_ending, total_revenue, cost_of_revenue,
                   gross_profit, selling_general_and_administrative, research_and_development,
                   depreciation_and_amortization, operating_income, interest_expense,
                   interest_income, net_income, reported_currency
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF'
              AND fiscal_date_ending BETWEEN '2020-01-01' AND '2025-12-31'
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC""",
    'get_date_range': """SELECT MIN(fiscal_date_ending) as min_date, MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF' AND report_type = 'annual'""",
    'get_available_dates': """SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_income_statement
            WHERE ticker = 'ANF' AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC""",
    'get_company_by_ticker': """SELECT ticker, name, name_coresight, exchange, source
            FROM coreiq_companies
            WHERE ticker = 'ANF'
            LIMIT 1""",
    'get_companies_dropdown': """SELECT
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            WHERE c.ticker IS NOT NULL
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_income_statement)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_balance_sheet)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_cash_flow)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_company_overview)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_earnings_call_transcripts)
            ORDER BY display_name""",
}

for name, query in queries.items():
    times = []
    for i in range(3):
        start = time.perf_counter()
        cursor.execute(query)
        _ = cursor.fetchall()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    avg = sum(times) / len(times)
    print(f'{name}: avg={avg*1000:.1f}ms  (runs: {[f"{t*1000:.1f}ms" for t in times]})')

# Check MySQL variables
print('\n=== RELEVANT MYSQL VARIABLES ===')
for var in ['innodb_buffer_pool_size', 'query_cache_type', 'query_cache_size', 'max_connections', 'innodb_io_capacity']:
    try:
        cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
        row = cursor.fetchone()
        if row:
            print(f'{row[0]}: {row[1]}')
    except:
        pass

conn.close()
