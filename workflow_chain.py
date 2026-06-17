from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Stage:
    output_globs: tuple[str, ...]
    remaining_globs: tuple[str, ...] = ()
    final_message: str = ""


STAGES = {
    "1": Stage(output_globs=("runs/*/candidates_scored.json",)),
    "2": Stage(output_globs=("examples/live_targets.json", "state/latest_targets.json")),
    "3": Stage(output_globs=("runs/*/candidates_scored.json", "state/latest_live_snapshot.json")),
    "4": Stage(output_globs=("deepwiki_briefs/*.json",)),
    "5": Stage(output_globs=("deepwiki_submissions/*.json",), remaining_globs=("deepwiki_briefs/*.json",)),
    "6": Stage(
        output_globs=(
            "needs_live_context/*.json",
            "needs_local_proof/*.json",
            "deepwiki_candidates/*.json",
            "deepwiki_unknown/*.json",
        ),
        remaining_globs=("deepwiki_submissions/*.json",),
    ),
    "7": Stage(output_globs=("proof_gate_submissions/*.json",), remaining_globs=("needs_local_proof/*.json", "deepwiki_candidates/*.json")),
    "8": Stage(
        output_globs=("local_proof_queue/*.md",),
        remaining_globs=("proof_gate_submissions/*.json",),
        final_message="DeepWiki proof-gate results are staged. Materialize Foundry targets before writing reports.",
    ),
    "9": Stage(
        output_globs=("foundry_targets/*/foundry.toml", "foundry_targets/*/test/LiveStateProof.t.sol"),
        final_message="Foundry target repos are materialized. Run forge tests with live RPC before reporting.",
    ),
}


def verify_stage(stage_id: str) -> bool:
    stage = STAGES[stage_id]
    outputs = _matches(stage.output_globs)
    if outputs:
        print(f"Stage {stage_id} verified with {len(outputs)} output item(s).")
        for item in outputs[:10]:
            print(f"  - {item}")
        return True
    print(f"Stage {stage_id} did not produce expected outputs.")
    for pattern in stage.output_globs:
        print(f"  - {pattern}")
    return False


def has_remaining(stage_id: str) -> bool:
    remaining = _matches(STAGES[stage_id].remaining_globs)
    print(f"Stage {stage_id} remaining input count: {len(remaining)}")
    return bool(remaining)


def dispatch_workflow(workflow: str, ref: str, smoke_limit: str = "", chain_next: bool = True) -> None:
    token = os.environ.get("PAT_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token:
        raise RuntimeError("PAT_TOKEN, GH_TOKEN, or GITHUB_TOKEN is required to dispatch the next workflow")
    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is required to dispatch the next workflow")

    payload = {"ref": ref, "inputs": {"smoke_limit": smoke_limit, "chain_next": "true" if chain_next else "false"}}
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/actions/workflows/{workflow}/dispatches",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status not in (200, 201, 202, 204):
                raise RuntimeError(f"Unexpected dispatch status {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Workflow dispatch failed: HTTP {exc.code}: {body}") from exc
    print(f"Dispatched {workflow}.")


def advance(stage_id: str, same_workflow: str | None, next_workflow: str | None, ref: str, smoke_limit: str) -> int:
    if not verify_stage(stage_id):
        return 1
    target = same_workflow if same_workflow and has_remaining(stage_id) else next_workflow
    if target:
        dispatch_workflow(target, ref=ref, smoke_limit=smoke_limit, chain_next=True)
    else:
        if STAGES[stage_id].final_message:
            print(STAGES[stage_id].final_message)
        print(f"Stage {stage_id} chain complete.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and advance the Sentinel DeepWiki workflow chain.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--stage", required=True, choices=sorted(STAGES))
    advance_parser = subparsers.add_parser("advance")
    advance_parser.add_argument("--stage", required=True, choices=sorted(STAGES))
    advance_parser.add_argument("--same-workflow", default="")
    advance_parser.add_argument("--next-workflow", default="")
    advance_parser.add_argument("--ref", default=os.environ.get("GITHUB_REF_NAME", "master"))
    advance_parser.add_argument("--smoke-limit", default=os.environ.get("BOT_SMOKE_LIMIT", ""))
    args = parser.parse_args()
    if args.command == "verify":
        return 0 if verify_stage(args.stage) else 1
    return advance(args.stage, args.same_workflow or None, args.next_workflow or None, args.ref, args.smoke_limit)


def _matches(patterns: Iterable[str]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        found.extend(glob.glob(pattern))
    return sorted(set(found))


if __name__ == "__main__":
    sys.exit(main())
