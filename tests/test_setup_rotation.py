import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from setup.deepwiki_setup import Account, load_repo_accounts, planned_repo_names, save_repo_url


class SetupRotationTest(unittest.TestCase):
    def test_load_repo_accounts_from_key_json_env_dict(self):
        old_env = dict(os.environ)
        os.environ["KEY_JSON"] = json.dumps({"alice": "token-a", "bob": "token-b"})
        os.environ.pop("PAT_JSON", None)
        try:
            accounts = load_repo_accounts(".")
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(accounts, [Account("alice", "token-a"), Account("bob", "token-b")])

    def test_pat_json_is_not_used_for_rotation_accounts(self):
        old_env = dict(os.environ)
        os.environ.pop("KEY_JSON", None)
        os.environ["PAT_JSON"] = "workflow-control-token"
        try:
            with self.assertRaises(ValueError):
                load_repo_accounts(".")
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_load_repo_accounts_from_local_key_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "key.json").write_text(json.dumps({"alice": "token-a"}))
            old_env = dict(os.environ)
            os.environ.pop("KEY_JSON", None)
            os.environ.pop("PAT_JSON", None)
            try:
                accounts = load_repo_accounts(tmp)
            finally:
                os.environ.clear()
                os.environ.update(old_env)

        self.assertEqual(accounts, [Account("alice", "token-a")])

    def test_planned_repo_names_skips_existing_rotation_urls(self):
        names = planned_repo_names(
            "protocol-sentinel",
            3,
            [
                "https://deepwiki.com/alice/protocol-sentinel--001",
                "https://deepwiki.com/bob/other-repo--002",
            ],
        )

        self.assertEqual(names, ["protocol-sentinel--002", "protocol-sentinel--003"])

    def test_save_repo_url_dedupes_repositories_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repositories.json"
            save_repo_url("protocol-sentinel--001", "alice", path)
            save_repo_url("protocol-sentinel--001", "alice", path)
            payload = json.loads(path.read_text())

        self.assertEqual(payload, ["https://deepwiki.com/alice/protocol-sentinel--001"])

    def test_setup_script_runs_directly_in_dry_run(self):
        env = dict(os.environ)
        env["KEY_JSON"] = json.dumps({"alice": "token-a"})
        result = subprocess.run(
            [sys.executable, "setup/deepwiki_setup.py", "--dry-run"],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("missing_repos", result.stdout)


if __name__ == "__main__":
    unittest.main()
