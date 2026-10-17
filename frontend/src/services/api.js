/**
 * SYRA AI - Centralized API Client
 * Connects exclusively to the FastAPI backend using VITE_API_BASE_URL.
 * No LLM API keys are ever stored or transmitted from the client.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Retrieve or generate a persistent session UUID for this browser session
export function getSessionId() {
  let sid = localStorage.getItem('syra_session_id');
  if (!sid) {
    sid = 'syra-' + Math.random().toString(36).substring(2, 11) + '-' + Date.now();
    localStorage.setItem('syra_session_id', sid);
  }
  return sid;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchStatus() {
  const res = await fetch(`${API_BASE_URL}/api/status`);
  if (!res.ok) throw new Error('Failed to fetch system status');
  return res.json();
}

export async function fetchProviders() {
  const res = await fetch(`${API_BASE_URL}/api/providers`);
  if (!res.ok) throw new Error('Failed to fetch providers');
  return res.json();
}

export async function sendChatMessage(payload) {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: getSessionId(),
      ...payload
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Chat request failed' }));
    throw new Error(err.detail || 'Chat request failed');
  }
  return res.json();
}

export async function comparePrompts(payload) {
  const res = await fetch(`${API_BASE_URL}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: getSessionId(),
      ...payload
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Comparison request failed' }));
    throw new Error(err.detail || 'Comparison request failed');
  }
  return res.json();
}

export async function fetchEvaluations() {
  const sid = getSessionId();
  const res = await fetch(`${API_BASE_URL}/api/evaluations?session_id=${encodeURIComponent(sid)}`);
  if (!res.ok) throw new Error('Failed to fetch evaluations');
  return res.json();
}

export async function fetchFAQ(category = null, search = null) {
  const params = new URLSearchParams();
  if (category && category !== 'All') params.append('category', category);
  if (search && search.trim()) params.append('search', search.trim());

  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${API_BASE_URL}/api/faq${query}`);
  if (!res.ok) throw new Error('Failed to fetch FAQs');
  return res.json();
}

export function getExportCsvUrl() {
  const sid = getSessionId();
  return `${API_BASE_URL}/api/export/csv?session_id=${encodeURIComponent(sid)}`;
}
