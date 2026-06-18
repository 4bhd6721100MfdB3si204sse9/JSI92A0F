from __future__ import annotations

import argparse
import json
from pathlib import Path

from .output import write_run
from .scoring import score_candidate
from .targets import refresh_live_targets, refresh_live_targets_from_latest_run
from .sources import load_candidates
from run_state import has_current_run, latest_path, update_stage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="protocol-sentinel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="discover and score protocol candidates")
    discover.add_argument(
        "--source",
        default="all",
        choices=[
            "all",
            "sample",
            "dexscreener_profiles",
            "dexscreener_boosts",
            "defillama_protocols",
            "ethereum_chain_scanner",
            "bsc_chain_scanner",
            "explorer_snapshot",
            "explorer_live",
        ],
    )
    discover.add_argument("--config", default="config/sentinel.json")
    discover.add_argument("--input", help="optional JSON input for fixture-backed sources")
    discover.add_argument("--limit", type=int, default=50)
    discover.add_argument("--output", default="runs")

    targets = subparsers.add_parser("refresh-targets", help="generate live target list from a scored queue")
    targets.add_argument("--input", help="path to candidates_scored.json or similar scored queue JSON")
    targets.add_argument("--latest", action="store_true", help="use the newest candidates_scored.json under --runs-dir")
    targets.add_argument("--runs-dir", default="runs", help="directory containing scored run folders")
    targets.add_argument("--output", default="examples/live_targets.json")
    targets.add_argument("--max-targets", type=int, default=50)

    args = parser.parse_args(argv)
    if args.command == "discover":
        return run_discover(args)
    if args.command == "refresh-targets":
        return run_refresh_targets(args)
    return 1


def run_discover(args: argparse.Namespace) -> int:
    config = json.loads(Path(args.config).read_text())
    stage = "3" if args.source == "explorer_live" else "1"
    update_stage(stage, {})
    candidates = load_candidates(args.source, config, args.limit, args.input)
    scored = [score_candidate(candidate, config) for candidate in candidates]
    scored.sort(key=lambda item: item.score, reverse=True)
    run_dir = write_run(scored, Path(args.output))
    update_stage(
        stage,
        {
            "run_dirs": run_dir,
            "candidates_scored": run_dir / "candidates_scored.json",
            "triage_queue_csv": run_dir / "triage_queue.csv",
            "triage_queue_md": run_dir / "triage_queue.md",
        },
    )
    protocol_recon = sum(1 for item in scored if item.next_action == "recon_bravo_then_corecritical")
    bot_trace = sum(1 for item in scored if item.next_action == "trace_bot_contract_then_target_protocols")
    unverified = sum(1 for item in scored if item.next_action == "reverse_engineer_unverified_funded_contract")
    price_spike = sum(1 for item in scored if item.next_action == "price_spike_recon_then_source_check")
    redeploy_cluster = sum(1 for item in scored if item.next_action == "investigate_redeploy_funding_cluster")
    print(
        f"loaded={len(candidates)} protocol_recon={protocol_recon} "
        f"bot_trace={bot_trace} unverified={unverified} "
        f"price_spike={price_spike} redeploy_cluster={redeploy_cluster} run_dir={run_dir}"
    )
    return 0


def run_refresh_targets(args: argparse.Namespace) -> int:
    if args.input:
        targets = refresh_live_targets(args.input, args.output, max_targets=args.max_targets)
        update_stage("2", {"live_targets": args.output})
        print(f"targets={len(targets)} output={args.output} input={args.input}")
        return 0

    if args.latest or not args.input:
        current_scored = latest_path("candidates_scored")
        if current_scored is not None:
            targets = refresh_live_targets(current_scored, args.output, max_targets=args.max_targets)
            update_stage("2", {"live_targets": args.output})
            print(f"targets={len(targets)} output={args.output} current_input={current_scored}")
            return 0
        if has_current_run():
            raise FileNotFoundError("current run has no candidates_scored manifest path")
        latest, targets = refresh_live_targets_from_latest_run(args.runs_dir, args.output, max_targets=args.max_targets)
        update_stage("2", {"live_targets": args.output})
        print(f"targets={len(targets)} output={args.output} latest_input={latest}")
        return 0

    return 0
