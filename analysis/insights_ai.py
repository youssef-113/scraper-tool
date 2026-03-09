import pandas as pd
import json
from typing import Dict, Any, Optional


def generate_comprehensive_insights(
    df: pd.DataFrame,
    kpis: Dict[str, Any],
    api_key: str,
    urls: Optional[list] = None,
) -> str:
    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    except Exception as e:
        return (
            f"Unable to generate AI insights: {str(e)}\n\nPlease check your Groq API key and try again."
        )

    summary: Dict[str, Any] = {
        "total_records": len(df),
        "columns": [col for col in df.columns if not col.startswith("_")],
        "sample_data": df.head(10).to_dict("records"),
        "data_types": df.dtypes.astype(str).to_dict(),
        "kpis": {
            "quality_score": kpis.get("quality_score", 0),
            "completeness": kpis.get("overall_completeness", 0),
            "duplicates": kpis.get("duplicate_percentage", 0),
            "numeric_stats": kpis.get("numeric_statistics", {}),
            "text_stats": kpis.get("text_statistics", {}),
        },
    }

    if urls:
        summary["source_urls"] = urls[:3]

    prompt = f"""You are a professional data analyst. Analyze this scraped dataset and provide comprehensive insights.

Dataset Summary:
{json.dumps(summary, indent=2, default=str)}

Provide a detailed analysis covering:

1. Dataset Overview
2. Key Findings
3. Data Quality Assessment
4. Recommendations

Keep the analysis professional, actionable, and under 400 words."""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior data analyst providing clear, actionable insights from scraped data.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return (
            f"Unable to generate AI insights: {str(e)}\n\nPlease check your OpenAI API key and try again."
        )
