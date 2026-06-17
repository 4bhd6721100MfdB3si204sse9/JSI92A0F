from __future__ import annotations

import json
import os
from pathlib import Path


def deepwiki_base_url(repo_name: str, source_repo: str, repositories_path: str = "repositories.json") -> str:
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "0")
    if run_number == "0":
        return f"https://deepwiki.com/{source_repo}"

    urls = load_repository_urls(repo_name, repositories_path)
    if not urls:
        return f"https://deepwiki.com/{source_repo}"

    index = (int(run_number) - 1) % len(urls)
    return urls[index]


def load_repository_urls(repo_name: str, repositories_path: str = "repositories.json") -> list[str]:
    path = Path(repositories_path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []

    expected = repo_name.lower()
    valid: list[str] = []
    for item in data:
        if not isinstance(item, str) or not item.strip():
            continue
        slug = item.rstrip("/").split("/")[-1].lower()
        if slug == expected or slug.startswith(f"{expected}--"):
            valid.append(item)
    return valid

