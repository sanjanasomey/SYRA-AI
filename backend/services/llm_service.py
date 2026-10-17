"""
SYRA AI - LLM Service Layer
Module: backend/services/llm_service.py

Handles API connections to LLM providers (Google Gemini and OpenAI)
using environment variables, secure key management from settings,
latency instrumentation, and graceful fallback for simulation/demo environments.
NOTE: Runtime api_key_override is strictly omitted for security.
"""

import time
from typing import Dict, Any, Optional
from backend.core.config import settings
from backend.core.security import sanitize_error_message, mask_key


# ==============================================================================
# PROVIDER CONFIGURATION & CONSTANTS
# ==============================================================================

SUPPORTED_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-flash-lite-latest",
        "models": [
            "gemini-flash-lite-latest",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
            "gemini-flash-latest"
        ],
        "env_var": "GEMINI_API_KEY"
    },
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "env_var": "OPENAI_API_KEY"
    }
}


def get_api_key(provider: str = "gemini") -> Optional[str]:
    """Retrieve API key strictly from environment configuration."""
    provider = provider.lower()
    if provider == "gemini":
        return settings.gemini_api_key
    elif provider == "openai":
        return settings.openai_api_key
    return None


def check_api_status() -> Dict[str, Any]:
    """Check API configuration status for all supported providers."""
    gemini_key = get_api_key("gemini")
    openai_key = get_api_key("openai")

    return {
        "gemini": {
            "configured": bool(gemini_key and len(gemini_key) > 8),
            "masked_key": mask_key(gemini_key),
            "env_var": "GEMINI_API_KEY"
        },
        "openai": {
            "configured": bool(openai_key and len(openai_key) > 8),
            "masked_key": mask_key(openai_key),
            "env_var": "OPENAI_API_KEY"
        }
    }


# ==============================================================================
# LLM INFERENCE EXECUTOR
# ==============================================================================

def generate_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: str = "gemini",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Executes LLM text generation with timing, error handling, and demo fallback.

    Returns:
        dict with keys:
            - text (str): Output text
            - latency (float): Response latency in seconds
            - model (str): Model name used
            - provider (str): Provider name
            - is_mock (bool): True if simulation fallback was used
            - error (str or None): Error message if an issue occurred
    """
    provider = provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        provider = "gemini"

    provider_info = SUPPORTED_PROVIDERS[provider]
    model_name = model or provider_info["default_model"]
    api_key = get_api_key(provider)

    start_time = time.perf_counter()

    # --------------------------------------------------------------------------
    # DEMO / SIMULATION FALLBACK (When no API key is configured)
    # --------------------------------------------------------------------------
    if not api_key:
        time.sleep(0.4)  # Simulate realistic network latency
        elapsed = round(time.perf_counter() - start_time, 3)

        simulated_text = _generate_simulated_response(prompt, system_prompt)
        return {
            "text": simulated_text,
            "latency": elapsed,
            "model": f"{model_name} (Simulation)",
            "provider": f"{provider_info['name']} [Demo Mode]",
            "is_mock": True,
            "error": None
        }

    # --------------------------------------------------------------------------
    # GOOGLE GEMINI EXECUTION (google-genai SDK)
    # --------------------------------------------------------------------------
    if provider == "gemini":
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_prompt if system_prompt else None
            )

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
            except Exception as first_err:
                err_str = str(first_err)
                if ("503" in err_str or "404" in err_str or "UNAVAILABLE" in err_str) and model_name != "gemini-flash-lite-latest":
                    model_name = "gemini-flash-lite-latest"
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )
                else:
                    raise first_err

            elapsed = round(time.perf_counter() - start_time, 3)
            response_text = response.text or ""

            return {
                "text": response_text,
                "latency": elapsed,
                "model": model_name,
                "provider": "Google Gemini",
                "is_mock": False,
                "error": None
            }

        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 3)
            error_msg = sanitize_error_message(str(e))
            if "Authentication Failed" in error_msg:
                simulated_text = _generate_simulated_response(prompt, system_prompt)
                return {
                    "text": simulated_text,
                    "latency": elapsed,
                    "model": f"{model_name} (Simulation)",
                    "provider": "Google Gemini [Demo Mode]",
                    "is_mock": True,
                    "error": "API Key Authentication Failed: Served demo mode simulation."
                }
            return {
                "text": f"⚠️ **API Request Failed**: {error_msg}\n\n*Please verify your `GEMINI_API_KEY` in `.env` or check API quota on Google AI Studio.*",
                "latency": elapsed,
                "model": model_name,
                "provider": "Google Gemini",
                "is_mock": False,
                "error": error_msg
            }

    # --------------------------------------------------------------------------
    # OPENAI EXECUTION (openai SDK)
    # --------------------------------------------------------------------------
    elif provider == "openai":
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            elapsed = round(time.perf_counter() - start_time, 3)
            response_text = response.choices[0].message.content or ""

            return {
                "text": response_text,
                "latency": elapsed,
                "model": model_name,
                "provider": "OpenAI",
                "is_mock": False,
                "error": None
            }

        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 3)
            error_msg = sanitize_error_message(str(e))
            if "Authentication Failed" in error_msg:
                simulated_text = _generate_simulated_response(prompt, system_prompt)
                return {
                    "text": simulated_text,
                    "latency": elapsed,
                    "model": f"{model_name} (Simulation)",
                    "provider": "OpenAI [Demo Mode]",
                    "is_mock": True,
                    "error": "API Key Authentication Failed: Served demo mode simulation."
                }
            return {
                "text": f"⚠️ **API Request Failed**: {error_msg}\n\n*Please verify your `OPENAI_API_KEY` in `.env` or check OpenAI billing.*",
                "latency": elapsed,
                "model": model_name,
                "provider": "OpenAI",
                "is_mock": False,
                "error": error_msg
            }

    return {
        "text": "Unsupported LLM Provider specified.",
        "latency": 0.0,
        "model": "unknown",
        "provider": provider,
        "is_mock": False,
        "error": "Unsupported provider"
    }


# ==============================================================================
# HELPER FUNCTIONS & SIMULATION
# ==============================================================================

def _generate_simulated_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Generates an intelligent simulated response matching the requested prompt structure
    when no API key is supplied, allowing seamless offline evaluation & testing.
    """
    p_lower = prompt.lower()

    if "json" in p_lower or "primary_sentiment" in p_lower:
        return (
            "```json\n"
            "{\n"
            '  "primary_sentiment": "Negative",\n'
            '  "confidence_score": 0.94,\n'
            '  "domain": "Product Review",\n'
            '  "key_triggers": ["hallucinated", "completely inaccurate", "disappointing"],\n'
            '  "rationale": "The user expressed severe dissatisfaction with model accuracy despite acknowledging fast latency."\n'
            "}\n"
            "```\n\n"
            "> ℹ️ *Running in SYRA Demo Mode (No API key found in `.env`). Add your `GEMINI_API_KEY` to run live queries.*"
        )

    if "executive tl;dr" in p_lower or "key findings" in p_lower:
        return (
            "### Executive TL;DR\n"
            "Autonomous AI agents are transitioning generative models from passive text completion to proactive cognitive controllers. "
            "However, enterprise adoption requires solving stochastic degradation and prompt-injection vulnerabilities through deterministic state-machine guardrails.\n\n"
            "### Key Findings / Core Arguments\n"
            "- **Cognitive Control Architecture**: Modern agents combine LLM reasoning with episodic memory, vector retrieval, and external API tool execution.\n"
            "- **Production Bottlenecks**: Recursive loops amplify compounding errors, while multi-turn execution introduces latency and security vulnerabilities.\n"
            "- **Defensive Engineering**: Robust implementations rely on sandboxed runtime execution, state-machine guardrails, and automated telemetry evaluation.\n\n"
            "### Target Audience\n"
            "AI System Architects, Machine Learning Engineers, and Enterprise Software Leaders.\n\n"
            "> ℹ️ *Running in SYRA Demo Mode (No API key found in `.env`). Add your `GEMINI_API_KEY` to run live queries.*"
        )

    return (
        "### Core Concept\n"
        "Self-attention dynamically calculates relational weights between every pair of tokens in an input sequence, "
        "allowing neural networks to capture long-range contextual relationships directly without sequential step-by-step processing.\n\n"
        "### Detailed Breakdown\n"
        "- **Query, Key, and Value Projections**: Input embeddings are linearly projected into three matrices ($Q, K, V$).\n"
        "- **Dot-Product Attention**: Attention scores are computed via $\\text{Softmax}(\\frac{QK^T}{\\sqrt{d_k}})V$.\n"
        "- **Parallel Computation**: Unlike RNNs which suffer from $O(n)$ sequential bottlenecks and vanishing gradients, self-attention processes the entire sequence in $O(1)$ sequential operations.\n\n"
        "### Practical Application\n"
        "Powering transformer models such as Gemini and GPT for real-time document comprehension and code generation.\n\n"
        "### Common Pitfalls / Trade-offs\n"
        "Standard full self-attention scales quadratically $O(n^2)$ with sequence length, requiring high GPU memory for long contexts.\n\n"
        "> ℹ️ *Running in SYRA Demo Mode (No API key found in `.env`). Add your `GEMINI_API_KEY` to run live queries.*"
    )
