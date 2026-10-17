import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, LoadingSpinner } from '../components/ui';
import { BarChart3, Download, Activity, Gauge, Clock, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { fetchEvaluations, getExportCsvUrl } from '../services/api';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';

export function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchEvaluations();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to fetch session analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const summary = data?.summary || {
    total_runs: 0,
    avg_latency: 0.0,
    avg_relevance: 0.0,
    avg_consistency: 0.0,
    avg_overall: 0.0
  };

  const records = data?.records || [];

  const kpis = [
    { 
      label: 'Total Inferences', 
      value: summary.total_runs.toString(), 
      icon: Activity, 
      desc: 'Runs in current session' 
    },
    { 
      label: 'Avg Latency', 
      value: `${summary.avg_latency}s`, 
      icon: Clock, 
      desc: summary.avg_latency < 2.0 ? 'Optimal latency' : 'Normal range' 
    },
    { 
      label: 'Avg Relevance', 
      value: `${Math.round(summary.avg_relevance * 100)}%`, 
      icon: Gauge, 
      desc: 'Lexical & semantic overlap' 
    },
    { 
      label: 'Composite Quality', 
      value: `${Math.round(summary.avg_overall * 100)}%`, 
      icon: Sparkles, 
      desc: '45% Rel / 40% Cons / 15% Lat' 
    },
  ];

  // Prepare chart dataset
  const chartData = records.map((r, idx) => ({
    name: `#${idx + 1}`,
    overall: Math.round((r.overall_score || 0) * 100),
    relevance: Math.round((r.relevance_score || 0) * 100),
    consistency: Math.round((r.consistency_score || 0) * 100),
    latency: r.latency_sec || 0,
    mode: r.task_mode
  }));

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-100 mb-1">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Response Evaluation Telemetry</span>
          </div>
          <h1 className="text-2xl font-extrabold text-syra-text">Evaluation & Analytics</h1>
          <p className="text-xs text-syra-muted">
            Live telemetry computed dynamically across session inferences. No hardcoded statistics.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={loadData} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>

          <a href={getExportCsvUrl()} download>
            <Button variant="primary" size="sm">
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </Button>
          </a>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <Card key={idx} className="p-4 space-y-2">
              <div className="flex items-center justify-between text-syra-muted">
                <span className="text-xs font-medium">{kpi.label}</span>
                <Icon className="w-4 h-4 text-syra-primary" />
              </div>
              <div className="text-2xl font-black text-syra-text">{kpi.value}</div>
              <div className="text-[10px] text-syra-muted">{kpi.desc}</div>
            </Card>
          );
        })}
      </div>

      {/* Charts Section */}
      {records.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Quality Metrics Trend Chart */}
          <Card className="p-5 space-y-3">
            <h3 className="text-sm font-bold text-syra-text">Evaluation Score Progression (%)</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1DCE8" />
                  <XAxis dataKey="name" stroke="#887887" fontSize={10} />
                  <YAxis domain={[0, 100]} stroke="#887887" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#F1DCE8', borderRadius: '12px', fontSize: '11px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Line type="monotone" dataKey="overall" name="Overall" stroke="#E879A9" strokeWidth={2.5} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="consistency" name="Consistency" stroke="#A78BFA" strokeWidth={1.5} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="relevance" name="Relevance" stroke="#10B981" strokeWidth={1.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Latency by Run Chart */}
          <Card className="p-5 space-y-3">
            <h3 className="text-sm font-bold text-syra-text">Roundtrip Latency (Seconds)</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1DCE8" />
                  <XAxis dataKey="name" stroke="#887887" fontSize={10} />
                  <YAxis stroke="#887887" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#F1DCE8', borderRadius: '12px', fontSize: '11px' }}
                  />
                  <Bar dataKey="latency" name="Latency (s)" fill="#E879A9" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      ) : (
        <Card className="p-10 flex flex-col items-center justify-center text-center space-y-2 border-dashed">
          <Activity className="w-10 h-10 text-syra-border" />
          <h3 className="text-sm font-semibold text-syra-text">No Telemetry Recorded Yet</h3>
          <p className="text-xs text-syra-muted max-w-sm">
            Inference evaluations will automatically appear here once you chat or compare prompts in this session.
          </p>
        </Card>
      )}

      {/* Audit Log Table */}
      {records.length > 0 && (
        <Card className="p-4 space-y-3 overflow-hidden">
          <h3 className="text-sm font-bold text-syra-text">Session Telemetry Audit Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-syra-bg text-syra-muted uppercase tracking-wider text-[10px] border-b border-syra-border">
                <tr>
                  <th className="p-2.5">Time</th>
                  <th className="p-2.5">Mode</th>
                  <th className="p-2.5">Model</th>
                  <th className="p-2.5">Latency</th>
                  <th className="p-2.5">Words</th>
                  <th className="p-2.5">Relevance</th>
                  <th className="p-2.5">Consistency</th>
                  <th className="p-2.5">Overall</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-syra-border">
                {records.slice().reverse().map((r, idx) => (
                  <tr key={idx} className="hover:bg-syra-bg/50">
                    <td className="p-2.5 text-syra-muted font-mono">{r.timestamp?.split(' ')[1] || '—'}</td>
                    <td className="p-2.5 font-medium text-syra-text">{r.task_mode}</td>
                    <td className="p-2.5 text-syra-muted">{r.model}</td>
                    <td className="p-2.5 font-mono">{r.latency_sec}s</td>
                    <td className="p-2.5">{r.word_count}</td>
                    <td className="p-2.5 font-semibold text-emerald-600">{Math.round((r.relevance_score || 0) * 100)}%</td>
                    <td className="p-2.5 font-semibold text-purple-600">{Math.round((r.consistency_score || 0) * 100)}%</td>
                    <td className="p-2.5 font-bold text-syra-primary">{Math.round((r.overall_score || 0) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
