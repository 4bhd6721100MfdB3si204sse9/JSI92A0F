import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from sentinel.cli import main
from sentinel.explorer import load_explorer_snapshot
from sentinel.scoring import score_candidate


class ExplorerCollectorTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(Path("config/sentinel.json").read_text())

    def test_snapshot_collector_classifies_contract_risks(self):
        candidates = load_explorer_snapshot("examples/explorer_snapshot.json", self.config, 25)
        by_name = {candidate.name: candidate for candidate in candidates}

        self.assertEqual(by_name["Unverified Funded Treasury"].entity_type, "unverified_contract")
        self.assertEqual(by_name["Unknown Spike Vault"].entity_type, "unknown_protocol")
        self.assertEqual(by_name["New Yield Migrator"].funding_cluster_id, "closed-yield-cluster-001")
        self.assertEqual(by_name["DexPathExecutor Bot"].entity_type, "bot_contract")
        self.assertNotIn("Small Verified Helper", by_name)

    def test_snapshot_scoring_routes_each_risk_to_expected_action(self):
        candidates = load_explorer_snapshot("examples/explorer_snapshot.json", self.config, 25)
        actions = {
            scored.candidate.name: scored.next_action
            for scored in (score_candidate(candidate, self.config) for candidate in candidates)
        }

        self.assertEqual(
            actions["Unverified Funded Treasury"],
            "reverse_engineer_unverified_funded_contract",
        )
        self.assertEqual(actions["Unknown Spike Vault"], "price_spike_recon_then_source_check")
        self.assertEqual(actions["New Yield Migrator"], "investigate_redeploy_funding_cluster")
        self.assertEqual(actions["DexPathExecutor Bot"], "trace_bot_contract_then_target_protocols")

    def test_cli_writes_snapshot_queue_and_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "discover",
                        "--source",
                        "explorer_snapshot",
                        "--input",
                        "examples/explorer_snapshot.json",
                        "--output",
                        tmpdir,
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("bot_trace=1", output)
            self.assertIn("unverified=1", output)
            self.assertIn("price_spike=1", output)
            self.assertIn("redeploy_cluster=1", output)

            run_dirs = list(Path(tmpdir).iterdir())
            self.assertEqual(len(run_dirs), 1)
            queue = (run_dirs[0] / "triage_queue.md").read_text()
            self.assertIn("reverse_engineer_unverified_funded_contract", queue)
            self.assertIn("investigate_redeploy_funding_cluster", queue)


if __name__ == "__main__":
    unittest.main()

