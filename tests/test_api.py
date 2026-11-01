"""Integration tests for the local Vonza Core API; no external network calls."""
import http.client
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import server


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(cls.temp.name) / "test.sqlite3"
        server.initialize()
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.httpd.server_port

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def api(self, path, method="GET", data=None, cookie=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        hdr = {"X-Vonza-Request": "1"}
        payload = None
        if data is not None:
            hdr["Content-Type"] = "application/json"
            payload = json.dumps(data)
        if cookie:
            hdr["Cookie"] = cookie
        if headers:
            hdr.update(headers)
        connection.request(method, path, payload, hdr)
        res = connection.getresponse()
        body = json.loads(res.read().decode())
        out = (res.status, body, res.getheader("Set-Cookie"))
        connection.close()
        return out

    def test_01_setup_required_and_authentication(self):
        self.assertEqual(self.api("/health")[0], 200)
        self.assertFalse(self.api("/api/auth/status")[1]["setup"])
        self.assertEqual(self.api("/api/tasks")[0], 401)
        self.assertEqual(self.api("/api/auth/setup", "POST", {"password": "short"})[0], 400)
        status, body, cookie = self.api("/api/auth/setup", "POST", {"password": "fancy-passphrase-12345"})
        self.assertEqual(status, 201)
        self.assertTrue(body["ok"])
        self.assertIn("HttpOnly", cookie)
        self.__class__.cookie = cookie.split(";", 1)[0]
        self.assertEqual(self.api("/api/auth/setup", "POST", {"password": "another-valid-passphrase"})[0], 409)
        self.assertEqual(self.api("/api/auth/status", cookie=self.cookie)[1]["authenticated"], True)
        self.assertEqual(self.api("/api/auth/status")[1]["authenticated"], False)

    def test_02_memory_requires_explicit_consent_and_deletes(self):
        cookie = self.cookie
        self.assertEqual(self.api("/api/memories", "POST", {"content": "I like coffee"}, cookie)[0], 400)
        st, data, _ = self.api("/api/memories", "POST", {"content": "I like coffee", "consent": True}, cookie)
        self.assertEqual(st, 201)
        ident = data["id"]
        memories = self.api("/api/memories", cookie=cookie)[1]["memories"]
        self.assertEqual(memories[0]["content"], "I like coffee")
        self.assertEqual(self.api("/api/memories/" + ident, "PATCH", {"content": "I prefer tea"}, cookie)[0], 200)
        self.assertEqual(self.api("/api/memories/" + ident, "DELETE", cookie=cookie)[0], 200)
        self.assertFalse(self.api("/api/memories", cookie=cookie)[1]["memories"])

    def test_03_tasks_crud(self):
        cookie = self.cookie
        st, data, _ = self.api("/api/tasks", "POST", {"title": "Ship MVP", "due": "2026-11-15"}, cookie)
        self.assertEqual(st, 201)
        ident = data["id"]
        tasks = self.api("/api/tasks", cookie=cookie)[1]["tasks"]
        self.assertEqual(tasks[0]["title"], "Ship MVP")
        self.assertEqual(self.api("/api/tasks/" + ident, "PATCH", {"done": True, "title": "Test MVP"}, cookie)[0], 200)
        tasks = self.api("/api/tasks", cookie=cookie)[1]["tasks"]
        self.assertEqual(tasks[0]["done"], 1)
        self.assertEqual(self.api("/api/tasks/" + ident, "DELETE", cookie=cookie)[0], 200)
        self.assertEqual(self.api("/api/tasks", cookie=cookie)[1]["tasks"], [])

    def test_04_conversation_and_missing_key(self):
        cookie = self.cookie
        st, result, _ = self.api("/api/conversations", "POST", {"title": "Ideas"}, cookie)
        self.assertEqual(st, 201)
        cid = result["id"]
        self.assertEqual(self.api("/api/chat", "POST", {"conversation_id": cid, "message": "Hello"}, cookie)[0], 503)
        messages = self.api("/api/conversations/" + cid + "/messages", cookie=cookie)[1]["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(self.api("/api/conversations/" + cid, "PATCH", {"title": "Brainstorming"}, cookie)[0], 200)
        self.assertEqual(self.api("/api/conversations/" + cid, "DELETE", cookie=cookie)[0], 200)
        self.assertEqual(self.api("/api/conversations/" + cid + "/messages", cookie=cookie)[0], 404)

    def test_05_provider_request_and_safe_auth(self):
        st, item, _ = self.api("/api/conversations", "POST", {"title": "Provider test"}, self.cookie)
        self.assertEqual(st, 201)
        original = server.urllib.request.urlopen

        def fake(request, timeout=None):
            self.assertEqual(request.full_url, "https://api.openai.com/v1/chat/completions")
            self.assertTrue(request.headers["Authorization"].startswith("Bearer test-"))
            payload = json.loads(request.data)
            self.assertEqual(payload["messages"][-1]["content"], "Szia")
            return io.BytesIO(b'{"choices":[{"message":{"content":"Szia! Miben segithetek?"}}]}')

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-never-commit", "OPENAI_MODEL": "gpt-4.1-mini"}):
            with patch.object(server.urllib.request, "urlopen", side_effect=fake):
                st, response, _ = self.api("/api/chat", "POST",
                                           {"conversation_id": item["id"], "message": "Szia"}, self.cookie)
        self.assertEqual(st, 200)
        self.assertIn("Szia!", response["reply"])
        st, content, _ = self.api("/api/conversations/" + item["id"] + "/messages", cookie=self.cookie)
        self.assertEqual(st, 200)
        self.assertEqual(len(content["messages"]), 2)
        self.assertEqual(self.api("/api/tasks", headers={"Cookie": "vonza_session=invalid"})[0], 401)

    def test_06_method_validation(self):
        self.assertEqual(self.api("/api/tasks", "POST", {"title": "Bad"}, self.cookie,
                                  headers={"X-Vonza-Request": "0"})[0], 403)
        self.assertEqual(self.api("/api/tasks", "POST", {"title": "Bad"}, self.cookie,
                                  headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.api("/api/tasks/no-id", "DELETE", cookie=self.cookie)[0], 404)

    def test_07_static_page_exists(self):
        page = server.STATIC.read_text(encoding="utf-8")
        for part in ("id=\"chat\"", "id=\"tasks\"", "id=\"memory\"",
                     "id=\"microphone\"", "id=\"auth-form\"", "textContent"):
            self.assertIn(part, page)

    def test_075_local_api_setup_without_terminal(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            st, result, _ = self.api("/api/ai/status", cookie=self.cookie)
            self.assertEqual(st, 200)
            self.assertEqual(result["configured"], False)
            self.assertNotIn("key", result)
            self.assertEqual(self.api("/api/ai/key", "POST", {"key": "short"}, self.cookie)[0], 400)
            self.assertEqual(self.api("/api/ai/key", "POST", {"key": "not-a-real-test-token-12345678"})[0], 401)
            st, result, _ = self.api("/api/ai/key", "POST",
                                     {"key": "not-a-real-test-token-12345678"}, self.cookie)
            self.assertEqual(st, 200)
            self.assertEqual(result, {"ok": True, "configured": True})
            key_file = server.DB_PATH.parent / "openai_api_key"
            self.assertTrue(key_file.exists())
            self.assertEqual(server.current_api_key(), "not-a-real-test-token-12345678")
            self.assertEqual(self.api("/api/ai/status", cookie=self.cookie)[1]["source"], "local")
            self.assertEqual(self.api("/api/ai/key", "DELETE", cookie=self.cookie)[0], 200)
            self.assertFalse(key_file.exists())
            self.assertFalse(self.api("/api/ai/status", cookie=self.cookie)[1]["configured"])

    def test_08_logout_revokes_session(self):
        st, _, cookie = self.api("/api/auth/logout", "POST", {}, self.cookie)
        self.assertEqual(st, 200)
        self.assertIn("Max-Age=0", cookie)
        self.assertEqual(self.api("/api/tasks", cookie=self.cookie)[0], 401)
        self.assertEqual(self.api("/api/auth/login", "POST", {"password": "wrong-password"})[0], 401)
        st, _, cookie = self.api("/api/auth/login", "POST", {"password": "fancy-passphrase-12345"})
        self.assertEqual(st, 200)


if __name__ == "__main__":
    unittest.main()
