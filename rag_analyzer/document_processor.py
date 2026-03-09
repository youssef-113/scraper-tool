import pandas as pd
import io
from typing import List, Dict, Any, Optional
import json


class DocumentProcessor:
    """Process and analyze uploaded documents for RAG."""

    def __init__(self):
        self.current_df: Optional[pd.DataFrame] = None

    def load_file(self, uploaded_file) -> pd.DataFrame:
        """Load CSV or Excel file from Streamlit upload."""
        file_name = uploaded_file.name.lower()

        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")

        self.current_df = df
        return df

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DataFrame structure and statistics."""
        analysis = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": [],
            "memory_usage": df.memory_usage(deep=True).sum(),
            "missing_data": {},
            "data_types": {}
        }

        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].count()),
                "null_count": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique()),
                "missing_pct": round(df[col].isnull().sum() / len(df) * 100, 2)
            }

            # Add type-specific stats
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                })

            analysis["columns"].append(col_info)
            analysis["data_types"][col] = str(df[col].dtype)
            analysis["missing_data"][col] = int(df[col].isnull().sum())

        return analysis

    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate natural language summary of the data."""
        summary_parts = []

        summary_parts.append(f"Dataset contains {len(df)} rows and {len(df.columns)} columns.")
        summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}.")

        # Identify key columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()

        if numeric_cols:
            summary_parts.append(f"Numeric columns: {', '.join(numeric_cols)}.")

        if text_cols:
            summary_parts.append(f"Text columns: {', '.join(text_cols[:5])}.")

        # Check for product-related columns
        product_keywords = ['name', 'title', 'product', 'item']
        price_keywords = ['price', 'cost', 'amount', 'value']
        category_keywords = ['category', 'type', 'brand', 'department']

        product_col = self._find_column(df, product_keywords)
        price_col = self._find_column(df, price_keywords)
        category_col = self._find_column(df, category_keywords)

        if product_col:
            summary_parts.append(f"Product column identified: '{product_col}'.")
        if price_col:
            summary_parts.append(f"Price column identified: '{price_col}'.")
        if category_col:
            summary_parts.append(f"Category column identified: '{category_col}'.")

        return " ".join(summary_parts)

    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Find column matching keywords."""
        for col in df.columns:
            col_lower = col.lower()
            for keyword in keywords:
                if keyword in col_lower:
                    return col
        return None

    def create_document_chunks(self, df: pd.DataFrame, chunk_size: int = 5) -> List[str]:
        """Create text chunks from DataFrame for vector storage."""
        chunks = []

        # Create summary chunk
        summary = self.generate_summary(df)
        chunks.append(f"DATASET_SUMMARY: {summary}")

        # Create column info chunks
        for col in df.columns:
            col_info = f"Column '{col}': dtype={df[col].dtype}, "
            col_info += f"unique={df[col].nunique()}, missing={df[col].isnull().sum()}"
            chunks.append(col_info)

        # Create row chunks in groups
        for i in range(0, len(df), chunk_size):
            chunk_df = df.iloc[i:i + chunk_size]
            chunk_text = f"ROWS_{i}_TO_{min(i + chunk_size, len(df))}: "

            for idx, row in chunk_df.iterrows():
                row_dict = row.to_dict()
                # Clean NaN values
                row_dict = {k: (v if pd.notna(v) else "N/A") for k, v in row_dict.items()}
                chunk_text += json.dumps(row_dict, default=str) + " | "

            chunks.append(chunk_text)

        # Create statistical chunks
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            stats = f"STATS_{col}: "
            stats += f"mean={df[col].mean():.2f}, median={df[col].median():.2f}, "
            stats += f"min={df[col].min():.2f}, max={df[col].max():.2f}"
            chunks.append(stats)

        # Create category value chunks
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols[:3]:  # Top 3 text columns
            value_counts = df[col].value_counts().head(10)
            cat_text = f"CATEGORIES_{col}: "
            cat_text += ", ".join([f"{k}({v})" for k, v in value_counts.items()])
            chunks.append(cat_text)

        return chunks

    def filter_dataframe(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame."""
        result = df.copy()

        for col, value in filters.items():
            if col in result.columns:
                if isinstance(value, tuple) and len(value) == 2:
                    # Range filter for numeric
                    result = result[
                        (result[col] >= value[0]) &
                        (result[col] <= value[1])
                    ]
                elif isinstance(value, list):
                    # Multi-select filter
                    result = result[result[col].isin(value)]
                else:
                    # Exact match
                    result = result[result[col] == value]

        return result

    def get_column_stats(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Get statistics for a specific column."""
        if column not in df.columns:
            return {}

        stats = {
            "column": column,
            "dtype": str(df[column].dtype),
            "count": int(df[column].count()),
            "null_count": int(df[column].isnull().sum()),
            "unique": int(df[column].nunique()),
        }

        if pd.api.types.is_numeric_dtype(df[column]):
            stats.update({
                "min": float(df[column].min()),
                "max": float(df[column].max()),
                "mean": float(df[column].mean()),
                "median": float(df[column].median()),
                "std": float(df[column].std()),
            })

        return stats
