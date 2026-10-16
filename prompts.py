"""
PromptLab AI - Reusable Prompt Engineering Templates & Catalogs
Module: prompts.py

This module contains standardized, modular prompt templates applying
classical and modern prompt engineering methodologies:
- Role & Persona Framing
- Delimiter-based Input Isolation (Defensive Prompting)
- Chain-of-Thought (CoT) and Step-by-Step Reasoning
- Structured Output Formatting (JSON / Markdown Tables)
- Context Grounding & Guardrails against Hallucinations
"""

from typing import Dict, Any, List


# ==============================================================================
# 1. SYSTEM PROMPTS BY TASK MODE
# ==============================================================================

SYSTEM_PROMPTS = {
    "qa": (
        "You are PromptLab AI, an expert NLP and AI research assistant. "
        "You provide accurate, well-structured, and technically rigorous explanations. "
        "Ground your answers in fundamental computational linguistics and modern deep learning. "
        "Use clear markdown headings, bullet points, and practical examples where helpful."
    ),
    "summarization": (
        "You are an expert technical editor and content synthesizer. "
        "Your task is to analyze documents and generate crisp, high-density summaries "
        "that capture core thesis statements, methodology, empirical findings, and actionable conclusions "
        "without losing nuance or introducing outside speculation."
    ),
    "classification": (
        "You are an automated text classification engine. "
        "Analyze the provided text objectively according to the specified taxonomy. "
        "Always adhere strictly to the requested output schema and justify your classification with textual evidence."
    )
}


# ==============================================================================
# 2. TASK MODE TEMPLATES (BASIC vs. IMPROVED / ENGINEERED)
# ==============================================================================

TEMPLATES: Dict[str, Dict[str, str]] = {
    # --------------------------------------------------------------------------
    # Question Answering
    # --------------------------------------------------------------------------
    "qa_basic": (
        "Answer the following question:\n"
        "{question}"
    ),
    "qa_improved": (
        "### Context & Role\n"
        "You are an authoritative Senior AI Engineer and NLP Professor.\n\n"
        "### Task Instruction\n"
        "Answer the user's question clearly, precisely, and with conceptual depth.\n\n"
        "### Requirements & Formatting Guidelines\n"
        "1. **Core Concept**: Provide an intuitive 1-2 sentence definition.\n"
        "2. **Detailed Breakdown**: Explain the working mechanism using structured bullet points.\n"
        "3. **Practical Application or Real-world Example**: Show how this applies in real-world systems.\n"
        "4. **Pitfalls / Edge Cases**: Mention 1 common mistake, trade-off, or misconception.\n"
        "5. Tone: Objective, academic yet engaging, zero fluff.\n\n"
        "### User Question:\n"
        "\"\"\"\n{question}\n\"\"\""
    ),
    "qa_context_grounded": (
        "### System Instruction\n"
        "You are a factual AI assistant grounded strictly in the verified reference context below.\n\n"
        "### Grounding Context:\n"
        "\"\"\"\n{context}\n\"\"\"\n\n"
        "### Strict Rules:\n"
        "- Answer the question using ONLY the provided context above.\n"
        "- If the answer cannot be determined directly from the context, state: 'The provided documentation does not contain sufficient information to answer this question.'\n"
        "- Do NOT speculate or introduce external knowledge.\n\n"
        "### Question:\n"
        "{question}"
    ),

    # --------------------------------------------------------------------------
    # Text Summarization
    # --------------------------------------------------------------------------
    "summarize_basic": (
        "Summarize this text:\n"
        "{text}"
    ),
    "summarize_improved": (
        "### Role\n"
        "You are a Senior Technical Analyst preparing an executive intelligence brief.\n\n"
        "### Source Document:\n"
        "\"\"\"\n{text}\n\"\"\"\n\n"
        "### Synthesis Guidelines:\n"
        "Generate a structured summary following this exact schema:\n\n"
        "1. **Executive TL;DR**: A high-impact 2-sentence synthesis of the primary takeaway.\n"
        "2. **Key Findings / Core Arguments**:\n"
        "   - Bullet 1 (Key premise)\n"
        "   - Bullet 2 (Methodology / Mechanisms)\n"
        "   - Bullet 3 (Impact / Implications)\n"
        "3. **Target Audience**: Who benefits most from this information?\n"
        "4. **Reading Level**: Concise, professional, direct tone with no filler phrases."
    ),
    "summarize_bullet_points": (
        "Extract the top 3-5 most critical actionable takeaways from the following text in concise bullet points.\n"
        "Prefix each bullet point with a bold 2-3 word concept tag.\n\n"
        "Text:\n\"\"\"\n{text}\n\"\"\""
    ),

    # --------------------------------------------------------------------------
    # Text Classification
    # --------------------------------------------------------------------------
    "classify_basic": (
        "Classify the following text into sentiment (Positive, Negative, Neutral):\n"
        "{text}"
    ),
    "classify_improved": (
        "### Role\n"
        "You are a high-precision Natural Language Processing classification model.\n\n"
        "### Classification Taxonomy:\n"
        "- Label Options: [Positive, Negative, Neutral, Mixed]\n"
        "- Domain Options: [Technology, Customer Support, Product Review, General]\n\n"
        "### Input Text:\n"
        "\"\"\"\n{text}\n\"\"\"\n\n"
        "### Instructions:\n"
        "Analyze the linguistic tone, lexical polarity, and sentiment indicators.\n"
        "Respond in pure, valid JSON format matching this exact schema:\n"
        "```json\n"
        "{{\n"
        "  \"primary_sentiment\": \"Positive | Negative | Neutral | Mixed\",\n"
        "  \"confidence_score\": 0.95,\n"
        "  \"domain\": \"Technology | Customer Support | Product Review | General\",\n"
        "  \"key_triggers\": [\"token1\", \"token2\"],\n"
        "  \"rationale\": \"Brief 1-sentence analytical reasoning explaining the classification decision.\"\n"
        "}}\n"
        "```\n"
        "Do not include any intro, outro, or markdown text outside the JSON code block."
    )
}


# ==============================================================================
# 3. PRE-CONFIGURED A/B COMPARISON EXAMPLES
# ==============================================================================

COMPARISON_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "qa_attention",
        "title": "QA: Transformers & Self-Attention",
        "category": "Question Answering",
        "input_text": "How does self-attention work in Transformer models and why is it better than RNNs?",
        "basic_template": "qa_basic",
        "improved_template": "qa_improved",
        "engineering_highlights": [
            "Role & Persona Definition (Senior AI Engineer)",
            "Step-by-step Structured Headings (Definition, Mechanism, Application, Pitfalls)",
            "Delimiters (\"\"\") guarding input boundaries",
            "Clear constraints against conversational fluff"
        ]
    },
    {
        "id": "qa_hallucination",
        "title": "QA: Hallucination Mitigation & RAG",
        "category": "Question Answering",
        "input_text": "What causes LLM hallucinations and how does Retrieval-Augmented Generation solve them?",
        "basic_template": "qa_basic",
        "improved_template": "qa_improved",
        "engineering_highlights": [
            "Encourages technical rigor over vague generalizations",
            "Requires real-world system architecture context",
            "Enforces balanced trade-off analysis"
        ]
    },
    {
        "id": "summary_ai_agents",
        "title": "Summarization: Autonomous AI Agents",
        "category": "Text Summarization",
        "input_text": (
            "Autonomous AI agents represent a paradigm shift in generative AI, moving beyond single-turn "
            "text completion to multi-step reasoning, environment interaction, and tool utilization. Modern "
            "agents leverage LLMs as cognitive controllers that orchestrate planning, memory retrieval (both "
            "short-term episodic and long-term vector stores), and external API execution. While frameworks "
            "like LangChain, AutoGen, and CrewAI enable rapid development, enterprise deployment faces major hurdles: "
            "stochastic degradation across recursive loops, compounding error propagation, latency bottlenecks, "
            "and severe security vulnerabilities including indirect prompt injection. Industry best practices "
            "increasingly emphasize deterministic state-machine guardrails, sandboxed tool execution, and "
            "continuous telemetry evaluation."
        ),
        "basic_template": "summarize_basic",
        "improved_template": "summarize_improved",
        "engineering_highlights": [
            "Executive TL;DR constraint (strictly 2 sentences)",
            "Structured thematic bullet points (Premise, Mechanism, Impact)",
            "Explicit target audience identification",
            "Guards against hallucinated facts"
        ]
    },
    {
        "id": "classify_sentiment",
        "title": "Classification: Customer Sentiment & Nuance",
        "category": "Text Classification",
        "input_text": (
            "The model response time was blazing fast, but honestly the generated output was completely "
            "inaccurate and hallucinated several citations. Very disappointing for a paid tier."
        ),
        "basic_template": "classify_basic",
        "improved_template": "classify_improved",
        "engineering_highlights": [
            "Strict JSON schema enforcement for zero-parsing-failure pipelines",
            "Multi-dimensional taxonomy (sentiment + domain + confidence)",
            "Extracts explicit textual evidence tokens (key_triggers)",
            "Requires analytical rationale justification"
        ]
    }
]


# ==============================================================================
# 4. TEMPLATE RETRIEVAL & RENDERING HELPERS
# ==============================================================================

def get_template(template_key: str) -> str:
    """Retrieve raw prompt template string by key."""
    if template_key not in TEMPLATES:
        raise KeyError(f"Template '{template_key}' not found in TEMPLATES catalog.")
    return TEMPLATES[template_key]


def render_prompt(template_key: str, **kwargs: Any) -> str:
    """Safely interpolate variables into prompt template."""
    raw = get_template(template_key)
    try:
        return raw.format(**kwargs)
    except KeyError as e:
        missing_var = str(e)
        raise ValueError(f"Missing required prompt template variable: {missing_var}")


def get_system_prompt(task_mode: str) -> str:
    """Retrieve the corresponding system prompt for a task mode."""
    return SYSTEM_PROMPTS.get(task_mode.lower(), SYSTEM_PROMPTS["qa"])
