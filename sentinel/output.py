from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .models import ScoredCandidate


def write_run(scored: list[ScoredCandidate], output_root: Path) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = allocate_run_dir(output_root, run_id)

    rows = [item.as_dict() for item in scored]
    (run_dir / "candidates_scored.json").write_text(json.dumps(rows, indent=2, sort_keys=True))
    write_csv(rows, run_dir / "triage_queue.csv")
    write_markdown(scored, run_dir / "triage_queue.md")
    return run_dir


def allocate_run_dir(output_root: Path, run_id: str) -> Path:
    while True:
        run_dir = unique_run_dir(output_root, run_id)
        try:
            run_dir.mkdir()
            return run_dir
        except FileExistsError:
            continue


def unique_run_dir(output_root: Path, run_id: str) -> Path:
    run_dir = output_root / run_id
    if not run_dir.exists():
        return run_dir
    index = 1
    while True:
        candidate = output_root / f"{run_id}-{index:02d}"
        if not candidate.exists():
            return candidate
        index += 1


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "score",
        "next_action",
        "name",
        "chain",
        "entity_type",
        "address",
        "category",
        "liquidity_usd",
        "tvl_usd",
        "volume24h_usd",
        "fdv_usd",
        "price_change_24h_pct",
        "verified_source",
        "deployer_address",
        "funding_cluster_id",
        "source",
        "url",
        "reasons",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            row = dict(row)
            row["reasons"] = ";".join(row.get("reasons", []))
            writer.writerow(row)


def write_markdown(scored: list[ScoredCandidate], path: Path) -> None:
    lines = [
        "# Protocol Sentinel Triage Queue",
        "",
        "| Rank | Score | Name | Type | Chain | Value | 24h % | Action | Reasons |",
        "| --- | ---: | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for index, item in enumerate(scored, start=1):
        candidate = item.candidate
        value = candidate.value_at_risk()
        name = candidate.name.replace("|", "/")
        reasons = ", ".join(item.reasons[:8]).replace("|", "/")
        lines.append(
            f"| {index} | {item.score} | {name} | {candidate.entity_type} | {candidate.chain} | "
            f"{value:.0f} | {candidate.price_change_24h_pct:.0f} | {item.next_action} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Analyst Next Steps",
            "",
            "1. Take the highest `recon_bravo_then_corecritical` item.",
            "2. Resolve its real protocol contracts and live balances.",
            "3. Run live recon into the 04-LIVE information path.",
            "4. List callable entrypoints and asset-moving paths.",
            "5. Prove the highest-risk mapped critical question before reporting.",
            "6. For `trace_bot_contract_then_target_protocols`, trace counterparties, repeated targets, DEX paths, flashloan providers, and profit sinks before choosing a protocol to audit.",
            "7. For `reverse_engineer_unverified_funded_contract`, recover selectors, storage/proxy shape, balances, and privileged callers before choosing a proof target.",
            "8. For `price_spike_recon_then_source_check`, verify liquidity locks, holder concentration, admin permissions, and whether verified source exists.",
            "9. For `investigate_redeploy_funding_cluster`, trace deployer/funder links to closed projects and promote the new funded contract or protocol cluster for audit.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
