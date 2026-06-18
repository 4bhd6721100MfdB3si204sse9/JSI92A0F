from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_state import save_state


ACTIVE_PATHS = (
    "runs",
    "deepwiki_briefs",
    "deepwiki_pending",
    "deepwiki_submissions",
    "needs_live_context",
    "needs_local_proof",
    "deepwiki_candidates",
    "deepwiki_unknown",
    "rejected_by_deepwiki",
    "proof_gate_pending",
    "proof_gate_submissions",
    "proof_gate_results",
    "local_proof_queue",
    "foundry_targets",
)
STATE_PATH = Path("state/current_run.json")


def start_run(reason: str = "pre_run") -> dict[str, Any]:
    archived = archive_active(reason="abandoned", require_files=True)
    run_id = _new_run_id()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": "sentinel-run-state-v1",
        "run_id": run_id,
        "started_at": _now(),
        "updated_at": _now(),
        "reason": reason,
        "active_stage": "1",
        "manifest_paths": {},
        "stages": {},
        "pre_run_archive": archived.get("archive_dir", ""),
    }
    save_state(state, STATE_PATH)
    print(f"current_run={run_id}")
    if archived.get("archive_dir"):
        print(f"archived_leftovers={archived['archive_dir']}")
    return state


def archive_active(reason: str, require_files: bool = False) -> dict[str, Any]:
    files = _active_files()
    if require_files and not files:
        return {"archived_files": 0, "archive_dir": ""}

    run_id = _current_run_id() or f"{reason}-{_new_run_id()}"
    archive_dir = Path("archive") / "runs" / run_id
    archive_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    for root_name in ACTIVE_PATHS:
        root = Path(root_name)
        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)
            continue
        destination_root = archive_dir / root_name
        for child in sorted(root.iterdir()):
            destination = destination_root / child.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                destination = destination_root / f"{child.stem}-{int(datetime.now(timezone.utc).timestamp())}{child.suffix}"
            shutil.move(str(child), str(destination))
            moved.append(str(destination))
        root.mkdir(parents=True, exist_ok=True)

    summary = {
        "schema_version": "sentinel-run-archive-v1",
        "run_id": run_id,
        "reason": reason,
        "archived_at": _now(),
        "archived_files": len(moved),
        "paths": moved,
        "run_state": _load_current_state(),
    }
    (archive_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if STATE_PATH.exists() and reason in {"completed", "abandoned"}:
        STATE_PATH.unlink()
    print(f"archived_files={len(moved)} archive_dir={archive_dir}")
    return {"archived_files": len(moved), "archive_dir": str(archive_dir)}


def _active_files() -> list[Path]:
    files: list[Path] = []
    for root_name in ACTIVE_PATHS:
        root = Path(root_name)
        if not root.exists():
            continue
        files.extend(path for path in root.rglob("*") if path.is_file())
    return files


def _current_run_id() -> str:
    payload = _load_current_state()
    return str(payload.get("run_id", "")).strip()


def _load_current_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {}
    try:
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _new_run_id() -> str:
    github_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    github_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "").strip()
    if github_id:
        suffix = f"-{github_attempt}" if github_attempt else ""
        return f"github-{github_id}{suffix}"
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive Sentinel workflow artifacts and prepare clean runs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--reason", default="pre_run")
    archive = subparsers.add_parser("archive")
    archive.add_argument("--reason", default="completed")
    archive.add_argument("--require-files", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "start":
        start_run(reason=args.reason)
        return 0
    archive_active(reason=args.reason, require_files=args.require_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
