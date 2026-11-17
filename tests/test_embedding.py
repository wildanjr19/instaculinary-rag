import json
import unittest
from unittest.mock import patch

import requests

from src.embedding import JinaEmbedding


def response(status=200, data=None):
    result = requests.Response()
    result.status_code = status
    result.url = "https://api.jina.ai/v1/embeddings"
    result._content = json.dumps(data or {}).encode()
    result._content_consumed = True
    return result


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.embedding = JinaEmbedding(api_key="offline-test-key", dimensions=2, max_retries=3)
        self.request = patch("requests.sessions.Session.request")
        self.post = self.request.start()
        self.addCleanup(self.request.stop)
        self.sleep = patch("src.embedding.time.sleep")
        self.sleep.start()
        self.addCleanup(self.sleep.stop)

    def test_authentication_and_payload_errors_are_not_retried(self):
        for status in (400, 401, 403, 404):
            with self.subTest(status=status):
                self.post.reset_mock()
                self.post.return_value = response(status)
                with self.assertRaises(requests.HTTPError):
                    self.embedding.embed_query("soto")
                self.assertEqual(self.post.call_count, 1)

    def test_temporary_failure_is_retried_then_succeeds(self):
        self.post.side_effect = [response(429), response(data={"data": [{"index": 0, "embedding": [0.1, 0.2]}]})]
        self.assertEqual(self.embedding.embed_query("soto"), [0.1, 0.2])
        self.assertEqual(self.post.call_count, 2)

    def test_exhausted_timeout_preserves_timeout_type(self):
        self.post.side_effect = requests.Timeout("offline timeout")
        with self.assertRaises(requests.Timeout):
            self.embedding.embed_query("soto")
        self.assertEqual(self.post.call_count, 3)

    def test_invalid_documents_are_rejected_before_any_network_call(self):
        for texts in (["soto", "", "bakso"], ["soto", "   "], [None], [12]):
            with self.subTest(texts=texts), self.assertRaises(ValueError):
                self.embedding.embed_documents(texts)
        self.post.assert_not_called()

    def test_invalid_query_is_rejected_before_network(self):
        for text in ("", "   ", None):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.embedding.embed_query(text)
        self.post.assert_not_called()

    def test_output_order_matches_document_order(self):
        self.post.return_value = response(data={"data": [
            {"index": 1, "embedding": [0.3, 0.4]}, {"index": 0, "embedding": [0.1, 0.2]},
        ]})
        self.assertEqual(self.embedding.embed_documents(["soto", "bakso"]), [[0.1, 0.2], [0.3, 0.4]])

    def test_malformed_vectors_are_not_retried_or_uploaded(self):
        invalid_data = [
            [], [{"embedding": [0.1]}], [{"embedding": [0.1, float("nan")]}],
            [{"index": 1, "embedding": [0.1, 0.2]}],
        ]
        for data in invalid_data:
            with self.subTest(data=data):
                self.post.reset_mock()
                self.post.return_value = response(data={"data": data})
                with self.assertRaises(ValueError):
                    self.embedding.embed_query("soto")
                self.assertEqual(self.post.call_count, 1)

    def test_outbound_call_has_timeout_and_does_not_follow_redirects(self):
        self.post.return_value = response(data={"data": [{"embedding": [0.1, 0.2]}]})
        self.embedding.embed_query("soto")
        kwargs = self.post.call_args.kwargs
        self.assertFalse(kwargs.get("allow_redirects", True))
        self.assertTrue(all(0 < limit <= 30 for limit in kwargs["timeout"]))

    def test_redirects_and_tls_errors_fail_without_retry(self):
        self.post.return_value = response(302)
        with self.assertRaises(requests.HTTPError):
            self.embedding.embed_query("soto")
        self.assertEqual(self.post.call_count, 1)
        self.post.reset_mock()
        self.post.side_effect = requests.exceptions.SSLError("offline certificate error")
        with self.assertRaises(requests.exceptions.SSLError):
            self.embedding.embed_query("soto")
        self.assertEqual(self.post.call_count, 1)
