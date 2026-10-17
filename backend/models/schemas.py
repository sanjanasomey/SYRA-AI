"""
SYRA AI - Pydantic Request / Response Schemas
Module: backend/models/schemas.py

Typed models for all API request and response payloads.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.models.enums import TaskMode, Provider, PromptType


# ==============================================================================
# CHAT
# ==============================================================================

class ChatRequest(BaseModel):
    """Payload for /api/chat endpoint."""
    session_id: str = Field(..., description="Client session UUID")
    message: str = Field(..., min_length=1, description="User message text")
    task_mode: TaskMode = Field(default=TaskMode.QA)
    provider: Provider = Field(default=Provider.GEMINI)
    model: Optional[str] = Field(default=None, description="Model override")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=64, le=8192)
    use_faq_grounding: bool = Field(default=False)
    prompt_type: PromptType = Field(default=PromptType.IMPROVED)


class EvaluationResult(BaseModel):
    """Metrics computed for a single LLM response."""
    relevance_score: float
    relevance_rating: str
    relevance_details: str
    consistency_score: float
    consistency_rating: str
    consistency_details: str
    overall_score: float
    latency_sec: float
    word_count: int
    char_count: int


class ChatResponse(BaseModel):
    """Payload returned from /api/chat."""
    session_id: str
    response_text: str
    model: str
    provider: str
    is_demo: bool = False
    error: Optional[str] = None
    evaluation: Optional[EvaluationResult] = None


# ==============================================================================
# PROMPT COMPARISON (A/B LAB)
# ==============================================================================

class CompareRequest(BaseModel):
    """Payload for /api/compare endpoint."""
    session_id: str
    input_text: str = Field(..., min_length=1)
    task_mode: TaskMode = Field(default=TaskMode.QA)
    basic_template: str = Field(default="qa_basic")
    improved_template: str = Field(default="qa_improved")
    provider: Provider = Field(default=Provider.GEMINI)
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=64, le=8192)


class SinglePromptResult(BaseModel):
    """Result for one side of an A/B comparison."""
    rendered_prompt: str
    response_text: str
    model: str
    provider: str
    is_demo: bool = False
    evaluation: EvaluationResult


class CompareResponse(BaseModel):
    """Payload returned from /api/compare."""
    basic: SinglePromptResult
    improved: SinglePromptResult
    delta: Dict[str, Any]


# ==============================================================================
# EVALUATION / ANALYTICS
# ==============================================================================

class EvalHistoryResponse(BaseModel):
    """Payload returned from /api/evaluations."""
    session_id: str
    total_runs: int
    records: List[Dict[str, Any]]
    summary: Dict[str, Any]


# ==============================================================================
# FAQ
# ==============================================================================

class FAQItem(BaseModel):
    """Single FAQ entry."""
    id: int
    category: str
    question: str
    answer: str
    keywords: str


class FAQResponse(BaseModel):
    """Payload returned from /api/faq."""
    total: int
    items: List[FAQItem]


# ==============================================================================
# STATUS & SETTINGS
# ==============================================================================

class ProviderStatus(BaseModel):
    """Status of a single LLM provider."""
    name: str
    default_model: str
    models: List[str]
    configured: bool
    masked_key: str
    env_var: str


class ProvidersResponse(BaseModel):
    """Payload returned from /api/providers."""
    providers: Dict[str, ProviderStatus]
    default_provider: str


class StatusResponse(BaseModel):
    """Payload returned from /api/status."""
    app_name: str = "SYRA AI"
    version: str
    tagline: str = "Think clearly. Prompt brilliantly."
    providers: Dict[str, ProviderStatus]
    active_sessions: int
