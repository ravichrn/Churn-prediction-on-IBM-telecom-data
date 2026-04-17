"""Correlation, OLS + White test, and logistic regression (SAS PROC CORR / MODEL / LOGISTIC)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_white


def correlation_matrix(encoded: pd.DataFrame) -> pd.DataFrame:
    numeric = encoded.select_dtypes(include=[np.number])
    return numeric.corr()


def ols_white_test(encoded: pd.DataFrame) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, tuple]:
    """OLS for `ChurnEn` on SAS-selected numerics; returns fit and White test (stat, pvalue, fstat, fpvalue)."""
    y = encoded["ChurnEn"].astype(float).values
    x_cols = [
        "SeniorCitizen",
        "ContractEn",
        "MonthlyCharges",
        "OnlineSecurityEn",
        "PaperlessBillingEn",
        "TechSupportEn",
        "DependentsEn",
        "PaymentEn",
        "tenure",
        "PhoneServiceEn",
    ]
    X = encoded[x_cols].astype(float)
    X = sm.add_constant(X, has_constant="add")
    res = sm.OLS(y, X).fit()
    white = het_white(res.resid, X)
    return res, white


def fit_logistic(raw: pd.DataFrame):
    """Logistic regression mirroring SAS `proc logistic` formula (reference coding differs slightly)."""
    df = raw.copy()
    df["Churn_yes"] = (df["Churn"] == "Yes").astype(int)
    formula = (
        "Churn_yes ~ SeniorCitizen + C(OnlineSecurity) + C(TechSupport) + C(Dependents) "
        "+ MonthlyCharges + C(PaperlessBilling) + C(Contract) + C(PaymentMethod) "
        "+ C(PhoneService) + tenure"
    )
    return smf.logit(formula, data=df).fit(disp=False)


def logistic_hit_ratio(raw: pd.DataFrame, results, threshold: float = 0.5) -> float:
    pred = (results.predict(raw) >= threshold).astype(int)
    actual = (raw["Churn"] == "Yes").astype(int)
    return float((pred == actual).mean() * 100.0)
