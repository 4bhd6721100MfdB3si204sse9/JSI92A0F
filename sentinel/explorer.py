from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Candidate


BOT_KEYWORDS = {
    "arbitrage",
    "bot",
    "executor",
    "flashloan",
    "keeper",
    "liquidator",
    "mev",
    "sandwich",
    "sniper",
}

FLASHLOAN_SELECTORS = {
    "0x0d8f6a1c",  # executeOperation(address[],uint256[],uint256[],address,bytes)
    "0x1b11d0ff",  # uniswapV2Call(address,uint256,uint256,bytes)
    "0x10d1e85c",  # pancakeCall(address,uint256,uint256,bytes)
    "0x414bf389",  # uniswapV3SwapCallback(int256,int256,bytes)
    "0xfa461e33",  # uniswapV3FlashCallback(uint256,uint256,bytes)
}


def load_explorer_snapshot(path: str | Path, config: dict[str, Any], limit: int) -> list[Candidate]:
    payload = json.loads(Path(path).read_text())
    return load_explorer_snapshot_payload(payload, config, limit)


def load_explorer_snapshot_payload(payload: Any, config: dict[str, Any], limit: int) -> list[Candidate]:
    contracts = payload.get("contracts", payload if isinstance(payload, list) else [])
    known_closed = _known_closed_clusters(payload, config)
    candidates = [
        candidate_from_contract(item, known_closed, config)
        for item in contracts[:limit]
    ]
    return [candidate for candidate in candidates if candidate is not None]


def candidate_from_contract(
    item: dict[str, Any],
    known_closed: dict[str, str],
    config: dict[str, Any],
) -> Candidate | None:
    chain = str(item.get("chain", "")).lower()
    address = str(item.get("address", "")).lower()
    if not chain or not address:
        return None

    verified = item.get("verified_source")
    value = _value_at_risk(item)
    tags = _base_tags(item)
    entity_type = "protocol"
    category = str(item.get("category") or item.get("contract_type") or "")
    name = str(item.get("name") or item.get("contract_name") or address)

    if _is_bot_contract(item):
        entity_type = "bot_contract"
        category = category or "bot contract"
        tags.extend(_bot_tags(item))
    elif verified is False and value >= float(config.get("min_unverified_value_usd", 100_000)):
        entity_type = "unverified_contract"
        category = category or "unverified contract"
        tags.extend(["unverified_contract", "unknown_protocol"])
    elif _has_price_spike(item, config):
        entity_type = "unknown_protocol"
        tags.extend(["unknown_protocol", "sudden_price_spike"])
    elif category and value >= float(config.get("min_value_usd", 250_000)):
        entity_type = "unknown_protocol"
        tags.append("unknown_protocol")

    cluster_id = _cluster_match(item, known_closed)
    if cluster_id:
        entity_type = "unknown_protocol"
        tags.extend(
            [
                "prior_project_closed",
                "same_deployer_closed_project",
                "funding_from_closed_project",
                "suspected_rug_redeploy",
            ]
        )

    if entity_type == "protocol" and value < float(config.get("min_value_usd", 250_000)):
        return None

    return Candidate(
        source="explorer_snapshot",
        external_id=f"{chain}:{address}",
        name=name,
        chain=chain,
        entity_type=entity_type,
        address=address,
        category=category,
        url=str(item.get("url", "")),
        liquidity_usd=float(item.get("liquidity_usd", 0) or 0),
        tvl_usd=value,
        volume24h_usd=float(item.get("volume24h_usd", 0) or 0),
        fdv_usd=float(item.get("fdv_usd", 0) or 0),
        price_change_24h_pct=float(item.get("price_change_24h_pct", 0) or 0),
        verified_source=verified,
        deployer_address=str(item.get("deployer_address", "")).lower(),
        funding_cluster_id=cluster_id,
        created_at_ms=item.get("created_at_ms"),
        tags=sorted(set(tags)),
        raw=item,
    )


def _value_at_risk(item: dict[str, Any]) -> float:
    token_total = sum(float(balance.get("usd", 0) or 0) for balance in item.get("token_balances", []))
    explicit = float(item.get("value_at_risk_usd", 0) or 0)
    native = float(item.get("native_balance_usd", 0) or 0)
    tvl = float(item.get("tvl_usd", 0) or 0)
    liquidity = float(item.get("liquidity_usd", 0) or 0)
    return max(explicit, native + token_total, tvl, liquidity)


def _base_tags(item: dict[str, Any]) -> list[str]:
    tags = list(item.get("tags", []))
    tx_count = int(item.get("tx_count_24h", 0) or 0)
    if tx_count >= 100:
        tags.append("high_tx_count")
    if item.get("verified_source") is False:
        tags.append("unverified_contract")
    return tags


def _is_bot_contract(item: dict[str, Any]) -> bool:
    text = " ".join(
        [
            str(item.get("name", "")),
            str(item.get("contract_name", "")),
            str(item.get("category", "")),
            str(item.get("contract_type", "")),
            str(item.get("source_excerpt", "")),
            " ".join(item.get("tags", [])),
        ]
    ).lower()
    selectors = {str(selector).lower() for selector in item.get("selectors", [])}
    return bool(BOT_KEYWORDS.intersection(text.split())) or bool(FLASHLOAN_SELECTORS.intersection(selectors))


def _bot_tags(item: dict[str, Any]) -> list[str]:
    tags = ["verified_bot_contract" if item.get("verified_source") else "bot_contract"]
    selectors = {str(selector).lower() for selector in item.get("selectors", [])}
    if FLASHLOAN_SELECTORS.intersection(selectors) or "flashloan" in " ".join(item.get("tags", [])).lower():
        tags.append("flashloan_user")
    if item.get("dex_paths") or "router" in " ".join(item.get("tags", [])).lower():
        tags.append("dex_path_executor")
    return tags


def _has_price_spike(item: dict[str, Any], config: dict[str, Any]) -> bool:
    price_change = float(item.get("price_change_24h_pct", 0) or 0)
    value = _value_at_risk(item)
    return (
        price_change >= float(config.get("price_spike_24h_pct", 100))
        and value >= float(config.get("min_spike_value_usd", 100_000))
    )


def _known_closed_clusters(payload: Any, config: dict[str, Any]) -> dict[str, str]:
    clusters: dict[str, str] = {}
    configured = config.get("closed_project_clusters", [])
    embedded = payload.get("closed_project_clusters", []) if isinstance(payload, dict) else []
    for cluster in [*configured, *embedded]:
        cluster_id = str(cluster.get("id", "closed-project-cluster"))
        for key in ("deployer_addresses", "funder_addresses", "treasury_addresses", "project_addresses"):
            for address in cluster.get(key, []):
                clusters[str(address).lower()] = cluster_id
    return clusters


def _cluster_match(item: dict[str, Any], known_closed: dict[str, str]) -> str:
    addresses = [
        str(item.get("deployer_address", "")).lower(),
        *[str(address).lower() for address in item.get("funder_addresses", [])],
        *[str(address).lower() for address in item.get("treasury_addresses", [])],
    ]
    for address in addresses:
        if address in known_closed:
            return known_closed[address]
    return str(item.get("funding_cluster_id", ""))
