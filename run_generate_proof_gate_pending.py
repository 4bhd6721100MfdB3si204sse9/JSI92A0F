from __future__ import annotations

import shutil
import time
from pathlib import Path

from bot_runtime import batch_limit


def move_proof_gate_pending(limit: int = 25) -> list[Path]:
    input_dirs = [Path("needs_local_proof"), Path("deepwiki_candidates")]
    pending = Path("proof_gate_pending")
    pending.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []

    candidates: list[Path] = []
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
    return moved


if __name__ == "__main__":
    moved_files = move_proof_gate_pending()
    print(f"proof_gate_pending={len(moved_files)}")

