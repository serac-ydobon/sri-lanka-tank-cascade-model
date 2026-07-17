"""Shared data-loading helpers for demo scripts.

Kept separate from hydrology.py/climate.py so both demos load the
Jaffna/Iranaimadu workbook the same way instead of each keeping their
own copy of the reshape logic.
"""

import pandas as pd


def load_daily_rainfall_jaffna(
    xlsx_path=r"C:\Users\sam_w\Desktop\Hydrological Model\1975-2025 daily Rainfall_ Jaffna and Iranaimadu .xlsx",
    sheet="qry_xdaily_data",
    station="JAFFNA",
):
    """Load and reshape the Jaffna/Iranaimadu daily rainfall workbook into
    a tidy (date, P) daily dataframe for one station.

    Path defaults to the original author's machine -- pass `xlsx_path`
    explicitly if running elsewhere. Returns the full station record;
    callers should filter by year range themselves if needed.
    """
    df = pd.read_excel(xlsx_path, sheet_name=sheet, header=1)  # header row is the 2nd row in the sheet
    df["station_name"] = df["station_name"].astype(str).str.strip().str.upper()

    sub = df[df["station_name"] == station.upper()].copy()

    # day columns are integers 1..31
    day_cols = [c for c in sub.columns if isinstance(c, int)]

    long = sub.melt(
        id_vars=["Year", "Month"],
        value_vars=day_cols,
        var_name="Day",
        value_name="P"
    )

    long["Year"] = long["Year"].astype(int)
    long["Month"] = long["Month"].astype(int)
    long["Day"] = long["Day"].astype(int)

    long["date"] = pd.to_datetime(
        dict(year=long["Year"], month=long["Month"], day=long["Day"]),
        errors="coerce"
    )
    long = long.dropna(subset=["date"])

    long["P"] = pd.to_numeric(long["P"], errors="coerce").fillna(0.0)

    daily = long.groupby("date", as_index=False)["P"].sum().sort_values("date").reset_index(drop=True)
    return daily
