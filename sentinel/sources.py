from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from .chain_scanner import load_bsc_chain_candidates, load_ethereum_chain_candidates
from .explorer import load_explorer_snapshot, load_explorer_snapshot_payload
from .live_adapters import build_explorer_snapshot, http_balance_fetcher, load_live_targets
from .models import Candidate


USER_AGENT = "protocol-sentinel/0.1 defensive-research"


def load_candidates(source: str, config: dict[str, Any], limit: int, input_path: str | None = None) -> list[Candidate]:
    if source == "sample":
        return load_sample(limit)
    if source == "explorer_snapshot":
        path = input_path or config.get("sources", {}).get("explorer_snapshot", {}).get("path", "examples/explorer_snapshot.json")
        return load_explorer_snapshot(path, config, limit)
    if source == "explorer_live":
        path = input_path or config.get("sources", {}).get("explorer_live", {}).get("path", "examples/live_targets.json")
        targets = load_live_targets(path)
        snapshot = build_explorer_snapshot(targets[:limit], config, fetch_json=fetch_json, fetch_balance=_balance_fetcher_for(config))
        snapshot_path = os.environ.get("SENTINEL_LIVE_SNAPSHOT_PATH")
        if snapshot_path:
            snapshot_output = Path(snapshot_path)
            snapshot_output.parent.mkdir(parents=True, exist_ok=True)
            snapshot_output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return load_explorer_snapshot_from_snapshot(snapshot, config, limit)
    if source == "all":
        candidates: list[Candidate] = []
        for source_name in (
            "dexscreener_profiles",
            "dexscreener_boosts",
            "defillama_protocols",
            "ethereum_chain_scanner",
            "bsc_chain_scanner",
            "explorer_snapshot",
            "explorer_live",
        ):
            if config.get("sources", {}).get(source_name, {}).get("enabled", False):
                candidates.extend(load_candidates(source_name, config, limit, input_path))
        return dedupe(candidates)
    if source == "dexscreener_profiles":
        return fetch_dexscreener_tokens(config, source, limit, "latest_profile")
    if source == "dexscreener_boosts":
        return fetch_dexscreener_tokens(config, source, limit, "latest_boost")
    if source == "defillama_protocols":
        return fetch_defillama_protocols(config, limit)
    if source == "ethereum_chain_scanner":
        return load_ethereum_chain_candidates(config, limit)
    if source == "bsc_chain_scanner":
        return load_bsc_chain_candidates(config, limit)
    raise ValueError(f"unknown source: {source}")


def load_sample(limit: int) -> list[Candidate]:
    path = Path(__file__).resolve().parent.parent / "examples" / "sample_source.json"
    payload = json.loads(path.read_text())
    return [candidate_from_dict(item) for item in payload[:limit]]


def load_explorer_snapshot_from_snapshot(snapshot: dict[str, Any], config: dict[str, Any], limit: int) -> list[Candidate]:
    return load_explorer_snapshot_payload(snapshot, config, limit)


def fetch_dexscreener_tokens(
    config: dict[str, Any],
    source_name: str,
    limit: int,
    tag: str,
) -> list[Candidate]:
    source_config = config["sources"][source_name]
    token_items = fetch_json(source_config["url"])
    if isinstance(token_items, dict):
        token_items = [token_items]

    candidates: list[Candidate] = []
    for item in token_items[:limit]:
        chain = str(item.get("chainId", "")).lower()
        token_address = str(item.get("tokenAddress", ""))
        if not chain or not token_address:
            continue
        pairs = fetch_dexscreener_pairs(chain, token_address)
        if not pairs:
            candidates.append(
                Candidate(
                    source=source_name,
                    external_id=f"{chain}:{token_address}",
                    name=token_address,
                    chain=chain,
                    entity_type="protocol",
                    address=token_address,
                    url=str(item.get("url", "")),
                    tags=[tag],
                    raw=item,
                )
            )
            continue
        for pair in pairs[:3]:
            candidates.append(candidate_from_dex_pair(source_name, pair, token_address, item, tag))
        time.sleep(0.2)
    return dedupe(candidates)


def fetch_dexscreener_pairs(chain: str, token_address: str) -> list[dict[str, Any]]:
    url = f"https://api.dexscreener.com/token-pairs/v1/{urllib.parse.quote(chain)}/{urllib.parse.quote(token_address)}"
    try:
        payload = fetch_json(url)
    except RuntimeError:
        return []
    if not isinstance(payload, list):
        return []
    return sorted(payload, key=lambda pair: _nested_float(pair, ["liquidity", "usd"]), reverse=True)


def fetch_defillama_protocols(config: dict[str, Any], limit: int) -> list[Candidate]:
    payload = fetch_json(config["sources"]["defillama_protocols"]["url"])
    if not isinstance(payload, list):
        return []
    protocols = sorted(payload, key=lambda item: float(item.get("tvl") or 0), reverse=True)
    candidates: list[Candidate] = []
    for item in protocols[:limit]:
        chains = item.get("chains") or []
        chain = str(chains[0]).lower() if chains else "multi"
        tags = ["defillama"]
        if len(chains) > 1:
            tags.append("multi_chain")
        category = str(item.get("category", ""))
        candidates.append(
            Candidate(
                source="defillama_protocols",
                external_id=str(item.get("slug") or item.get("name")),
                name=str(item.get("name") or item.get("slug")),
                chain=chain,
                entity_type="protocol",
                category=category,
                url=str(item.get("url", "")),
                tvl_usd=float(item.get("tvl") or 0),
                tags=tags,
                raw=item,
            )
        )
    return candidates


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=float(os.environ.get("SENTINEL_FETCH_TIMEOUT_SECONDS", "60"))) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"fetch failed for {_redact_url_secret(url)}: {exc}") from exc


def _redact_url_secret(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted = [
        (key, "[REDACTED]" if key.lower() in {"apikey", "api_key", "key", "token"} and value else value)
        for key, value in query
    ]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(redacted), parsed.fragment))


def _balance_fetcher_for(config: dict[str, Any]):
    live_explorers = config.get("live_explorers", {})

    def fetch(chain: str, address: str, explorer: dict[str, Any]) -> int:
        rpc_template = explorer.get("rpc_url", "")
        if not rpc_template:
            return 0
        fetcher = http_balance_fetcher(rpc_template)
        return fetcher(chain, address, explorer)

    return fetch


def candidate_from_dex_pair(
    source_name: str,
    pair: dict[str, Any],
    token_address: str,
    profile: dict[str, Any],
    tag: str,
) -> Candidate:
    base = pair.get("baseToken") or {}
    quote = pair.get("quoteToken") or {}
    name = str(base.get("name") or base.get("symbol") or token_address)
    tags = [tag, str(pair.get("dexId", ""))]
    labels = pair.get("labels") or []
    tags.extend(str(label) for label in labels)
    description = str(profile.get("description", ""))
    return Candidate(
        source=source_name,
        external_id=f"{pair.get('chainId')}:{pair.get('pairAddress') or token_address}",
        name=name,
        chain=str(pair.get("chainId", "")).lower(),
        entity_type="protocol",
        address=token_address,
        category=str(quote.get("symbol", "")),
        url=str(pair.get("url") or profile.get("url") or ""),
        liquidity_usd=_nested_float(pair, ["liquidity", "usd"]),
        volume24h_usd=_nested_float(pair, ["volume", "h24"]),
        fdv_usd=float(pair.get("fdv") or 0),
        price_change_24h_pct=_nested_float(pair, ["priceChange", "h24"]),
        created_at_ms=int(pair["pairCreatedAt"]) if pair.get("pairCreatedAt") else None,
        tags=[tag for tag in tags if tag],
        raw={**pair, "profileDescription": description},
    )


def candidate_from_dict(item: dict[str, Any]) -> Candidate:
    return Candidate(
        source=str(item.get("source", "sample")),
        external_id=str(item.get("external_id", item.get("name", "sample"))),
        name=str(item.get("name", "")),
        chain=str(item.get("chain", "")),
        entity_type=str(item.get("entity_type", "protocol")),
        address=str(item.get("address", "")),
        category=str(item.get("category", "")),
        url=str(item.get("url", "")),
        liquidity_usd=float(item.get("liquidity_usd", 0) or 0),
        tvl_usd=float(item.get("tvl_usd", 0) or 0),
        volume24h_usd=float(item.get("volume24h_usd", 0) or 0),
        fdv_usd=float(item.get("fdv_usd", 0) or 0),
        price_change_24h_pct=float(item.get("price_change_24h_pct", 0) or 0),
        verified_source=item.get("verified_source"),
        deployer_address=str(item.get("deployer_address", "")),
        funding_cluster_id=str(item.get("funding_cluster_id", "")),
        created_at_ms=item.get("created_at_ms"),
        tags=list(item.get("tags", [])),
        raw=dict(item.get("raw", {})),
    )


def dedupe(candidates: Iterable[Candidate]) -> list[Candidate]:
    seen: dict[str, Candidate] = {}
    for candidate in candidates:
        key = candidate.stable_key()
        previous = seen.get(key)
        if previous is None or candidate.value_at_risk() > previous.value_at_risk():
            seen[key] = candidate
    return list(seen.values())


def _nested_float(item: dict[str, Any], path: list[str]) -> float:
    current: Any = item
    for key in path:
        if not isinstance(current, dict):
            return 0.0
        current = current.get(key)
    return float(current or 0)
