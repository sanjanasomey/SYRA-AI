"""
SYRA AI - Prompt Comparison Router
Module: backend/routers/comparison.py

Executes side-by-side A/B evaluation of Basic vs Improved prompts.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    CompareRequest, CompareResponse, SinglePromptResult, EvaluationResult
)
from backend.services.prompts import render_prompt, get_system_prompt
from backend.services.llm_service import generate_response
from backend.services.evaluation import evaluate_response, compare_evaluations, eval_repo

router = APIRouter(prefix="/api", tags=["Prompt Comparison"])


@router.post("/compare", response_model=CompareResponse)
async def compare_prompts(request: CompareRequest):
    """
    Run A/B inference comparing a basic prompt template against an improved one.
    """
    try:
        input_text = request.input_text.strip()
        if not input_text:
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")

        task_mode = request.task_mode.value
        system_prompt = get_system_prompt(task_mode)

        # 1. Render Basic Prompt
        arg_name = "text" if task_mode in ["summarization", "classification"] else "question"
        try:
            rendered_basic = render_prompt(request.basic_template, **{arg_name: input_text})
        except Exception:
            rendered_basic = input_text

        # 2. Render Improved Prompt
        try:
            rendered_improved = render_prompt(request.improved_template, **{arg_name: input_text})
        except Exception:
            rendered_improved = input_text

        # 3. Execute Basic Generation
        llm_basic = generate_response(
            prompt=rendered_basic,
            system_prompt=system_prompt,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        eval_basic = evaluate_response(
            input_text=input_text,
            response_text=llm_basic.get("text", ""),
            latency=llm_basic.get("latency", 0.0),
            task_mode=task_mode,
            model=llm_basic.get("model", "unknown"),
            prompt_type=f"ab_{request.basic_template}"
        )
        eval_repo.log(request.session_id, eval_basic)

        # 4. Execute Improved Generation
        llm_improved = generate_response(
            prompt=rendered_improved,
            system_prompt=system_prompt,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        eval_improved = evaluate_response(
            input_text=input_text,
            response_text=llm_improved.get("text", ""),
            latency=llm_improved.get("latency", 0.0),
            task_mode=task_mode,
            model=llm_improved.get("model", "unknown"),
            prompt_type=f"ab_{request.improved_template}"
        )
        eval_repo.log(request.session_id, eval_improved)

        # 5. Compute Deltas & Verdict
        delta = compare_evaluations(eval_basic, eval_improved)

        res_basic = SinglePromptResult(
            rendered_prompt=rendered_basic,
            response_text=llm_basic.get("text", ""),
            model=llm_basic.get("model", "unknown"),
            provider=llm_basic.get("provider", request.provider.value),
            is_demo=llm_basic.get("is_mock", False),
            evaluation=EvaluationResult(
                relevance_score=eval_basic["relevance_score"],
                relevance_rating=eval_basic["relevance_rating"],
                relevance_details=eval_basic["relevance_details"],
                consistency_score=eval_basic["consistency_score"],
                consistency_rating=eval_basic["consistency_rating"],
                consistency_details=eval_basic["consistency_details"],
                overall_score=eval_basic["overall_score"],
                latency_sec=eval_basic["latency_sec"],
                word_count=eval_basic["word_count"],
                char_count=eval_basic["char_count"]
            )
        )

        res_improved = SinglePromptResult(
            rendered_prompt=rendered_improved,
            response_text=llm_improved.get("text", ""),
            model=llm_improved.get("model", "unknown"),
            provider=llm_improved.get("provider", request.provider.value),
            is_demo=llm_improved.get("is_mock", False),
            evaluation=EvaluationResult(
                relevance_score=eval_improved["relevance_score"],
                relevance_rating=eval_improved["relevance_rating"],
                relevance_details=eval_improved["relevance_details"],
                consistency_score=eval_improved["consistency_score"],
                consistency_rating=eval_improved["consistency_rating"],
                consistency_details=eval_improved["consistency_details"],
                overall_score=eval_improved["overall_score"],
                latency_sec=eval_improved["latency_sec"],
                word_count=eval_improved["word_count"],
                char_count=eval_improved["char_count"]
            )
        )

        return CompareResponse(
            basic=res_basic,
            improved=res_improved,
            delta=delta
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)[:200]}")
