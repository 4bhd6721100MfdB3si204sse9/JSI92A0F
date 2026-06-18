import json
import os
import tempfile
import unittest
from pathlib import Path

from run_materialize_foundry_target import main, materialize_targets, normalize_candidate


class FoundryMaterializerTest(unittest.TestCase):
    def test_normalize_candidate_from_sentinel_brief(self):
        payload = {
            "candidate": {
                "name": "Unverified Treasury",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "entity_type": "unverified_contract",
            },
            "score": {"value": 80, "next_action": "reverse_engineer_unverified_funded_contract"},
            "value_at_risk": {"usd": 500000},
        }

        candidate = normalize_candidate(payload, Path("candidate.json"))

        self.assertEqual(candidate["chain"], "bsc")
        self.assertEqual(candidate["address"], "0x5555555555555555555555555555555555555555")
        self.assertEqual(candidate["next_action"], "reverse_engineer_unverified_funded_contract")

    def test_normalize_candidate_from_proof_gate_result(self):
        payload = {
            "active_target": {
                "chain": "base",
                "address": "0x6666666666666666666666666666666666666666",
            },
            "candidate": {
                "title_or_claim": "Spike vault share drift",
            },
            "hard_gates": {"unprivileged_attacker": True},
            "paid_scope_match": "protocol_value_drain",
        }

        candidate = normalize_candidate(payload, Path("proof_gate.json"))

        self.assertEqual(candidate["chain"], "base")
        self.assertEqual(candidate["address"], "0x6666666666666666666666666666666666666666")
        self.assertEqual(candidate["paid_scope_match"], "protocol_value_drain")

    def test_materialize_targets_writes_foundry_repo_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "local_proof_queue"
            output_dir = Path(tmp) / "foundry_targets"
            input_dir.mkdir()
            (input_dir / "candidate.md").write_text(
                "\n".join(
                    [
                        "# Local Proof Queue Item",
                        "",
                        "- verdict: `NEEDS_LOCAL_PROOF`",
                        "- chain: `bsc`",
                        "- address: `0x4444444444444444444444444444444444444444`",
                        "- paid_scope_match: `fund_extraction`",
                        "",
                    ]
                )
            )

            written = materialize_targets([str(input_dir)], str(output_dir), limit=5)
            target = written[0]

            self.assertTrue((target / "foundry.toml").is_file())
            self.assertTrue((target / "addresses.json").is_file())
            self.assertTrue((target / "live_state.json").is_file())
            self.assertTrue((target / "test" / "LiveStateProof.t.sol").is_file())
            self.assertTrue((target / "script" / "Snapshot.s.sol").is_file())
            self.assertIn("forge test", (target / "README.md").read_text())
            self.assertIn("TARGET_ADDRESS", (target / ".env.example").read_text())

    def test_materialize_targets_skips_rejected_proof_gate_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "proof_gate_results"
            output_dir = Path(tmp) / "foundry_targets"
            input_dir.mkdir()
            (input_dir / "rejected.json").write_text(
                json.dumps(
                    {
                        "verdict": "REJECT",
                        "candidate_context": {
                            "chain": "bsc",
                            "address": "0x238a358808379702088667322f80ac48bad5e6c4",
                        },
                    }
                )
            )

            with self.assertRaises(FileNotFoundError):
                materialize_targets([str(input_dir)], str(output_dir), limit=5)

    def test_materialize_targets_accepts_candidate_context_for_proof_gate_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "proof_gate_results"
            output_dir = Path(tmp) / "foundry_targets"
            input_dir.mkdir()
            (input_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "verdict": "NEEDS_LOCAL_PROOF",
                        "candidate_context": {
                            "chain": "bsc",
                            "address": "0x238a358808379702088667322f80ac48bad5e6c4",
                        },
                    }
                )
            )

            written = materialize_targets([str(input_dir)], str(output_dir), limit=5)

        self.assertEqual(written[0].name, "bsc-0x238a358808379702088667322f80ac48bad5e6c4")

    def test_materialize_cli_refuses_stale_active_files_during_current_run_without_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                Path("local_proof_queue").mkdir()
                Path("local_proof_queue/candidate.md").write_text(
                    "\n".join(
                        [
                            "# Local Proof Queue Item",
                            "",
                            "- verdict: `NEEDS_LOCAL_PROOF`",
                            "- chain: `bsc`",
                            "- address: `0x4444444444444444444444444444444444444444`",
                            "",
                        ]
                    )
                )
                Path("state").mkdir()
                Path("state/current_run.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "sentinel-run-state-v1",
                            "run_id": "current",
                            "manifest_paths": {},
                        }
                    )
                )

                with self.assertRaises(FileNotFoundError):
                    main(["--output", "foundry_targets"])
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
