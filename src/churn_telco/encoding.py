"""SAS `churn_en` encoding rules from `churn.sas`."""

from __future__ import annotations

import pandas as pd


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with SAS-style `*En` columns; original categoricals dropped."""
    out = df.copy()

    out["genderEn"] = (out["gender"] == "Male").astype(int)
    out["PartnerEn"] = (out["Partner"] == "Yes").astype(int)
    out["DependentsEn"] = (out["Dependents"] == "Yes").astype(int)
    out["PhoneServiceEn"] = (out["PhoneService"] == "Yes").astype(int)
    out["MultipleLinesEn"] = (out["MultipleLines"] == "Yes").astype(int)
    out["InternetServiceEn"] = out["InternetService"].isin(["DSL", "Fiber optic"]).astype(int)
    out["OnlineSecurityEn"] = (
        ~out["OnlineSecurity"].isin(["No", "No internet service"])
    ).astype(int)
    out["OnlineBackupEn"] = (~out["OnlineBackup"].isin(["No", "No internet service"])).astype(int)
    out["DeviceProtectionEn"] = (
        ~out["DeviceProtection"].isin(["No", "No internet service"])
    ).astype(int)
    out["TechSupportEn"] = (~out["TechSupport"].isin(["No", "No internet service"])).astype(int)
    out["StreamingTVEn"] = (~out["StreamingTV"].isin(["No", "No internet service"])).astype(int)
    out["StreamingMoviesEn"] = (
        ~out["StreamingMovies"].isin(["No", "No internet service"])
    ).astype(int)

    contract_map = {"Month-to-month": 1, "One year": 2, "Two year": 3}
    out["ContractEn"] = out["Contract"].map(contract_map).astype("Int64")

    out["PaperlessBillingEn"] = (out["PaperlessBilling"] == "Yes").astype(int)

    payment_map = {
        "Bank transfer (automatic)": 1,
        "Credit card (automatic)": 2,
        "Electronic check": 3,
        "Mailed check": 4,
    }
    out["PaymentEn"] = out["PaymentMethod"].map(payment_map).astype("Int64")

    out["ChurnEn"] = (out["Churn"] == "Yes").astype(int)

    drop_cols = [
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
    out = out.drop(columns=[c for c in drop_cols if c in out.columns])
    return out
