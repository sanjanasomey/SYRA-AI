import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Badge } from '../components/ui';
import { 
  Sparkles, 
  HelpCircle, 
  FileText, 
  Tags, 
  Send, 
  Cpu, 
  Sliders, 
  CheckCircle, 
  AlertCircle,
  Database,
  RefreshCw,
  Clock,
  Gauge
} from 'lucide-react';
import { sendChatMessage, fetchProviders } from '../services/api';

export function ChatPage() {
  const [taskMode, setTaskMode] = useState('qa');
  const [promptType, setPromptType] = useState('improved');
  const [useFaqGrounding, setUseFaqGrounding] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Provider & Model state
  const [providersData, setProvidersData] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [selectedModel, setSelectedModel] = useState('');
  const [temperature, setTemperature] = useState(0.7);

  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I'm SYRA (Smart Yield, Refined Answers). What would you like to explore today?",
      model: 'SYRA AI Engine',
      provider: 'System',
      isDemo: false,
      evaluation: null
    }
  ]);

  // Load available providers from backend
  useEffect(() => {
    async function loadProviders() {
      try {
        const data = await fetchProviders();
        setProvidersData(data);
        if (data.default_provider && data.providers[data.default_provider]) {
          setSelectedProvider(data.default_provider);
          setSelectedModel(data.providers[data.default_provider].default_model);
        }
      } catch (err) {
        // Backend offline or fallback to default
        setSelectedModel('gemini-flash-lite-latest');
      }
    }
    loadProviders();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const taskModes = [
    { 
      id: 'qa', 
      label: 'Question Answering', 
      icon: HelpCircle, 
      desc: 'Conceptual explanations & deep technical dives' 
    },
    { 
      id: 'summarization', 
      label: 'Text Summarization', 
      icon: FileText, 
      desc: 'Executive TL;DRs and key takeaway briefs' 
    },
    { 
      id: 'classification', 
      label: 'Text Classification', 
      icon: Tags, 
      desc: 'Structured sentiment & domain categorization' 
    },
  ];

  const handleProviderChange = (prov) => {
    setSelectedProvider(prov);
    if (providersData?.providers[prov]) {
      setSelectedModel(providersData.providers[prov].default_model);
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    const query = inputMessage.trim();
    if (!query || loading) return;

    setError(null);
    setInputMessage('');

    // Append user message immediately
    const userMsg = {
      role: 'user',
      text: query,
      model: null,
      provider: null,
      evaluation: null
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: query,
        task_mode: taskMode,
        provider: selectedProvider,
        model: selectedModel || null,
        temperature: parseFloat(temperature),
        max_tokens: 1024,
        use_faq_grounding: taskMode === 'qa' && useFaqGrounding,
        prompt_type: promptType
      });

      const assistantMsg = {
        role: 'assistant',
        text: response.response_text,
        model: response.model,
        provider: response.provider,
        isDemo: response.is_demo,
        error: response.error,
        evaluation: response.evaluation
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.message || 'Could not communicate with SYRA AI backend.');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `⚠️ **Request Error**: ${err.message || 'The server could not process the request.'}`,
          model: 'Error State',
          provider: 'System',
          isDemo: false,
          error: err.message,
          evaluation: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="text-center py-2 space-y-1.5">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-syra-sidebar border border-syra-border text-syra-primary text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Intelligent Chatbot & Prompt Engineering Studio</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-syra-text">
          Ask <span className="text-syra-primary">SYRA</span> Anything
        </h1>
        <p className="text-xs text-syra-muted max-w-lg mx-auto">
          Think clearly. Prompt brilliantly. Choose a mode below or configure runtime prompts.
        </p>
      </div>

      {/* Task Mode Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {taskModes.map((mode) => {
          const Icon = mode.icon;
          const isSelected = taskMode === mode.id;
          return (
            <button
              key={mode.id}
              onClick={() => {
                setTaskMode(mode.id);
                // Reset prompt type to standard improved for mode
                setPromptType('improved');
              }}
              className={`p-4 rounded-2xl border text-left transition-all duration-150 ${
                isSelected
                  ? 'bg-white border-syra-primary shadow-sm ring-1 ring-syra-primary/20'
                  : 'bg-syra-card border-syra-border hover:border-syra-primary/40 hover:bg-syra-cardHover'
              }`}
            >
              <div className="flex items-center gap-2.5 mb-1">
                <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-syra-bg text-syra-primary' : 'bg-syra-sidebar text-syra-muted'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-semibold text-syra-text">{mode.label}</h3>
              </div>
              <p className="text-xs text-syra-muted leading-relaxed">{mode.desc}</p>
            </button>
          );
        })}
      </div>

      {/* Runtime Configuration Bar */}
      <div className="bg-white border border-syra-border rounded-2xl p-3.5 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Provider selector */}
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-syra-muted" />
            <span className="text-syra-muted font-medium">Provider:</span>
            <select
              value={selectedProvider}
              onChange={(e) => handleProviderChange(e.target.value)}
              className="px-2.5 py-1 rounded-lg bg-syra-bg border border-syra-border text-syra-text font-semibold focus:outline-none focus:border-syra-primary"
            >
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          {/* Model selector */}
          {providersData?.providers[selectedProvider]?.models && (
            <div className="flex items-center gap-1.5">
              <span className="text-syra-muted font-medium">Model:</span>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="px-2.5 py-1 rounded-lg bg-syra-bg border border-syra-border text-syra-text font-medium focus:outline-none focus:border-syra-primary"
              >
                {providersData.providers[selectedProvider].models.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          )}

          {/* Prompt Type selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-syra-muted font-medium">Prompt:</span>
            <select
              value={promptType}
              onChange={(e) => setPromptType(e.target.value)}
              className="px-2.5 py-1 rounded-lg bg-syra-bg border border-syra-border text-syra-text font-medium focus:outline-none focus:border-syra-primary"
            >
              <option value="improved">SYRA Engineered</option>
              <option value="basic">Basic (Naïve)</option>
              {taskMode === 'summarization' && (
                <option value="bullet_points">Key Action Bullets</option>
              )}
            </select>
          </div>
        </div>

        {/* Mode-specific toggle: FAQ Grounding for QA */}
        {taskMode === 'qa' && (
          <label className="flex items-center gap-1.5 cursor-pointer text-syra-text select-none">
            <input
              type="checkbox"
              checked={useFaqGrounding}
              onChange={(e) => setUseFaqGrounding(e.target.checked)}
              className="rounded text-syra-primary focus:ring-syra-primary"
            />
            <Database className="w-3.5 h-3.5 text-syra-lavender" />
            <span className="font-semibold text-xs">FAQ Grounding (RAG)</span>
          </label>
        )}
      </div>

      {/* Conversation Thread Area */}
      <Card className="min-h-[420px] flex flex-col justify-between space-y-4">
        <div className="space-y-4 flex-1 overflow-y-auto max-h-[500px] pr-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <Badge variant={msg.role === 'user' ? 'default' : 'pink'} size="xs">
                  {msg.role === 'user' ? 'YOU' : 'SYRA AI'}
                </Badge>
                {msg.model && (
                  <span className="text-[10px] text-syra-muted font-medium flex items-center gap-1">
                    <span>{msg.model}</span>
                    {msg.isDemo && (
                      <span className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-semibold text-[9px]">
                        Demo / Simulation
                      </span>
                    )}
                  </span>
                )}
              </div>

              {msg.error && (
                <div className="mb-1.5 px-3 py-1 bg-amber-50/80 border border-amber-200 rounded-xl text-[11px] text-amber-800 flex items-center gap-1.5 max-w-[85%]">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>{msg.error}</span>
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-syra-primary text-white rounded-tr-none'
                    : 'bg-syra-bg border border-syra-border text-syra-text rounded-tl-none whitespace-pre-wrap'
                }`}
              >
                {msg.text}
              </div>

              {/* Evaluation Metrics Badge Row */}
              {msg.evaluation && (
                <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[10px]">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-purple-50 text-syra-lavender border border-purple-100 font-semibold">
                    <Sparkles className="w-2.5 h-2.5" />
                    Overall: {Math.round(msg.evaluation.overall_score * 100)}%
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white border border-syra-border text-syra-muted">
                    <Gauge className="w-2.5 h-2.5 text-syra-primary" />
                    Rel: {Math.round(msg.evaluation.relevance_score * 100)}% ({msg.evaluation.relevance_rating})
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white border border-syra-border text-syra-muted">
                    <CheckCircle className="w-2.5 h-2.5 text-emerald-500" />
                    Cons: {Math.round(msg.evaluation.consistency_score * 100)}%
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white border border-syra-border text-syra-muted">
                    <Clock className="w-2.5 h-2.5" />
                    {msg.evaluation.latency_sec}s
                  </span>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 p-3 bg-syra-bg rounded-2xl border border-syra-border text-xs text-syra-muted w-fit animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-syra-primary" />
              <span>SYRA is thinking & evaluating response...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Composer */}
        <form onSubmit={handleSendMessage} className="pt-3 border-t border-syra-border flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={loading}
            placeholder={`Ask SYRA about ${taskMode === 'qa' ? 'NLP, self-attention, prompt injection...' : taskMode}...`}
            className="flex-1 px-4 py-2.5 text-sm bg-syra-bg border border-syra-border rounded-xl focus:outline-none focus:border-syra-primary focus:ring-1 focus:ring-syra-primary/30 transition-all placeholder:text-syra-muted disabled:opacity-50"
          />
          <Button variant="primary" size="md" type="submit" disabled={loading || !inputMessage.trim()} loading={loading}>
            <Send className="w-4 h-4" />
            <span>Send</span>
          </Button>
        </form>
      </Card>
    </div>
  );
}
