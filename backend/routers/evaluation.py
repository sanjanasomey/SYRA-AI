"""
SYRA AI - Evaluation Analytics Router
Module: backend/routers/evaluation.py

Provides session-scoped evaluation history and summary statistics.
"""

from fastapi import APIRouter, Query
from backend.models.schemas import EvalHistoryResponse
from backend.services.evaluation import eval_repo

router = APIRouter(prefix="/api", tags=["Evaluation & Analytics"])


@router.get("/evaluations", response_model=EvalHistoryResponse)
async def get_evaluations(session_id: str = Query(..., description="Client session UUID")):
    """
    Return all evaluation audit records and aggregated statistics for the requested session.
    """
    records = eval_repo.get_records(session_id)
    summary = eval_repo.get_summary_stats(session_id)

    return EvalHistoryResponse(
        session_id=session_id,
        total_runs=len(records),
        records=records,
        summary=summary
    )
