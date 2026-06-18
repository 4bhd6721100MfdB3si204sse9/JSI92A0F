from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_PATH = Path("state/current_run.json")


def has_current_run(state_path: str | Path = STATE_PATH) -> bool:
    return Path(state_path).is_file()


def load_state(state_path: str | Path = STATE_PATH) -> dict[str, Any]:
    path = Path(state_path)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def save_state(state: dict[str, Any], state_path: str | Path = STATE_PATH) -> None:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_stage(stage: str, outputs: dict[str, Any], state_path: str | Path = STATE_PATH) -> None:
    state = load_state(state_path)
    if not state:
        return
    now = datetime.now(timezone.utc).isoformat()
    state["active_stage"] = str(stage)
    state["updated_at"] = now
    stages = state.setdefault("stages", {})
    stage_state = stages.setdefault(str(stage), {})
    stage_state["updated_at"] = now
    stage_outputs = stage_state.setdefault("outputs", {})
    manifest = state.setdefault("manifest_paths", {})

    for key, value in outputs.items():
        values = _string_list(value)
        if not values:
            continue
        stage_outputs[key] = values if len(values) != 1 else values[0]
        existing = [str(item) for item in manifest.get(key, []) if str(item)]
        for item in values:
            if item not in existing:
                existing.append(item)
        manifest[key] = existing
    save_state(state, state_path)


def latest_path(key: str, state_path: str | Path = STATE_PATH) -> Path | None:
    paths = manifest_paths(key, state_path=state_path)
    return paths[-1] if paths else None


def manifest_paths(key: str, state_path: str | Path = STATE_PATH, existing_only: bool = True) -> list[Path]:
    state = load_state(state_path)
    manifest = state.get("manifest_paths", {}) if isinstance(state.get("manifest_paths"), dict) else {}
    raw = manifest.get(key, [])
    values = raw if isinstance(raw, list) else [raw]
    paths = [Path(str(item)) for item in values if str(item)]
    if existing_only:
        paths = [path for path in paths if path.exists()]
    return paths


def manifest_paths_by_dirs(
    keys: list[str],
    allowed_dirs: set[str],
    state_path: str | Path = STATE_PATH,
    existing_only: bool = True,
) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for key in keys:
        for path in manifest_paths(key, state_path=state_path, existing_only=existing_only):
            if path.parent.name not in allowed_dirs:
                continue
            path_text = str(path)
            if path_text in seen:
                continue
            seen.add(path_text)
            files.append(path)
    return sorted(files)


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, Path)):
        return [str(value)]
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value if str(item)]
    return [str(value)]
