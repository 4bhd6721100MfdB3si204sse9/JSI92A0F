import json
import tempfile
import unittest
from pathlib import Path

from run_materialize_foundry_target import materialize_targets, normalize_candidate


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
            input_dir = Path(tmp) / "deepwiki_briefs"
            output_dir = Path(tmp) / "foundry_targets"
            input_dir.mkdir()
            (input_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "candidate": {
                            "name": "Dex Bot",
                            "chain": "bsc",
                            "address": "0x4444444444444444444444444444444444444444",
                            "entity_type": "bot_contract",
                        },
                        "score": {"value": 75, "next_action": "trace_bot_contract_then_target_protocols"},
                        "value_at_risk": {"usd": 18000},
                    }
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


if __name__ == "__main__":
    unittest.main()
