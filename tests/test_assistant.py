import json
import urllib.error
import urllib.request

from conftest import make_profile
from engine import assistant as S
from engine.constants import ELIGIBLE


def test_context_has_no_name_and_matches_engine(kb, weak):
    p = {**weak, "name": "SECRET PERSON"}
    ctx = S.build_context(p, kb)
    assert "SECRET" not in json.dumps(ctx)
    assert len(ctx["programmes"]) == len(kb["programmes"])


def test_offline_answers_are_grounded(kb, weak):
    ctx = S.build_context(weak, kb)
    cse = next(p for p in ctx["programmes"] if p["id"] == "btech_cse")
    text = S.local_answer("Why am I not eligible for B.Tech Computer Science?", weak, kb)
    assert cse["name"] in text and cse["decision"] in text and "needed 60%" in text
    assert "Eligible" in S.local_answer("Which programmes am I eligible for?", weak, kb)
    assert "Try one of these" in S.local_answer("hello", weak, kb)


class _Resp:
    def __init__(self, body): self.body = body
    def read(self): return json.dumps(self.body).encode()
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_claude_mode_and_fallbacks(kb, weak, monkeypatch):
    seen = {}

    def ok(req, timeout=0):
        seen["body"] = json.loads(req.data)
        return _Resp({"content": [{"type": "text", "text": "hi"}]})
    monkeypatch.setattr(urllib.request, "urlopen", ok)
    out = S.answer("q", [{"role": "assistant", "content": "x", "source": "offline"}], weak, kb, "claude", "key")
    assert out["source"] == "claude" and seen["body"]["messages"][0] == {"role": "user", "content": "q"}
    assert "FACTS" in seen["body"]["system"]

    def bad(req, timeout=0):
        raise urllib.error.URLError("down")
    monkeypatch.setattr(urllib.request, "urlopen", bad)
    out = S.answer("Which programmes am I eligible for?", [], weak, kb, "claude", "key")
    assert out["source"] == "offline" and "unreachable" in out["notice"]
    assert S.answer("hi", [], weak, kb, "claude", "")["notice"]
    assert S.answer("hi", [], weak, kb, "offline")["notice"] is None


def test_assistant_never_changes_decisions(kb, strong):
    ctx = S.build_context(strong, kb)
    assert next(p for p in ctx["programmes"] if p["id"] == "btech_cse")["decision"] == ELIGIBLE
