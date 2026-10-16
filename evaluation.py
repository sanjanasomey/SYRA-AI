"""
PromptLab AI - Response Evaluation Engine
Module: evaluation.py

Evaluates LLM generations across three fundamental dimensions:
1. Relevance: Lexical and semantic overlap between the prompt and generated output.
2. Consistency: Structural adherence, logical formatting, length appropriateness, and schema compliance.
3. Response Time (Latency): Quantitative roundtrip execution duration in seconds.

Also supports A/B prompt comparison metrics and audit logging into Pandas DataFrames.
"""

import re
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd


# Common stop words to exclude from relevance tokenization
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should", "so", "some",
    "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would",
    "you", "your", "yours", "yourself", "yourselves"
}


# ==============================================================================
# TOKEN & LEXICAL ANALYSIS HELPERS
# ==============================================================================

def tokenize_meaningful_words(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens, stripping common punctuation and stopwords."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]


# ==============================================================================
# 1. RELEVANCE EVALUATION
# ==============================================================================

def compute_relevance_score(input_text: str, response_text: str, task_mode: str = "qa") -> Dict[str, Any]:
    """
    Computes lexical coverage and semantic grounding of the response relative to input.
    Returns a normalized score (0.0 - 1.0) and explanatory diagnosis.
    """
    if not response_text or not input_text:
        return {"score": 0.0, "rating": "Zero", "details": "Empty input or response."}

    query_tokens = set(tokenize_meaningful_words(input_text))
    response_tokens = set(tokenize_meaningful_words(response_text))

    if not query_tokens:
        return {"score": 0.70, "rating": "Moderate", "details": "General query without distinctive lexical terms."}

    # Intersect key terms
    overlap = query_tokens.intersection(response_tokens)
    overlap_ratio = len(overlap) / len(query_tokens)

    # Base score calibrated to realistic NLP generation
    # Even a good response uses synonyms and expansions rather than purely repeating prompt terms
    raw_score = 0.50 + (overlap_ratio * 0.45)

    # Length penalty if output is too brief (e.g. fewer than 10 words for an explanation)
    word_count = len(response_text.split())
    if word_count < 10 and task_mode != "classification":
        raw_score *= 0.6

    score = min(1.0, max(0.1, round(raw_score, 2)))

    if score >= 0.85:
        rating = "High"
        details = f"Strong conceptual alignment ({len(overlap)} of {len(query_tokens)} core query terms addressed)."
    elif score >= 0.65:
        rating = "Good"
        details = f"Adequate thematic alignment ({len(overlap)} key terms detected)."
    elif score >= 0.40:
        rating = "Moderate"
        details = "Partial topical overlap. May be overly generic."
    else:
        rating = "Low"
        details = "Low relevance; response does not sufficiently answer the specific prompt terms."

    return {
        "score": score,
        "rating": rating,
        "overlap_count": len(overlap),
        "query_token_count": len(query_tokens),
        "details": details
    }


# ==============================================================================
# 2. CONSISTENCY & STRUCTURE EVALUATION
# ==============================================================================

def compute_consistency_score(response_text: str, task_mode: str = "qa") -> Dict[str, Any]:
    """
    Evaluates formatting integrity, structural cohesion, and adherence to instructions.
    - QA: Checks headings, bullet points, clean formatting, absence of repetition.
    - Summarization: Checks section headers, conciseness, structured takeaway bullets.
    - Classification: Validates strict JSON syntax and schema keys.
    """
    if not response_text:
        return {"score": 0.0, "rating": "Zero", "details": "Empty response."}

    score = 0.70  # Baseline reasonable text
    reasons = []

    words = response_text.split()
    word_count = len(words)

    # 1. Structural markdown checks (headings, bullet points)
    has_bullets = bool(re.search(r"^\s*[-*•]\s+", response_text, re.MULTILINE))
    has_headings = bool(re.search(r"^#{1,4}\s+", response_text, re.MULTILINE))
    has_bold = bool(re.search(r"\*\*[^*]+\*\*", response_text))

    if task_mode == "classification":
        # Check for valid JSON block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        candidate_json = json_match.group(1) if json_match else response_text.strip()
        try:
            parsed = json.loads(candidate_json)
            if isinstance(parsed, dict) and "primary_sentiment" in parsed:
                score = 0.98
                reasons.append("Perfect JSON schema compliance.")
            else:
                score = 0.80
                reasons.append("Valid JSON but missing expected taxonomy keys.")
        except json.JSONDecodeError:
            score = 0.40
            reasons.append("Non-JSON output or syntax error in classification mode.")

    elif task_mode == "summarization":
        if has_headings or "TL;DR" in response_text:
            score += 0.15
            reasons.append("Executive structure and headers present.")
        if has_bullets:
            score += 0.10
            reasons.append("Key takeaway bullets present.")
        if word_count < 25:
            score -= 0.20
            reasons.append("Summary is excessively terse.")
        elif word_count > 350:
            score -= 0.10
            reasons.append("Summary may exceed ideal executive brevity.")
        else:
            reasons.append("Balanced word length.")

    else:  # Question Answering
        if has_headings:
            score += 0.10
            reasons.append("Clear conceptual headings.")
        if has_bullets:
            score += 0.10
            reasons.append("Structured analytical bullet points.")
        if has_bold:
            score += 0.05
            reasons.append("Effective emphasis on key terminology.")
        if word_count < 20:
            score -= 0.25
            reasons.append("Answer lacks conceptual depth.")
        elif word_count > 600:
            score -= 0.05
            reasons.append("Answer may be overly verbose.")

    # Repetition penalty
    unique_words = len(set(tokenize_meaningful_words(response_text)))
    if word_count > 40:
        lexical_diversity = unique_words / max(1, len(tokenize_meaningful_words(response_text)))
        if lexical_diversity < 0.40:
            score -= 0.20
            reasons.append("Low lexical diversity (repetitive phrasing).")

    score = min(1.0, max(0.1, round(score, 2)))

    if score >= 0.85:
        rating = "High"
    elif score >= 0.65:
        rating = "Good"
    elif score >= 0.45:
        rating = "Moderate"
    else:
        rating = "Low"

    return {
        "score": score,
        "rating": rating,
        "details": "; ".join(reasons) if reasons else "Standard structural formatting."
    }


# ==============================================================================
# 3. COMPOSITE EVALUATION RUNNER
# ==============================================================================

def evaluate_response(
    input_text: str,
    response_text: str,
    latency: float,
    task_mode: str = "qa",
    model: str = "unknown",
    prompt_type: str = "custom"
) -> Dict[str, Any]:
    """
    Computes a comprehensive evaluation dictionary for a given LLM output.
    """
    relevance = compute_relevance_score(input_text, response_text, task_mode)
    consistency = compute_consistency_score(response_text, task_mode)

    words = response_text.split()
    word_count = len(words)
    char_count = len(response_text)

    # Composite index: 45% Relevance, 40% Consistency, 15% Latency efficiency
    # Assume 1.0s is optimal, penalizing latencies > 5s
    latency_efficiency = max(0.2, min(1.0, 1.0 - (latency / 10.0)))
    overall_score = round(
        (relevance["score"] * 0.45) +
        (consistency["score"] * 0.40) +
        (latency_efficiency * 0.15),
        2
    )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task_mode": task_mode,
        "prompt_type": prompt_type,
        "model": model,
        "latency_sec": round(latency, 3),
        "word_count": word_count,
        "char_count": char_count,
        "relevance_score": relevance["score"],
        "relevance_rating": relevance["rating"],
        "relevance_details": relevance["details"],
        "consistency_score": consistency["score"],
        "consistency_rating": consistency["rating"],
        "consistency_details": consistency["details"],
        "overall_score": overall_score
    }


# ==============================================================================
# 4. A/B COMPARISON ENGINE
# ==============================================================================

def compare_evaluations(basic_eval: Dict[str, Any], improved_eval: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes delta metrics and generates an analytical verdict comparing
    Basic Prompt output vs. Improved Prompt output.
    """
    latency_delta = round(improved_eval["latency_sec"] - basic_eval["latency_sec"], 3)
    word_delta = improved_eval["word_count"] - basic_eval["word_count"]
    relevance_delta = round(improved_eval["relevance_score"] - basic_eval["relevance_score"], 2)
    consistency_delta = round(improved_eval["consistency_score"] - basic_eval["consistency_score"], 2)
    overall_delta = round(improved_eval["overall_score"] - basic_eval["overall_score"], 2)

    if overall_delta > 0:
        verdict = (
            f"🚀 **Improved Prompt Outperformed by +{int(overall_delta * 100)}% overall score!** "
            f"It demonstrated superior structure (+{int(consistency_delta * 100)}% consistency) "
            f"and enriched conceptual depth (+{word_delta} words)."
        )
    elif overall_delta == 0:
        verdict = "⚖️ **Both prompts performed comparably** on automated heuristics."
    else:
        verdict = (
            f"⚡ **Basic Prompt was faster** by {abs(latency_delta)}s with simpler structure, "
            "though the improved prompt may offer greater specificity."
        )

    return {
        "latency_delta_sec": latency_delta,
        "word_count_delta": word_delta,
        "relevance_delta": relevance_delta,
        "consistency_delta": consistency_delta,
        "overall_delta": overall_delta,
        "verdict": verdict
    }


# ==============================================================================
# 5. EVALUATION LOGGING & DATAFRAME REPOSITORY
# ==============================================================================

class EvaluationRepository:
    """In-memory audit log for evaluations during the Streamlit session."""

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def log(self, eval_record: Dict[str, Any]) -> None:
        self.records.append(eval_record)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.records:
            return pd.DataFrame(columns=[
                "timestamp", "task_mode", "prompt_type", "model",
                "latency_sec", "word_count", "relevance_score",
                "consistency_score", "overall_score"
            ])
        return pd.DataFrame(self.records)

    def get_summary_stats(self) -> Dict[str, Any]:
        df = self.to_dataframe()
        if df.empty:
            return {
                "total_runs": 0,
                "avg_latency": 0.0,
                "avg_relevance": 0.0,
                "avg_consistency": 0.0,
                "avg_overall": 0.0
            }
        return {
            "total_runs": len(df),
            "avg_latency": round(df["latency_sec"].mean(), 2),
            "avg_relevance": round(df["relevance_score"].mean(), 2),
            "avg_consistency": round(df["consistency_score"].mean(), 2),
            "avg_overall": round(df["overall_score"].mean(), 2)
        }
