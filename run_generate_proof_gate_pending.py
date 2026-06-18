from __future__ import annotations

import shutil
import time
from pathlib import Path

from bot_runtime import batch_limit
from run_state import has_current_run, manifest_paths_by_dirs, update_stage


def move_proof_gate_pending(limit: int = 25) -> list[Path]:
    input_dirs = [Path("needs_local_proof"), Path("deepwiki_candidates")]
    pending = Path("proof_gate_pending")
    pending.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []

    candidates = manifest_paths_by_dirs(
        ["needs_local_proof", "deepwiki_candidates"],
        {"needs_local_proof", "deepwiki_candidates"},
    )
    if candidates or has_current_run():
        for directory in input_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    else:
        for directory in input_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            candidates.extend(directory.glob("*.json"))
            candidates.extend(directory.glob("*.md"))

    for path in sorted(candidates)[:batch_limit(limit)]:
        destination = pending / path.name
        if destination.exists():
            destination = pending / f"{path.stem}-{int(time.time())}{path.suffix}"
        shutil.move(str(path), destination)
        moved.append(destination)
        print(f"Moved {path} to {destination}")

    if not moved:
        raise FileNotFoundError("no proof-gate candidate files found")
    update_stage("7", {"proof_gate_pending": moved})
    return moved


if __name__ == "__main__":
    moved_files = move_proof_gate_pending()
    print(f"proof_gate_pending={len(moved_files)}")
