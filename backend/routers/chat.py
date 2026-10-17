"""
SYRA AI - Chat Router
Module: backend/routers/chat.py

Handles interactive conversation generation, prompt template interpolation,
context grounding, LLM calling, automated response evaluation, and logging.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse, EvaluationResult
from backend.models.enums import TaskMode, PromptType
from backend.services.prompts import render_prompt, get_system_prompt
from backend.services.llm_service import generate_response
from backend.services.evaluation import evaluate_response, eval_repo
from backend.services.faq_service import faq_service

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Execute chat inference with prompt engineering, evaluation, and session tracking.
    """
    try:
        user_msg = request.message.strip()
        if not user_msg:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        task_mode = request.task_mode.value
        system_prompt = get_system_prompt(task_mode)

        # 1. Determine prompt template and render
        final_prompt = user_msg
        prompt_type_str = request.prompt_type.value

        if task_mode == "qa":
            if request.use_faq_grounding:
                grounding_context = faq_service.find_relevant_context(user_msg)
                if grounding_context:
                    final_prompt = render_prompt(
                        "qa_context_grounded",
                        question=user_msg,
                        context=grounding_context
                    )
                    prompt_type_str = "context_grounded"
                else:
                    final_prompt = render_prompt("qa_improved", question=user_msg)
            elif request.prompt_type == PromptType.BASIC:
                final_prompt = render_prompt("qa_basic", question=user_msg)
            else:
                final_prompt = render_prompt("qa_improved", question=user_msg)

        elif task_mode == "summarization":
            if request.prompt_type == PromptType.BULLET_POINTS:
                final_prompt = render_prompt("summarize_bullet_points", text=user_msg)
            elif request.prompt_type == PromptType.BASIC:
                final_prompt = render_prompt("summarize_basic", text=user_msg)
            else:
                final_prompt = render_prompt("summarize_improved", text=user_msg)

        elif task_mode == "classification":
            if request.prompt_type == PromptType.BASIC:
                final_prompt = render_prompt("classify_basic", text=user_msg)
            else:
                final_prompt = render_prompt("classify_improved", text=user_msg)

        # 2. Call LLM Service
        llm_out = generate_response(
            prompt=final_prompt,
            system_prompt=system_prompt,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        response_text = llm_out.get("text", "")
        latency = llm_out.get("latency", 0.0)
        is_demo = llm_out.get("is_mock", False)
        err = llm_out.get("error")

        # 3. Compute Evaluation Metrics
        eval_dict = evaluate_response(
            input_text=user_msg,
            response_text=response_text,
            latency=latency,
            task_mode=task_mode,
            model=llm_out.get("model", "unknown"),
            prompt_type=prompt_type_str
        )

        # 4. Log evaluation into session repository
        eval_repo.log(request.session_id, eval_dict)

        eval_res = EvaluationResult(
            relevance_score=eval_dict["relevance_score"],
            relevance_rating=eval_dict["relevance_rating"],
            relevance_details=eval_dict["relevance_details"],
            consistency_score=eval_dict["consistency_score"],
            consistency_rating=eval_dict["consistency_rating"],
            consistency_details=eval_dict["consistency_details"],
            overall_score=eval_dict["overall_score"],
            latency_sec=eval_dict["latency_sec"],
            word_count=eval_dict["word_count"],
            char_count=eval_dict["char_count"]
        )

        return ChatResponse(
            session_id=request.session_id,
            response_text=response_text,
            model=llm_out.get("model", "unknown"),
            provider=llm_out.get("provider", request.provider.value),
            is_demo=is_demo,
            error=err,
            evaluation=eval_res
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)[:200]}")
