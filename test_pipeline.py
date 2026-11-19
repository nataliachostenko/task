import io

import pandas as pd
import pytest

import pipeline

HEADER = "Order ID,Region,Product,Quantity ,Unit Price,Discount,Order Date\n"


def _load(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_text), dtype=str)


def test_strips_trailing_space_from_quantity_column_name():
    raw = _load(HEADER + "SO-1,North,Mouse,1,29.50,,2026-01-01\n")
    cleaned = pipeline.clean(raw)
    assert "Quantity" in cleaned.columns
    assert "Quantity " not in cleaned.columns


def test_drops_stray_header_row_and_total_row():
    raw = _load(
        HEADER
        + "SO-1,North,Mouse,1,29.50,,2026-01-01\n"
        + HEADER
        + "TOTAL,,,1,,0,\n"
    )
    cleaned = pipeline.clean(raw)
    assert len(cleaned) == 1
    assert cleaned["Order_ID"].tolist() == ["SO-1"]


def test_normalises_region_case_and_whitespace():
    raw = _load(
        HEADER
        + "SO-1, North,Mouse,1,29.50,,2026-01-01\n"
        + "SO-2,north ,Mouse,1,29.50,,2026-01-01\n"
        + "SO-3,NORTH,Mouse,1,29.50,,2026-01-01\n"
    )
    cleaned = pipeline.clean(raw)
    assert cleaned["Region"].unique().tolist() == ["North"]


def test_removes_thousands_separator_space_from_quantity():
    raw = _load(HEADER + "SO-1,North,Mouse,1 234,29.50,,2026-01-01\n")
    cleaned = pipeline.clean(raw)
    assert cleaned["Quantity"].tolist() == [1234]


def test_negative_quantity_is_made_positive():
    raw = _load(HEADER + "SO-1,North,Mouse,-3,29.50,,2026-01-01\n")
    cleaned = pipeline.clean(raw)
    assert cleaned["Quantity"].tolist() == [3]


def test_comma_decimal_separator_in_unit_price_is_parsed():
    raw = _load(HEADER + 'SO-1,North,Mouse,1,"29,50",,2026-01-01\n')
    cleaned = pipeline.clean(raw)
    assert cleaned["Unit_Price"].tolist() == [29.50]


def test_missing_unit_price_is_filled_from_same_product():
    raw = _load(
        HEADER
        + "SO-1,North,Mouse,1,29.50,,2026-01-01\n"
        + "SO-2,South,Mouse,2,,,2026-01-02\n"
    )
    cleaned = pipeline.clean(raw)
    assert cleaned.loc[cleaned["Order_ID"] == "SO-2", "Unit_Price"].iloc[0] == 29.50


def test_missing_discount_becomes_zero():
    raw = _load(HEADER + "SO-1,North,Mouse,1,29.50,,2026-01-01\n")
    cleaned = pipeline.clean(raw)
    assert cleaned["Discount"].tolist() == [0.0]


def test_duplicate_order_id_rows_are_collapsed_to_one():
    raw = _load(
        HEADER
        + "SO-1,North,Mouse,1,29.50,,2026-01-01\n"
        + "SO-1,North,Mouse,1,29.50,,2026-01-01\n"
    )
    cleaned = pipeline.clean(raw)
    assert len(cleaned) == 1


def test_revenue_is_quantity_times_price_minus_discount():
    raw = _load(HEADER + "SO-1,North,Mouse,10,2.00,3.00,2026-01-01\n")
    cleaned = pipeline.clean(raw)
    with_revenue = pipeline.add_revenue(cleaned)
    assert with_revenue["Revenue"].tolist() == [17.0]


def test_revenue_by_region_sums_per_region():
    raw = _load(
        HEADER
        + "SO-1,North,Mouse,10,2.00,0,2026-01-01\n"
        + "SO-2,North,Mouse,5,2.00,0,2026-01-02\n"
        + "SO-3,South,Mouse,1,2.00,0,2026-01-03\n"
    )
    cleaned = pipeline.clean(raw)
    with_revenue = pipeline.add_revenue(cleaned)
    result = pipeline.revenue_by_region(with_revenue)
    result = result.set_index("Region")["Revenue"]
    assert result["North"] == pytest.approx(30.0)
    assert result["South"] == pytest.approx(2.0)


def test_run_writes_output_file(tmp_path):
    input_path = tmp_path / "sales.csv"
    output_path = tmp_path / "revenue_by_region.csv"
    input_path.write_text(
        HEADER + "SO-1,North,Mouse,10,2.00,0,2026-01-01\n", encoding="utf-8"
    )

    result = pipeline.run(str(input_path), str(output_path))

    assert output_path.exists()
    on_disk = pd.read_csv(output_path)
    assert on_disk["Region"].tolist() == result["Region"].tolist()
    assert on_disk["Revenue"].tolist() == result["Revenue"].tolist()
