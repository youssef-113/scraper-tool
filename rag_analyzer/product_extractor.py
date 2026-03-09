import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class ProductExtractor:
    """Extract and analyze product-related information from data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._identify_product_columns()

    def _identify_product_columns(self):
        """Identify columns that likely contain product information."""
        self.name_col = self._find_column_by_keywords([
            'name', 'title', 'product', 'item', 'description'
        ])
        self.price_col = self._find_column_by_keywords([
            'price', 'cost', 'amount', 'value', 'total', 'price_usd', 'price_eur'
        ])
        self.category_col = self._find_column_by_keywords([
            'category', 'type', 'department', 'section', 'group', 'class'
        ])
        self.brand_col = self._find_column_by_keywords([
            'brand', 'manufacturer', 'maker', 'company', 'vendor', 'seller'
        ])
        self.rating_col = self._find_column_by_keywords([
            'rating', 'review', 'score', 'stars', 'rate', 'grade'
        ])
        self.quantity_col = self._find_column_by_keywords([
            'quantity', 'qty', 'count', 'stock', 'inventory', 'units', 'amount'
        ])

    def _find_column_by_keywords(self, keywords: List[str]) -> Optional[str]:
        """Find a column that matches any of the keywords."""
        for col in self.df.columns:
            col_lower = col.lower().replace('_', '').replace(' ', '')
            for keyword in keywords:
                if keyword.lower() in col_lower:
                    return col
        return None

    def generate_product_summary(self) -> str:
        """Generate a summary of product data."""
        parts = []

        parts.append(f"Dataset contains {len(self.df)} products/items.")

        if self.category_col:
            unique_cats = self.df[self.category_col].nunique()
            parts.append(f"Products are categorized into {unique_cats} categories.")

        if self.brand_col:
            unique_brands = self.df[self.brand_col].nunique()
            parts.append(f"There are {unique_brands} unique brands.")

        if self.price_col:
            avg_price = self.df[self.price_col].mean()
            min_price = self.df[self.price_col].min()
            max_price = self.df[self.price_col].max()
            parts.append(f"Price range: ${min_price:.2f} - ${max_price:.2f}, average: ${avg_price:.2f}.")

        if self.rating_col:
            avg_rating = self.df[self.rating_col].mean()
            parts.append(f"Average rating: {avg_rating:.2f}/5.")

        if self.quantity_col:
            total_qty = self.df[self.quantity_col].sum()
            parts.append(f"Total inventory: {total_qty:.0f} units.")

        return " ".join(parts)

    def extract_price_stats(self) -> Optional[Dict[str, float]]:
        """Extract price statistics."""
        if not self.price_col:
            return None

        prices = pd.to_numeric(self.df[self.price_col], errors='coerce').dropna()

        if len(prices) == 0:
            return None

        return {
            'min_price': float(prices.min()),
            'max_price': float(prices.max()),
            'avg_price': float(prices.mean()),
            'median_price': float(prices.median()),
            'std_price': float(prices.std()),
            'total_value': float(prices.sum())
        }

    def extract_category_breakdown(self) -> Optional[Dict[str, int]]:
        """Get breakdown by category."""
        if not self.category_col:
            return None

        breakdown = self.df[self.category_col].value_counts().to_dict()
        return {str(k): int(v) for k, v in breakdown.items()}

    def extract_brand_breakdown(self) -> Optional[Dict[str, int]]:
        """Get breakdown by brand."""
        if not self.brand_col:
            return None

        breakdown = self.df[self.brand_col].value_counts().to_dict()
        return {str(k): int(v) for k, v in breakdown.items()}

    def extract_rating_stats(self) -> Optional[Dict[str, Any]]:
        """Extract rating statistics."""
        if not self.rating_col:
            return None

        ratings = pd.to_numeric(self.df[self.rating_col], errors='coerce').dropna()

        if len(ratings) == 0:
            return None

        return {
            'avg_rating': float(ratings.mean()),
            'median_rating': float(ratings.median()),
            'min_rating': float(ratings.min()),
            'max_rating': float(ratings.max()),
            'rating_distribution': {
                '5_star': int((ratings >= 4.5).sum()),
                '4_star': int(((ratings >= 3.5) & (ratings < 4.5)).sum()),
                '3_star': int(((ratings >= 2.5) & (ratings < 3.5)).sum()),
                '2_star': int(((ratings >= 1.5) & (ratings < 2.5)).sum()),
                '1_star': int((ratings < 1.5).sum())
            }
        }

    def get_top_products(self, by: str = 'price', limit: int = 10) -> pd.DataFrame:
        """Get top products by a specific column."""
        if by not in self.df.columns:
            # Try to find similar column
            by = self._find_column_by_keywords([by]) or by

        if by not in self.df.columns:
            return pd.DataFrame()

        # Sort and get top
        sorted_df = self.df.sort_values(by=by, ascending=False).head(limit)

        # Select relevant columns for display
        display_cols = []
        if self.name_col:
            display_cols.append(self.name_col)
        if self.category_col:
            display_cols.append(self.category_col)
        if self.brand_col:
            display_cols.append(self.brand_col)
        display_cols.append(by)
        if self.rating_col and self.rating_col != by:
            display_cols.append(self.rating_col)

        # Return only available columns
        available_cols = [c for c in display_cols if c in self.df.columns]

        if not available_cols:
            available_cols = self.df.columns[:5].tolist()

        return sorted_df[available_cols].reset_index(drop=True)

    def find_products_by_criteria(self, **criteria) -> pd.DataFrame:
        """Find products matching specific criteria."""
        result = self.df.copy()

        for key, value in criteria.items():
            col = self._find_column_by_keywords([key])
            if col and col in result.columns:
                if isinstance(value, tuple):
                    result = result[
                        (result[col] >= value[0]) &
                        (result[col] <= value[1])
                    ]
                elif isinstance(value, list):
                    result = result[result[col].isin(value)]
                else:
                    result = result[result[col] == value]

        return result.reset_index(drop=True)

    def get_price_by_category(self) -> Optional[Dict[str, Dict[str, float]]]:
        """Get price statistics grouped by category."""
        if not self.price_col or not self.category_col:
            return None

        grouped = self.df.groupby(self.category_col)[self.price_col].agg([
            'mean', 'median', 'min', 'max', 'count'
        ]).to_dict('index')

        return {
            str(cat): {
                'avg_price': float(stats['mean']),
                'median_price': float(stats['median']),
                'min_price': float(stats['min']),
                'max_price': float(stats['max']),
                'count': int(stats['count'])
            }
            for cat, stats in grouped.items()
        }

    def get_inventory_summary(self) -> Optional[Dict[str, Any]]:
        """Get inventory/stock summary."""
        if not self.quantity_col:
            return None

        quantities = pd.to_numeric(self.df[self.quantity_col], errors='coerce').dropna()

        return {
            'total_units': float(quantities.sum()),
            'avg_per_product': float(quantities.mean()),
            'products_in_stock': int((quantities > 0).sum()),
            'out_of_stock': int((quantities == 0).sum()),
            'low_stock': int((quantities > 0) & (quantities < 10)).sum()
        }
