import json
import tempfile
import unittest
from datetime import datetime, timezone
import os
from pathlib import Path

from sentinel.cli import main
from sentinel.targets import generate_live_targets, refresh_live_targets


class TargetGeneratorTest(unittest.TestCase):
    def test_generate_live_targets_prefers_high_risk_actions_and_dedupes(self):
        rows = [
            {
                "score": 90,
                "next_action": "proxy_change_live_funds",
                "name": "Live Proxy",
                "chain": "base",
                "address": "0x9999999999999999999999999999999999999999",
            },
            {
                "score": 147,
                "next_action": "investigate_redeploy_funding_cluster",
                "name": "New Yield Migrator",
                "chain": "bsc",
                "address": "0x7777777777777777777777777777777777777777",
                "entity_type": "unknown_protocol",
                "category": "migrator vault",
                "tags": ["suspected_rug_redeploy"],
            },
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Unverified Funded Treasury",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "entity_type": "unverified_contract",
                "category": "treasury",
            },
            {
                "score": 75,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "DexPathExecutor Bot",
                "chain": "bsc",
                "address": "0x4444444444444444444444444444444444444444",
                "entity_type": "bot_contract",
                "category": "mev executor",
            },
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Unverified Funded Treasury Duplicate",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "entity_type": "unverified_contract",
                "category": "treasury",
            },
            {
                "score": 10,
                "next_action": "watch_mainstream",
                "name": "Lido",
                "chain": "ethereum",
                "address": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            },
        ]

        targets = generate_live_targets(rows, max_targets=10)

        self.assertEqual([target["label"] for target in targets], [
            "Live Proxy",
            "New Yield Migrator",
            "Unverified Funded Treasury",
            "DexPathExecutor Bot",
        ])
        self.assertEqual(targets[0]["metadata"]["next_action"], "proxy_change_live_funds")

    def test_refresh_live_targets_writes_json(self):
        rows = [
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Unverified Funded Treasury",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "entity_type": "unverified_contract",
                "category": "treasury",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "candidates_scored.json"
            output_path = Path(tmpdir) / "live_targets.json"
            input_path.write_text(json.dumps(rows))

            targets = refresh_live_targets(input_path, output_path, max_targets=10)

            payload = json.loads(output_path.read_text())
            self.assertEqual(len(targets), 1)
            self.assertEqual(payload["targets"][0]["address"], "0x5555555555555555555555555555555555555555")
            self.assertEqual(payload["targets"][0]["metadata"]["entity_type"], "unverified_contract")

    def test_refresh_live_targets_creates_output_parent_directory(self):
        rows = [
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Unverified Funded Treasury",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "entity_type": "unverified_contract",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "candidates_scored.json"
            output_path = root / "nested" / "live_targets.json"
            input_path.write_text(json.dumps(rows))

            targets = refresh_live_targets(input_path, output_path, max_targets=10)

            self.assertEqual(len(targets), 1)
            self.assertTrue(output_path.is_file())

    def test_refresh_latest_run_picks_most_recent_scored_queue(self):
        rows_old = [
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Old Target",
                "chain": "bsc",
                "address": "0x1111111111111111111111111111111111111111",
                "entity_type": "unverified_contract",
            }
        ]
        rows_new = [
            {
                "score": 80,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "New Target",
                "chain": "bsc",
                "address": "0x2222222222222222222222222222222222222222",
                "entity_type": "bot_contract",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            old_run = root / "20260614T000000Z"
            new_run = root / "20260614T010000Z"
            old_run.mkdir()
            new_run.mkdir()
            (old_run / "candidates_scored.json").write_text(json.dumps(rows_old))
            (new_run / "candidates_scored.json").write_text(json.dumps(rows_new))

            now = datetime.now(timezone.utc).timestamp()
            older = now - 120
            newer = now - 60
            Path(old_run / "candidates_scored.json").touch()
            Path(new_run / "candidates_scored.json").touch()
            os.utime(old_run / "candidates_scored.json", (older, older))
            os.utime(new_run / "candidates_scored.json", (newer, newer))

            output_path = root / "live_targets.json"
            from sentinel.targets import refresh_live_targets_from_latest_run

            latest, targets = refresh_live_targets_from_latest_run(root, output_path, max_targets=10)

            self.assertEqual(latest.parent.name, "20260614T010000Z")
            self.assertEqual(targets[0]["label"], "New Target")
            self.assertEqual(json.loads(output_path.read_text())["targets"][0]["label"], "New Target")

    def test_refresh_targets_cli_uses_latest_run_by_default(self):
        rows_old = [
            {
                "score": 70,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Old Target",
                "chain": "bsc",
                "address": "0x1111111111111111111111111111111111111111",
                "entity_type": "unverified_contract",
            }
        ]
        rows_new = [
            {
                "score": 80,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "New Target",
                "chain": "bsc",
                "address": "0x2222222222222222222222222222222222222222",
                "entity_type": "bot_contract",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                root = Path("runs")
                old_run = root / "20260614T000000Z"
                new_run = root / "20260614T010000Z"
                old_run.mkdir(parents=True)
                new_run.mkdir()
                (old_run / "candidates_scored.json").write_text(json.dumps(rows_old))
                (new_run / "candidates_scored.json").write_text(json.dumps(rows_new))
                os.utime(old_run / "candidates_scored.json", (1000, 1000))
                os.utime(new_run / "candidates_scored.json", (2000, 2000))

                output_path = Path("live_targets.json")
                exit_code = main([
                    "refresh-targets",
                    "--runs-dir",
                    str(root),
                    "--output",
                    str(output_path),
                ])
                payload = json.loads(output_path.read_text())
            finally:
                os.chdir(old_cwd)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["targets"][0]["label"], "New Target")

    def test_refresh_targets_cli_prefers_current_run_manifest_over_latest_folder(self):
        rows_current = [
            {
                "score": 90,
                "next_action": "reverse_engineer_unverified_funded_contract",
                "name": "Current Run Target",
                "chain": "bsc",
                "address": "0x3333333333333333333333333333333333333333",
                "entity_type": "unverified_contract",
            }
        ]
        rows_stale = [
            {
                "score": 99,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "Stale Latest Target",
                "chain": "bsc",
                "address": "0x4444444444444444444444444444444444444444",
                "entity_type": "bot_contract",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                root = Path("runs")
                current_run = root / "current"
                stale_run = root / "stale-newer"
                current_run.mkdir(parents=True)
                stale_run.mkdir()
                current_scored = current_run / "candidates_scored.json"
                stale_scored = stale_run / "candidates_scored.json"
                current_scored.write_text(json.dumps(rows_current))
                stale_scored.write_text(json.dumps(rows_stale))
                os.utime(current_scored, (1000, 1000))
                os.utime(stale_scored, (2000, 2000))
                Path("state").mkdir()
                Path("state/current_run.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "sentinel-run-state-v1",
                            "run_id": "current",
                            "manifest_paths": {"candidates_scored": [str(current_scored)]},
                        }
                    )
                )

                exit_code = main([
                    "refresh-targets",
                    "--runs-dir",
                    str(root),
                    "--output",
                    "live_targets.json",
                ])
                payload = json.loads(Path("live_targets.json").read_text())
            finally:
                os.chdir(old_cwd)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["targets"][0]["label"], "Current Run Target")

    def test_refresh_targets_cli_refuses_latest_fallback_during_current_run_without_manifest(self):
        rows_stale = [
            {
                "score": 99,
                "next_action": "trace_bot_contract_then_target_protocols",
                "name": "Stale Latest Target",
                "chain": "bsc",
                "address": "0x4444444444444444444444444444444444444444",
                "entity_type": "bot_contract",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                root = Path("runs")
                stale_run = root / "stale"
                stale_run.mkdir(parents=True)
                (stale_run / "candidates_scored.json").write_text(json.dumps(rows_stale))
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
                    main([
                        "refresh-targets",
                        "--runs-dir",
                        str(root),
                        "--output",
                        "live_targets.json",
                    ])
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
