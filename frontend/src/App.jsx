import React, { useState } from 'react';
import { 
  MessageSquare, 
  SplitSquareVertical, 
  BarChart3, 
  BookOpen, 
  Sparkles, 
  ShieldCheck, 
  Sliders, 
  Menu, 
  X,
  ExternalLink
} from 'lucide-react';
import { Badge } from './components/ui';

// Pages
import { ChatPage } from './pages/ChatPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { FAQPage } from './pages/FAQPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { id: 'chat', label: 'AI Chat', icon: MessageSquare, badge: 'Active' },
    { id: 'compare', label: 'Prompt Lab (A/B)', icon: SplitSquareVertical },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'faq', label: 'Knowledge Base', icon: BookOpen, badge: '15 FAQs' },
  ];

  return (
    <div className="min-h-screen bg-syra-bg flex flex-col md:flex-row text-syra-text">
      {/* Mobile Top Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-syra-sidebar border-b border-syra-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-syra-primary to-syra-lavender flex items-center justify-center text-white shadow-sm">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight text-syra-text">SYRA AI</h1>
            <p className="text-[10px] text-syra-muted">Smart Yield, Refined Answers</p>
          </div>
        </div>
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-xl border border-syra-border bg-white text-syra-text"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-40 w-64 bg-syra-sidebar border-r border-syra-border flex flex-col justify-between p-5 transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="space-y-6">
          {/* Brand Logo & Tagline */}
          <div className="hidden md:flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-syra-primary to-syra-lavender flex items-center justify-center text-white shadow-sm shadow-syra-primary/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tight text-syra-text">SYRA AI</h1>
              <p className="text-[10px] text-syra-muted font-medium">Smart Yield, Refined Answers</p>
            </div>
          </div>

          <div className="px-3 py-2 rounded-xl bg-white/70 border border-syra-border text-xs text-syra-muted flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-syra-primary" />
            <span className="italic font-medium">"Think clearly. Prompt brilliantly."</span>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1.5">
            <div className="text-[10px] font-bold uppercase tracking-wider text-syra-muted px-3 mb-2">
              Workspace
            </div>
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-white text-syra-primary shadow-sm border border-syra-border'
                      : 'text-syra-muted hover:text-syra-text hover:bg-white/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-syra-primary' : 'text-syra-muted'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <Badge variant={isActive ? 'pink' : 'default'} size="xs">
                      {item.badge}
                    </Badge>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Info */}
        <div className="pt-4 border-t border-syra-border space-y-3">
          <div className="p-3 bg-white/60 rounded-xl border border-syra-border space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-syra-text">API Connection</span>
              <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-600">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Backend Ready
              </span>
            </div>
            <p className="text-[10px] text-syra-muted leading-tight">
              FastAPI backend running locally on port 8000.
            </p>
          </div>

          <div className="text-[10px] text-center text-syra-muted">
            SYRA AI v2.0 &bull; NLP Prompt Studio
          </div>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto p-4 sm:p-6 md:p-8">
        {activeTab === 'chat' && <ChatPage />}
        {activeTab === 'compare' && <ComparisonPage />}
        {activeTab === 'analytics' && <AnalyticsPage />}
        {activeTab === 'faq' && <FAQPage />}
      </main>
    </div>
  );
}
