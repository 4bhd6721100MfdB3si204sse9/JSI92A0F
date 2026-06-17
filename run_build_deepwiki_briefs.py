from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from bot_runtime import batch_limit
from sentinel.targets import TARGET_ACTIONS, find_latest_scored_run, load_scored_rows


LOW_PRIORITY_ACTIONS = {"drop_low_value", "watch_mainstream", "watch", "watch_bot_contract"}


def build_briefs(
    rows: list[dict[str, Any]],
    output_dir: str | Path,
    limit: int,
) -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selected = select_rows(rows, limit)
    written: list[Path] = []

    for index, row in enumerate(selected, start=1):
        brief = build_brief(row, index)
        filename = output / f"{index:03d}-{_slug(row.get('chain', 'chain'))}-{_slug(row.get('address') or row.get('name') or 'candidate')}.json"
        filename.write_text(json.dumps(brief, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(filename)

    state_dir = Path("state")
    state_dir.mkdir(exist_ok=True)
    (state_dir / "latest_deepwiki_briefs.json").write_text(
        json.dumps([str(path) for path in written], indent=2) + "\n",
        encoding="utf-8",
    )
    return written


def select_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    eligible = [
        row for row in rows
        if str(row.get("next_action", "")) not in LOW_PRIORITY_ACTIONS
        and (row.get("address") or row.get("name"))
    ]
    eligible.sort(key=_sort_key)
    return eligible[:limit]


def build_brief(row: dict[str, Any], rank: int) -> dict[str, Any]:
    reasons = list(row.get("reasons", []))
    if isinstance(row.get("reasons"), str):
        reasons = [part for part in str(row["reasons"]).split(";") if part]
    value = max(float(row.get("liquidity_usd", 0) or 0), float(row.get("tvl_usd", 0) or 0))
    action = str(row.get("next_action", ""))
    return {
        "schema_version": "sentinel-candidate-brief-v1",
        "rank": rank,
        "candidate": {
            "name": row.get("name", ""),
            "chain": row.get("chain", ""),
            "address": str(row.get("address", "")).lower(),
            "entity_type": row.get("entity_type", "protocol"),
            "category": row.get("category", ""),
            "url": row.get("url", ""),
            "source": row.get("source", ""),
            "external_id": row.get("external_id", ""),
        },
        "score": {
            "value": int(row.get("score", 0) or 0),
            "next_action": action,
            "reasons": reasons,
        },
        "value_at_risk": {
            "usd": value,
            "liquidity_usd": float(row.get("liquidity_usd", 0) or 0),
            "tvl_usd": float(row.get("tvl_usd", 0) or 0),
            "volume24h_usd": float(row.get("volume24h_usd", 0) or 0),
            "fdv_usd": float(row.get("fdv_usd", 0) or 0),
            "price_change_24h_pct": float(row.get("price_change_24h_pct", 0) or 0),
        },
        "live_evidence": {
            "verified_source": row.get("verified_source"),
            "deployer_address": row.get("deployer_address", ""),
            "funding_cluster_id": row.get("funding_cluster_id", ""),
            "tags": list(row.get("tags", [])),
        },
        "deepwiki_focus": {
            "why_this_candidate_matters": _why_it_matters(action, value),
            "proof_route": action,
            "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
            "local_questions": _local_questions(action),
        },
        "raw_scored_row": row,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build DeepWiki candidate briefs from Sentinel scored queues.")
    parser.add_argument("--input", help="Path to candidates_scored.json")
    parser.add_argument("--latest", action="store_true", help="Use newest candidates_scored.json under --runs-dir")
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--output", default="deepwiki_briefs")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)

    input_path = Path(args.input) if args.input else None
    if args.latest or input_path is None:
        input_path = find_latest_scored_run(args.runs_dir)
        if input_path is None:
            raise FileNotFoundError(f"no candidates_scored.json found under {args.runs_dir}")

    rows = load_scored_rows(input_path)
    limit = batch_limit(args.limit)
    written = build_briefs(rows, args.output, limit)
    print(f"briefs={len(written)} input={input_path} output={args.output}")
    return 0


def _sort_key(row: dict[str, Any]) -> tuple[int, int]:
    action = str(row.get("next_action", ""))
    action_rank = TARGET_ACTIONS.get(action, 99)
    score = int(row.get("score", 0) or 0)
    return (action_rank, -score)


def _slug(value: object) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:64] or "candidate"


def _why_it_matters(action: str, value: float) -> str:
    if action == "trace_bot_contract_then_target_protocols":
        return "Bot activity can reveal repeated profitable target protocols, flashloan paths, and DEX execution routes before public attention catches up."
    if action == "reverse_engineer_unverified_funded_contract":
        return "A funded unverified contract can hide value-moving selectors, proxy behavior, or privileged withdrawal paths with live value at risk."
    if action == "price_spike_recon_then_source_check":
        return "A sudden price or liquidity expansion can expose fresh custody, reward, router, or admin surfaces before they are well reviewed."
    if action == "investigate_redeploy_funding_cluster":
        return "Funding links to a closed project can indicate migrated user funds, reused vulnerable code, or redeployed custody contracts."
    if action == "proxy_change_live_funds":
        return "A proxy or implementation change while funds remain live can expose storage mismatches, authorization drift, or newly reachable value-moving code."
    if action == "reward_pool_claimability_check":
        return "A live reward pool with claimable value can expose accumulator, snapshot, dust-stake, or flashloan-amplified reward extraction."
    if action == "bridge_escrow_message_validation_check":
        return "Bridge escrow value depends on message validation and release accounting; weak validation can unlock user funds."
    if action == "approval_router_drain_surface":
        return "Routers or migrators with many approvals can become direct fund movement surfaces if authorization or recipient checks are weak."
    if action == "vault_share_asset_invariant_check":
        return "Vault share/asset imbalance can allow over-redemption, under-collateralized share minting, or repeated rounding extraction."
    if action == "lending_oracle_liquidation_check":
        return "Lending markets with stale or thin oracle/liquidity conditions can expose borrow, liquidation, or collateral extraction paths."
    return f"Candidate has live value at risk near ${value:,.0f} and matches Sentinel fund/reward extraction surfaces."


def _local_questions(action: str) -> list[str]:
    common = [
        "What exact live contract holds or controls the funds/rewards?",
        "Which public selectors can move, mint, claim, redeem, release, or sweep value?",
        "Can an unprivileged caller gain more than their entitlement?",
    ]
    if action == "trace_bot_contract_then_target_protocols":
        return [
            "Which counterparties are repeatedly called before profit sweeps?",
            "Do repeated target protocols expose stale price, reward, callback, or accounting paths?",
            *common,
        ]
    if action == "reverse_engineer_unverified_funded_contract":
        return [
            "Which selectors are used by depositors, admins, and withdrawal callers?",
            "Does proxy/storage reconstruction show a public value-moving path?",
            *common,
        ]
    if action == "investigate_redeploy_funding_cluster":
        return [
            "Did closed-project funds, deployers, or treasuries migrate into this candidate?",
            "Is the new funded surface reusing a known unsafe flow?",
            *common,
        ]
    if action == "proxy_change_live_funds":
        return [
            "Which implementation/admin slots changed while funds were live?",
            "Does the implementation expose new public value-moving selectors or storage layout mismatch?",
            *common,
        ]
    if action == "reward_pool_claimability_check":
        return [
            "What reward balance is claimable and how is entitlement calculated?",
            "Can stake timing, dust stake, repeated claim, stale index, or flashloan size increase rewards beyond entitlement?",
            *common,
        ]
    if action == "bridge_escrow_message_validation_check":
        return [
            "Which escrowed asset can be released and what validates the release message?",
            "Can replay, forged proof, stale root, wrong chain id, or recipient mismatch unlock value?",
            *common,
        ]
    if action == "approval_router_drain_surface":
        return [
            "Which users or contracts have approvals into this router or migrator?",
            "Can caller-controlled calldata, recipient, token, permit, or migration target move approved funds?",
            *common,
        ]
    if action == "vault_share_asset_invariant_check":
        return [
            "Do shares, assets, and total supply match under deposit, withdraw, harvest, and donation states?",
            "Can rounding or exchange-rate drift be repeated for net gain?",
            *common,
        ]
    if action == "lending_oracle_liquidation_check":
        return [
            "Which oracle value, collateral listing, borrow cap, or liquidation path controls solvency?",
            "Can stale prices or thin liquidity let an attacker borrow or liquidate beyond safe entitlement?",
            *common,
        ]
    return common


if __name__ == "__main__":
    sys.exit(main())
