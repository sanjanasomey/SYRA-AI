"""
SYRA AI - FAQ Knowledge Base Router
Module: backend/routers/faq.py

Provides searching, category filtering, and item retrieval from the FAQ dataset.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.models.schemas import FAQResponse, FAQItem
from backend.services.faq_service import faq_service

router = APIRouter(prefix="/api", tags=["FAQ Knowledge Base"])


@router.get("/faq", response_model=FAQResponse)
async def get_faq(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Keyword search query")
):
    """
    Retrieve FAQ items with optional keyword search and category filtering.
    """
    items = faq_service.get_all(category=category, search=search)
    typed_items = [
        FAQItem(
            id=int(item["id"]),
            category=str(item["category"]),
            question=str(item["question"]),
            answer=str(item["answer"]),
            keywords=str(item["keywords"])
        )
        for item in items
    ]
    return FAQResponse(
        total=len(typed_items),
        items=typed_items
    )
