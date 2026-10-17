"""
SYRA AI - Comprehensive Backend Test Suite
Module: backend/tests/test_api.py

Automated tests covering:
1. Health and System Status endpoints.
2. Safe provider status (no secret exposure).
3. Chat inference (QA, Summarization, Classification).
4. Prompt Comparison Lab (A/B testing and deltas).
5. FAQ retrieval, keyword searching, and category filtering.
6. Session-scoped evaluation history and analytics.
7. CSV export with proper Content-Disposition and headers.
8. Error handling on invalid/empty inputs.
9. Verification that no raw API keys leak into any response payload.
10. CORS preflight simulation.
11. Explicit demo/simulation identification on auth error or missing keys.
"""

import sys
import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestSyraBackendAPI(unittest.TestCase):

    def test_01_health_check(self):
        """Verify health endpoint works unconditionally without any credentials."""
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "syra-ai-backend")

    def test_02_system_status(self):
        """Verify system status without secret exposure."""
        res = client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["app_name"], "SYRA AI")
        self.assertIn("providers", data)
        # Ensure raw API key is never present
        res_str = res.text
        self.assertNotIn("AIza", res_str)
        self.assertNotIn("sk-", res_str)

    def test_03_get_providers(self):
        """Verify /api/providers endpoint lists available models and masked status."""
        res = client.get("/api/providers")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("providers", data)
        self.assertIn("gemini", data["providers"])
        self.assertIn("openai", data["providers"])
        gemini_info = data["providers"]["gemini"]
        self.assertIn("models", gemini_info)
        self.assertGreater(len(gemini_info["models"]), 0)
        self.assertEqual(gemini_info["default_model"], "gemini-flash-lite-latest")
        self.assertNotIn("AIza", res.text)

    def test_04_faq_retrieval_and_filtering(self):
        """Verify FAQ items, category filtering, and keyword search."""
        res_all = client.get("/api/faq")
        self.assertEqual(res_all.status_code, 200)
        data_all = res_all.json()
        self.assertEqual(data_all["total"], 15)

        res_cat = client.get("/api/faq?category=Prompt%20Engineering")
        self.assertEqual(res_cat.status_code, 200)
        data_cat = res_cat.json()
        self.assertGreater(data_cat["total"], 0)
        for item in data_cat["items"]:
            self.assertEqual(item["category"], "Prompt Engineering")

        res_search = client.get("/api/faq?search=tokenization")
        self.assertEqual(res_search.status_code, 200)
        data_search = res_search.json()
        self.assertGreaterEqual(data_search["total"], 1)
        found = any(
            "token" in item["question"].lower() or "token" in item["answer"].lower()
            for item in data_search["items"]
        )
        self.assertTrue(found)

    def test_05_chat_endpoint_qa(self):
        """Verify /api/chat QA mode with evaluation results."""
        session_id = "test-session-qa-01"
        payload = {
            "session_id": session_id,
            "message": "Explain how self-attention works in Transformer models.",
            "task_mode": "qa",
            "provider": "gemini",
            "prompt_type": "improved"
        }
        res = client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["session_id"], session_id)
        self.assertGreater(len(data["response_text"]), 0)
        self.assertIsNotNone(data["evaluation"])
        self.assertTrue(0.0 <= data["evaluation"]["overall_score"] <= 1.0)
        self.assertGreater(data["evaluation"]["relevance_score"], 0)
        self.assertNotIn("AIza", res.text)
        self.assertNotIn("sk-", res.text)

    def test_06_chat_endpoint_classification(self):
        """Verify classification mode produces evaluation and transparency flag."""
        session_id = "test-session-class-01"
        payload = {
            "session_id": session_id,
            "message": "The product was completely inaccurate and failed repeatedly.",
            "task_mode": "classification",
            "provider": "gemini",
            "prompt_type": "improved"
        }
        res = client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["evaluation"]["consistency_score"], 0.70)
        self.assertIn("is_demo", data)

    def test_07_prompt_comparison_endpoint(self):
        """Verify /api/compare executes A/B evaluation with deltas and demo flags."""
        session_id = "test-session-ab-01"
        payload = {
            "session_id": session_id,
            "input_text": "What causes LLM hallucinations?",
            "task_mode": "qa",
            "basic_template": "qa_basic",
            "improved_template": "qa_improved",
            "provider": "gemini"
        }
        res = client.post("/api/compare", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("basic", data)
        self.assertIn("improved", data)
        self.assertIn("is_demo", data["basic"])
        self.assertIn("is_demo", data["improved"])
        self.assertIn("delta", data)
        self.assertIn("overall_delta", data["delta"])
        self.assertIn("verdict", data["delta"])

    def test_08_session_isolation_and_analytics(self):
        """Verify evaluations are strictly partitioned by session_id."""
        session_a = "session-alice-100"
        session_b = "session-bob-200"

        client.post("/api/chat", json={
            "session_id": session_a,
            "message": "What is NLP?",
            "task_mode": "qa"
        })

        res_a = client.get(f"/api/evaluations?session_id={session_a}")
        self.assertEqual(res_a.status_code, 200)
        data_a = res_a.json()
        self.assertGreaterEqual(data_a["total_runs"], 1)

        res_b = client.get(f"/api/evaluations?session_id={session_b}")
        self.assertEqual(res_b.status_code, 200)
        data_b = res_b.json()
        self.assertEqual(data_b["total_runs"], 0)

    def test_09_csv_export(self):
        """Verify CSV export endpoint produces valid CSV headers and content."""
        session_id = "session-csv-test"
        client.post("/api/chat", json={
            "session_id": session_id,
            "message": "Summarize machine learning.",
            "task_mode": "summarization"
        })

        res = client.get(f"/api/export/csv?session_id={session_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers["content-type"])
        self.assertIn("attachment; filename=", res.headers["content-disposition"])
        content = res.text
        self.assertIn("session_id", content)
        self.assertIn("overall_score", content)
        self.assertIn(session_id, content)

    def test_10_invalid_input_handling(self):
        """Verify 422 validation on empty or invalid payloads."""
        res = client.post("/api/chat", json={
            "session_id": "test-err",
            "message": "",
            "task_mode": "qa"
        })
        self.assertEqual(res.status_code, 422)

        res_enum = client.post("/api/chat", json={
            "session_id": "test-err",
            "message": "Valid text",
            "task_mode": "invalid_mode"
        })
        self.assertEqual(res_enum.status_code, 422)

    def test_11_cors_preflight(self):
        """Verify CORS preflight OPTIONS returns allowed methods and headers."""
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        res = client.options("/api/chat", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertIn("POST", res.headers.get("access-control-allow-methods", ""))


if __name__ == "__main__":
    unittest.main()
