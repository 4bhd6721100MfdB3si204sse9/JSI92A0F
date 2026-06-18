from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path

from bot_runtime import batch_limit
from run_state import has_current_run, manifest_paths, update_stage


PLACEHOLDER_ADDRESS_RE = re.compile(r"^0x([0-9a-f])\1{39}$", re.IGNORECASE)


def move_pending(
    source_dir: str = "deepwiki_briefs",
    pending_dir: str = "deepwiki_pending",
    limit: int = 25,
    manifest_path: str | Path = "state/latest_deepwiki_briefs.json",
) -> list[Path]:
    source = Path(source_dir)
    pending = Path(pending_dir)
    source.mkdir(parents=True, exist_ok=True)
    pending.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []

    files = manifest_paths("deepwiki_briefs")
    if files:
        files = [path for path in files if path.parent == source]
    if not files and not has_current_run():
        files = _manifest_files(manifest_path, source)
    if not files and not has_current_run():
        files = sorted(source.glob("*.json"))
    if not files:
        existing_pending = _manifest_files(manifest_path, pending) if not has_current_run() else []
        if existing_pending:
            for path in existing_pending[:batch_limit(limit)]:
                _reject_placeholder_brief(path)
            print(f"pending={len(existing_pending[:batch_limit(limit)])} existing_manifest={manifest_path}")
            selected_pending = existing_pending[:batch_limit(limit)]
            update_stage("5", {"deepwiki_pending": selected_pending})
            return selected_pending

    for path in files[:batch_limit(limit)]:
        _reject_placeholder_brief(path)
        destination = pending / path.name
        if destination.exists():
            destination = pending / f"{path.stem}-{int(time.time())}{path.suffix}"
        shutil.move(str(path), destination)
        moved.append(destination)
        print(f"Moved {path} to {destination}")

    if not moved:
        raise FileNotFoundError(f"no DeepWiki brief files found in {source}")
    _write_manifest(manifest_path, moved)
    update_stage("5", {"deepwiki_pending": moved})
    return moved


def _manifest_files(manifest_path: str | Path, source: Path) -> list[Path]:
    manifest = Path(manifest_path)
    if not manifest.is_file():
        return []
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(entries, list):
        return []
    files: list[Path] = []
    for entry in entries:
        path = Path(str(entry))
        if path.is_file() and path.parent == source:
            files.append(path)
    return sorted(files)


def _write_manifest(manifest_path: str | Path, moved: list[Path]) -> None:
    manifest = Path(manifest_path)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps([str(path) for path in moved], indent=2) + "\n", encoding="utf-8")


def _reject_placeholder_brief(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    address = str(payload.get("candidate", {}).get("address", ""))
    if PLACEHOLDER_ADDRESS_RE.match(address):
        raise ValueError(f"refusing to submit placeholder DeepWiki brief address: {address} in {path}")


if __name__ == "__main__":
    moved_files = move_pending()
    print(f"pending={len(moved_files)}")
