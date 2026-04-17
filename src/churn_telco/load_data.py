"""Load IBM Telco churn data from Excel (SAS PROC IMPORT equivalent)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_churn_excel(path: str | Path, sheet_name: str | int = 0) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        msg = f"Data file not found: {path.resolve()}"
        raise FileNotFoundError(msg)
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df
