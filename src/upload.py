import pandas as pd
import streamlit as st

MAP_RULES = {
    "Wellbore name": ["well", "well name", "wellbore", "wellbore name", "well_name", "well_name"],
    "Year": ["year", "yr", "production year", "date year"],
    "Month": ["month", "mo", "production month", "date month", "period"],
    "Oil": ["oil", "oil production", "oil volume", "oil_prod", "oil_vol", "oil_sm3"],
    "Gas": ["gas", "gas production", "gas volume", "gas_prod", "gas_vol", "gas_sm3"],
    "Water": ["water", "water production", "water volume", "water_prod", "water_vol", "water_sm3"],
    "Water Injection": ["wi", "water injection", "water_injection", "inj_water"],
    "Gas Injection": ["gi", "gas injection", "gas_injection", "inj_gas"],
    "Operating Days": ["on stream", "operating days", "days online", "days_on_stream", "operating_days", "days"],
}

REQUIRED = ["Wellbore name", "Oil"]
OPTIONAL = ["Gas", "Water", "Water Injection", "Gas Injection", "Operating Days", "Year", "Month"]


def detect_columns(df):
    detected = {}
    cols = [str(c) for c in df.columns]
    col_map = {c.lower().replace("_", " ").strip(): c for c in cols}
    for std, variants in MAP_RULES.items():
        for v in variants:
            key = v.lower().replace("_", " ").strip()
            if key in col_map:
                detected[std] = col_map[key]
                break
    return detected


def validate(df, mapping):
    issues = []
    valid = df.copy()
    missing_vals = {}
    for std in REQUIRED + OPTIONAL:
        if std in mapping:
            col = mapping[std]
            missing_vals[col] = int(df[col].isna().sum()) if col in df.columns else 0
    well_col = mapping.get("Wellbore name")
    if well_col and well_col in df.columns:
        empty_wells = int((df[well_col].astype(str).str.strip() == "").sum())
        if empty_wells > 0:
            issues.append(f"{empty_wells} missing/empty well names")
    date_cols = [mapping.get("Year"), mapping.get("Month")]
    if any(dc in df.columns for dc in date_cols if dc):
        issues.append("Date construction from Year/Month; full date validation deferred to cleaning.")
    prod_cols = [mapping.get("Oil"), mapping.get("Gas"), mapping.get("Water")]
    for pc in prod_cols:
        if pc and pc in df.columns:
            non_numeric = int(pd.to_numeric(df[pc], errors="coerce").isna().sum() - missing_vals.get(pc, 0))
            if non_numeric > 0:
                issues.append(f"{pc}: {non_numeric} non-numeric values")
            negatives = int((pd.to_numeric(df[pc], errors="coerce") < 0).sum())
            if negatives > 0:
                issues.append(f"{pc}: {negatives} negative production values")
    dupes = int(df.duplicated(subset=[mapping.get("Wellbore name")]).sum()) if mapping.get("Wellbore name") in df.columns else 0
    if dupes > 0:
        issues.append(f"{dupes} duplicate well-date records detected")
    total = len(df)
    valid_count = len(valid.dropna(subset=[mapping.get("Oil")])) if mapping.get("Oil") in df.columns else total
    return {
        "total": total,
        "valid": valid_count,
        "invalid": total - valid_count,
        "duplicates": dupes,
        "missing_by_col": {mapping.get(k, k): v for k, v in missing_vals.items() if v > 0},
        "issues": issues,
    }
