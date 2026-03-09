import pandas as pd
import re
from typing import List, Dict, Any


def clean_text(text: Any) -> str:
    if pd.isna(text) or text is None:
        return ""

    text = str(text)

    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    text = text.replace("\u200b", "").replace("\ufeff", "")

    return text


def normalize_price(price: Any) -> str:
    if pd.isna(price) or not price:
        return ""

    price_str = str(price)

    numbers = re.findall(r"\d+[.,]?\d*", price_str)

    if numbers:
        clean_number = numbers[0].replace(",", "")
        try:
            float(clean_number)
            return clean_number
        except ValueError:
            pass

    return price_str


def normalize_rating(rating: Any) -> str:
    if pd.isna(rating) or not rating:
        return ""

    rating_str = str(rating)

    numbers = re.findall(r"\d+\.?\d*", rating_str)
    if numbers:
        return numbers[0]

    return rating_str


def normalize_url(url: Any, base_url: str = "") -> str:
    if pd.isna(url) or not url:
        return ""

    url_str = str(url).strip()

    if url_str.startswith("//"):
        url_str = "https:" + url_str
    elif url_str.startswith("/") and base_url:
        from urllib.parse import urljoin

        url_str = urljoin(base_url, url_str)

    return url_str


def detect_and_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.drop_duplicates()

    text_columns = df.select_dtypes(include=["object"]).columns
    if len(text_columns) > 0:
        primary_col = text_columns[0]
        df = df.drop_duplicates(subset=[primary_col], keep="first")

    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    for col in df.columns:
        if "email" in col.lower():
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            df[col] = df[col].apply(
                lambda x: x if pd.isna(x) or re.match(email_pattern, str(x)) else ""
            )

        if "url" in col.lower() or "link" in col.lower():
            url_pattern = r"^https?://"
            df[col] = df[col].apply(
                lambda x: x if pd.isna(x) or re.match(url_pattern, str(x)) else ""
            )

    return df


def calculate_quality_score(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0

    total_cells = df.size
    non_empty_cells = df.replace("", pd.NA).count().sum()

    completeness_score = (non_empty_cells / total_cells) * 100 if total_cells > 0 else 0

    duplicate_ratio = 1 - (len(df.drop_duplicates()) / len(df)) if len(df) > 0 else 0
    uniqueness_score = (1 - duplicate_ratio) * 100

    quality_score = (completeness_score * 0.7) + (uniqueness_score * 0.3)

    return round(quality_score, 2)


def clean_data_advanced(data: List[Dict[str, Any]], base_url: str = "") -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if df.empty:
        return df

    for col in df.columns:
        if col == "_extraction_source":
            continue

        df[col] = df[col].apply(clean_text)

        if "price" in col.lower() or "cost" in col.lower():
            df[col] = df[col].apply(normalize_price)

        elif "rating" in col.lower() or "score" in col.lower():
            df[col] = df[col].apply(normalize_rating)

        elif (
            "url" in col.lower()
            or "link" in col.lower()
            or "image" in col.lower()
        ):
            df[col] = df[col].apply(lambda x: normalize_url(x, base_url))

    df = df.replace("", pd.NA)

    threshold = 0.8
    df = df.dropna(thresh=int(threshold * len(df.columns)))

    df = detect_and_remove_duplicates(df)

    df = validate_data(df)

    df = df.reset_index(drop=True)

    df.attrs["quality_score"] = calculate_quality_score(df)

    return df
