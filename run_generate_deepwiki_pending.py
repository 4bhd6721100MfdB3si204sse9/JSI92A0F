from __future__ import annotations

import shutil
import time
from pathlib import Path

from bot_runtime import batch_limit


def move_pending(source_dir: str = "deepwiki_briefs", pending_dir: str = "deepwiki_pending", limit: int = 25) -> list[Path]:
    source = Path(source_dir)
    pending = Path(pending_dir)
    source.mkdir(parents=True, exist_ok=True)
    pending.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []

    for path in sorted(source.glob("*.json"))[:batch_limit(limit)]:
        destination = pending / path.name
        if destination.exists():
            destination = pending / f"{path.stem}-{int(time.time())}{path.suffix}"
        shutil.move(str(path), destination)
        moved.append(destination)
        print(f"Moved {path} to {destination}")

    if not moved:
        raise FileNotFoundError(f"no DeepWiki brief files found in {source}")
    return moved


if __name__ == "__main__":
    moved_files = move_pending()
    print(f"pending={len(moved_files)}")

