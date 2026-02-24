#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  SEC Filing Data Pipeline — Unified Runner
═══════════════════════════════════════════════════════════════════════

Runs the full 6-step SEC filing pipeline in the correct order for any
company and any year.  Instead of running 6 separate scripts, just run:

    python scripts/run_pipeline.py AAPL 2024
    python scripts/run_pipeline.py AMZN 2025
    python scripts/run_pipeline.py M 2024 --form 10-K
    python scripts/run_pipeline.py AAPL 2022 2023 2024 2025   # multiple years
    python scripts/run_pipeline.py AAPL --all-years            # all available

Steps executed in order:
  Step 1: Export XBRL facts from SEC EDGAR   (export_xbrl_facts.py)
  Step 2: Load facts into MySQL DB           (load_filings_to_db.py)
  Step 3: Load segments & ratios into DB     (load_supplementary_json.py)
  Step 4: Cache 10-K section text            (enrich_from_edgartools.py)
  Step 5: Calculate derived metrics          (calculate_derived_metrics.py)
  Step 6: Extract store counts               (extract_store_counts.py)

You can also run individual steps:
    python scripts/run_pipeline.py AAPL 2024 --step 1      # only Step 1
    python scripts/run_pipeline.py AAPL 2024 --from-step 3  # steps 3-6 only
    python scripts/run_pipeline.py AAPL 2024 --skip-step 4  # skip Step 4

═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime

# ── Path setup ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


# ══════════════════════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════════════════════

def banner(text: str, char: str = "═", width: int = 60):
    """Print a banner line."""
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def step_header(step_num: int, title: str, ticker: str, year: int):
    """Print a step header."""
    print(f"\n{'─' * 60}")
    print(f"  Step {step_num}/6: {title}")
    print(f"  Ticker: {ticker}  |  Year: {year}")
    print(f"{'─' * 60}")


def elapsed(start: float) -> str:
    """Format elapsed time."""
    secs = time.time() - start
    if secs < 60:
        return f"{secs:.1f}s"
    return f"{int(secs // 60)}m {secs % 60:.0f}s"


# ══════════════════════════════════════════════════════════════════════
#  STEP 1: Export XBRL Facts from SEC EDGAR
# ══════════════════════════════════════════════════════════════════════

def run_step_1(ticker: str, year: int, form: str, skip_existing: bool = False):
    """
    Fetch XBRL data from SEC, extract iXBRL locations, filter, enrich,
    clean facts, extract segments, calculate ratios, and save JSON files.

    Output: data/filings/{TICKER}/{YEAR}/{FORM}/
            ├── FINAL_FACTS_FILTERED.json
            ├── BUSINESS_SEGMENTS.json
            ├── GEOGRAPHIC_SEGMENTS.json
            ├── FINANCIAL_RATIOS.json
            └── filing.html
    """
    step_header(1, "Export XBRL Facts from SEC EDGAR", ticker, year)
    start = time.time()

    # Import the export module
    from scripts.export_xbrl_facts import (
        Config, process_company_year, set_identity
    )

    config = Config()
    config.TICKERS = [ticker]
    config.YEARS = [year]
    config.FORM = form
    config.SKIP_EXISTING = skip_existing

    set_identity(config.SEC_IDENTITY)

    success = process_company_year(ticker, year, config)

    if success:
        print(f"\n  ✅ Step 1 completed in {elapsed(start)}")
    else:
        print(f"\n  ❌ Step 1 FAILED for {ticker} {year}")

    return success


# ══════════════════════════════════════════════════════════════════════
#  STEP 2: Load XBRL Facts into MySQL
# ══════════════════════════════════════════════════════════════════════

def run_step_2(ticker: str, year: int, form: str):
    """
    Load FINAL_FACTS_FILTERED.json into the filing_metrics MySQL table.
    Idempotent — deletes existing rows before inserting.
    """
    step_header(2, "Load XBRL Facts into MySQL", ticker, year)
    start = time.time()

    from scripts.load_filings_to_db import scan_and_load

    scan_and_load(
        filter_ticker=ticker,
        filter_year=str(year),
        filter_doc_type=form,
    )

    print(f"\n  ✅ Step 2 completed in {elapsed(start)}")
    return True


# ══════════════════════════════════════════════════════════════════════
#  STEP 3: Load Segments & Financial Ratios into MySQL
# ══════════════════════════════════════════════════════════════════════

def run_step_3(ticker: str, year: int, form: str):
    """
    Load BUSINESS_SEGMENTS.json, GEOGRAPHIC_SEGMENTS.json, and
    FINANCIAL_RATIOS.json into MySQL.
    """
    step_header(3, "Load Segments & Ratios into MySQL", ticker, year)
    start = time.time()

    from scripts.load_supplementary_json import get_conn, process
    from pathlib import Path as P

    doc_dir = PROJECT_ROOT / "data" / "filings" / ticker / str(year) / form
    if not doc_dir.exists():
        print(f"  ⚠️  Filing directory not found: {doc_dir}")
        print(f"  Skipping Step 3 (no supplementary files)")
        return True

    conn = get_conn()
    try:
        process(conn, ticker, year, form, doc_dir)
    finally:
        conn.close()

    print(f"\n  ✅ Step 3 completed in {elapsed(start)}")
    return True


# ══════════════════════════════════════════════════════════════════════
#  STEP 4: Cache 10-K Section Text (for LLM Fallback)
# ══════════════════════════════════════════════════════════════════════

def run_step_4(ticker: str, year: int, form: str, force: bool = False):
    """
    Pre-extract and cache key 10-K sections (Item 1, Item 7, Item 8)
    from the local filing.html into SECTION_CACHE.json.

    Used by the LLM extractor as a fallback when XBRL data is missing.
    """
    step_header(4, "Cache 10-K Section Text for LLM", ticker, year)
    start = time.time()

    from scripts.enrich_from_edgartools import (
        discover_filings, process_filing
    )

    filings = discover_filings(
        ticker_filter=ticker,
        year_filter=year,
        doc_filter=form,
    )

    if not filings:
        print(f"  ⚠️  No filing.html found for {ticker} {year}")
        print(f"  Skipping Step 4 (run Step 1 first)")
        return True

    for t, fy, dt, html_path in filings:
        process_filing(t, fy, dt, html_path, force=force)

    print(f"\n  ✅ Step 4 completed in {elapsed(start)}")
    return True


# ══════════════════════════════════════════════════════════════════════
#  STEP 5: Calculate Derived Metrics (EBITDA, Margins, Debt, etc.)
# ══════════════════════════════════════════════════════════════════════

def run_step_5(ticker: str, year: int, form: str):
    """
    Compute derived/calculated metrics from DB values:
    - EBITDA, Operating Margin %, Net Margin %, EBITDA Margin %
    - Total Debt, Net Debt, Total Cash & ST Investments
    - Gross Margin %, Total Operating Expenses

    Writes results to both MySQL AND FINAL_FACTS_FILTERED.json.
    """
    step_header(5, "Calculate Derived Metrics", ticker, year)
    start = time.time()

    from scripts.calculate_derived_metrics import (
        get_engine, calculate_for_filing, insert_to_db, update_json
    )

    engine = get_engine()
    # Normalize form: calculate_derived_metrics expects directory name (e.g. "10-K")
    with engine.begin() as conn:
        print(f"\n  [{ticker} {year} {form}]")
        entries = calculate_for_filing(conn, ticker, year, form)

        if not entries:
            print("  No source values found — skipping derived metrics")
        else:
            print(f"  Calculated {len(entries)} metrics:")
            for e in entries:
                val = e["numeric_value"]
                unit = e["unit_ref"]
                if unit == "usd":
                    if abs(val) >= 1e9:
                        display = f"${val/1e9:,.3f}B"
                    elif abs(val) >= 1e6:
                        display = f"${val/1e6:,.0f}M"
                    else:
                        display = f"${val:,.0f}"
                elif unit == "percent":
                    display = f"{val:.2f}%"
                else:
                    display = str(val)
                print(f"    {e['original_label']:<40} = {display}")

            insert_to_db(conn, ticker, year, form, entries)
            print(f"  DB updated ({len(entries)} rows inserted)")

            update_json(ticker, year, form, entries)

    print(f"\n  ✅ Step 5 completed in {elapsed(start)}")
    return True


# ══════════════════════════════════════════════════════════════════════
#  STEP 6: Extract Store Counts (EdgarTools → Regex → LLM → DB)
# ══════════════════════════════════════════════════════════════════════

def run_step_6(ticker: str, year: int, form: str, force: bool = False):
    """
    Extract store/location counts from 10-K sections.
    Uses EdgarTools section text → enhanced regex → LLM verification.
    Inserts into filing_metrics with source='store_count'.
    """
    step_header(6, "Extract Store Counts", ticker, year)
    start = time.time()

    from scripts.extract_store_counts import process_filing, get_engine

    result = process_filing(ticker, year, form, use_llm=True, force=force)

    if result and result.get("store_count") is not None:
        # Insert into DB
        from scripts.extract_store_counts import insert_store_count_to_db
        engine = get_engine()
        with engine.begin() as conn:
            insert_store_count_to_db(
                conn=conn,
                ticker=ticker,
                fiscal_year=year,
                doc_type=form,
                store_count=result["store_count"],
                store_type=result["store_type"],
                as_of_date=result.get("as_of_date"),
                source_sentence=result.get("source_sentence", ""),
                extraction_method=result["extraction_method"],
                confidence=result["confidence"],
                section_source=result.get("section", ""),
                notes=result.get("notes", ""),
            )
            print(f"    💾 Saved to DB (filing_metrics, source='store_count')")

    print(f"\n  ✅ Step 6 completed in {elapsed(start)}")
    return True


# ══════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE RUNNER
# ══════════════════════════════════════════════════════════════════════

STEPS = {
    1: ("Export XBRL Facts",        run_step_1),
    2: ("Load Facts to MySQL",      run_step_2),
    3: ("Load Segments & Ratios",   run_step_3),
    4: ("Cache Section Text",       run_step_4),
    5: ("Calculate Derived Metrics", run_step_5),
    6: ("Extract Store Counts",     run_step_6),
}


def run_pipeline(
    ticker: str,
    years: list,
    form: str = "10-K",
    only_step: int = None,
    from_step: int = 1,
    skip_steps: list = None,
    skip_existing: bool = False,
    force_cache: bool = False,
):
    """Run the full or partial pipeline for one ticker across one or more years."""
    skip_steps = skip_steps or []
    ticker = ticker.upper()

    # Determine which steps to run
    if only_step:
        steps_to_run = [only_step]
    else:
        steps_to_run = [s for s in range(from_step, 7) if s not in skip_steps]

    banner(f"SEC Filing Pipeline — {ticker}", "═")
    print(f"  Years: {', '.join(map(str, years))}")
    print(f"  Form: {form}")
    print(f"  Steps: {' → '.join(f'{s}:{STEPS[s][0]}' for s in steps_to_run)}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_start = time.time()
    results = {}  # {(ticker, year, step): True/False}

    for year in years:
        banner(f"{ticker} — FY{year}", "─")

        for step_num in steps_to_run:
            step_name, step_fn = STEPS[step_num]

            try:
                if step_num == 1:
                    ok = step_fn(ticker, year, form, skip_existing=skip_existing)
                elif step_num in (4, 6):
                    ok = step_fn(ticker, year, form, force=force_cache)
                else:
                    ok = step_fn(ticker, year, form)

                results[(ticker, year, step_num)] = ok

                if not ok and step_num == 1:
                    print(f"\n  ⚠️  Step 1 failed — skipping remaining steps for {ticker} {year}")
                    for remaining in steps_to_run:
                        if remaining > step_num:
                            results[(ticker, year, remaining)] = None
                    break

            except Exception as e:
                print(f"\n  ❌ Step {step_num} ERROR: {e}")
                traceback.print_exc()
                results[(ticker, year, step_num)] = False

    # ── Final Summary ────────────────────────────────────────────────
    banner("PIPELINE SUMMARY", "═")

    success = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for year in years:
        statuses = []
        for step_num in steps_to_run:
            r = results.get((ticker, year, step_num))
            if r is True:
                statuses.append(f"Step {step_num}:✅")
            elif r is False:
                statuses.append(f"Step {step_num}:❌")
            else:
                statuses.append(f"Step {step_num}:⏭️")
        print(f"  {ticker} {year}: {' | '.join(statuses)}")

    print(f"\n  Total: {success} passed, {failed} failed, {skipped} skipped")
    print(f"  Time: {elapsed(total_start)}")

    output_dir = PROJECT_ROOT / "data" / "filings" / ticker
    print(f"\n  📁 Output: {output_dir}/")
    print(f"     └── <YEAR>/{form}/")
    print(f"         ├── FINAL_FACTS_FILTERED.json")
    print(f"         ├── BUSINESS_SEGMENTS.json")
    print(f"         ├── GEOGRAPHIC_SEGMENTS.json")
    print(f"         ├── FINANCIAL_RATIOS.json")
    print(f"         ├── SECTION_CACHE.json")
    print(f"         ├── STORE_COUNT.json")
    print(f"         └── filing.html")

    if failed == 0:
        print(f"\n  🎉 All done!")
    else:
        print(f"\n  ⚠️  {failed} step(s) failed — check logs above")

    return failed == 0


# ══════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SEC Filing Data Pipeline — Unified Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_pipeline.py AAPL 2024              # Full pipeline for AAPL 2024
  python scripts/run_pipeline.py AMZN 2023 2024 2025    # Multiple years
  python scripts/run_pipeline.py M 2024 --form 10-K     # Specify form type
  python scripts/run_pipeline.py AAPL 2024 --step 1     # Only run Step 1
  python scripts/run_pipeline.py AAPL 2024 --from-step 3 # Run steps 3-5
  python scripts/run_pipeline.py AAPL 2024 --skip-step 4 # Skip Step 4

Steps:
  1  Export XBRL Facts from SEC EDGAR
  2  Load Facts into MySQL
  3  Load Segments & Financial Ratios into MySQL
  4  Cache 10-K Section Text (for LLM fallback)
  5  Calculate Derived Metrics (EBITDA, margins, etc.)
  6  Extract Store Counts (EdgarTools + Regex + LLM)
        """,
    )

    parser.add_argument("ticker", help="Company ticker symbol (e.g. AAPL, AMZN, M)")
    parser.add_argument("years", nargs="+", type=int, help="Fiscal year(s) to process (e.g. 2024 or 2022 2023 2024)")
    parser.add_argument("--form", default="10-K", help="Filing form type (default: 10-K)")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5, 6],
                        help="Run ONLY this step")
    parser.add_argument("--from-step", type=int, choices=[1, 2, 3, 4, 5, 6], default=1,
                        help="Start from this step (run this and all subsequent)")
    parser.add_argument("--skip-step", type=int, action="append", default=[],
                        choices=[1, 2, 3, 4, 5, 6],
                        help="Skip this step (can specify multiple times)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip Step 1 if FINAL_FACTS_FILTERED.json already exists")
    parser.add_argument("--force-cache", action="store_true",
                        help="Force re-extraction in Step 4 even if cache exists")

    args = parser.parse_args()

    run_pipeline(
        ticker=args.ticker,
        years=args.years,
        form=args.form,
        only_step=args.step,
        from_step=args.from_step,
        skip_steps=args.skip_step,
        skip_existing=args.skip_existing,
        force_cache=args.force_cache,
    )


if __name__ == "__main__":
    main()
