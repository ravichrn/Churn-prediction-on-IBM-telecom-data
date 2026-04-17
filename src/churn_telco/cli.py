"""CLI entry: run the SAS workflow steps on an Excel file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from churn_telco.encoding import encode_features
from churn_telco.load_data import load_churn_excel
from churn_telco.mean_diff import mean_percent_difference
from churn_telco.modeling import correlation_matrix, fit_logistic, logistic_hit_ratio, ols_white_test


def _print_freq_tables(raw: pd.DataFrame, columns: list[str]) -> None:
    print("\n--- Frequency tables (SAS PROC FREQ) ---")
    for col in columns:
        if col not in raw.columns:
            continue
        print(f"\n{col}")
        print(raw[col].value_counts(dropna=False).to_string())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="IBM Telco churn analysis (Python port of churn.sas).",
    )
    parser.add_argument(
        "data",
        nargs="?",
        default=str(Path("data") / "IBM-Telco-Customer-Churn.xlsx"),
        help="Path to IBM-Telco-Customer-Churn.xlsx (default: ./data/IBM-Telco-Customer-Churn.xlsx)",
    )
    parser.add_argument(
        "--sheet",
        default=0,
        help="Excel sheet name or index (default: 0).",
    )
    args = parser.parse_args(argv)

    path = Path(args.data)
    try:
        raw = load_churn_excel(path, sheet_name=args.sheet)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        print(
            "Place the Kaggle/IBM Telco file at the path above, or pass a path explicitly.",
            file=sys.stderr,
        )
        return 1

    print("--- First 10 rows (SAS PROC PRINT) ---")
    print(raw.head(10).to_string())
    print("\n--- Column types (SAS PROC CONTENTS) ---")
    print(raw.dtypes.to_string())

    freq_cols = [
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod",
        "Churn",
    ]
    _print_freq_tables(raw, freq_cols)

    encoded = encode_features(raw)
    print("\n--- Encoded data, first 10 rows ---")
    print(encoded.head(10).to_string())
    print("\n--- Encoded dtypes ---")
    print(encoded.dtypes.to_string())

    ranked = mean_percent_difference(encoded)
    print("\n--- Mean absolute percent difference churn vs non-churn (sorted) ---")
    print(ranked.to_string(index=False))

    print("\n--- Correlation matrix (encoded numerics, SAS PROC CORR) ---")
    corr = correlation_matrix(encoded)
    with pd.option_context("display.max_rows", 50, "display.max_columns", 50, "display.width", 200):
        print(corr.round(3).to_string())

    print("\n--- OLS + White heteroskedasticity test (SAS PROC MODEL / WHITE) ---")
    ols_res, white = ols_white_test(encoded.dropna())
    print(ols_res.summary().as_text())
    lm_stat, lm_pval, f_stat, f_pval = white
    print(f"\nWhite test LM stat={lm_stat:.4f}, p={lm_pval:.4g}; F={f_stat:.4f}, p={f_pval:.4g}")

    print("\n--- Logistic regression (SAS PROC LOGISTIC) ---")
    clean = raw.dropna()
    logit = fit_logistic(clean)
    print(logit.summary().as_text())
    hit = logistic_hit_ratio(clean, logit)
    print(f"\nHit ratio (predicted class vs actual, ~SAS SCORE): {hit:.2f}%")

    return 0
