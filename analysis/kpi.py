import pandas as pd
from typing import Dict, Any


def calculate_comprehensive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    kpis: Dict[str, Any] = {}

    kpis["total_records"] = len(df)
    kpis["total_fields"] = len(df.columns)

    completeness: Dict[str, float] = {}
    for col in df.columns:
        if col.startswith("_"):
            continue
        non_empty = (df[col].notna() & (df[col] != "")).sum()
        completeness[col] = round((non_empty / len(df)) * 100, 2) if len(df) > 0 else 0

    kpis["field_completeness"] = completeness
    kpis["overall_completeness"] = (
        round(sum(completeness.values()) / len(completeness), 2) if completeness else 0
    )

    kpis["quality_score"] = df.attrs.get("quality_score", 0)

    numeric_stats: Dict[str, Any] = {}
    text_stats: Dict[str, Any] = {}

    for col in df.columns:
        if col.startswith("_"):
            continue

        col_lower = col.lower()

        if "price" in col_lower or "cost" in col_lower:
            prices = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(prices) > 0:
                numeric_stats[col] = {
                    "mean": round(prices.mean(), 2),
                    "median": round(prices.median(), 2),
                    "min": round(prices.min(), 2),
                    "max": round(prices.max(), 2),
                    "std": round(prices.std(), 2) if len(prices) > 1 else 0,
                }

        elif "rating" in col_lower or "score" in col_lower:
            ratings = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(ratings) > 0:
                numeric_stats[col] = {
                    "mean": round(ratings.mean(), 2),
                    "median": round(ratings.median(), 2),
                    "min": round(ratings.min(), 2),
                    "max": round(ratings.max(), 2),
                    "count": len(ratings),
                }

        else:
            non_empty = df[col].dropna()
            non_empty = non_empty[non_empty != ""]
            if len(non_empty) > 0:
                lengths = non_empty.astype(str).str.len()
                text_stats[col] = {
                    "avg_length": round(lengths.mean(), 2),
                    "max_length": int(lengths.max()),
                    "min_length": int(lengths.min()),
                }

    kpis["numeric_statistics"] = numeric_stats
    kpis["text_statistics"] = text_stats

    duplicates = len(df) - len(df.drop_duplicates())
    kpis["duplicate_count"] = duplicates
    kpis["duplicate_percentage"] = (
        round((duplicates / len(df)) * 100, 2) if len(df) > 0 else 0
    )

    missing_data: Dict[str, Any] = {}
    for col in df.columns:
        if col.startswith("_"):
            continue
        missing = (df[col].isna() | (df[col] == "")).sum()
        missing_data[col] = {
            "count": int(missing),
            "percentage": round((missing / len(df)) * 100, 2) if len(df) > 0 else 0,
        }
    kpis["missing_data"] = missing_data

    unique_counts: Dict[str, int] = {}
    for col in df.columns:
        if col.startswith("_"):
            continue
        unique_counts[col] = int(df[col].nunique(dropna=True))
    kpis["unique_values"] = unique_counts

    return kpis
