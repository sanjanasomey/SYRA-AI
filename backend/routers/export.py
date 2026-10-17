"""
SYRA AI - Data Export Router
Module: backend/routers/export.py

Exports session evaluation logs as downloadable CSV files.
"""

import io
from fastapi import APIRouter, Query, HTTPException, Response
from backend.services.evaluation import eval_repo

router = APIRouter(prefix="/api/export", tags=["Data Export"])


@router.get("/csv")
async def export_session_csv(session_id: str = Query(..., description="Client session UUID")):
    """
    Generate and stream a CSV file containing evaluation metrics for the given session.
    """
    df = eval_repo.to_dataframe(session_id=session_id)
    if df.empty:
        # Return an empty CSV with standard headers rather than erroring out
        headers = [
            "session_id", "timestamp", "task_mode", "prompt_type", "model",
            "latency_sec", "word_count", "relevance_score",
            "consistency_score", "overall_score"
        ]
        csv_content = ",".join(headers) + "\n"
    else:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

    filename = f"syra_telemetry_{session_id[:8]}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
