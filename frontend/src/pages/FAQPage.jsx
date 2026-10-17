import React, { useState, useEffect } from 'react';
import { Card, Badge, LoadingSpinner, Button } from '../components/ui';
import { BookOpen, Search, Filter, RefreshCw, AlertCircle, Copy, Check } from 'lucide-react';
import { fetchFAQ } from '../services/api';

export function FAQPage() {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [selectedCat, setSelectedCat] = useState('All');
  const [copiedId, setCopiedId] = useState(null);

  const categories = [
    'All', 
    'NLP Fundamentals', 
    'Prompt Engineering', 
    'LLM Architectures & Training', 
    'Evaluation & Hallucinations'
  ];

  const loadFaqs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFAQ(selectedCat, search);
      setFaqs(data.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load FAQ knowledge base');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Debounce search slightly or reload on category change
    const timeout = setTimeout(() => {
      loadFaqs();
    }, 250);
    return () => clearTimeout(timeout);
  }, [selectedCat, search]);

  const handleCopyQuestion = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-syra-bg text-syra-primary text-xs font-semibold border border-syra-border">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Curated NLP & LLM Knowledge Base</span>
          </div>
          <h1 className="text-2xl font-extrabold text-syra-text">FAQ Knowledge Base</h1>
          <p className="text-xs text-syra-muted">
            15 curated concepts retrieved from the backend CSV dataset for reference and RAG prompt grounding.
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={loadFaqs} disabled={loading}>
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Filter / Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-syra-muted absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search FAQs by concept, keyword, or question..."
            className="w-full pl-10 pr-4 py-2.5 text-xs bg-white border border-syra-border rounded-xl focus:outline-none focus:border-syra-primary"
          />
        </div>
        <div className="flex gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCat(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-colors ${
                selectedCat === cat
                  ? 'bg-syra-primary text-white shadow-sm'
                  : 'bg-white border border-syra-border text-syra-muted hover:bg-syra-bg'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* FAQ Cards List */}
      {loading ? (
        <LoadingSpinner size="md" />
      ) : faqs.length > 0 ? (
        <div className="space-y-3">
          {faqs.map((faq) => (
            <Card key={faq.id} className="space-y-2 hover:border-syra-primary/40 transition-all">
              <div className="flex items-center justify-between">
                <Badge variant="pink">{faq.category}</Badge>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-syra-muted font-mono">#{faq.id}</span>
                  <button
                    onClick={() => handleCopyQuestion(faq.id, faq.question)}
                    title="Copy Question to Clipboard"
                    className="p-1 rounded hover:bg-syra-bg text-syra-muted hover:text-syra-primary transition-colors"
                  >
                    {copiedId === faq.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
              <h3 className="text-sm font-bold text-syra-text">{faq.question}</h3>
              <p className="text-xs text-syra-muted leading-relaxed whitespace-pre-wrap">{faq.answer}</p>
              {faq.keywords && (
                <div className="pt-2 border-t border-syra-border/60 flex flex-wrap gap-1">
                  {faq.keywords.split(',').map((kw, i) => (
                    <span key={i} className="px-2 py-0.5 rounded-md bg-syra-bg text-[10px] text-syra-muted">
                      #{kw.trim()}
                    </span>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-10 flex flex-col items-center justify-center text-center space-y-2 border-dashed">
          <BookOpen className="w-8 h-8 text-syra-border" />
          <h3 className="text-sm font-semibold text-syra-text">No FAQ Questions Found</h3>
          <p className="text-xs text-syra-muted">
            Try adjusting your search query or choosing another category filter.
          </p>
        </Card>
      )}
    </div>
  );
}
