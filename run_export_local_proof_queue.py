from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from bot_runtime import batch_limit


def export_queue(input_dirs: list[str], output_dir: str, limit: int) -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    candidates = _candidate_files(input_dirs)
    written: list[Path] = []
    for index, path in enumerate(candidates[:batch_limit(limit)], start=1):
        payload = _load_payload(path)
        destination = output / f"{index:03d}-{_title_slug(payload, path)}.md"
        destination.write_text(_render_markdown(payload, path), encoding="utf-8")
        written.append(destination)
    if not written:
        raise FileNotFoundError("no staged DeepWiki candidates found for local proof export")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export staged DeepWiki candidates into a local proof queue.")
    parser.add_argument("--input-dir", action="append", default=["proof_gate_results", "deepwiki_candidates", "needs_local_proof"])
    parser.add_argument("--output", default="local_proof_queue")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)

    written = export_queue(args.input_dir, args.output, args.limit)
    print(f"local_proof_items={len(written)} output={args.output}")
    return 0


def _candidate_files(input_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for directory in input_dirs:
        root = Path(directory)
        if not root.exists():
            continue
        files.extend(root.glob("*.json"))
        files.extend(root.glob("*.md"))
    return sorted(files)


def _load_payload(path: Path) -> dict[str, Any]:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return {"title": path.stem, "raw_markdown": path.read_text(encoding="utf-8")}


def _render_markdown(payload: dict[str, Any], source: Path) -> str:
    candidate = payload.get("candidate") if isinstance(payload.get("candidate"), dict) else {}
    hard_gates = payload.get("hard_gates") if isinstance(payload.get("hard_gates"), dict) else {}
    proof = payload.get("local_proof_required") if isinstance(payload.get("local_proof_required"), dict) else {}
    lines = [
        "# Local Proof Queue Item",
        "",
        f"- source_file: `{source}`",
        f"- verdict: `{payload.get('verdict', payload.get('deepwiki_verdict', 'unknown'))}`",
        f"- chain: `{candidate.get('chain', payload.get('chain', ''))}`",
        f"- address: `{candidate.get('address', payload.get('address', ''))}`",
        f"- paid_scope_match: `{payload.get('paid_scope_match', '')}`",
        "",
        "## Gate Question",
        "",
        "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
        "",
        "## Hard Gates",
        "",
    ]
    if hard_gates:
        lines.extend(f"- {key}: {value}" for key, value in hard_gates.items())
    else:
        lines.append("- Review hard gates manually from the DeepWiki response.")
    lines.extend(
        [
            "",
            "## Local Proof Required",
            "",
            f"- test_type: `{proof.get('test_type', '')}`",
            f"- test_file_to_add: `{proof.get('test_file_to_add', '')}`",
            f"- reject_if_assertion_fails: {proof.get('reject_if_assertion_fails', '')}",
            "",
            "## Suggested Next Commands",
            "",
            "```bash",
            "bravo <project>",
            "list entrypoints",
            "prove corecritical",
            "prove critical",
            "```",
            "",
        ]
    )
    if "raw_markdown" in payload:
        lines.extend(["## Raw DeepWiki Response", "", payload["raw_markdown"], ""])
    return "\n".join(lines)


def _title_slug(payload: dict[str, Any], path: Path) -> str:
    candidate = payload.get("candidate") if isinstance(payload.get("candidate"), dict) else {}
    value = candidate.get("name") or candidate.get("address") or payload.get("title") or path.stem
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value)).strip("-").lower()
    return text[:72] or "candidate"


if __name__ == "__main__":
    sys.exit(main())

