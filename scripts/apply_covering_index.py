"""Apply covering index with fewer columns (max 16 parts for MySQL)."""
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

# Covering index with the most queried columns (under 16 part limit)
# Includes: WHERE cols + key SELECT cols for the income statement queries
print('Creating covering index idx_income_stmt_cover...')
try:
    cursor.execute(
        'ALTER TABLE coreiq_av_financials_income_statement '
        'ADD INDEX idx_income_stmt_cover ('
        '  ticker, report_type, fiscal_date_ending,'
        '  reported_currency,'
        '  total_revenue, cost_of_revenue, gross_profit,'
        '  operating_income, net_income,'
        '  selling_general_and_administrative, research_and_development,'
        '  depreciation_and_amortization,'
        '  interest_expense, interest_income,'
        '  operating_expenses, net_interest_income'
        ')'
    )
    conn.commit()
    print('  SUCCESS')
except Exception as e:
    print(f'  Skipped: {e}')

# Also optimize ANALYZE TABLE to update statistics for the optimizer
print('Running ANALYZE TABLE...')
cursor.execute('ANALYZE TABLE coreiq_av_financials_income_statement')
for row in cursor.fetchall():
    print(f'  {row}')

# Verify
print('\n=== FINAL INDEXES ===')
cursor.execute('SHOW INDEX FROM coreiq_av_financials_income_statement')
for row in cursor.fetchall():
    print(f'  {row[2]}  col={row[4]}  seq={row[3]}')

# EXPLAIN with covering index
print('\n=== EXPLAIN (should show Using index) ===')
cursor.execute(
    'EXPLAIN SELECT fiscal_date_ending, total_revenue, cost_of_revenue, '
    'gross_profit, selling_general_and_administrative, research_and_development, '
    'depreciation_and_amortization, operating_income, interest_expense, '
    'interest_income, net_income, reported_currency '
    'FROM coreiq_av_financials_income_statement '
    "WHERE ticker = 'ANF' AND report_type = 'annual' "
    "AND fiscal_date_ending BETWEEN '2020-01-01' AND '2025-12-31' "
    'ORDER BY fiscal_date_ending ASC'
)
for row in cursor.fetchall():
    print(f'  {row}')

conn.close()
print('\nDone.')
