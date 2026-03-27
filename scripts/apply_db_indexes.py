"""Apply database index optimizations to coreiq_av_financials_income_statement."""
import pymysql
import os
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

# 1. Composite index for the most common query pattern
print('Creating composite index idx_income_stmt_ticker_report_date...')
try:
    cursor.execute(
        'ALTER TABLE coreiq_av_financials_income_statement '
        'ADD INDEX idx_income_stmt_ticker_report_date (ticker, report_type, fiscal_date_ending)'
    )
    conn.commit()
    print('  SUCCESS')
except Exception as e:
    print(f'  Skipped: {e}')

# 2. Covering index including all SELECT columns for the main query
print('Creating covering index idx_income_stmt_covering...')
try:
    cursor.execute(
        'ALTER TABLE coreiq_av_financials_income_statement '
        'ADD INDEX idx_income_stmt_covering ('
        '  ticker, report_type, fiscal_date_ending,'
        '  total_revenue, cost_of_revenue, gross_profit,'
        '  selling_general_and_administrative, research_and_development,'
        '  depreciation_and_amortization, operating_income,'
        '  interest_expense, interest_income, net_income,'
        '  reported_currency, operating_expenses, other_non_operating_income, net_interest_income'
        ')'
    )
    conn.commit()
    print('  SUCCESS')
except Exception as e:
    print(f'  Skipped: {e}')

# 3. Drop redundant single-column idx_fiscal_date (now covered by composites)
print('Dropping redundant idx_fiscal_date...')
try:
    cursor.execute('ALTER TABLE coreiq_av_financials_income_statement DROP INDEX idx_fiscal_date')
    conn.commit()
    print('  SUCCESS')
except Exception as e:
    print(f'  Skipped: {e}')

# 4. Verify
print('\n=== UPDATED INDEXES ===')
cursor.execute('SHOW INDEX FROM coreiq_av_financials_income_statement')
for row in cursor.fetchall():
    print(f'  {row[2]}  col={row[4]}  unique={row[1]==0}')

# 5. EXPLAIN after
print('\n=== EXPLAIN AFTER OPTIMIZATION ===')
cursor.execute(
    'EXPLAIN SELECT fiscal_date_ending, total_revenue, cost_of_revenue, '
    'gross_profit, selling_general_and_administrative, research_and_development, '
    'depreciation_and_amortization, operating_income, interest_expense, '
    'interest_income, net_income, reported_currency '
    'FROM coreiq_av_financials_income_statement '
    "WHERE ticker = 'ANF' AND fiscal_date_ending BETWEEN '2020-01-01' AND '2025-12-31' "
    "AND report_type = 'annual' ORDER BY fiscal_date_ending ASC"
)
for row in cursor.fetchall():
    print(f'  {row}')

conn.close()
print('\nDatabase index optimization complete.')
