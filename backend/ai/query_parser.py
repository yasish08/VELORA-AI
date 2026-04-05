"""
Query Parser — Groq LLM (llama3-70b-8192) with rule-based fallback
"""

import os
import re
import json
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

REGION_ALIASES = {
    "Indian Ocean":   ["indian", "india", "arabian", "bay of bengal"],
    "Pacific Ocean":  ["pacific"],
    "Atlantic Ocean": ["atlantic"],
    "Arctic Ocean":   ["arctic", "polar", "north pole"],
}


# ── Fallback rule-based parser ─────────────────────────────────────────────────
def _rule_based(question: str) -> Dict:
    q = question.lower()
    region = None
    for r, aliases in REGION_ALIASES.items():
        if any(a in q for a in aliases):
            region = r
            break

    parameter = "salinity" if "salin" in q else "temperature"

    years = [int(y) for y in re.findall(r"\b(20\d{2})\b", q)]
    years = sorted(list(set(years)))  # Remove duplicates and sort
    start_year = min(years) if years else None
    end_year   = max(years) if len(years) >= 2 else None

    return {"region": region, "parameter": parameter,
            "start_year": start_year, "end_year": end_year,
            "source": "rule-based"}


# ── LLM parser ─────────────────────────────────────────────────────────────────
def parse_query(question: str) -> Dict:
    """
    Parse a natural language ocean query.
    Uses Groq LLaMA-3 if available, falls back to rule-based.
    """
    if not _client:
        return _rule_based(question)

    system = (
        "You are an ocean data query parser. "
        "Extract structured information from the user query and return ONLY valid JSON "
        "with these exact keys: "
        "\"region\" (one of: Indian Ocean, Pacific Ocean, Atlantic Ocean, Arctic Ocean, or null), "
        "\"parameter\" (\"temperature\" or \"salinity\"), "
        "\"start_year\" (integer or null), "
        "\"end_year\" (integer or null). "
        "Return nothing except the JSON object."
    )

    try:
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": question},
            ],
            temperature=0,
            max_tokens=150,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown fences if model adds them
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        parsed = json.loads(raw)
        parsed["source"] = "llm"
        return parsed
    except Exception as e:
        print(f"[QueryParser] LLM failed ({e}), using rule-based fallback")
        return _rule_based(question)
