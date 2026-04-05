"""
Insight Generator — Groq LLM (llama3-70b-8192) with template fallback
"""

import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _make_client() -> Optional[OpenAI]:
    key = os.getenv("GROQ_API_KEY")
    base = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    if not key:
        return None
    return OpenAI(api_key=key, base_url=base)


_client = _make_client()
_MODEL  = os.getenv("LLM_MODEL", "llama3-70b-8192")


# ── Template fallback ──────────────────────────────────────────────────────────
def _template(region: str, parameter: str, stats: Dict, trend: Dict) -> str:
    direction = trend.get("direction", "stable")
    per_year  = abs(trend.get("per_year", 0))
    unit      = "°C" if parameter == "temperature" else " PSU"

    lines = [
        f"Analysis of {parameter} in {region}:",
        f"• Mean: {stats.get('mean', 'N/A')}{unit} "
        f"(range {stats.get('min', 'N/A')}–{stats.get('max', 'N/A')}{unit})",
        f"• Trend: {direction} at {per_year}{unit}/year",
    ]

    if parameter == "temperature" and direction == "rising":
        lines.append(
            "Rising ocean temperatures are a key indicator of climate change "
            "and can drive coral bleaching and shifts in marine biodiversity."
        )
    elif parameter == "salinity" and direction == "falling":
        lines.append(
            "Declining salinity may reflect accelerated ice melt or increased "
            "precipitation — both consistent with broader climate warming signals."
        )
    elif parameter == "temperature" and direction == "falling":
        lines.append(
            "Cooling trends in this region may indicate changes in ocean circulation "
            "patterns such as upwelling intensity or shifts in major current systems."
        )
    else:
        lines.append(
            f"Sustained changes in ocean {parameter} are important indicators "
            "of climate health and require continued monitoring."
        )

    return "\n".join(lines)


# ── LLM insight ────────────────────────────────────────────────────────────────
def generate_insight(region: str, parameter: str, stats: Dict, trend: Dict) -> Dict:
    """
    Generate a scientific 2–3 sentence insight.
    Returns {"text": str, "source": "llm"|"template"}
    """
    if not _client:
        return {"text": _template(region, parameter, stats, trend), "source": "template"}

    unit      = "°C" if parameter == "temperature" else "PSU"
    direction = trend.get("direction", "stable")
    per_year  = abs(trend.get("per_year", 0))

    prompt = (
        f"You are an expert oceanographer providing a brief scientific summary.\n\n"
        f"Region: {region}\n"
        f"Parameter: {parameter}\n"
        f"Mean value: {stats.get('mean')}{unit}\n"
        f"Range: {stats.get('min')}–{stats.get('max')}{unit}\n"
        f"Trend: {direction} at {per_year}{unit}/year\n\n"
        "Write exactly 2–3 sentences of clear, scientific insight about what these "
        "ocean measurements indicate about climate or environmental conditions. "
        "Be specific, cite the numbers, and mention any risks or implications. "
        "Do NOT use bullet points or headers — plain prose only."
    )

    try:
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert oceanographer and climate scientist."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.4,
            max_tokens=200,
        )
        text = resp.choices[0].message.content.strip()
        return {"text": text, "source": "llm"}
    except Exception as e:
        print(f"[InsightGenerator] LLM failed ({e}), using template fallback")
        return {"text": _template(region, parameter, stats, trend), "source": "template"}


def _answer_template(region: str, parameter: str, stats: Dict, trend: Dict, risk: Dict) -> str:
    direction = trend.get("direction", "stable")
    per_year = abs(trend.get("per_year", 0))
    unit = "°C" if parameter == "temperature" else " PSU"
    risk_level = risk.get("level", "Unknown")
    risk_score = risk.get("score", 0)

    return (
        f"For {region}, {parameter} averages {stats.get('mean', 'N/A')}{unit} "
        f"(range {stats.get('min', 'N/A')}–{stats.get('max', 'N/A')}{unit}). "
        f"The trend is {direction} at about {per_year}{unit}/year. "
        f"Marine Risk Index: {risk_level} (score {risk_score}/7)."
    )


def generate_answer(
    region: str,
    parameter: str,
    stats: Dict,
    trend: Dict,
    risk: Dict,
    question: str,
) -> Dict:
    """
    Generate a chat-style response grounded in database stats.
    Returns {"text": str, "source": "llm"|"template"}
    """
    if not _client:
        return {"text": _answer_template(region, parameter, stats, trend, risk), "source": "template"}

    unit = "°C" if parameter == "temperature" else "PSU"
    direction = trend.get("direction", "stable")
    per_year = abs(trend.get("per_year", 0))
    risk_level = risk.get("level", "Unknown")
    risk_score = risk.get("score", 0)

    prompt = (
        f"You are a helpful ocean data assistant. Answer the user's question "
        f"using ONLY the provided data summary and do not fabricate numbers.\n\n"
        f"User question: {question}\n"
        f"Region: {region}\n"
        f"Parameter: {parameter}\n"
        f"Mean: {stats.get('mean')}{unit}\n"
        f"Range: {stats.get('min')}–{stats.get('max')}{unit}\n"
        f"Trend: {direction} at {per_year}{unit}/year\n"
        f"Marine Risk Index: {risk_level} (score {risk_score}/7)\n\n"
        "Respond in 2–4 sentences, in clear, plain language."
    )

    try:
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert ocean data assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=220,
        )
        text = resp.choices[0].message.content.strip()
        return {"text": text, "source": "llm"}
    except Exception as e:
        print(f"[InsightGenerator] Answer LLM failed ({e}), using template fallback")
        return {"text": _answer_template(region, parameter, stats, trend, risk), "source": "template"}
