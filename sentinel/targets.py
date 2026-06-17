from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


TARGET_ACTIONS = {
    "proxy_change_live_funds": 0,
    "reward_pool_claimability_check": 1,
    "bridge_escrow_message_validation_check": 2,
    "approval_router_drain_surface": 3,
    "vault_share_asset_invariant_check": 4,
    "lending_oracle_liquidation_check": 5,
    "investigate_redeploy_funding_cluster": 6,
    "reverse_engineer_unverified_funded_contract": 7,
    "price_spike_recon_then_source_check": 8,
    "trace_bot_contract_then_target_protocols": 9,
    "recon_bravo_then_corecritical": 10,
}


def load_scored_rows(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text())
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("candidates"), list):
        return [row for row in payload["candidates"] if isinstance(row, dict)]
    return []


def generate_live_targets(rows: list[dict[str, Any]], max_targets: int = 50) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in sorted(rows, key=_sort_key):
        address = str(row.get("address", "")).lower().strip()
        chain = str(row.get("chain", "")).lower().strip()
        action = str(row.get("next_action", "")).strip()
        if not address or not chain or action not in TARGET_ACTIONS:
            continue
        if _is_low_priority(row):
            continue
        key = f"{chain}:{address}"
        if key in seen:
            continue
        seen.add(key)
        selected.append(_target_row(row))
        if len(selected) >= max_targets:
            break

    return selected


def write_live_targets(rows: list[dict[str, Any]], path: str | Path) -> None:
    payload = {"targets": rows}
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    latest_path = os.environ.get("SENTINEL_LATEST_TARGETS_PATH")
    if latest_path:
        latest = Path(latest_path)
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def refresh_live_targets(input_path: str | Path, output_path: str | Path, max_targets: int = 50) -> list[dict[str, Any]]:
    rows = load_scored_rows(input_path)
    targets = generate_live_targets(rows, max_targets=max_targets)
    write_live_targets(targets, output_path)
    return targets


def refresh_live_targets_from_latest_run(
    runs_dir: str | Path,
    output_path: str | Path,
    max_targets: int = 50,
) -> tuple[Path, list[dict[str, Any]]]:
    latest = find_latest_scored_run(runs_dir)
    if latest is None:
        raise FileNotFoundError(f"no candidates_scored.json found under {runs_dir}")
    targets = refresh_live_targets(latest, output_path, max_targets=max_targets)
    return latest, targets


def find_latest_scored_run(runs_dir: str | Path) -> Path | None:
    root = Path(runs_dir)
    candidates: list[Path] = []
    if not root.exists():
        return None
    for run_dir in root.iterdir():
        scored = run_dir / "candidates_scored.json"
        if scored.is_file():
            candidates.append(scored)
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime, path.parent.name))


def _sort_key(row: dict[str, Any]) -> tuple[int, int]:
    action = str(row.get("next_action", ""))
    action_rank = TARGET_ACTIONS.get(action, 99)
    score = int(row.get("score", 0) or 0)
    return (action_rank, -score)


def _is_low_priority(row: dict[str, Any]) -> bool:
    return str(row.get("next_action", "")) in {"drop_low_value", "watch_mainstream", "watch", "watch_bot_contract", "watch_known_protocol"}


def _target_row(row: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "score": row.get("score", 0),
        "next_action": row.get("next_action", ""),
        "entity_type": row.get("entity_type", "protocol"),
        "source": row.get("source", ""),
        "category": row.get("category", ""),
        "liquidity_usd": row.get("liquidity_usd", 0),
        "tvl_usd": row.get("tvl_usd", 0),
        "volume24h_usd": row.get("volume24h_usd", 0),
        "fdv_usd": row.get("fdv_usd", 0),
        "price_change_24h_pct": row.get("price_change_24h_pct", 0),
        "verified_source": row.get("verified_source"),
        "deployer_address": row.get("deployer_address", ""),
        "funding_cluster_id": row.get("funding_cluster_id", ""),
        "tags": list(row.get("tags", [])),
    }
    return {
        "chain": row.get("chain", ""),
        "address": str(row.get("address", "")).lower(),
        "label": row.get("name", "") or row.get("address", ""),
        "category": row.get("category", ""),
        "liquidity_usd": row.get("liquidity_usd", 0),
        "volume24h_usd": row.get("volume24h_usd", 0),
        "price_change_24h_pct": row.get("price_change_24h_pct", 0),
        "tags": list(row.get("tags", [])),
        "metadata": metadata,
    }
