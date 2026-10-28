"""不联网的自测：认名字、AI 回话怎么认、去重、两种 AI 接法、AI 关掉时页面放什么。

跑法: python3 -I tests/test_offline.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix="leaders-test-")
os.environ["LEADERS_DATA"] = TMP                     # 不碰真的库
os.environ["LEADERS_OUT"] = os.path.join(TMP, "leaders.json")
os.environ["LEADERS_NO_PROXY"] = "1"                 # 本机假接口不走代理
sys.path.insert(0, os.path.join(ROOT, "fetcher"))
import judge as J  # noqa: E402
import leaders as L  # noqa: E402
import people as P  # noqa: E402

PERSON = L.PERSON


def vid(person, i, **kw):
    v = {"id": f"{person[:5]:_<5}{i:06d}", "person": person, "title": f"t{i}", "channel": "c", "duration": 3600,
         "published": "2026-10-27T00:00:00Z"}
    v.update(kw)
    return v


class Names(unittest.TestCase):
    def test_full_and_surname(self):
        self.assertTrue(P.name_hits(PERSON["musk"], "Elon Musk on AI and Mars"))
        self.assertFalse(P.name_hits(PERSON["musk"], "Kimbal Musk interview"))           # 同姓家人
        self.assertTrue(P.name_hits(PERSON["feifei"], "Fei Fei Li: spatial intelligence"))  # 连字符可有可无
        self.assertTrue(P.name_hits(PERSON["feifei"], "Fei‑Fei Li talk"))                # 不断行连字符

    def test_short_name_needs_context(self):
        self.assertTrue(P.name_hits(PERSON["jensen"], "Jensen at GTC keynote"))
        self.assertFalse(P.name_hits(PERSON["jensen"], "Jensen Ackles panel"))
        self.assertFalse(P.name_hits(PERSON["dario"], "Daniela Amodei on Anthropic"))   # 只有姓又带 Daniela

    def test_role_only_when_allowed(self):
        self.assertTrue(P.name_hits(PERSON["lisasu"], "AMD's CEO on MI400"))
        self.assertFalse(P.name_hits(PERSON["lisasu"], "AMD's CEO on MI400", allow_role=False))


class Reply(unittest.TestCase):
    def test_json_items_variants(self):
        self.assertEqual(J.json_items('```json\n[{"i":0,"keep":true}]\n```'), [{"i": 0, "keep": True}])
        self.assertEqual(J.json_items('好的：\n{"i":0,"keep":false}\n{"i":1,"keep":true}'),
                         [{"i": 0, "keep": False}, {"i": 1, "keep": True}])
        self.assertIsNone(J.json_items("没有结果"))

    def test_judge_dup_rules(self):
        batch = [vid("jensen", 1), vid("jensen", 2), vid("lisasu", 3)]
        reply = json.dumps([
            {"i": 0, "keep": True, "kind": "演讲", "zh": "甲", "gist": "g", "dup": None},
            {"i": 1, "keep": True, "kind": "演讲", "zh": "乙", "gist": "g", "dup": 0},     # 跟 0 同一场
            {"i": 2, "keep": True, "kind": "访谈", "zh": "丙", "gist": "g", "dup": 0},     # 指到别人名下：不认，这条不下结论
        ])

        class Fake(J.Provider):
            name = "fake"

            def ask(self, prompt):
                return reply
        out = J.judge(Fake(), batch, {}, PERSON, os.path.join(TMP, "bad.txt"), lambda m: None)
        self.assertTrue(out[0]["keep"])
        self.assertFalse(out[1]["keep"])
        self.assertEqual(out[1]["dup"], batch[0]["id"])
        self.assertNotIn(2, out)

    def test_bad_reply_is_kept_for_reading(self):
        class Fake(J.Provider):
            name = "fake"

            def ask(self, prompt):
                return "我不知道"
        bad = os.path.join(TMP, "bad.txt")
        self.assertIsNone(J.judge(Fake(), [vid("ilya", 1)], {}, PERSON, bad, lambda m: None))
        with open(bad, encoding="utf-8") as f:
            self.assertIn("我不知道", f.read())


class _Handler(BaseHTTPRequestHandler):
    seen = {}

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _Handler.seen = {"auth": self.headers.get("Authorization"), "body": body}
        if body["model"] == "bad":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid key sk-test-123"}')
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"choices": [{"message": {"content": '[{"i":0,"keep":true}]'}}]}).encode())

    def log_message(self, *a):
        pass


class Providers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}/v1/chat/completions"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def test_openai_compatible(self):
        p = J.OpenAICompatible(self.url, "m1", "sk-test-123", 10)
        self.assertEqual(p.ask("你好"), '[{"i":0,"keep":true}]')
        self.assertEqual(_Handler.seen["auth"], "Bearer sk-test-123")
        self.assertEqual(_Handler.seen["body"]["messages"][0]["content"], "你好")
        self.assertEqual(_Handler.seen["body"]["model"], "m1")

    def test_openai_error_hides_key(self):
        p = J.OpenAICompatible(self.url, "bad", "sk-test-123", 10)
        self.assertIsNone(p.ask("x"))
        self.assertIn("401", p.last_error)
        self.assertNotIn("sk-test-123", p.last_error)

    def test_no_key_for_local_model(self):
        p = J.OpenAICompatible(self.url, "m1", "", 10)
        self.assertIsNotNone(p.ask("x"))
        self.assertIsNone(_Handler.seen["auth"])

    def test_command(self):
        cmd = f'"{sys.executable}" -I -c "import sys; sys.stdout.write(sys.stdin.read().upper())"'
        self.assertEqual(J.Command(cmd, 10).ask("abc"), "ABC")
        self.assertIsNone(J.Command(f'"{sys.executable}" -I -c "raise SystemExit(3)"', 10).ask("x"))

    def test_from_env_checks(self):
        os.environ.pop("LEADERS_AI_MODEL", None)
        with self.assertRaises(ValueError):
            J.from_env("openai")
        with self.assertRaises(ValueError):
            J.from_env("gpt")
        self.assertEqual(J.from_env("off").name, "off")


class Page(unittest.TestCase):
    def test_ai_off_shows_only_known_channels(self):
        vids = {}
        for v in (vid("jensen", 1, channel="NVIDIA", verified=True),                   # 认证的官方频道
                  vid("jensen", 2, channel="NVIDIA", verified=False),                  # 名字对但没认证
                  vid("altman", 3, channelId="UCSHZKyawb77ixDdsGog4iWA"),              # 访谈节目
                  vid("altman", 4, aiv=J.AI_VERSION, keep=False),                      # 判过不收
                  vid("altman", 5, aiv=J.AI_VERSION, keep=True, zh="中文")):          # 判过收
            vids[f"{v['person']}:{v['id']}"] = v
        doc = L.build_doc(vids, {}, [], None, "off", L.now_utc())
        got = {p["key"]: sorted(x["id"] for x in p["videos"]) for p in doc["people"] if p["videos"]}
        self.assertEqual(got, {"jensen": [vid("jensen", 1)["id"]],
                               "altman": sorted([vid("altman", 3)["id"], vid("altman", 5)["id"]])})

    def test_every_person_has_both_roles(self):
        # 网站中文版用 role、英文版用 role_en，名单里少写一个，英文版那个人就没有头衔
        doc = L.build_doc({}, {}, [], None, "off", L.now_utc())
        self.assertEqual(len(doc["people"]), len(L.PEOPLE))
        for p in doc["people"]:
            self.assertTrue(p["role"] and p["role_en"], p["key"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
