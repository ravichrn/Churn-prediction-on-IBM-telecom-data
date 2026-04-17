"""Churner vs non-churner mean comparison (SAS `perChange` / `chDiff_sorted`)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def mean_percent_difference(encoded: pd.DataFrame, churn_col: str = "ChurnEn") -> pd.DataFrame:
    numeric = encoded.select_dtypes(include=[np.number]).copy()
    if churn_col in numeric.columns:
        feature_cols = [c for c in numeric.columns if c != churn_col]
    else:
        feature_cols = list(numeric.columns)

    yes = encoded[encoded[churn_col] == 1][feature_cols].mean().astype("float64")
    no = encoded[encoded[churn_col] == 0][feature_cols].mean().astype("float64")
    diff = (yes - no).abs()
    denom = no.replace(0, np.nan).astype("float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        per_change = ((diff / denom) * 100.0).astype("float64")

    result = pd.DataFrame({"variable": feature_cols})
    result["yes_mean"] = yes[feature_cols].to_numpy(dtype=float, na_value=np.nan)
    result["no_mean"] = no[feature_cols].to_numpy(dtype=float, na_value=np.nan)
    result["perChng"] = per_change[feature_cols].to_numpy(dtype=float, na_value=np.nan)
    return result.sort_values("perChng", ascending=False, na_position="last").reset_index(drop=True)
