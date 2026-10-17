"""
SYRA AI - FAQ Service
Module: backend/services/faq_service.py

Loads, parses, and searches the FAQ knowledge base for both
display and context-grounded retrieval.
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd


_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faq_dataset.csv")


class FAQService:
    def __init__(self, csv_path: str = _CSV_PATH):
        self.csv_path = csv_path
        self._df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        if os.path.exists(self.csv_path):
            self._df = pd.read_csv(self.csv_path)
        else:
            self._df = pd.DataFrame(columns=["id", "category", "question", "answer", "keywords"])

    def get_all(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._df is None or self._df.empty:
            return []

        filtered = self._df.copy()

        if category and category.lower() != "all":
            filtered = filtered[filtered["category"].str.lower() == category.lower()]

        if search and search.strip():
            term = search.strip().lower()
            mask = (
                filtered["question"].str.lower().str.contains(term, na=False) |
                filtered["answer"].str.lower().str.contains(term, na=False) |
                filtered["keywords"].str.lower().str.contains(term, na=False)
            )
            filtered = filtered[mask]

        return filtered.to_dict(orient="records")

    def find_relevant_context(self, query: str, top_k: int = 1) -> Optional[str]:
        """Find the best matching FAQ answer to ground the prompt context."""
        if self._df is None or self._df.empty:
            return None

        q_terms = set(query.lower().split())
        best_match = None
        best_overlap = 0

        for _, row in self._df.iterrows():
            faq_terms = set(str(row["question"]).lower().split() + str(row["keywords"]).lower().split(","))
            faq_terms = {t.strip() for t in faq_terms}
            overlap = len(q_terms.intersection(faq_terms))
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = f"Question: {row['question']}\nVerified Answer: {row['answer']}"

        return best_match if best_overlap >= 1 else None


# Global service instance
faq_service = FAQService()
