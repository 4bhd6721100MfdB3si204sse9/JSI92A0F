from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Literal


Verdict = Literal[
    "reject",
    "needs_live_context",
    "needs_local_proof",
    "high_confidence_candidate",
    "unknown",
]

NO_VULNERABILITY_MARKERS = (
    "NoVulnerability",
    "I cannot perform this security",
)


def classify_deepwiki_response(content: str | None) -> Verdict:
    if not content or not content.strip():
        return "reject"
    if any(marker in content for marker in NO_VULNERABILITY_MARKERS):
        return "reject"

    parsed = parse_json_response(content)
    if isinstance(parsed, dict):
        verdict = _normalize_verdict(parsed.get("verdict"))
        if verdict:
            return verdict

    verdict_match = re.search(r"(?im)^\s*##\s*Verdict\s*$\s*([A-Z_ -]+)", content)
    verdict_text = verdict_match.group(1) if verdict_match else content
    return _normalize_verdict(verdict_text) or "unknown"


def parse_json_response(content: str | None) -> dict | None:
    if not content:
        return None
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def directory_for_verdict(verdict: Verdict) -> Path:
    if verdict == "high_confidence_candidate":
        return Path(os.environ.get("DEEPWIKI_CANDIDATE_DIR", "deepwiki_candidates"))
    if verdict == "needs_live_context":
        return Path(os.environ.get("NEEDS_LIVE_CONTEXT_DIR", "needs_live_context"))
    if verdict == "needs_local_proof":
        return Path(os.environ.get("NEEDS_LOCAL_PROOF_DIR", "needs_local_proof"))
    if verdict == "reject":
        return Path(os.environ.get("REJECTED_BY_DEEPWIKI_DIR", "rejected_by_deepwiki"))
    return Path(os.environ.get("DEEPWIKI_UNKNOWN_DIR", "deepwiki_unknown"))


def save_deepwiki_response(content: str, source_url: str, prefix: str = "sentinel") -> Path | None:
    verdict = classify_deepwiki_response(content)
    if verdict == "reject" and not os.environ.get("SAVE_REJECTED_DEEPWIKI"):
        return None

    destination = directory_for_verdict(verdict)
    destination.mkdir(parents=True, exist_ok=True)
    parsed = parse_json_response(content)
    if parsed is not None:
        parsed["deepwiki_source_url"] = source_url
        parsed["deepwiki_verdict"] = verdict
        output = destination / f"{prefix}_{uuid.uuid4().hex}.json"
        output.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return output

    output = destination / f"{prefix}_{uuid.uuid4().hex}.md"
    header = f"<!-- deepwiki_source_url: {source_url} -->\n<!-- deepwiki_verdict: {verdict} -->\n\n"
    output.write_text(header + content, encoding="utf-8")
    return output


def _normalize_verdict(value: object) -> Verdict | None:
    text = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
    if "high_confidence_candidate" in text:
        return "high_confidence_candidate"
    if "needs_live_context" in text:
        return "needs_live_context"
    if "needs_local_proof" in text:
        return "needs_local_proof"
    if "reject" in text:
        return "reject"
    return None

