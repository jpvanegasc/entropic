"""Compound interest example for entropic.

Demonstrates that entropic is format-agnostic by using plain CSV files
(stdlib only, no numpy). Exercises run_or_retrieve, sweep, and list.

Simulation: compound interest  A(t) = P * (1 + r/n)^(n*t)
"""

import csv
from pathlib import Path

from entropic import Store, Base, Mapped


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class InterestResult(Base):
    __tablename__ = "interest_results"

    principal: Mapped[float]
    rate: Mapped[float]
    compounds_per_year: Mapped[int]
    years: Mapped[int]


# ---------------------------------------------------------------------------
# Runner: compound interest over time
# ---------------------------------------------------------------------------


def interest_runner(params: dict) -> None:
    """Compute compound interest and write year,balance columns to CSV."""
    principal = float(params["principal"])
    rate = float(params["rate"])
    compounds_per_year = int(params["compounds_per_year"])
    years = int(params["years"])

    with open(params["result_file"], "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "balance"])
        for year in range(years + 1):
            balance = principal * (1 + rate / compounds_per_year) ** (
                compounds_per_year * year
            )
            writer.writerow([year, round(balance, 2)])


# ---------------------------------------------------------------------------
# Store setup
# ---------------------------------------------------------------------------


EXAMPLES_DIR = Path(__file__).parent
store: Store[InterestResult] = Store(
    runner=interest_runner,
    result_cls=InterestResult,
    results_dir=EXAMPLES_DIR / "csv_results",
    db_url=f"sqlite:///{EXAMPLES_DIR / 'csv_entropic.sqlite3'}",
    file_suffix=".csv",
)


# ---------------------------------------------------------------------------
# Run: single scenario
# ---------------------------------------------------------------------------

print("=== Single run ===")
record = store.run_or_retrieve(
    {"principal": 1000, "rate": 0.05, "compounds_per_year": 12, "years": 10},
)
print(f"  Result:  {record.result_file}")
print(f"  Elapsed: {record.custom_data.get('elapsed_seconds')}s")

# ---------------------------------------------------------------------------
# Sweep: compare different interest rates
# ---------------------------------------------------------------------------

print("\n=== Sweep over rates ===")
sweep_params = [
    {"principal": 1000, "rate": r, "compounds_per_year": 12, "years": 10}
    for r in [0.03, 0.05, 0.07, 0.10]
]
records = store.sweep(sweep_params)
for r in records:
    print(f"  rate={r.rate:.0%} → {Path(r.result_file).name}")

# ---------------------------------------------------------------------------
# List all runs
# ---------------------------------------------------------------------------

print(f"\n=== All records ({len(store.list())}) ===")
for r in store.list():
    print(f"  [{r.id}] rate={r.rate}")
