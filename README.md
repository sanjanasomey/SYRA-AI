# SYRA AI: An Intelligent Chatbot Using LLM and Prompt Engineering

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-SDK%202.0+-green.svg)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-SDK-orange.svg)](https://platform.openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced academic Natural Language Processing (NLP) web application demonstrating modern Large Language Model (LLM) orchestration, structured prompt engineering paradigms, multi-dimensional response evaluation, and A/B prompt testing.

---

## 📌 Project Overview

**SYRA AI** bridges the gap between raw LLM generation and production-grade NLP engineering. While foundation models are capable of generating fluent text, naive prompts often produce vague answers, hallucinations, and unstructured outputs. 

This project explores how structured **prompt engineering methodologies** (such as Persona framing, Delimiter isolation, Chain-of-Thought decomposition, and JSON schema enforcement) dramatically improve LLM consistency, relevance, and programmatic reliability.

---

## 🚀 Key Features

1. **Multi-Turn Chatbot Interface**:
   - Modern conversational UI built with Streamlit.
   - Message history persistence across the session.
   - Real-time telemetry badges (Latency, Relevance, Consistency, Word count).

2. **Three NLP Task Modes**:
   - **Question Answering**: Conceptual explanations with optional RAG-style context grounding from the local FAQ knowledge base to minimize hallucinations.
   - **Text Summarization**: Multi-style summarization (Executive Intelligence Brief with strict TL;DR budgets vs. Key Actionable Takeaways).
   - **Text Classification**: Zero-shot sentiment and domain classification enforcing strict JSON schema compliance.

3. **Systematic Prompt Engineering**:
   - Modular prompt template library in [`prompts.py`](prompts.py).
   - Live inspection panel in the UI showing the exact engineered prompt structure sent to the LLM.
   - Techniques demonstrated: Role & Persona Framing, Input Delimiters (`"""`), Few-Shot Formatting, Output Constraints.

4. **A/B Prompt Comparison Playground**:
   - Run side-by-side experiments comparing a **Basic Naive Prompt** against an **Engineered Prompt** using the same test input.
   - Displays comparative metrics: Latency Delta, Word Count Delta, Relevance Delta, and Consistency Delta.
   - Educational breakdown detailing *why* the engineered prompt outperformed.

5. **Multi-Dimensional Response Evaluation Module**:
   - **Relevance**: Semantic/lexical term overlap and intent coverage between prompt and output.
   - **Consistency**: Structural adherence (headings, bullet points, absence of repetition, schema validity).
   - **Response Time**: Millisecond-level roundtrip latency instrumentation.
   - Interactive Analytics Dashboard with performance charts and downloadable CSV audit reports.

6. **Curated FAQ Knowledge Base**:
   - Custom CSV dataset (`data/faq_dataset.csv`) covering NLP Fundamentals, Prompt Engineering, LLM Architectures, and Hallucinations.
   - Interactive search, category filtering, and one-click "Test in Chat" workflow.

7. **Security & Zero-Exposure Credentials**:
   - Complete isolation of API keys via `python-dotenv` and `.env`.
   - Never exposes keys in code, logs, or UI.
   - Intelligent demo simulation fallback if running offline or without credentials.

---

## 📂 Project Architecture

```text
SYRA-AI/
│
├── app.py                  # Main Streamlit web application & user interface
├── prompts.py              # Catalog of reusable basic & engineered prompt templates
├── llm_service.py          # Secure LLM API abstraction (Google Gemini & OpenAI)
├── evaluation.py           # Automated evaluation engine (Relevance, Consistency, Latency)
├── requirements.txt        # Pinned Python package dependencies
├── .env.example            # Environment configuration template
├── .gitignore              # Protects secrets (.env) and Python artifacts from Git
├── README.md               # Complete academic documentation & setup guide
│
└── data/
    └── faq_dataset.csv     # Custom NLP and Prompt Engineering FAQ dataset
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Core programming runtime |
| **Frontend UI** | Streamlit | Responsive web application interface |
| **LLM Provider (Primary)** | Google Gemini (`google-genai` SDK) | `gemini-2.5-flash`, `gemini-2.5-pro` (Generous free tier) |
| **LLM Provider (Secondary)** | OpenAI (`openai` SDK) | `gpt-4o-mini`, `gpt-4o` |
| **Data Processing** | Pandas | FAQ dataset querying & evaluation audit logging |
| **Configuration** | python-dotenv | Secure environment variable management |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Pip package manager
- (Optional) A free API key from [Google AI Studio](https://aistudio.google.com/)

### Step 1: Navigate to the Project Directory
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\SYRA-AI
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the `.env.example` template to `.env`:
```powershell
copy .env.example .env
```

Open `.env` in any text editor and supply your Google Gemini API key:
```env
# Get a free key at: https://aistudio.google.com
GEMINI_API_KEY=AIzaSyYourActualKeyHere

# Default model settings
DEFAULT_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.5-flash
```

> 💡 **No API Key Yet?** No problem! SYRA AI includes an intelligent **Demo Simulation Mode**. You can launch and test the full application, compare prompts, view metrics, and browse the FAQ database even before adding a key.

---

## 🖥️ Running the Application

Launch the Streamlit web server via Python's module launcher:
```powershell
python -m streamlit run app.py
```

*Or simply double-click / run the included batch launcher:*
```powershell
.\run.bat
```

The application will automatically open in your default browser at:
```text
http://localhost:8501
```

---

## 🧪 Prompt Engineering Methodology Guide

### 1. Naive vs. Engineered Question Answering
* **Naive Prompt**: `"Answer the following question: {question}"`
  - *Symptom*: Vague, unstructured paragraphs with arbitrary depth and occasional hallucinated citations.
* **Engineered Prompt**: Combines **Role Framing** (*"You are a Senior AI Engineer..."*), **Input Delimiters** (`"""`), and **Explicit Section Constraints** (Core Concept, Working Mechanism, Real-World Application, Common Pitfalls).
  - *Result*: Crisp, pedagogically sound, and deterministic technical breakdowns.

### 2. Output Schema Enforcement in Classification
* **Naive Prompt**: `"Classify the sentiment of this text: {text}"`
  - *Symptom*: Returns conversational text (*"Sure! The text expresses a somewhat negative feeling..."*) which breaks automated data pipelines.
* **Engineered Prompt**: Strictly mandates a JSON code block with specific typed keys (`primary_sentiment`, `confidence_score`, `domain`, `key_triggers`, `rationale`).
  - *Result*: 100% deterministic, machine-parseable data outputs.

---

## 📊 Evaluation Metrics Explained

- **Latency ($\text{s}$)**: Precise roundtrip execution time measured via `time.perf_counter()`.
- **Relevance Index ($0.0 - 1.0$)**: Lexical and semantic term overlap between the prompt instructions and the response tokens.
- **Consistency Score ($0.0 - 1.0$)**: Structural integrity score assessing markdown headings, bulleted logic, syntactic compliance, and absence of repetitive degeneration.
- **Overall Composite Index**:
  $$\text{Score} = 0.45 \times \text{Relevance} + 0.40 \times \text{Consistency} + 0.15 \times \text{LatencyEfficiency}$$

---

## 🔒 Security & Privacy

- **Zero Hardcoding**: All secrets are stored exclusively in `.env` and loaded into runtime memory.
- **Git Protection**: `.gitignore` is pre-configured to ensure `.env` and sensitive files are never committed to version control.
- **UI Masking**: API keys are masked in the application interface (e.g. `AIza...4X1a`).

---

## 📜 License
This project is developed for educational purposes under the MIT License.
