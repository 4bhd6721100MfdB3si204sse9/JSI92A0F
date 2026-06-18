from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from bot_runtime import batch_limit
from deepwiki_client import DeepWikiClient
from deepwiki_prompts import candidate_triage_prompt, load_blueprint, proof_gate_prompt
from repositories import deepwiki_base_url
from run_state import has_current_run, manifest_paths, update_stage


def submit_pending(stage: str, pending_dir: str, submissions_dir: str, limit: int) -> list[Path]:
    blueprint = load_blueprint()
    base_url = deepwiki_base_url(
        repo_name=str(blueprint.get("repo_name", "protocol-sentinel")),
        source_repo=str(blueprint.get("source_repo", "maker-deepwiki/maker")),
    )
    pending = Path(pending_dir)
    submissions = Path(submissions_dir)
    submissions.mkdir(parents=True, exist_ok=True)
    manifest_key = "proof_gate_pending" if stage == "proof_gate" else "deepwiki_pending"
    submission_key = "proof_gate_submissions" if stage == "proof_gate" else "deepwiki_submissions"
    current_files = manifest_paths(manifest_key)
    submitted_names = _submitted_filenames_for_paths(manifest_paths(submission_key)) if has_current_run() else _submitted_filenames(submissions)
    if current_files:
        source_files = [path for path in current_files if path.parent == pending]
    elif has_current_run():
        source_files = []
    else:
        source_files = sorted(list(pending.glob("*.json")) + list(pending.glob("*.md")))
    files = [path for path in source_files if path.name not in submitted_names][:batch_limit(limit)]
    if not files:
        raise FileNotFoundError(f"no pending files found in {pending}")

    client = DeepWikiClient(base_url, teardown=True)
    written: list[Path] = []
    try:
        for path in files:
            content = path.read_text(encoding="utf-8")
            prompt = proof_gate_prompt(content, blueprint=blueprint) if stage == "proof_gate" else candidate_triage_prompt(content, blueprint=blueprint)
            url = client.ask(prompt)
            output = submissions / f"{stage}_{uuid.uuid4().hex}.json"
            output.write_text(
                json.dumps(
                    {
                        "stage": stage,
                        "filename": path.name,
                        "source_path": str(path),
                        "url": url,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "collected": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            written.append(output)
    finally:
        client.close()
    update_stage("7" if stage == "proof_gate" else "5", {submission_key: written})
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Submit Sentinel DeepWiki pending prompts and record result URLs.")
    parser.add_argument("--stage", choices=["triage", "proof_gate"], default="triage")
    parser.add_argument("--pending-dir", default=None)
    parser.add_argument("--submissions-dir", default=None)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)

    pending_dir = args.pending_dir or ("proof_gate_pending" if args.stage == "proof_gate" else "deepwiki_pending")
    submissions_dir = args.submissions_dir or ("proof_gate_submissions" if args.stage == "proof_gate" else "deepwiki_submissions")
    written = submit_pending(args.stage, pending_dir, submissions_dir, args.limit)
    print(f"submitted={len(written)} submissions_dir={submissions_dir}")
    return 0


def _submitted_filenames(submissions_dir: Path) -> set[str]:
    return _submitted_filenames_for_paths(submissions_dir.glob("*.json"))


def _submitted_filenames_for_paths(paths) -> set[str]:
    names: set[str] = set()
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        filename = str(payload.get("filename", ""))
        if filename:
            names.add(filename)
    return names


if __name__ == "__main__":
    sys.exit(main())
