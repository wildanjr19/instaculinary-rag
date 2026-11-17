import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.documents import Document

with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-deepseek-key"}):
    from backend.api import app


class ChatAPITests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-deepseek-key"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.search = patch("backend.api.search_documents")
        self.search_mock = self.search.start()
        self.addCleanup(self.search.stop)
        self.search_mock.return_value = [Document(page_content="Nama: Soto Solo")]
        self.invoke = patch("langchain_openai.ChatOpenAI.invoke")
        self.invoke_mock = self.invoke.start()
        self.addCleanup(self.invoke.stop)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_health_does_not_call_external_services(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.search_mock.assert_not_called()
        self.invoke_mock.assert_not_called()

    def test_empty_retrieval_preserves_empty_response(self):
        self.search_mock.return_value = []
        response = self.client.post("/api/chat", json={"query": "kuliner Jogja"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "query_summary": "Tidak ada data relevan ditemukan.", "results": []
        })
        self.invoke_mock.assert_not_called()

    def test_structured_results_and_markdown_fences_are_preserved(self):
        expected = {
            "query_summary": "Soto di Solo",
            "results": [{
                "rank": 1, "name": "Soto Solo", "address": "Solo",
                "hours": "07:00 - 14:00", "price": "Rp 15.000",
                "categories": ["Soto"], "description": "Soto hangat.",
                "source": "@contoh", "source_url": "https://instagram.com/p/contoh/",
            }],
        }
        for fenced in (False, True):
            with self.subTest(fenced=fenced):
                raw = json.dumps(expected)
                if fenced:
                    raw = f"```json\n{raw}\n```"
                self.invoke_mock.return_value = SimpleNamespace(content=raw)
                response = self.client.post("/api/chat", json={"query": "soto Solo"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected)

    def test_non_json_reply_keeps_existing_text_fallback(self):
        self.invoke_mock.return_value = SimpleNamespace(content="Jawaban teks biasa")
        response = self.client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 200)
        result = response.json()["results"][0]
        self.assertEqual(result["description"], "Jawaban teks biasa")
        self.assertEqual(result["categories"], [])

    def test_retrieval_failure_is_http_error_without_private_details(self):
        self.search_mock.side_effect = RuntimeError("private-upstream-details")
        with self.assertLogs("backend.api", level="ERROR") as logs:
            response = self.client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["results"], [])
        self.assertIn("error", response.json())
        self.assertNotIn("private-upstream-details", response.text)
        self.assertIn("private-upstream-details", "\n".join(logs.output))
        self.invoke_mock.assert_not_called()

    def test_generation_failure_is_http_error_without_private_details(self):
        self.invoke_mock.side_effect = RuntimeError("private-generation-details")
        with self.assertLogs("backend.api", level="ERROR") as logs:
            response = self.client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["results"], [])
        self.assertNotIn("private-generation-details", response.text)
        self.assertIn("private-generation-details", "\n".join(logs.output))

    def test_invalid_result_shapes_are_rejected(self):
        invalid_results = [[], {"query_summary": "Soto"}, {
            "query_summary": "Soto", "results": [{"name": "Soto Solo"}]
        }]
        for result in invalid_results:
            with self.subTest(result=result):
                self.invoke_mock.return_value = SimpleNamespace(content=json.dumps(result))
                with self.assertLogs("backend.api", level="WARNING"):
                    response = self.client.post("/api/chat", json={"query": "soto"})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json()["results"], [])

    def test_invalid_requests_do_not_reach_retrieval(self):
        for payload in ({}, {"query": ""}, {"query": "   "}, {"query": None}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/chat", json=payload)
                self.assertEqual(response.status_code, 422)
        self.search_mock.assert_not_called()
        self.invoke_mock.assert_not_called()
