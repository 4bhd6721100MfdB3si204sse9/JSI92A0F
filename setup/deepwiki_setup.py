from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepwiki_prompts import load_blueprint
from repositories import load_repository_urls


SECRET_FILE_CANDIDATES = ("key.json",)
COPY_IGNORE = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "key.json",
    "pat.json",
    "pat_json",
    "KEY_JSON",
    "PAT_JSON",
    "temp_repo",
}


@dataclass(frozen=True)
class Account:
    username: str
    token: str


def load_repo_accounts(root: str | Path = ".") -> list[Account]:
    payload = _load_secret_payload(root)
    accounts = _accounts_from_payload(payload)
    if not accounts:
        raise ValueError("No GitHub rotation account tokens found in KEY_JSON or key.json")
    return accounts


def planned_repo_names(base_name: str, max_repo: int, existing_urls: list[str]) -> list[str]:
    existing = {url.rstrip("/").split("/")[-1].lower() for url in existing_urls}
    names: list[str] = []
    for index in range(1, max_repo + 1):
        name = f"{base_name}--{index:03d}"
        if name.lower() not in existing:
            names.append(name)
    return names


def save_repo_url(repo_name: str, username: str, path: str | Path = "repositories.json") -> None:
    repo_url = f"https://deepwiki.com/{username}/{repo_name}"
    output = Path(path)
    if output.exists():
        try:
            repos = json.loads(output.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            repos = []
    else:
        repos = []
    if not isinstance(repos, list):
        repos = []
    if repo_url not in repos:
        repos.append(repo_url)
        output.write_text(json.dumps(repos, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create rotating DeepWiki GitHub repositories for Protocol Sentinel.")
    parser.add_argument("--root", default=".", help="repository root to copy into generated repos")
    parser.add_argument("--repositories", default="repositories.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep-seconds", type=int, default=int(os.environ.get("SETUP_SLEEP_SECONDS", "0") or 0))
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    blueprint = load_blueprint(root / "blueprints" / "sentinel_fund_reward_discovery.json")
    repo_name = str(blueprint.get("repo_name", "protocol-sentinel"))
    source_repo = os.environ.get("SENTINEL_SOURCE_REPO", str(blueprint.get("source_repo", "")))
    max_repo = int(os.environ.get("SENTINEL_MAX_REPO", blueprint.get("max_repo", 10)))
    accounts = load_repo_accounts(root)
    existing_urls = load_repository_urls(repo_name, str(root / args.repositories))
    missing_names = planned_repo_names(repo_name, max_repo, existing_urls)

    print(f"accounts={len(accounts)} existing_deepwiki_repos={len(existing_urls)} missing_repos={len(missing_names)}")
    if args.dry_run:
        for name in missing_names:
            print(f"would_create={name}")
        return 0

    for index, repo in enumerate(missing_names):
        account = accounts[index % len(accounts)]
        print(f"creating={repo} account={account.username}")
        create_and_push_repo(root, repo, account, source_repo)
        save_repo_url(repo, account.username, root / args.repositories)
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    return 0


def create_and_push_repo(root: Path, repo_name: str, account: Account, source_repo: str) -> None:
    create_github_repo(repo_name, account.token, source_repo)
    with tempfile.TemporaryDirectory(prefix="sentinel-deepwiki-") as tmp:
        worktree = Path(tmp) / repo_name
        copy_worktree(root, worktree)
        run_git(["init"], worktree)
        run_git(["add", "."], worktree)
        run_git(["config", "user.name", "GitHub Actions"], worktree)
        run_git(["config", "user.email", "actions@github.com"], worktree)
        run_git(["commit", "-m", "Initial DeepWiki mirror"], worktree)
        remote_url = f"https://{account.username}:{account.token}@github.com/{account.username}/{repo_name}.git"
        run_git(["remote", "add", "origin", remote_url], worktree, redact=account.token)
        run_git(["push", "-f", "origin", "master"], worktree)


def create_github_repo(repo_name: str, token: str, source_repo: str) -> None:
    payload = {
        "name": repo_name,
        "description": f"DeepWiki mirror for {source_repo or repo_name}",
        "private": False,
        "auto_init": False,
    }
    request = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"unexpected GitHub status {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 422 and "already_exists" in body:
            return
        if exc.code == 422 and "name already exists" in body.lower():
            return
        raise RuntimeError(f"GitHub repository create failed: HTTP {exc.code}: {body}") from exc


def copy_worktree(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in COPY_IGNORE}

    shutil.copytree(source, destination, ignore=ignore)


def run_git(args: list[str], cwd: Path, redact: str = "") -> None:
    printable = "git " + " ".join(arg.replace(redact, "***") if redact else arg for arg in args)
    print(f"running={printable}")
    result = subprocess.run(["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"{printable} failed: {result.stderr.strip()}")


def _load_secret_payload(root: str | Path) -> Any:
    raw = os.environ.get("KEY_JSON", "").strip()
    if raw:
        return json.loads(_normalize_json_text(raw))
    for filename in SECRET_FILE_CANDIDATES:
        path = Path(root) / filename
        if path.exists():
            return json.loads(_normalize_json_text(path.read_text(encoding="utf-8")))
    return {}


def _accounts_from_payload(payload: Any) -> list[Account]:
    if isinstance(payload, dict):
        return [Account(str(username), str(token)) for username, token in payload.items() if username and token]
    if isinstance(payload, list):
        accounts: list[Account] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            username = str(item.get("username") or item.get("user") or "")
            token = str(item.get("token") or item.get("pat") or "")
            if username and token:
                accounts.append(Account(username, token))
        return accounts
    return []


def _normalize_json_text(raw: str) -> str:
    return (
        raw.replace("\u201c", "\"")
        .replace("\u201d", "\"")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


if __name__ == "__main__":
    sys.exit(main())
