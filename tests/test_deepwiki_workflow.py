import json
import os
import tempfile
import unittest
from pathlib import Path

from deepwiki_triage import classify_deepwiki_response, save_deepwiki_response
from repositories import deepwiki_base_url, load_repository_urls
from run_deepwiki_submit import _submitted_filenames
from run_build_deepwiki_briefs import build_briefs, select_rows
from run_export_local_proof_queue import export_queue


class DeepWikiWorkflowTest(unittest.TestCase):
    def test_brief_builder_selects_high_priority_rows(self):
        rows = [
            {
                "score": 10,
                "next_action": "watch",
                "name": "Watch Only",
                "chain": "bsc",
                "address": "0x1111111111111111111111111111111111111111",
            },
            {
                "score": 80,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Unverified Funded",
                "chain": "bsc",
                "address": "0x2222222222222222222222222222222222222222",
                "tvl_usd": 500000,
                "reasons": ["unverified_contract:20"],
            },
        ]

        selected = select_rows(rows, limit=5)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["name"], "Unverified Funded")

    def test_build_briefs_writes_schema_payload(self):
        rows = [
            {
                "score": 75,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "Dex Bot",
                "chain": "base",
                "address": "0x3333333333333333333333333333333333333333",
                "tvl_usd": 15000,
                "tags": ["flashloan_user"],
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                written = build_briefs(rows, "deepwiki_briefs", limit=1)
                payload = json.loads(written[0].read_text())
            finally:
                os.chdir(old_cwd)

        self.assertEqual(payload["schema_version"], "sentinel-candidate-brief-v1")
        self.assertEqual(payload["score"]["next_action"], "trace_bot_contract_then_target_protocols")
        self.assertIn("gate_question", payload["deepwiki_focus"])

    def test_deepwiki_triage_routes_needs_live_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_env = dict(os.environ)
            os.environ["NEEDS_LIVE_CONTEXT_DIR"] = str(Path(tmp) / "needs_live_context")
            try:
                content = '{"verdict":"NEEDS_LIVE_CONTEXT","paid_scope_match":"fund_extraction"}'
                self.assertEqual(classify_deepwiki_response(content), "needs_live_context")
                saved = save_deepwiki_response(content, "https://deepwiki.com/example/protocol-sentinel--001")
            finally:
                os.environ.clear()
                os.environ.update(old_env)

        self.assertIsNotNone(saved)
        self.assertEqual(Path(saved).parent.name, "needs_live_context")

    def test_repository_urls_filter_stale_protocol_repos(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repositories.json"
            path.write_text(
                json.dumps(
                    [
                        "https://deepwiki.com/example/protocol-sentinel--001",
                        "https://deepwiki.com/example/midnight--001",
                        "https://deepwiki.com/example/protocol-sentinel",
                    ]
                )
            )

            urls = load_repository_urls("protocol-sentinel", str(path))

        self.assertEqual(
            urls,
            [
                "https://deepwiki.com/example/protocol-sentinel--001",
                "https://deepwiki.com/example/protocol-sentinel",
            ],
        )

    def test_deepwiki_base_url_uses_rotation_when_run_number_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repositories.json"
            path.write_text(
                json.dumps(
                    [
                        "https://deepwiki.com/example/protocol-sentinel--001",
                        "https://deepwiki.com/example/protocol-sentinel--002",
                    ]
                )
            )
            old_env = dict(os.environ)
            os.environ["GITHUB_RUN_NUMBER"] = "2"
            try:
                url = deepwiki_base_url("protocol-sentinel", "source/repo", str(path))
            finally:
                os.environ.clear()
                os.environ.update(old_env)

        self.assertEqual(url, "https://deepwiki.com/example/protocol-sentinel--002")

    def test_export_local_proof_queue_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "proof_gate_results"
            output_dir = Path(tmp) / "local_proof_queue"
            input_dir.mkdir()
            (input_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "verdict": "NEEDS_LOCAL_PROOF",
                        "paid_scope_match": "reward_extraction",
                        "candidate": {"chain": "bsc", "address": "0x4444444444444444444444444444444444444444"},
                        "hard_gates": {"unprivileged_attacker": True},
                        "local_proof_required": {"test_type": "fork"},
                    }
                )
            )

            written = export_queue([str(input_dir)], str(output_dir), limit=10)
            content = written[0].read_text()

        self.assertIn("Local Proof Queue Item", content)
        self.assertIn("prove corecritical", content)

    def test_submitted_filenames_reads_existing_submissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.json").write_text(json.dumps({"filename": "001-target.json"}))
            (root / "bad.json").write_text("{")

            names = _submitted_filenames(root)

        self.assertEqual(names, {"001-target.json"})


if __name__ == "__main__":
    unittest.main()
