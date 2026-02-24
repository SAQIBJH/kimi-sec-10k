#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  Master Orchestrator — All USA Companies Pipeline
═══════════════════════════════════════════════════════════════════════

Runs the full 7-step SEC filing pipeline for ALL USA-based companies
from the coreiq_companies table. Fully resumable — tracks every step
in the pipeline_status DB table so you can stop and continue anytime.

Usage:
    python scripts/run_all_usa.py                        # Run all pending/failed
    python scripts/run_all_usa.py --years 2021 2022 2023 # Specific years
    python scripts/run_all_usa.py --ticker WMT            # Single ticker
    python scripts/run_all_usa.py --from-step 2           # Resume from step 2
    python scripts/run_all_usa.py --retry-failed          # Retry failed steps
    python scripts/run_all_usa.py --status                # Show progress report
    python scripts/run_all_usa.py --dry-run               # Preview work only

Status table: pipeline_status (ticker, fiscal_year, form_type, step_num)
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import signal
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# ── Edgar cache: set BEFORE edgar is imported so it picks up the right dir ────
_EDGAR_CACHE = "/tmp/edgar_cache"
os.makedirs(_EDGAR_CACHE, exist_ok=True)
os.environ.setdefault("EDGAR_LOCAL_DATA_DIR", _EDGAR_CACHE)
os.environ.setdefault("EDGAR_CACHE_DIR", _EDGAR_CACHE)

import pymysql

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════

DB_CONFIG = {
    "host":   os.getenv("DB_HOST", "localhost"),
    "port":   int(os.getenv("DB_PORT", "3306")),
    "db":     os.getenv("DB_NAME", "chainxydata_stg"),
    "user":   os.getenv("DB_USER", "root"),
    "passwd": os.getenv("DB_PASSWORD", ""),
    "charset": "utf8mb4",
}

DEFAULT_YEARS    = [2021, 2022, 2023, 2024, 2025]
DEFAULT_FORM     = "10-K"
STEP_NAMES       = {
    1: "Export XBRL Facts from SEC EDGAR",
    2: "Load XBRL Facts into MySQL",
    3: "Load Financial Ratios into MySQL",
    4: "Cache 10-K Section Text",
    5: "Calculate Derived Metrics",
    6: "Extract Store Counts",
    7: "Extract Credit Ratings",
}

# Global flag for graceful shutdown on Ctrl+C
_SHUTDOWN = False


# ══════════════════════════════════════════════════════════════════════════════
#  DB HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_conn():
    return pymysql.connect(**DB_CONFIG, autocommit=True)


def get_usa_tickers(conn) -> List[Tuple[str, str]]:
    """Return list of (ticker, name) for unique USA companies, sorted."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ticker, MIN(COALESCE(name_coresight, name)) AS display_name
            FROM coreiq_companies
            WHERE country_of_incorporation = 'United States'
              AND ticker IS NOT NULL
              AND ticker != ''
            GROUP BY ticker
            ORDER BY ticker
        """)
        return [(row[0].strip(), row[1]) for row in cur.fetchall() if row[0].strip()]


def ensure_status_rows(conn, ticker: str, fiscal_year: int, form_type: str, steps: List[int]):
    """Insert pending rows for steps that don't exist yet. Skip if already present."""
    with conn.cursor() as cur:
        for step in steps:
            cur.execute("""
                INSERT IGNORE INTO pipeline_status
                    (ticker, fiscal_year, form_type, step_num, step_name, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """, (ticker, fiscal_year, form_type, step, STEP_NAMES[step]))


def get_pending_work(conn, ticker_filter: Optional[str], years: List[int],
                     form_type: str, from_step: int,
                     retry_failed: bool) -> List[Tuple[str, int, str, int]]:
    """
    Return list of (ticker, fiscal_year, form_type, step_num) that need running.
    Ordered: ticker → year → step (so each company completes fully before next).
    """
    statuses = ["'pending'"]
    if retry_failed:
        statuses.append("'failed'")
    # 'in_progress' rows are treated as failed (interrupted previous run)
    statuses.append("'in_progress'")

    ticker_clause = f"AND ticker = %s" if ticker_filter else ""
    year_placeholders = ",".join(["%s"] * len(years))

    query = f"""
        SELECT ticker, fiscal_year, form_type, step_num
        FROM pipeline_status
        WHERE status IN ({','.join(statuses)})
          AND step_num >= %s
          AND fiscal_year IN ({year_placeholders})
          {ticker_clause}
        ORDER BY ticker, fiscal_year, step_num
    """
    params = [from_step] + years
    if ticker_filter:
        params.append(ticker_filter)

    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def mark_step(conn, ticker: str, fiscal_year: int, form_type: str,
              step_num: int, status: str, error: str = None):
    """Update a step's status in pipeline_status."""
    now = datetime.utcnow()
    if status == "in_progress":
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pipeline_status
                SET status = 'in_progress', started_at = %s,
                    error_message = NULL, updated_at = %s
                WHERE ticker = %s AND fiscal_year = %s
                  AND form_type = %s AND step_num = %s
            """, (now, now, ticker, fiscal_year, form_type, step_num))
    elif status == "completed":
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pipeline_status
                SET status = 'completed', completed_at = %s, updated_at = %s
                WHERE ticker = %s AND fiscal_year = %s
                  AND form_type = %s AND step_num = %s
            """, (now, now, ticker, fiscal_year, form_type, step_num))
    elif status == "failed":
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pipeline_status
                SET status = 'failed', completed_at = %s, error_message = %s,
                    retry_count = retry_count + 1, updated_at = %s
                WHERE ticker = %s AND fiscal_year = %s
                  AND form_type = %s AND step_num = %s
            """, (now, (error or "")[:2000], now, ticker, fiscal_year, form_type, step_num))
    elif status == "skipped":
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pipeline_status
                SET status = 'skipped', completed_at = %s, updated_at = %s
                WHERE ticker = %s AND fiscal_year = %s
                  AND form_type = %s AND step_num = %s
            """, (now, now, ticker, fiscal_year, form_type, step_num))


def is_step_completed(conn, ticker: str, fiscal_year: int,
                      form_type: str, step_num: int) -> bool:
    """Check if a specific step is already completed."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT status FROM pipeline_status
            WHERE ticker = %s AND fiscal_year = %s
              AND form_type = %s AND step_num = %s
        """, (ticker, fiscal_year, form_type, step_num))
        row = cur.fetchone()
        return row is not None and row[0] == "completed"


# ══════════════════════════════════════════════════════════════════════════════
#  STATUS REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_status_report(conn, years: List[int]):
    """Print a nicely formatted progress dashboard."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                status,
                COUNT(*) as cnt,
                COUNT(DISTINCT ticker) as companies
            FROM pipeline_status
            WHERE fiscal_year IN ({})
            GROUP BY status
            ORDER BY FIELD(status,'completed','in_progress','pending','failed','skipped')
        """.format(",".join(["%s"] * len(years))), years)
        rows = cur.fetchall()

    print("\n" + "═" * 60)
    print("  PIPELINE STATUS REPORT")
    print("═" * 60)
    total_steps = sum(r[1] for r in rows)
    for status, cnt, companies in rows:
        bar = "█" * min(30, int(30 * cnt / max(total_steps, 1)))
        pct = 100 * cnt / max(total_steps, 1)
        icon = {"completed": "✅", "in_progress": "🔄", "pending": "⏳",
                "failed": "❌", "skipped": "⏭️"}.get(status, "?")
        print(f"  {icon} {status:<12} {cnt:>5} steps  ({pct:5.1f}%)  {companies} companies  {bar}")

    # Per-ticker breakdown
    print("\n" + "─" * 60)
    print(f"  {'TICKER':<8} {'DONE':>5} {'FAIL':>5} {'PEND':>5}  YEARS")
    print("─" * 60)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                ticker,
                SUM(status='completed') as done,
                SUM(status='failed')    as fail,
                SUM(status='pending')   as pend,
                GROUP_CONCAT(DISTINCT fiscal_year ORDER BY fiscal_year) as years
            FROM pipeline_status
            WHERE fiscal_year IN ({})
            GROUP BY ticker
            ORDER BY ticker
        """.format(",".join(["%s"] * len(years))), years)
        for ticker, done, fail, pend, years_str in cur.fetchall():
            flag = "❌" if fail else ("✅" if not pend else "🔄")
            print(f"  {flag} {ticker:<8} {done:>5} {fail:>5} {pend:>5}  {years_str}")
    print("═" * 60 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE STEP RUNNERS
# ══════════════════════════════════════════════════════════════════════════════

def run_step(step_num: int, ticker: str, year: int, form: str) -> Tuple[bool, str]:
    """
    Run a single pipeline step. Returns (success, error_message).
    Each step is imported from its script module.
    """
    try:
        if step_num == 1:
            from scripts.export_xbrl_facts import Config, process_company_year, set_identity
            cfg = Config()
            cfg.TICKERS = [ticker]
            cfg.YEARS = [year]
            cfg.FORM = form
            cfg.SKIP_EXISTING = False
            set_identity(cfg.SEC_IDENTITY)
            success = process_company_year(ticker, year, cfg)
            if not success:
                return False, f"export_xbrl_facts returned False for {ticker} {year}"
            return True, ""

        elif step_num == 2:
            from scripts.load_filings_to_db import scan_and_load
            scan_and_load(filter_ticker=ticker, filter_year=str(year), filter_doc_type=form)
            return True, ""

        elif step_num == 3:
            from scripts.load_supplementary_json import get_conn as get_conn3, process
            doc_dir = PROJECT_ROOT / "data" / "filings" / ticker / str(year) / form
            if not doc_dir.exists():
                return True, ""  # step skipped gracefully — no JSON to load
            conn3 = get_conn3()
            try:
                process(conn3, ticker, year, form, doc_dir)
            finally:
                conn3.close()
            return True, ""

        elif step_num == 4:
            from scripts.enrich_from_edgartools import discover_filings, process_filing
            filings = discover_filings(ticker_filter=ticker, year_filter=year, doc_filter=form)
            if not filings:
                return True, ""  # no filing.html yet — Step 1 must run first
            for t, fy, dt, html_path in filings:
                process_filing(t, fy, dt, html_path, force=False)
            return True, ""

        elif step_num == 5:
            from scripts.calculate_derived_metrics import get_engine, calculate_for_filing, insert_to_db, update_json
            engine = get_engine()
            with engine.begin() as conn5:
                entries = calculate_for_filing(conn5, ticker, year, form)
                if entries:
                    insert_to_db(conn5, ticker, year, form, entries)
                    update_json(ticker, year, form, entries)
            return True, ""

        elif step_num == 6:
            from scripts.extract_store_counts import run_store_count_extraction
            run_store_count_extraction(ticker_filter=ticker, year_filter=year, doc_filter=form, force=False, use_llm=True)
            return True, ""

        elif step_num == 7:
            from scripts.extract_credit_ratings import run_credit_rating_extraction
            run_credit_rating_extraction(ticker_filter=ticker, year_filter=year, doc_filter=form, force=False, use_llm=True)
            return True, ""

        else:
            return False, f"Unknown step number: {step_num}"

    except Exception as e:
        return False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=5)}"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def seed_status_table(conn, tickers: List[Tuple[str, str]], years: List[int],
                      form_type: str, steps: List[int]):
    """Pre-populate pipeline_status with pending rows for all work."""
    print(f"\n  Seeding status table: {len(tickers)} companies × {len(years)} years × {len(steps)} steps...")
    for ticker, _ in tickers:
        for year in years:
            ensure_status_rows(conn, ticker, year, form_type, steps)
    print(f"  Done — {len(tickers) * len(years) * len(steps)} rows ensured.")


def run_all(args):
    global _SHUTDOWN

    # ── Signal handler for graceful Ctrl+C ────────────────────────────────
    def _handle_sigint(sig, frame):
        global _SHUTDOWN
        print("\n\n  ⚠️  Interrupt received — finishing current step then stopping...")
        _SHUTDOWN = True
    signal.signal(signal.SIGINT, _handle_sigint)

    conn = get_conn()

    # ── Get USA companies ──────────────────────────────────────────────────
    tickers = get_usa_tickers(conn)
    if args.ticker:
        tickers = [(t, n) for t, n in tickers if t.upper() == args.ticker.upper()]
        if not tickers:
            print(f"  ❌ Ticker '{args.ticker}' not found in coreiq_companies (USA)")
            sys.exit(1)

    years     = args.years
    form_type = DEFAULT_FORM
    steps     = list(range(args.from_step, 8))  # steps from_step → 7

    print("\n" + "═" * 60)
    print("  USA COMPANIES PIPELINE — MASTER ORCHESTRATOR")
    print("═" * 60)
    print(f"  Companies : {len(tickers)}")
    print(f"  Years     : {years}")
    print(f"  Form      : {form_type}")
    print(f"  Steps     : {steps}")
    print(f"  Retry fail: {args.retry_failed}")
    print("═" * 60)

    if args.status:
        print_status_report(conn, years)
        conn.close()
        return

    # ── Seed status table ──────────────────────────────────────────────────
    seed_status_table(conn, tickers, years, form_type, steps)

    if args.dry_run:
        print("\n  DRY RUN — no pipeline steps will execute.")
        print_status_report(conn, years)
        conn.close()
        return

    # ── Collect pending work ───────────────────────────────────────────────
    ticker_filter = args.ticker.upper() if args.ticker else None
    pending = get_pending_work(conn, ticker_filter, years, form_type,
                               args.from_step, args.retry_failed)

    total   = len(pending)
    done    = 0
    failed  = 0
    skipped = 0

    print(f"\n  Total steps to run: {total}")
    if total == 0:
        print("  ✅ Nothing to do — all steps completed. Use --retry-failed to retry failures.")
        print_status_report(conn, years)
        conn.close()
        return

    overall_start = time.time()

    # Track current company/year for progress header
    current_company = None

    for (ticker, fiscal_year, ftype, step_num) in pending:
        if _SHUTDOWN:
            print("\n  🛑 Stopping gracefully after current step.")
            break

        label = f"{ticker} {fiscal_year} Step {step_num}"

        # ── Print company/year header when switching ─────────────────────
        company_key = (ticker, fiscal_year)
        if company_key != current_company:
            current_company = company_key
            company_name = next((n for t, n in tickers if t == ticker), ticker)
            print(f"\n{'═' * 60}")
            print(f"  {ticker} — {company_name}  |  FY {fiscal_year}")
            print(f"{'═' * 60}")

        # ── Check if previous step completed (guard) ─────────────────────
        if step_num > 1 and not is_step_completed(conn, ticker, fiscal_year, ftype, step_num - 1):
            if step_num == 2:
                # Step 1 is the gatekeeper — skip all subsequent steps if step 1 failed
                print(f"  ⏭️  [{label}] Skipping — Step 1 not completed")
                mark_step(conn, ticker, fiscal_year, ftype, step_num, "skipped",
                          "Skipped: prerequisite step not completed")
                skipped += 1
                continue

        print(f"\n  ▶  [{label}] {STEP_NAMES[step_num]}")
        step_start = time.time()

        # ── Mark in_progress ─────────────────────────────────────────────
        mark_step(conn, ticker, fiscal_year, ftype, step_num, "in_progress")

        # ── Run step ─────────────────────────────────────────────────────
        success, error_msg = run_step(step_num, ticker, fiscal_year, ftype)
        elapsed_s = time.time() - step_start
        done += 1

        if success:
            mark_step(conn, ticker, fiscal_year, ftype, step_num, "completed")
            print(f"  ✅ [{label}] Done in {elapsed_s:.1f}s")
        else:
            mark_step(conn, ticker, fiscal_year, ftype, step_num, "failed", error_msg)
            print(f"  ❌ [{label}] FAILED in {elapsed_s:.1f}s")
            print(f"     Error: {error_msg[:200]}")
            failed += 1

        # ── Rate limiting: pause between Step 1 calls (SEC EDGAR rate limit) ──
        if step_num == 1 and success:
            time.sleep(1.0)  # 1s between EDGAR requests

    # ── Final summary ──────────────────────────────────────────────────────
    total_elapsed = time.time() - overall_start
    mins = int(total_elapsed // 60)
    secs = int(total_elapsed % 60)

    print(f"\n{'═' * 60}")
    print(f"  COMPLETED")
    print(f"  Steps run   : {done}")
    print(f"  Failed      : {failed}")
    print(f"  Skipped     : {skipped}")
    print(f"  Total time  : {mins}m {secs}s")
    print(f"{'═' * 60}")

    print_status_report(conn, years)
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run SEC filing pipeline for all USA companies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_all_usa.py                         Run all pending steps
  python scripts/run_all_usa.py --status                Show progress report
  python scripts/run_all_usa.py --years 2022 2023 2024  Only these years
  python scripts/run_all_usa.py --ticker WMT            Single company
  python scripts/run_all_usa.py --from-step 2           Resume from step 2
  python scripts/run_all_usa.py --retry-failed          Retry failed steps
  python scripts/run_all_usa.py --dry-run               Preview only
        """,
    )
    parser.add_argument("--ticker",       type=str,  help="Process only this ticker")
    parser.add_argument("--years",        type=int,  nargs="+", default=DEFAULT_YEARS,
                        help=f"Fiscal years to process (default: {DEFAULT_YEARS})")
    parser.add_argument("--from-step",   type=int,  default=1, choices=range(1, 8),
                        help="Start from this step number (default: 1)")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Also retry steps that previously failed")
    parser.add_argument("--status",      action="store_true",
                        help="Print status report and exit")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Seed status table but don't run any steps")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_all(args)
