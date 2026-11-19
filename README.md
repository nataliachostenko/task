# Virtual columns in a pandas DataFrame

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python pipeline.py   # cleans sales.csv, writes revenue_by_region.csv
pytest                # runs all tests
```

## Files

- `solution.py` — `add_virtual_column` (Part 1)
- `pipeline.py` — cleaning + revenue pipeline (Part 2)
- `revenue_by_region.csv` — pipeline output
- `test_virtual_column.py` — given sample tests
- `test_solution_extra.py`, `test_pipeline.py` — own tests (Part 3)
- `sales.csv` — given raw data

## Assumptions

- `role` = column names joined by `+ - *`, with `*` before `+/-`
  (needed for `Quantity * Unit_Price - Discount`).
- Invalid `new_column`/`role`/unknown column → empty DataFrame.
- Task example shows column `price_total` but passes `new_column="total"`
  — assumed typo, new column is always named `new_column`.
- Revenue = `Quantity * Unit_Price - Discount`.
- Columns with spaces are renamed with underscores before computing
  revenue (`add_virtual_column` only allows letters/underscores).
- `Order ID` is the order's identity; a repeated one = same order twice.

## Problems in sales.csv

- Header row repeated mid-file (1 row) — dropped.
- `TOTAL` row at the end (1 row) — dropped.
- `Quantity ` header has a trailing space — stripped.
- Region casing/whitespace is inconsistent, e.g. `EAST`, `west  `, ` North`
  (15 rows) — normalised to one spelling per region.
- Quantity uses a space as thousands separator, e.g. `"1 762"` (4 rows) —
  space removed.
- Quantity is negative in some rows (6 rows) — fixed with `abs()`.
- Unit Price uses a comma as decimal separator, e.g. `"59,00"` (7 rows) —
  comma replaced with a dot.
- Unit Price missing (4 rows) — filled from that product's known price.
- Discount blank means no discount (963 rows) — filled with 0.
- Exact duplicate orders (5 rows) — dropped, kept the first.

1505 real orders remain after dropping the header/TOTAL rows, 1500 after
dropping duplicates — that's what `revenue_by_region.csv` is based on.
