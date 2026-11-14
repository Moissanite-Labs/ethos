import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mep.server import dispatch_tool_call, handle_jsonrpc_message

REPO_ROOT = Path(__file__).resolve().parent.parent


def make_tree(root: Path) -> None:
    (root / "principles").mkdir(parents=True)
    (root / "principles" / "ethos.md").write_text(
        "# Ethos\n\nRead before acting. Verify before claiming.\n", encoding="utf-8"
    )
    (root / "README.md").write_text("# test ethos\n", encoding="utf-8")


class JsonRpcTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_tree(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_initialize(self):
        reply = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            self.root,
        )
        self.assertEqual(reply["result"]["serverInfo"]["name"], "mep")
        self.assertEqual(reply["result"]["protocolVersion"], "2025-03-26")
        self.assertIn("instructions", reply["result"])

    def test_tools_list_has_13_tools(self):
        reply = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, self.root)
        self.assertEqual(len(reply["result"]["tools"]), 13)

    def test_tools_call_capabilities(self):
        reply = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ethos_capabilities", "arguments": {}}},
            self.root,
        )
        payload = reply["result"]["structuredContent"]
        self.assertEqual(payload["mep_version"], "0.1")

    def test_unknown_tool_error(self):
        reply = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nope"}},
            self.root,
        )
        self.assertEqual(reply["error"]["code"], -32602)

    def test_tool_error_is_structured(self):
        reply = handle_jsonrpc_message(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "ethos_get", "arguments": {"path": "../outside.md"}},
            },
            self.root,
        )
        self.assertTrue(reply["result"]["isError"])

    def test_resources(self):
        listed = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 6, "method": "resources/list"}, self.root)
        self.assertEqual({r["uri"] for r in listed["result"]["resources"]}, {"ethos://about", "ethos://status", "ethos://revisions"})
        about = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 7, "method": "resources/read", "params": {"uri": "ethos://about"}}, self.root
        )
        self.assertIn("mep_version", about["result"]["contents"][0]["text"])
        doc = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 8, "method": "resources/read", "params": {"uri": "ethos://document/principles/ethos.md"}},
            self.root,
        )
        self.assertIn("Read before acting", doc["result"]["contents"][0]["text"])
        bad = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 9, "method": "resources/read", "params": {"uri": "ethos://document/../x.md"}},
            self.root,
        )
        self.assertIn("error", bad)

    def test_prompts(self):
        listed = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 10, "method": "prompts/list"}, self.root)
        self.assertEqual({p["name"] for p in listed["result"]["prompts"]}, {"reflect", "review"})
        got = handle_jsonrpc_message(
            {"jsonrpc": "2.0", "id": 11, "method": "prompts/get", "params": {"name": "reflect", "arguments": {"situation": "shipped a fix"}}},
            self.root,
        )
        self.assertIn("shipped a fix", got["result"]["messages"][0]["content"]["text"])

    def test_learning_off_blocks_writes(self):
        (self.root / ".mep").mkdir()
        (self.root / ".mep" / "learning").write_text("off\n", encoding="utf-8")
        for tool in ("ethos_propose", "ethos_decide", "ethos_correct"):
            payload = dispatch_tool_call(
                tool,
                {
                    "statement": "x",
                    "origin": "inferred",
                    "confidence": 0.5,
                    "source_kind": "user",
                    "source_reference": "t",
                    "owner_id": "o",
                    "author_id": "a",
                    "target_revision_id": "rev-x",
                    "decision": "approve",
                },
                self.root,
            )
            self.assertEqual(payload["learning"], "off")
            self.assertFalse(payload["written"])


class StdioSmokeTests(unittest.TestCase):
    def test_stdio_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_tree(root)
            env = dict(os.environ)
            env["MEP_ROOT"] = str(root)
            messages = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "ping"},
            ]
            stdin = "".join(json.dumps(m) + "\n" for m in messages).encode("utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mep", "serve"],
                input=stdin,
                capture_output=True,
                cwd=str(REPO_ROOT),
                env=env,
                timeout=30,
            )
            replies = [json.loads(line) for line in proc.stdout.decode("utf-8").splitlines() if line.strip()]
            by_id = {r.get("id"): r for r in replies}
            self.assertEqual(by_id[1]["result"]["serverInfo"]["name"], "mep")
            self.assertEqual(len(by_id[2]["result"]["tools"]), 13)
            self.assertEqual(by_id[3]["result"], {})


if __name__ == "__main__":
    unittest.main()
