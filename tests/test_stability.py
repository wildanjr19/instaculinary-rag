import asyncio
import json
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import requests
from openai import APITimeoutError
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from backend.api import app


class ConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_remains_available_during_blocking_retrieval(self):
        entered = threading.Event()
        release = threading.Event()
        finished = threading.Event()

        def retrieval(*args, **kwargs):
            entered.set()
            release.wait(timeout=1)
            finished.set()
            return []

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("backend.api.search_documents", side_effect=retrieval):
                search = asyncio.create_task(client.post("/api/chat", json={"query": "soto"}))
                try:
                    for _ in range(200):
                        if entered.is_set():
                            break
                        await asyncio.sleep(0.005)
                    self.assertTrue(entered.is_set(), "Retrieval never started")
                    health = await client.get("/")
                    self.assertEqual(health.status_code, 200)
                    self.assertFalse(finished.is_set(), "Retrieval blocked the ASGI event loop")
                finally:
                    release.set()
                    response = await search
                self.assertEqual(response.status_code, 200)


class BoundaryTests(unittest.TestCase):
    def test_provider_timeout_is_504_without_private_details(self):
        with TestClient(app) as client, patch(
            "backend.api.search_documents", side_effect=requests.Timeout("private-timeout")
        ), self.assertLogs("backend.api", level="ERROR"):
            response = client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["results"], [])
        self.assertNotIn("private-timeout", response.text)

    def test_generation_timeout_is_504_without_private_details(self):
        error = APITimeoutError(request=httpx.Request("POST", "https://example.invalid/private"))
        with TestClient(app) as client, patch(
            "backend.api.search_documents", return_value=[Document(page_content="Soto")]
        ), patch("backend.api.load_llm") as llm, self.assertLogs("backend.api", level="ERROR"):
            llm.return_value.invoke.side_effect = error
            response = client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["results"], [])
        self.assertNotIn("example.invalid", response.text)

    def test_browser_origin_does_not_receive_credentialed_cors(self):
        with TestClient(app) as client:
            response = client.get("/", headers={"Origin": "https://untrusted.example"})
        self.assertNotIn("access-control-allow-credentials", response.headers)
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_unsafe_generated_source_url_falls_back_to_account(self):
        result = {
            "query_summary": "Soto", "results": [{
                "rank": 1, "name": "Soto", "address": "Solo", "hours": "-", "price": "-",
                "categories": [], "description": "Soto.", "source": "instagram @contoh",
                "source_url": "javascript:alert(1)",
            }],
        }
        with TestClient(app) as client, patch(
            "backend.api.search_documents", return_value=[Document(page_content="Soto")]
        ), patch("backend.api.load_llm") as llm:
            llm.return_value.invoke.return_value = SimpleNamespace(content=json.dumps(result))
            response = client.post("/api/chat", json={"query": "soto"})
        self.assertEqual(response.status_code, 200)
        item = response.json()["results"][0]
        self.assertEqual(item["source"], "@contoh")
        self.assertEqual(item["source_url"], "https://instagram.com/contoh")
