from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from bot_runtime import batch_limit
from deepwiki_client import DeepWikiClient
from deepwiki_triage import parse_json_response, save_deepwiki_response
from deepwiki_prompts import load_blueprint
from repositories import deepwiki_base_url
from run_state import has_current_run, manifest_paths, update_stage


def collect_results(stage: str, submissions_dir: str, limit: int) -> int:
    submission_key = "proof_gate_submissions" if stage == "proof_gate" else "deepwiki_submissions"
    submissions = manifest_paths(submission_key)
    if not submissions and not has_current_run():
        submissions = sorted(Path(submissions_dir).glob("*.json"))
    pending = [path for path in submissions if not _load_submission(path).get("collected")]
    if not pending:
        print(f"No uncollected submissions in {submissions_dir}")
        return 0

    blueprint = load_blueprint()
    base_url = deepwiki_base_url(
        repo_name=str(blueprint.get("repo_name", "protocol-sentinel")),
        source_repo=str(blueprint.get("source_repo", "maker-deepwiki/maker")),
    )
    client = DeepWikiClient(base_url, teardown=True)
    count = 0
    routed_outputs: dict[str, list[Path]] = {}
    try:
        for submission_path in pending[:batch_limit(limit)]:
            submission = _load_submission(submission_path)
            url = str(submission.get("url", ""))
            if not url:
                continue
            content = client.collect_response(url)
            if content is None:
                submission["collected"] = True
                submission["collection_error"] = "not_found"
                _save_submission(submission_path, submission)
                continue

            if stage == "proof_gate":
                saved = _save_proof_gate_result(content, url)
                routed_outputs.setdefault("proof_gate_results", []).append(saved)
            else:
                saved = save_deepwiki_response(content, url, prefix="sentinel")
                if saved is not None:
                    routed_outputs.setdefault(Path(saved).parent.name, []).append(Path(saved))

            submission["collected"] = True
            _save_submission(submission_path, submission)
            count += 1
    finally:
        client.close()
    if routed_outputs:
        update_stage("8" if stage == "proof_gate" else "6", routed_outputs)
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect DeepWiki Sentinel responses and route them.")
    parser.add_argument("--stage", choices=["triage", "proof_gate"], default="triage")
    parser.add_argument("--submissions-dir", default=None)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)

    submissions_dir = args.submissions_dir or ("proof_gate_submissions" if args.stage == "proof_gate" else "deepwiki_submissions")
    count = collect_results(args.stage, submissions_dir, args.limit)
    print(f"collected={count} stage={args.stage}")
    return 0


def _save_proof_gate_result(content: str, url: str) -> Path:
    output_dir = Path("proof_gate_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    parsed = parse_json_response(content)
    if parsed is not None:
        parsed["deepwiki_source_url"] = url
        output = output_dir / f"proof_gate_{uuid.uuid4().hex}.json"
        output.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return output
    output = output_dir / f"proof_gate_{uuid.uuid4().hex}.md"
    output.write_text(f"<!-- deepwiki_source_url: {url} -->\n\n{content}", encoding="utf-8")
    return output


def _load_submission(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_submission(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
