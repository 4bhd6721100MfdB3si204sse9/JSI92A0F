from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from bot_runtime import batch_limit

EXPORTABLE_VERDICTS = {"NEEDS_LOCAL_PROOF", "HIGH_CONFIDENCE_CANDIDATE"}


def export_queue(input_dirs: list[str], output_dir: str, limit: int) -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    candidates = _candidate_files(input_dirs)
    written: list[Path] = []
    for index, path in enumerate(_exportable_files(candidates)[:batch_limit(limit)], start=1):
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
    parser.add_argument("--allow-empty", action="store_true", help="Exit successfully when no proof-ready candidates exist.")
    args = parser.parse_args(argv)

    try:
        written = export_queue(args.input_dir, args.output, args.limit)
    except FileNotFoundError:
        if not args.allow_empty:
            raise
        print(f"local_proof_items=0 output={args.output}")
        return 0
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


def _exportable_files(paths: list[Path]) -> list[Path]:
    exportable: list[Path] = []
    for path in paths:
        payload = _load_payload(path)
        if _verdict(payload).upper() in EXPORTABLE_VERDICTS:
            exportable.append(path)
    return exportable


def _load_payload(path: Path) -> dict[str, Any]:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    raw = path.read_text(encoding="utf-8")
    parsed = _parse_markdown_json(raw)
    if parsed is None:
        return {"title": path.stem, "raw_markdown": raw}
    parsed.setdefault("title", path.stem)
    parsed["raw_markdown"] = raw
    return parsed


def _parse_markdown_json(raw: str) -> dict[str, Any] | None:
    stripped = raw.strip()
    if stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass
    for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL | re.IGNORECASE):
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _render_markdown(payload: dict[str, Any], source: Path) -> str:
    candidate = _candidate(payload)
    hard_gates = payload.get("hard_gates") if isinstance(payload.get("hard_gates"), dict) else {}
    proof = payload.get("local_proof_required") if isinstance(payload.get("local_proof_required"), dict) else {}
    lines = [
        "# Local Proof Queue Item",
        "",
        f"- source_file: `{source}`",
        f"- verdict: `{_verdict(payload)}`",
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
    candidate = _candidate(payload)
    value = candidate.get("name") or candidate.get("address") or payload.get("title") or path.stem
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value)).strip("-").lower()
    return text[:72] or "candidate"


def _candidate(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("candidate", "candidate_context", "active_target"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _verdict(payload: dict[str, Any]) -> str:
    return str(payload.get("verdict") or payload.get("deepwiki_verdict") or "unknown")


if __name__ == "__main__":
    sys.exit(main())
