import pandas as pd

from solution import add_virtual_column

INPUT_FILE = "sales.csv"
OUTPUT_FILE = "revenue_by_region.csv"


def load_raw(path: str = INPUT_FILE) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [c.strip() for c in df.columns]

    df = df[~df["Order ID"].isin(["Order ID", "TOTAL"])].copy()

    df["Region"] = df["Region"].str.strip().str.title()

    df["Quantity"] = (
        df["Quantity"].str.replace(" ", "", regex=False).astype(int).abs()
    )

    df["Unit Price"] = (
        df["Unit Price"].str.replace(",", ".", regex=False).astype(float)
    )
    price_by_product = df.groupby("Product")["Unit Price"].transform("median")
    df["Unit Price"] = df["Unit Price"].fillna(price_by_product)

    df["Discount"] = df["Discount"].astype(float).fillna(0.0)

    df = df.drop_duplicates(subset=["Order ID"], keep="first")

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    df = df.rename(
        columns={
            "Order ID": "Order_ID",
            "Unit Price": "Unit_Price",
            "Order Date": "Order_Date",
        }
    )
    return df.reset_index(drop=True)


def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return add_virtual_column(df, "Quantity * Unit_Price - Discount", "Revenue")


def revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Region")
        .reset_index(drop=True)
    )


def run(input_path: str = INPUT_FILE, output_path: str = OUTPUT_FILE) -> pd.DataFrame:
    raw = load_raw(input_path)
    cleaned = clean(raw)
    with_revenue = add_revenue(cleaned)
    result = revenue_by_region(with_revenue)
    result.to_csv(output_path, index=False)
    return result


if __name__ == "__main__":
    print(run())
