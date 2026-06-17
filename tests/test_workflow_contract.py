import re
import unittest
from pathlib import Path


class WorkflowContractTest(unittest.TestCase):
    def test_main_workflows_have_dispatch_controls(self):
        for path in sorted(Path(".github/workflows").glob("[1-9]_*.yml")):
            content = path.read_text()
            self.assertIn("workflow_dispatch:", content, path)
            self.assertIn("smoke_limit:", content, path)
            self.assertIn("chain_next:", content, path)

    def test_chain_next_targets_exist(self):
        workflow_dir = Path(".github/workflows")
        known = {path.name for path in workflow_dir.glob("*.yml")}
        for path in workflow_dir.glob("*.yml"):
            content = path.read_text()
            for match in re.findall(r"--(?:same-workflow|next-workflow)\s+([A-Za-z0-9_.-]+\.yml)", content):
                self.assertIn(match, known, f"{path} references missing workflow {match}")

    def test_workflows_do_not_force_push(self):
        for path in Path(".github/workflows").glob("*.yml"):
            content = path.read_text()
            self.assertNotIn("push --force", content, path)
            self.assertNotIn("push -f", content, path)

    def test_setup_workflow_uses_json_secrets_without_committing_secret_files(self):
        path = Path(".github/workflows/0_setup_deepwiki_repos.yml")
        content = path.read_text()
        self.assertIn("KEY_JSON", content)
        self.assertNotIn("PAT_JSON", content)
        self.assertNotIn("Path(\"key.json\").write_text", content)

    def test_chain_workflows_accept_pat_json_as_dispatch_token(self):
        for path in sorted(Path(".github/workflows").glob("[1-7]_*.yml")):
            content = path.read_text()
            self.assertIn("secrets.PAT_JSON", content, path)


if __name__ == "__main__":
    unittest.main()
