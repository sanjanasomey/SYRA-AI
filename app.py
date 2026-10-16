"""
SYRA AI — Smart Yield, Refined Answers
File: app.py

Think clearly. Prompt brilliantly.
A minimal, premium, pastel-pink aesthetic inspired by modern AI chatbot interfaces.
Design System:
- Canvas: #FFF7FB (Soft blush ambient mesh)
- Sidebar: #FCEEF5 (Tender pastel pink)
- Primary Pink: #E879A9
- Lavender Accent: #A78BFA
- Surfaces/Cards: #FFFFFF
- Main Text: #302536 (Deep plum-slate)
- Secondary Text: #887887 (Muted mauve)
- Borders: #F1DCE8 (Delicate rose-quartz)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

import pandas as pd
import altair as alt
import streamlit as st

# Local application modules
from prompts import (
    TEMPLATES,
    render_prompt,
    get_system_prompt,
    COMPARISON_PRESETS
)
from llm_service import (
    generate_response,
    check_api_status,
    SUPPORTED_PROVIDERS
)
from evaluation import (
    evaluate_response,
    compare_evaluations,
    EvaluationRepository
)


# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="SYRA AI — Smart Yield, Refined Answers",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# 2. SESSION STATE MANAGEMENT
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm **SYRA** — your **S**mart **Y**ield, **R**efined **A**nswers assistant. "
                "What would you like to explore today?\n\n"
                "I can help you with:\n\n"
                "1. **Question Answering**: Factual conceptual explanations of NLP, Transformers, and Prompt Engineering, with optional verified FAQ grounding.\n"
                "2. **Text Summarization**: Crisp executive intelligence briefs or actionable takeaway bullets tailored to your target length.\n"
                "3. **Text Classification**: Zero-shot sentiment and domain taxonomy adhering strictly to structured JSON schemas.\n\n"
                "You can also use the **Prompt Comparison Lab** tab to benchmark naive vs. engineered prompts side-by-side!"
            ),
            "eval": None,
            "task_mode": "System"
        }
    ]

if "eval_repo" not in st.session_state:
    st.session_state.eval_repo = EvaluationRepository()

if "prefill_chat" not in st.session_state:
    st.session_state.prefill_chat = None

if "active_task_mode" not in st.session_state:
    st.session_state.active_task_mode = "Question Answering"


# ==============================================================================
# 3. PASTEL-PINK & LAVENDER DESIGN SYSTEM (CUSTOM CSS)
# ==============================================================================

def get_pastel_pink_css() -> str:
    """Generate minimal, premium pastel-pink and lavender CSS design language."""
    bg_canvas = """
        radial-gradient(ellipse 95% 65% at 50% 95%, rgba(232, 121, 169, 0.14) 0%, rgba(167, 139, 250, 0.10) 40%, rgba(255, 247, 251, 0.95) 80%, #FFF7FB 100%), #FFF7FB
    """
    bg_card = "#FFFFFF"
    bg_card_translucent = "rgba(255, 255, 255, 0.92)"
    bg_sidebar = "#FCEEF5"
    primary_pink = "#E879A9"
    lavender_accent = "#A78BFA"
    text_main = "#302536"
    text_muted = "#887887"
    border_color = "#F1DCE8"
    border_hover = "#E879A9"
    shadow_card = "0 4px 20px -2px rgba(232, 121, 169, 0.08)"
    shadow_glow = "0 8px 30px rgba(232, 121, 169, 0.18)"

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Typography & Global Resets */
        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_main};
        }}

        /* Pastel-Pink Canvas Mesh */
        .stApp {{
            background: {bg_canvas} !important;
            background-attachment: fixed !important;
        }}

        /* Clean Header */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}

        /* Soft-Pink Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            border-right: 1px solid {border_color} !important;
            box-shadow: 2px 0 16px rgba(232, 121, 169, 0.04) !important;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }}

        /* Centered Hero Section (Sparkle + Title) */
        .figma-hero {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2.2rem 1rem 1.6rem 1rem;
            margin-bottom: 0.5rem;
        }}

        .figma-sparkle {{
            font-size: 28px;
            color: {primary_pink};
            margin-bottom: 12px;
            display: inline-block;
            filter: drop-shadow(0 2px 10px rgba(232, 121, 169, 0.4));
            animation: sparklePulse 3s ease-in-out infinite;
        }}

        @keyframes sparklePulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.95; }}
            50% {{ transform: scale(1.15); opacity: 1; filter: drop-shadow(0 4px 14px rgba(167, 139, 250, 0.5)); }}
        }}

        .figma-hero-title {{
            font-size: 2.3rem;
            font-weight: 700;
            letter-spacing: -0.035em;
            color: {text_main};
            margin: 0;
            line-height: 1.2;
        }}

        .figma-hero-subtitle {{
            font-size: 0.92rem;
            color: {text_muted};
            margin-top: 0.45rem;
            font-weight: 400;
        }}

        /* Pastel Feature Cards */
        .pastel-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 1.25rem 1.45rem;
            box-shadow: {shadow_card};
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            margin-bottom: 1rem;
        }}

        .pastel-card:hover {{
            border-color: {border_hover};
            box-shadow: {shadow_glow};
            transform: translateY(-1px);
        }}

        .pastel-card-highlight {{
            background: {bg_card};
            border: 1.5px solid {primary_pink};
            border-radius: 16px;
            padding: 1.25rem 1.45rem;
            box-shadow: 0 6px 24px rgba(232, 121, 169, 0.16);
            margin-bottom: 1rem;
            position: relative;
        }}

        /* Chat Message Wrapper (Figma "ME" & "OUR AI" Pattern) */
        .msg-container-user {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 1.4rem;
            animation: fadeIn 0.25s ease;
        }}

        .msg-container-ai {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 1.8rem;
            animation: fadeIn 0.25s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .msg-tag {{
            font-size: 0.70rem;
            font-weight: 700;
            color: {text_muted};
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 6px;
            margin-left: 6px;
        }}

        .msg-bubble-user {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 18px;
            padding: 0.85rem 1.35rem;
            font-size: 0.95rem;
            color: {text_main};
            box-shadow: 0 2px 10px rgba(232, 121, 169, 0.04);
            max-width: 82%;
            line-height: 1.5;
        }}

        .msg-bubble-ai {{
            background: {bg_card_translucent};
            backdrop-filter: blur(14px);
            border: 1px solid {border_color};
            border-radius: 20px;
            padding: 1.35rem 1.6rem;
            font-size: 0.95rem;
            color: {text_main};
            box-shadow: {shadow_card};
            width: 100%;
            line-height: 1.6;
        }}

        /* Suggestions Section */
        .suggestions-title {{
            font-size: 0.76rem;
            font-weight: 600;
            color: {text_muted};
            margin-bottom: 8px;
            margin-left: 4px;
        }}

        /* Floating Chat Composer */
        div[data-testid="stChatInput"] {{
            border-radius: 16px !important;
            border: 1.5px solid {border_color} !important;
            background: {bg_card_translucent} !important;
            backdrop-filter: blur(16px) !important;
            box-shadow: 0 8px 30px rgba(232, 121, 169, 0.08) !important;
            transition: all 0.2s ease !important;
            padding: 4px 6px !important;
        }}

        div[data-testid="stChatInput"]:focus-within {{
            border-color: {primary_pink} !important;
            box-shadow: 0 8px 35px rgba(232, 121, 169, 0.22) !important;
        }}

        /* Telemetry Badges */
        .telemetry-badge {{
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 500;
            margin-right: 6px;
            margin-top: 8px;
            font-family: 'JetBrains Mono', monospace;
        }}

        .badge-lat {{
            background: #FCEEF5;
            color: #C02674;
            border: 1px solid #F8D5E6;
        }}

        .badge-rel {{
            background: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
        }}

        .badge-cons {{
            background: #F5EEF9;
            color: #7C3AED;
            border: 1px solid #DDD6FE;
        }}

        /* Code/Prompt Box */
        .code-preview-box {{
            background: #FFFBFD;
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            line-height: 1.55;
            color: {text_main};
            white-space: pre-wrap;
            border-left: 3px solid {primary_pink};
        }}

        /* Navigation Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 1px solid {border_color};
            padding-bottom: 0px;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 9px 18px;
            border-radius: 8px 8px 0 0;
            font-weight: 500;
            font-size: 0.88rem;
            color: {text_muted};
            border: none;
            background: transparent;
            transition: all 0.15s ease;
        }}

        .stTabs [aria-selected="true"] {{
            color: {primary_pink} !important;
            border-bottom: 2px solid {primary_pink} !important;
            font-weight: 600;
        }}

        /* Buttons with Pastel Gradient */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 500;
            font-size: 0.86rem;
            padding: 0.5rem 1rem;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            border: 1px solid {border_color};
            background: {bg_card};
            color: {text_main};
        }}

        .stButton > button:hover {{
            border-color: {primary_pink};
            box-shadow: 0 4px 12px rgba(232, 121, 169, 0.15);
            color: {primary_pink};
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {primary_pink} 0%, {lavender_accent} 100%);
            color: #FFFFFF;
            border: none;
            font-weight: 600;
            box-shadow: 0 4px 14px rgba(232, 121, 169, 0.3);
        }}

        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 6px 20px rgba(232, 121, 169, 0.45);
            transform: translateY(-1px);
            color: #FFFFFF;
        }}
                      /* SYRA AI: Improve text contrast on light backgrounds */
        .stApp {{
            color: #33263A !important;
        }}

        /* Main headings */
        h1, h2, h3, h4 {{
            color: #33263A !important;
        }}

        /* Sidebar text */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {{
            color: #49384F;
        }}

        /* Main SYRA heading */
        .syra-title {{
            color: #33263A !important;
        }}

        /* Paragraphs and descriptions */
        .stMarkdown p {{
            color: #756579;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{
            color: #49384F !important;
        }}

        .stTabs [aria-selected="true"] {{
            color: #D94F91 !important;
        }}

        /* Input fields */
        .stTextInput input,
        .stTextArea textarea,
        .stChatInput textarea,
        .stSelectbox div[data-baseweb="select"] {{
            color: #33263A !important;
            background-color: #FFFFFF !important;
        }}

        /* Chat messages */
        [data-testid="stChatMessage"] {{
            color: #33263A !important;
        }}

        /* Keep primary button text white */
        .stButton > button[kind="primary"] {{
            color: #FFFFFF !important;
        }}
    </style>
    
    """

st.markdown(get_pastel_pink_css(), unsafe_allow_html=True)


# ==============================================================================
# 4. FAQ DATASET LOADER
# ==============================================================================

@st.cache_data
def load_faq_dataset() -> pd.DataFrame:
    """Load verified FAQ knowledge base from local CSV."""
    faq_path = os.path.join(os.path.dirname(__file__), "data", "faq_dataset.csv")
    if os.path.exists(faq_path):
        return pd.read_csv(faq_path)
    return pd.DataFrame(columns=["id", "category", "question", "answer", "keywords"])

faq_df = load_faq_dataset()


# ==============================================================================
# 5. SOFT-PINK SIDEBAR ORCHESTRATION & SETTINGS
# ==============================================================================

with st.sidebar:
    # Minimal Pastel Brand Header — SYRA AI
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
        <div style="width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg, #E879A9 0%, #A78BFA 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: bold;">
            ✦
        </div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; color: #302536;">SYRA <span style="color: #E879A9;">AI</span></div>
            <div style="font-size: 0.72rem; color: #887887;">Smart Yield, Refined Answers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #F1DCE8;'>", unsafe_allow_html=True)

    # Provider & Model Settings
    st.caption("LLM ORCHESTRATION")
    provider_option = st.selectbox(
        "Provider",
        options=["gemini", "openai"],
        format_func=lambda x: "Google Gemini" if x == "gemini" else "OpenAI",
        index=0,
        label_visibility="collapsed"
    )

    provider_info = SUPPORTED_PROVIDERS[provider_option]
    selected_model = st.selectbox(
        "Model",
        options=provider_info["models"],
        index=0,
        label_visibility="collapsed"
    )

    with st.expander("Parameters & Sampling", expanded=False):
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        max_tokens = st.slider("Max Output Tokens", min_value=128, max_value=2048, value=1024, step=64)

    # API Connection Status
    st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #F1DCE8;'>", unsafe_allow_html=True)
    st.caption("CONNECTION STATUS")

    api_override = st.text_input(
        "API Key Override",
        type="password",
        placeholder="Override .env key (optional)",
        label_visibility="collapsed"
    )

    status = check_api_status(
        override_gemini=api_override if provider_option == "gemini" else None,
        override_openai=api_override if provider_option == "openai" else None
    )

    active_status = status[provider_option]
    if active_status["configured"]:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.80rem; color: #059669; font-weight: 500; padding: 6px 10px; background: rgba(16, 185, 129, 0.08); border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#059669;"></span>
            Connected: <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem;">{active_status['masked_key']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.80rem; color: #D97706; font-weight: 500; padding: 6px 10px; background: rgba(245, 158, 11, 0.08); border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.2);">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#D97706;"></span>
            Demo Mode (Simulation Active)
        </div>
        """, unsafe_allow_html=True)

    # Session Reset Action
    st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #F1DCE8;'>", unsafe_allow_html=True)
    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation reset. Choose a task mode or suggestion to begin.",
                "eval": None,
                "task_mode": "System"
            }
        ]
        st.rerun()


# ==============================================================================
# 6. MAIN WORKSPACE TABS
# ==============================================================================

tab_chat, tab_compare, tab_analytics, tab_faq = st.tabs([
    "💬 Interactive Chatbot",
    "⚖️ Prompt Comparison Lab",
    "📊 Evaluation & Analytics",
    "📚 FAQ Knowledge Base"
])


# ==============================================================================
# TAB 1: INTERACTIVE CHATBOT (PASTEL-PINK AI HOMEPAGE)
# ==============================================================================

with tab_chat:
    # 1. Centered Hero Section (Sparkle + Title)
    st.markdown("""
    <div class="figma-hero">
        <div class="figma-sparkle">✦</div>
        <h1 class="figma-hero-title">Ask SYRA Anything</h1>
        <div class="figma-hero-subtitle">
            Think clearly. Prompt brilliantly. • SYRA AI Prompt Engineering Workspace
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Three Attractive Feature Cards (QA, Summarization, Classification)
    col_m1, col_m2, col_m3 = st.columns(3)
    modes_info = [
        ("Question Answering", "💡", "Factual conceptual reasoning with optional RAG FAQ grounding"),
        ("Text Summarization", "📝", "Executive intelligence briefs & key actionable takeaway bullets"),
        ("Text Classification", "🏷️", "Zero-shot sentiment & domain taxonomy with JSON schema")
    ]

    for col, (m_title, m_icon, m_desc) in zip([col_m1, col_m2, col_m3], modes_info):
        is_sel = (st.session_state.active_task_mode == m_title)
        card_class = "pastel-card-highlight" if is_sel else "pastel-card"
        with col:
            st.markdown(f"""
            <div class="{card_class}" style="padding: 14px 16px; min-height: 84px;">
                <div style="font-size: 0.94rem; font-weight: 700; color: {'#E879A9' if is_sel else '#302536'};">
                    {m_icon} {m_title}
                </div>
                <div style="font-size: 0.76rem; color: #887887; margin-top: 4px; line-height: 1.35;">
                    {m_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {m_title}", key=f"sel_{m_title}", use_container_width=True):
                st.session_state.active_task_mode = m_title
                st.rerun()

    active_mode = st.session_state.active_task_mode

    # Contextual controls for active mode
    grounding_text = ""
    summary_style = "Executive Intelligence Brief (Structured)"

    if active_mode == "Question Answering":
        c_gr1, c_gr2 = st.columns([1, 2])
        with c_gr1:
            use_faq_context = st.checkbox(
                "Ground response with FAQ Context (RAG)",
                value=False,
                help="Appends verified FAQ reference context to eliminate hallucinations."
            )
        with c_gr2:
            if use_faq_context and not faq_df.empty:
                selected_faq = st.selectbox(
                    "Verified Grounding Reference:",
                    options=faq_df["question"].tolist(),
                    index=0,
                    label_visibility="collapsed"
                )
                faq_row = faq_df[faq_df["question"] == selected_faq].iloc[0]
                grounding_text = f"FAQ Topic: {faq_row['question']}\nVerified Fact: {faq_row['answer']}"
                st.caption(f"📌 Grounding Context: *{selected_faq}*")

    elif active_mode == "Text Summarization":
        summary_style = st.selectbox(
            "Summarization Strategy:",
            options=["Executive Intelligence Brief (Structured)", "Key Actionable Takeaways (Bullets)"],
            index=0
        )

    elif active_mode == "Text Classification":
        st.markdown("""
        <div style="font-size: 0.80rem; color: #887887; margin-bottom: 8px;">
            Enforces strict JSON schema output: <code>{"primary_sentiment", "confidence_score", "domain", "key_triggers", "rationale"}</code>
        </div>
        """, unsafe_allow_html=True)

    # Active Prompt Template Expander
    with st.expander("🔍 View Active Prompt Engineering Architecture", expanded=False):
        if active_mode == "Question Answering":
            if 'use_faq_context' in locals() and use_faq_context:
                tmpl_text = TEMPLATES["qa_context_grounded"]
            else:
                tmpl_text = TEMPLATES["qa_improved"]
        elif active_mode == "Text Summarization":
            if summary_style.startswith("Executive"):
                tmpl_text = TEMPLATES["summarize_improved"]
            else:
                tmpl_text = TEMPLATES["summarize_bullet_points"]
        else:
            tmpl_text = TEMPLATES["classify_improved"]

        st.markdown(f'<div class="code-preview-box">{tmpl_text}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Render Conversation Messages
    # Keep Markdown rendering separate from raw HTML to avoid displaying HTML tags.
    for msg in st.session_state.messages:
        role = "user" if msg.get("role") == "user" else "assistant"
        with st.chat_message(role, avatar="user" if role == "user" else "assistant"):
            st.caption("YOU" if role == "user" else "SYRA AI")
            st.markdown(msg.get("content", ""))

            if role == "assistant" and msg.get("eval"):
                ev = msg["eval"]
                st.markdown(f"""
                <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #F1DCE8;">
                    <span class="telemetry-badge badge-lat">⏱️ {ev['latency_sec']}s</span>
                    <span class="telemetry-badge badge-rel">🎯 Relevance: {int(ev['relevance_score']*100)}% ({ev['relevance_rating']})</span>
                    <span class="telemetry-badge badge-cons">📐 Consistency: {int(ev['consistency_score']*100)}% ({ev['consistency_rating']})</span>
                    <span class="telemetry-badge badge-lat">📝 {ev['word_count']} words</span>
                    {'<span class="telemetry-badge" style="background:#FFFBEB; color:#D97706; border:1px solid #FDE68A;">ℹ️ Demo Simulation</span>' if ev.get('is_mock') else ''}
                </div>
                """, unsafe_allow_html=True)

    # 4. Suggestions Section (Interactive Quick Starters)
    st.markdown("""
    <div style="margin: 1.4rem 0 0.5rem 2px;">
        <div class="suggestions-title">Suggestions on what to ask SYRA</div>
    </div>
    """, unsafe_allow_html=True)

    c_sug1, c_sug2, c_sug3 = st.columns([1, 1, 1])
    with c_sug1:
        if st.button("What can I ask you to do?", use_container_width=True, key="sug_1"):
            st.session_state.prefill_chat = "What can I ask you to do?"
            st.rerun()
    with c_sug2:
        if st.button("How does self-attention work?", use_container_width=True, key="sug_2"):
            st.session_state.prefill_chat = "How does self-attention work in Transformers and why is it better than RNNs?"
            st.session_state.active_task_mode = "Question Answering"
            st.rerun()
    with c_sug3:
        if st.button("Summarize key challenges of AI agents", use_container_width=True, key="sug_3"):
            st.session_state.prefill_chat = "Summarize the key architectural challenges and security hurdles of autonomous AI agents."
            st.session_state.active_task_mode = "Text Summarization"
            st.rerun()

    # 5. Floating Message Composer
    default_input = ""
    if st.session_state.prefill_chat:
        default_input = st.session_state.prefill_chat
        st.session_state.prefill_chat = None

    user_prompt = st.chat_input(placeholder=f"Ask SYRA anything about {active_mode.lower()}...")
    prompt_to_process = user_prompt or (default_input if default_input else None)

    if prompt_to_process:
        # Append User Message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt_to_process,
            "eval": None,
            "task_mode": active_mode
        })

        # Assemble prompt according to task mode
        if active_mode == "Question Answering":
            sys_prompt = get_system_prompt("qa")
            if 'use_faq_context' in locals() and use_faq_context and grounding_text:
                final_prompt = render_prompt("qa_context_grounded", question=prompt_to_process, context=grounding_text)
            else:
                final_prompt = render_prompt("qa_improved", question=prompt_to_process)

        elif active_mode == "Text Summarization":
            sys_prompt = get_system_prompt("summarization")
            if summary_style.startswith("Executive"):
                final_prompt = render_prompt("summarize_improved", text=prompt_to_process)
            else:
                final_prompt = render_prompt("summarize_bullet_points", text=prompt_to_process)

        else:  # Text Classification
            sys_prompt = get_system_prompt("classification")
            final_prompt = render_prompt("classify_improved", text=prompt_to_process)

        # Generate response with clean spinner
        with st.spinner("SYRA AI is thinking..."):
            res = generate_response(
                prompt=final_prompt,
                system_prompt=sys_prompt,
                provider=provider_option,
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key_override=api_override
            )

            # Evaluate output
            eval_data = evaluate_response(
                input_text=prompt_to_process,
                response_text=res["text"],
                latency=res["latency"],
                task_mode=active_mode.lower(),
                model=res["model"],
                prompt_type="engineered"
            )
            eval_data["is_mock"] = res.get("is_mock", False)

            # Log to repository
            st.session_state.eval_repo.log(eval_data)

            # Save assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": res["text"],
                "eval": eval_data,
                "task_mode": active_mode
            })

        st.rerun()


# ==============================================================================
# TAB 2: PROMPT COMPARISON LAB (A/B TESTING)
# ==============================================================================

with tab_compare:
    st.markdown("""
    <div style="margin: 0.5rem 0 1.25rem 0;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0 0 4px 0; color: #302536;">Prompt Comparison Lab</h2>
        <p style="font-size: 0.85rem; color: #887887; margin: 0;">
            Benchmark a <b>Basic Naive Prompt</b> against an <b>Engineered Prompt</b> side-by-side using identical test input.
        </p>
    </div>
    """, unsafe_allow_html=True)

    preset_choice = st.selectbox(
        "Evaluation Scenario:",
        options=["Custom Query"] + [p["title"] for p in COMPARISON_PRESETS],
        index=1
    )

    if preset_choice != "Custom Query":
        preset_data = next(p for p in COMPARISON_PRESETS if p["title"] == preset_choice)
        test_input = st.text_area("Test Input Text / Query:", value=preset_data["input_text"], height=100)
        basic_key = preset_data["basic_template"]
        improved_key = preset_data["improved_template"]
        highlights = preset_data["engineering_highlights"]
    else:
        test_input = st.text_area(
            "Test Input Text / Query:",
            value="Explain what word embeddings are and why they are useful in NLP.",
            height=100
        )
        basic_key = "qa_basic"
        improved_key = "qa_improved"
        highlights = [
            "Role & Persona Definition",
            "Structured Headings & Markdown Formatting",
            "Delimiters guarding user input",
            "Length & tone constraints"
        ]

    # Inspection expander
    with st.expander("🔍 Inspect Underlying Prompt Architectures", expanded=False):
        c_code_a, c_code_b = st.columns(2)
        with c_code_a:
            st.caption("Basic Naive Template")
            st.code(TEMPLATES[basic_key], language="markdown")
        with c_code_b:
            st.caption("Engineered Template (Persona + Constraints)")
            st.code(TEMPLATES[improved_key], language="markdown")

    if st.button("⚡ Run Comparative Inference", type="primary", use_container_width=True):
        if not test_input.strip():
            st.warning("Please enter input text to benchmark.")
        else:
            var_name = "question" if "qa" in basic_key else "text"
            basic_prompt_rendered = render_prompt(basic_key, **{var_name: test_input})
            improved_prompt_rendered = render_prompt(improved_key, **{var_name: test_input})

            with st.spinner("Executing comparative LLM calls concurrently..."):
                res_basic = generate_response(
                    prompt=basic_prompt_rendered,
                    provider=provider_option,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key_override=api_override
                )

                res_improved = generate_response(
                    prompt=improved_prompt_rendered,
                    provider=provider_option,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key_override=api_override
                )

            eval_basic = evaluate_response(
                input_text=test_input,
                response_text=res_basic["text"],
                latency=res_basic["latency"],
                task_mode="comparison",
                model=selected_model,
                prompt_type="basic"
            )
            eval_improved = evaluate_response(
                input_text=test_input,
                response_text=res_improved["text"],
                latency=res_improved["latency"],
                task_mode="comparison",
                model=selected_model,
                prompt_type="improved"
            )

            st.session_state.eval_repo.log(eval_basic)
            st.session_state.eval_repo.log(eval_improved)

            comp_metrics = compare_evaluations(eval_basic, eval_improved)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(f"""
                <div class="pastel-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 0.95rem; color: #887887;">⚪ Basic Prompt</span>
                        <span style="font-size: 0.75rem; color: #887887;">Naive Baseline</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(res_basic["text"])
                st.markdown(f"""
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #F1DCE8; display: flex; flex-wrap: wrap; gap: 6px;">
                        <span class="telemetry-badge badge-lat">⏱️ {eval_basic['latency_sec']}s</span>
                        <span class="telemetry-badge badge-rel">🎯 {int(eval_basic['relevance_score']*100)}% Rel</span>
                        <span class="telemetry-badge badge-cons">📐 {int(eval_basic['consistency_score']*100)}% Cons</span>
                        <span class="telemetry-badge badge-lat">📝 {eval_basic['word_count']} words</span>
                        <span class="telemetry-badge" style="background: rgba(232,121,169,0.12); color: #E879A9; font-weight: 700;">Score: {eval_basic['overall_score']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class="pastel-card-highlight">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 0.95rem; color: #E879A9;">✦ Engineered Prompt</span>
                        <span style="font-size: 0.72rem; background: rgba(232,121,169,0.14); color: #E879A9; padding: 2px 8px; border-radius: 6px; font-weight: 600;">OPTIMIZED</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(res_improved["text"])
                st.markdown(f"""
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #F1DCE8; display: flex; flex-wrap: wrap; gap: 6px;">
                        <span class="telemetry-badge badge-lat">⏱️ {eval_improved['latency_sec']}s</span>
                        <span class="telemetry-badge badge-rel">🎯 {int(eval_improved['relevance_score']*100)}% Rel</span>
                        <span class="telemetry-badge badge-cons">📐 {int(eval_improved['consistency_score']*100)}% Cons</span>
                        <span class="telemetry-badge badge-lat">📝 {eval_improved['word_count']} words</span>
                        <span class="telemetry-badge" style="background: rgba(232,121,169,0.12); color: #E879A9; font-weight: 700;">Score: {eval_improved['overall_score']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.info(comp_metrics["verdict"])

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Latency Delta", f"{comp_metrics['latency_delta_sec']:+0.2f}s")
            col_m2.metric("Word Count Delta", f"{comp_metrics['word_count_delta']:+d}")
            col_m3.metric("Relevance Delta", f"{int(comp_metrics['relevance_delta']*100):+d}%")
            col_m4.metric("Consistency Delta", f"{int(comp_metrics['consistency_delta']*100):+d}%")

            st.markdown("<div style='margin-top: 1rem; font-size: 0.88rem; font-weight: 600; color: #302536;'>Applied Prompt Engineering Patterns:</div>", unsafe_allow_html=True)
            for h in highlights:
                st.markdown(f"- **{h}**")


# ==============================================================================
# TAB 3: EVALUATION & ANALYTICS DASHBOARD
# ==============================================================================

with tab_analytics:
    st.markdown("""
    <div style="margin: 0.5rem 0 1.25rem 0;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0 0 4px 0; color: #302536;">Evaluation Telemetry & Analytics</h2>
        <p style="font-size: 0.85rem; color: #887887; margin: 0;">
            Real-time quality metrics aggregated across all active inference runs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = st.session_state.eval_repo.get_summary_stats()
    df_eval = st.session_state.eval_repo.to_dataframe()

    # Pastel KPI Metric Cards
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="pastel-card" style="padding: 1.1rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #887887; text-transform: uppercase;">Total Inferences</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: #302536; margin: 4px 0;">{stats['total_runs']}</div>
            <div style="font-size: 0.74rem; color: #887887;">Logged runs</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="pastel-card" style="padding: 1.1rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #887887; text-transform: uppercase;">Average Latency</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: #302536; margin: 4px 0;">{stats['avg_latency']}s</div>
            <div style="font-size: 0.74rem; color: #887887;">Roundtrip duration</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="pastel-card" style="padding: 1.1rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #887887; text-transform: uppercase;">Average Relevance</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: #302536; margin: 4px 0;">{int(stats['avg_relevance']*100)}%</div>
            <div style="font-size: 0.74rem; color: #887887;">Semantic overlap</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="pastel-card" style="padding: 1.1rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #887887; text-transform: uppercase;">Average Consistency</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: #302536; margin: 4px 0;">{int(stats['avg_consistency']*100)}%</div>
            <div style="font-size: 0.74rem; color: #887887;">Schema compliance</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    if not df_eval.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("<div style='font-size: 0.90rem; font-weight: 600; margin-bottom: 8px; color: #302536;'>⏱️ Latency Progression by Run</div>", unsafe_allow_html=True)
            df_plot = df_eval.reset_index()
            df_plot["run_id"] = df_plot.index + 1
            
            latency_chart = (
                alt.Chart(df_plot)
                .mark_line(point=True, color="#E879A9", strokeWidth=2.5)
                .encode(
                    x=alt.X("run_id:O", title="Run #"),
                    y=alt.Y("latency_sec:Q", title="Latency (s)"),
                    tooltip=["run_id", "task_mode", "prompt_type", "latency_sec", "overall_score"]
                )
                .properties(height=250)
                .configure_axis(gridColor="#F1DCE8", labelFontSize=11, titleFontSize=12)
            )
            st.altair_chart(latency_chart, use_container_width=True)

        with chart_col2:
            st.markdown("<div style='font-size: 0.90rem; font-weight: 600; margin-bottom: 8px; color: #302536;'>📊 Relevance & Consistency</div>", unsafe_allow_html=True)
            df_melted = df_plot.melt(
                id_vars=["run_id"],
                value_vars=["relevance_score", "consistency_score"],
                var_name="Metric",
                value_name="Score"
            )
            df_melted["Metric"] = df_melted["Metric"].replace({
                "relevance_score": "Relevance",
                "consistency_score": "Consistency"
            })

            metrics_chart = (
                alt.Chart(df_melted)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("run_id:O", title="Run #"),
                    y=alt.Y("Score:Q", title="Score"),
                    color=alt.Color("Metric:N", scale=alt.Scale(domain=["Relevance", "Consistency"], range=["#10B981", "#A78BFA"])),
                    xOffset="Metric:N",
                    tooltip=["run_id", "Metric", "Score"]
                )
                .properties(height=250)
                .configure_axis(gridColor="#F1DCE8", labelFontSize=11, titleFontSize=12)
            )
            st.altair_chart(metrics_chart, use_container_width=True)

        st.markdown("<div style='margin: 1.4rem 0 0.5rem 0; font-size: 0.95rem; font-weight: 700; color: #302536;'>Audit Log Repository</div>", unsafe_allow_html=True)
        st.dataframe(
            df_eval[[
                "timestamp", "task_mode", "prompt_type", "model",
                "latency_sec", "word_count", "relevance_score",
                "consistency_score", "overall_score"
            ]],
            use_container_width=True,
            height=250
        )

        csv_bytes = df_eval.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Telemetry Audit Log (CSV)",
            data=csv_bytes,
            file_name=f"syra_ai_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.info("No evaluations logged yet. Ask questions in the Chatbot or run A/B Comparisons to populate analytics.")


# ==============================================================================
# TAB 4: FAQ KNOWLEDGE BASE
# ==============================================================================

with tab_faq:
    st.markdown("""
    <div style="margin: 0.5rem 0 1.25rem 0;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0 0 4px 0; color: #302536;">NLP & Prompt Engineering Knowledge Base</h2>
        <p style="font-size: 0.85rem; color: #887887; margin: 0;">
            Curated dataset of verified NLP, Transformer, and Prompt Engineering concepts. Click <b>Test in Chat</b> to benchmark in the conversational engine.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not faq_df.empty:
        search_col, cat_col = st.columns([2, 1])

        with search_col:
            search_query = st.text_input(
                "Search Knowledge Base",
                placeholder="Search topics, questions, keywords...",
                label_visibility="collapsed"
            )

        with cat_col:
            categories = ["All Categories"] + sorted(faq_df["category"].unique().tolist())
            selected_cat = st.selectbox("Category Filter", options=categories, label_visibility="collapsed")

        filtered_df = faq_df.copy()
        if selected_cat != "All Categories":
            filtered_df = filtered_df[filtered_df["category"] == selected_cat]

        if search_query.strip():
            sq = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["question"].str.lower().str.contains(sq) |
                filtered_df["answer"].str.lower().str.contains(sq) |
                filtered_df["keywords"].str.lower().str.contains(sq)
            ]

        st.caption(f"Displaying {len(filtered_df)} of {len(faq_df)} reference entries")

        for _, row in filtered_df.iterrows():
            with st.expander(f"**[{row['category']}]** {row['question']}", expanded=False):
                st.markdown(f"**Verified Answer:**\n\n{row['answer']}")
                st.markdown(f"""
                <div style="margin: 8px 0 12px 0;">
                    <span style="font-size: 0.75rem; color: #887887;">🏷️ Keywords: <code>{row['keywords']}</code></span>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"💬 Test in Chat (ID: {row['id']})", key=f"faq_btn_{row['id']}"):
                    st.session_state.prefill_chat = row["question"]
                    st.session_state.active_task_mode = "Question Answering"
                    st.success("✅ Question loaded into Chatbot! Switch to the 'Interactive Chatbot' tab.")
    else:
        st.error("FAQ dataset could not be loaded. Please ensure `data/faq_dataset.csv` exists.")
