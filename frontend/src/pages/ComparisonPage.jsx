import React, { useState } from 'react';
import { Card, Button, Badge } from '../components/ui';
import { SplitSquareVertical, Zap, CheckCircle2, RefreshCw, AlertCircle, ArrowUpRight, Sparkles, Clock, FileText } from 'lucide-react';
import { comparePrompts } from '../services/api';

export function ComparisonPage() {
  const [taskMode, setTaskMode] = useState('qa');
  const [inputText, setInputText] = useState('How does self-attention work in Transformer models and why is it better than RNNs?');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);

  const presets = [
    {
      label: 'QA: Self-Attention',
      mode: 'qa',
      text: 'How does self-attention work in Transformer models and why is it better than RNNs?',
      basic: 'qa_basic',
      improved: 'qa_improved'
    },
    {
      label: 'QA: Hallucinations & RAG',
      mode: 'qa',
      text: 'What causes LLM hallucinations and how does Retrieval-Augmented Generation solve them?',
      basic: 'qa_basic',
      improved: 'qa_improved'
    },
    {
      label: 'Summary: AI Agents',
      mode: 'summarization',
      text: 'Autonomous AI agents represent a paradigm shift in generative AI, moving beyond single-turn text completion to multi-step reasoning, environment interaction, and tool utilization. Modern agents leverage LLMs as cognitive controllers that orchestrate planning, memory retrieval, and external API tool execution.',
      basic: 'summarize_basic',
      improved: 'summarize_improved'
    },
    {
      label: 'Classify: Product Sentiment',
      mode: 'classification',
      text: 'The model response time was blazing fast, but honestly the generated output was completely inaccurate and hallucinated several citations. Very disappointing for a paid tier.',
      basic: 'classify_basic',
      improved: 'classify_improved'
    }
  ];

  const handleRunComparison = async (presetOverride = null) => {
    const query = presetOverride ? presetOverride.text : inputText.trim();
    const mode = presetOverride ? presetOverride.mode : taskMode;
    const basicTpl = presetOverride ? presetOverride.basic : `${mode}_basic`;
    const improvedTpl = presetOverride ? presetOverride.improved : `${mode}_improved`;

    if (!query || loading) return;

    setLoading(true);
    setError(null);

    try {
      const data = await comparePrompts({
        input_text: query,
        task_mode: mode,
        basic_template: basicTpl,
        improved_template: improvedTpl,
        provider: 'gemini',
        temperature: 0.7,
        max_tokens: 1024
      });
      setComparisonResult(data);
    } catch (err) {
      setError(err.message || 'Comparison request failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (p) => {
    setInputText(p.text);
    setTaskMode(p.mode);
    handleRunComparison(p);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-50 text-syra-lavender text-xs font-semibold border border-purple-100">
          <SplitSquareVertical className="w-3.5 h-3.5" />
          <span>A/B Prompt Engineering Lab</span>
        </div>
        <h1 className="text-2xl font-extrabold text-syra-text">Prompt Comparison Lab</h1>
        <p className="text-xs text-syra-muted">
          Scientifically evaluate prompt engineering deltas. Compare naïve prompt output against structured persona & delimiter engineering.
        </p>
      </div>

      {/* Preset Pills */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-syra-muted mr-1">Presets:</span>
        {presets.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSelectPreset(p)}
            className="px-3 py-1 rounded-xl text-xs bg-white border border-syra-border hover:border-syra-primary text-syra-text font-medium transition-all shadow-sm"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Input Control */}
      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-syra-text uppercase tracking-wider">Test Input Query</label>
          <div className="flex items-center gap-2">
            <span className="text-xs text-syra-muted">Task Mode:</span>
            <select
              value={taskMode}
              onChange={(e) => setTaskMode(e.target.value)}
              className="px-2 py-1 rounded-lg bg-syra-bg border border-syra-border text-xs text-syra-text font-semibold focus:outline-none"
            >
              <option value="qa">Question Answering</option>
              <option value="summarization">Text Summarization</option>
              <option value="classification">Text Classification</option>
            </select>
          </div>
        </div>

        <textarea
          rows={3}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter text or question to compare..."
          className="w-full p-3 text-sm bg-syra-bg border border-syra-border rounded-xl focus:outline-none focus:border-syra-primary"
        />

        <div className="flex justify-end">
          <Button 
            variant="lavender" 
            size="md" 
            onClick={() => handleRunComparison()} 
            disabled={loading || !inputText.trim()}
            loading={loading}
          >
            <Zap className="w-4 h-4" />
            <span>Run A/B Comparison</span>
          </Button>
        </div>
      </Card>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* Delta Verdict Banner */}
      {comparisonResult?.delta && (
        <Card className="bg-gradient-to-r from-purple-50/50 to-pink-50/50 border-syra-lavender/40 p-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-syra-lavender" />
              <span className="text-xs font-bold text-syra-text uppercase tracking-wider">Automated Heuristic Verdict</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold">
              <span className="text-syra-primary">Score Delta: {comparisonResult.delta.overall_delta > 0 ? `+${Math.round(comparisonResult.delta.overall_delta * 100)}%` : `${Math.round(comparisonResult.delta.overall_delta * 100)}%`}</span>
              <span className="text-syra-muted">&bull;</span>
              <span className="text-syra-muted">{comparisonResult.delta.word_count_delta > 0 ? `+${comparisonResult.delta.word_count_delta} words` : `${comparisonResult.delta.word_count_delta} words`}</span>
            </div>
          </div>
          <p className="text-xs text-syra-text leading-relaxed whitespace-pre-wrap">
            {comparisonResult.delta.verdict}
          </p>
        </Card>
      )}

      {/* Side-by-Side Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Basic Prompt */}
        <Card className="space-y-3 border-l-4 border-l-slate-400">
          <div className="flex items-center justify-between pb-2 border-b border-syra-border">
            <div className="flex items-center gap-1.5">
              <Badge variant="default">A: BASIC PROMPT</Badge>
              {comparisonResult?.basic?.is_demo && (
                <span className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-semibold text-[9px]">
                  Demo
                </span>
              )}
            </div>
            <span className="text-xs text-syra-muted">
              {comparisonResult?.basic?.model || 'qa_basic'}
            </span>
          </div>

          <div className="p-2.5 bg-syra-bg rounded-xl text-xs font-mono text-syra-muted line-clamp-2">
            {comparisonResult?.basic?.rendered_prompt || `Answer the following question:\n${inputText}`}
          </div>

          <div className="min-h-[220px] p-3 text-xs leading-relaxed text-syra-text whitespace-pre-wrap bg-white rounded-xl border border-syra-border/60">
            {comparisonResult?.basic?.response_text || (
              <span className="text-syra-muted italic">Click 'Run A/B Comparison' to view output...</span>
            )}
          </div>

          {comparisonResult?.basic?.evaluation && (
            <div className="pt-2 border-t border-syra-border flex flex-wrap gap-2 text-[10px]">
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted font-medium">
                Overall: {Math.round(comparisonResult.basic.evaluation.overall_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                Rel: {Math.round(comparisonResult.basic.evaluation.relevance_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                Cons: {Math.round(comparisonResult.basic.evaluation.consistency_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                {comparisonResult.basic.evaluation.latency_sec}s
              </span>
            </div>
          )}
        </Card>

        {/* Right: Improved Prompt */}
        <Card className="space-y-3 border-l-4 border-l-syra-primary">
          <div className="flex items-center justify-between pb-2 border-b border-syra-border">
            <div className="flex items-center gap-1.5">
              <Badge variant="pink">B: SYRA ENGINEERED</Badge>
              {comparisonResult?.improved?.is_demo && (
                <span className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-semibold text-[9px]">
                  Demo
                </span>
              )}
            </div>
            <span className="text-xs text-syra-muted">
              {comparisonResult?.improved?.model || 'qa_improved'}
            </span>
          </div>

          <div className="p-2.5 bg-syra-bg rounded-xl text-xs font-mono text-syra-muted line-clamp-2">
            {comparisonResult?.improved?.rendered_prompt || 'Structured Persona Framing & Delimiter Isolated'}
          </div>

          <div className="min-h-[220px] p-3 text-xs leading-relaxed text-syra-text whitespace-pre-wrap bg-white rounded-xl border border-syra-border/60">
            {comparisonResult?.improved?.response_text || (
              <span className="text-syra-muted italic">Click 'Run A/B Comparison' to view output...</span>
            )}
          </div>

          {comparisonResult?.improved?.evaluation && (
            <div className="pt-2 border-t border-syra-border flex flex-wrap gap-2 text-[10px]">
              <span className="px-2 py-0.5 rounded bg-purple-50 text-syra-lavender font-bold">
                Overall: {Math.round(comparisonResult.improved.evaluation.overall_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                Rel: {Math.round(comparisonResult.improved.evaluation.relevance_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                Cons: {Math.round(comparisonResult.improved.evaluation.consistency_score * 100)}%
              </span>
              <span className="px-2 py-0.5 rounded bg-syra-bg text-syra-muted">
                {comparisonResult.improved.evaluation.latency_sec}s
              </span>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
