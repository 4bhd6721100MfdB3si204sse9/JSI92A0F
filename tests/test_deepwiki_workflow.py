import json
import os
import tempfile
import unittest
from pathlib import Path

from deepwiki_triage import classify_deepwiki_response, save_deepwiki_response
from deepwiki_client import DeepWikiClient, _origin_for_url
from repositories import deepwiki_base_url, load_repository_urls
from run_deepwiki_submit import _submitted_filenames
from run_build_deepwiki_briefs import build_briefs, find_latest_eligible_scored_run, select_rows
from run_generate_deepwiki_pending import move_pending
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
                stale_dir = Path("deepwiki_briefs")
                stale_dir.mkdir()
                (stale_dir / "stale.json").write_text("{}")
                written = build_briefs(rows, "deepwiki_briefs", limit=1)
                payload = json.loads(written[0].read_text())
            finally:
                os.chdir(old_cwd)

        self.assertEqual(payload["schema_version"], "sentinel-candidate-brief-v1")
        self.assertEqual(payload["score"]["next_action"], "trace_bot_contract_then_target_protocols")
        self.assertIn("gate_question", payload["deepwiki_focus"])
        self.assertFalse((Path(tmp) / "deepwiki_briefs" / "stale.json").exists())

    def test_latest_eligible_run_skips_new_empty_run(self):
        rows_real = [
            {
                "score": 55,
                "next_action": "recon_bravo_then_corecritical",
                "name": "Real Target",
                "chain": "bsc",
                "address": "0x238a358808379702088667322f80ac48bad5e6c4",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_run = root / "20260617T071239Z"
            empty_run = root / "20260617T074248Z"
            real_run.mkdir()
            empty_run.mkdir()
            (real_run / "candidates_scored.json").write_text(json.dumps(rows_real))
            (empty_run / "candidates_scored.json").write_text(json.dumps([]))
            os.utime(real_run / "candidates_scored.json", (1000, 1000))
            os.utime(empty_run / "candidates_scored.json", (2000, 2000))

            selected = find_latest_eligible_scored_run(root, limit=25)

        self.assertEqual(selected.parent.name, "20260617T071239Z")

    def test_move_pending_uses_manifest_and_rejects_placeholder_stale_files(self):
        real_brief = {
            "candidate": {
                "chain": "bsc",
                "address": "0x238a358808379702088667322f80ac48bad5e6c4",
                "name": "Real Target",
            }
        }
        placeholder_brief = {
            "candidate": {
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "name": "Fake Target",
            }
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "deepwiki_briefs"
            pending = root / "deepwiki_pending"
            state = root / "state" / "latest_deepwiki_briefs.json"
            source.mkdir()
            (source / "real.json").write_text(json.dumps(real_brief))
            (source / "stale-placeholder.json").write_text(json.dumps(placeholder_brief))
            state.parent.mkdir()
            state.write_text(json.dumps([str(source / "real.json")]))

            moved = move_pending(source, pending, manifest_path=state)

            self.assertEqual([path.name for path in moved], ["real.json"])
            self.assertTrue((pending / "real.json").exists())
            self.assertTrue((source / "stale-placeholder.json").exists())
            self.assertEqual(json.loads(state.read_text()), [str(pending / "real.json")])

            state.write_text(json.dumps([str(source / "stale-placeholder.json")]))
            with self.assertRaises(ValueError):
                move_pending(source, pending, manifest_path=state)

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

    def test_browser_clipboard_reader_uses_page_origin(self):
        class FakeDriver:
            current_url = "https://deepwiki.com/search/example?mode=deep"

            def __init__(self):
                self.permissions_origin = None

            def execute_cdp_cmd(self, command, payload):
                self.permissions_origin = payload["origin"]

            def execute_async_script(self, script):
                return '{"verdict":"NEEDS_LOCAL_PROOF"}'

        client = DeepWikiClient.__new__(DeepWikiClient)
        client.driver = FakeDriver()
        client.base_url = "https://deepwiki.com/example/repo"

        self.assertEqual(client._read_browser_clipboard(), '{"verdict":"NEEDS_LOCAL_PROOF"}')
        self.assertEqual(client.driver.permissions_origin, "https://deepwiki.com")

    def test_origin_for_url_defaults_to_deepwiki(self):
        self.assertEqual(_origin_for_url("not-a-url"), "https://deepwiki.com")


if __name__ == "__main__":
    unittest.main()
