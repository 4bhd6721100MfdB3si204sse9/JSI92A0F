from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable


JsonFetcher = Callable[[str], Any]
BalanceFetcher = Callable[[str, str, dict[str, Any]], int | dict[str, Any]]


@dataclass(frozen=True)
class LiveTarget:
    chain: str
    address: str
    label: str = ""
    metadata: dict[str, Any] | None = None


def build_explorer_snapshot(
    targets: list[LiveTarget],
    config: dict[str, Any],
    fetch_json: JsonFetcher,
    fetch_balance: BalanceFetcher | None = None,
) -> dict[str, Any]:
    clusters: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []
    closed_index = _closed_cluster_index(config)

    for target in targets:
        explorer = _chain_explorer_config(config, target.chain)
        if not explorer:
            continue
        try:
            item = _fetch_contract_snapshot(target, explorer, fetch_json, fetch_balance)
        except (RuntimeError, TimeoutError, OSError):
            continue
        if item is None:
            continue
        cluster_id = _cluster_id(item, closed_index)
        if cluster_id:
            item["funding_cluster_id"] = cluster_id
        contracts.append(item)

    for cluster in closed_index.values():
        clusters.append(cluster)

    return {
        "closed_project_clusters": clusters,
        "contracts": contracts,
    }


def _fetch_contract_snapshot(
    target: LiveTarget,
    explorer: dict[str, Any],
    fetch_json: JsonFetcher,
    fetch_balance: BalanceFetcher | None,
) -> dict[str, Any] | None:
    address = target.address.lower()
    source_code = _fetch_source_code(target.chain, address, explorer, fetch_json)
    txs = _fetch_recent_transactions(target.chain, address, explorer, fetch_json)
    token_txs = _fetch_token_transfers(target.chain, address, explorer, fetch_json)
    native_wei = _fetch_native_balance(target.chain, address, explorer, fetch_balance)

    native_balance_usd = _estimate_native_usd(native_wei, explorer)
    token_balances = _estimate_token_balances(token_txs)
    liquidity_usd = float(source_code.get("liquidity_usd", 0) or 0)
    volume24h_usd = float(source_code.get("volume24h_usd", 0) or 0)
    price_change_24h_pct = float(source_code.get("price_change_24h_pct", 0) or 0)
    metadata = _flatten_target_metadata(target.metadata or {})
    verified_source = _metadata_value(metadata, "verified_source", _is_verified_source(source_code))
    selectors = _selectors_from_transactions(txs)
    metadata_liquidity_usd = _metadata_float(metadata, "liquidity_usd")
    metadata_tvl_usd = _metadata_float(metadata, "tvl_usd")
    metadata_value_usd = _metadata_float(metadata, "value_at_risk_usd")
    metadata_token_balances = _metadata_token_balances(metadata)
    all_token_balances = [*token_balances, *metadata_token_balances]
    live_value_usd = native_balance_usd + sum(item["usd"] for item in token_balances)
    carried_value_usd = max(metadata_value_usd, metadata_tvl_usd, metadata_liquidity_usd)
    value_at_risk_usd = max(live_value_usd, carried_value_usd, liquidity_usd)
    return {
        "chain": target.chain,
        "address": address,
        "name": target.label or source_code.get("name") or source_code.get("ContractName") or address,
        "contract_name": source_code.get("contract_name") or source_code.get("ContractName") or source_code.get("name") or target.label or address,
        "contract_type": source_code.get("contract_type") or source_code.get("ContractType", ""),
        "category": metadata.get("category", source_code.get("category", "")),
        "url": metadata.get("url", source_code.get("url", "")),
        "verified_source": verified_source,
        "source_excerpt": source_code.get("source_excerpt", ""),
        "deployer_address": metadata.get("deployer_address", source_code.get("deployer_address", "")),
        "funder_addresses": source_code.get("funder_addresses", []),
        "treasury_addresses": source_code.get("treasury_addresses", []),
        "selectors": selectors,
        "native_balance_usd": native_balance_usd,
        "token_balances": all_token_balances,
        "liquidity_usd": max(metadata_liquidity_usd, liquidity_usd),
        "tvl_usd": max(metadata_tvl_usd, value_at_risk_usd),
        "volume24h_usd": float(metadata.get("volume24h_usd", volume24h_usd) or volume24h_usd),
        "price_change_24h_pct": float(metadata.get("price_change_24h_pct", price_change_24h_pct) or price_change_24h_pct),
        "tx_count_24h": len(txs),
        "tags": sorted(set(_source_tags(source_code, txs, token_txs) + list(metadata.get("tags", [])))),
        "value_at_risk_usd": value_at_risk_usd,
        "raw": {
            "source_code": source_code,
            "transactions": txs,
            "token_transfers": token_txs,
            "native_wei": native_wei,
            "metadata": metadata,
        },
    }


def _fetch_source_code(chain: str, address: str, explorer: dict[str, Any], fetch_json: JsonFetcher) -> dict[str, Any]:
    try:
        payload = _fetch_explorer_json(chain, address, explorer, "source_code_url", fetch_json)
    except (RuntimeError, TimeoutError, OSError):
        return {}
    return _normalize_first_result(payload)


def _fetch_recent_transactions(chain: str, address: str, explorer: dict[str, Any], fetch_json: JsonFetcher) -> list[dict[str, Any]]:
    try:
        payload = _fetch_explorer_json(chain, address, explorer, "txlist_url", fetch_json)
    except (RuntimeError, TimeoutError, OSError):
        return []
    return _normalize_result_list(payload)


def _fetch_token_transfers(chain: str, address: str, explorer: dict[str, Any], fetch_json: JsonFetcher) -> list[dict[str, Any]]:
    try:
        payload = _fetch_explorer_json(chain, address, explorer, "tokentx_url", fetch_json)
    except (RuntimeError, TimeoutError, OSError):
        return []
    return _normalize_result_list(payload)


def _fetch_explorer_json(
    chain: str,
    address: str,
    explorer: dict[str, Any],
    url_key: str,
    fetch_json: JsonFetcher,
) -> Any:
    last_error: Exception | None = None
    keys = _rotation_values(explorer, "api_keys", "api_key")
    for api_key in keys:
        url = explorer[url_key].format(address=address, chain=chain, api_key=api_key)
        try:
            payload = fetch_json(url)
        except (RuntimeError, TimeoutError, OSError) as exc:
            last_error = exc
            continue
        if _is_retryable_explorer_payload(payload):
            last_error = RuntimeError(f"explorer retryable response for {url_key}: {_payload_error_text(payload)}")
            continue
        return payload
    if last_error is not None:
        raise last_error
    url = explorer[url_key].format(address=address, chain=chain, api_key="")
    payload = fetch_json(url)
    if _is_retryable_explorer_payload(payload):
        raise RuntimeError(f"explorer retryable response for {url_key}: {_payload_error_text(payload)}")
    return payload


def _fetch_native_balance(
    chain: str,
    address: str,
    explorer: dict[str, Any],
    fetch_balance: BalanceFetcher | None,
) -> int | dict[str, Any]:
    if fetch_balance is None:
        return 0
    last_error: Exception | None = None
    rpc_urls = _rotation_values(explorer, "rpc_urls", "rpc_url")
    for rpc_url in rpc_urls:
        rotated = dict(explorer)
        rotated["rpc_url"] = rpc_url
        try:
            balance = fetch_balance(chain, address, rotated) or 0
        except (RuntimeError, TimeoutError, OSError) as exc:
            last_error = exc
            continue
        if _is_retryable_rpc_balance(balance):
            last_error = RuntimeError(f"rpc retryable balance response: {_payload_error_text(balance)}")
            continue
        return balance
    if last_error is not None:
        raise last_error
    return fetch_balance(chain, address, explorer) or 0


def _estimate_native_usd(native_balance: int | dict[str, Any], explorer: dict[str, Any]) -> float:
    if isinstance(native_balance, dict) and "usd" in native_balance:
        return float(native_balance.get("usd", 0) or 0)
    native_wei = int(native_balance or 0)
    native_price_usd = float(explorer.get("native_price_usd", 0) or 0)
    if native_wei <= 0 or native_price_usd <= 0:
        return 0.0
    return native_wei / 10**18 * native_price_usd


def _estimate_token_balances(token_txs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    balances: dict[str, float] = {}
    for tx in token_txs:
        symbol = str(tx.get("tokenSymbol") or tx.get("symbol") or tx.get("contractAddress") or "TOKEN")
        usd = float(tx.get("usdValue") or tx.get("valueUsd") or tx.get("usd") or 0)
        balances[symbol] = balances.get(symbol, 0.0) + usd
    return [{"token": token, "usd": usd} for token, usd in balances.items() if usd > 0]


def _flatten_target_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    nested = metadata.get("metadata")
    if not isinstance(nested, dict):
        return dict(metadata)
    flat = {**nested, **{key: value for key, value in metadata.items() if key != "metadata"}}
    tags = [
        *list(nested.get("tags", [])),
        *list(metadata.get("tags", [])),
    ]
    if tags:
        flat["tags"] = sorted({str(tag) for tag in tags if str(tag)})
    return flat


def _metadata_float(metadata: dict[str, Any], key: str) -> float:
    return float(metadata.get(key, 0) or 0)


def _metadata_value(metadata: dict[str, Any], key: str, fallback: Any) -> Any:
    value = metadata.get(key)
    return fallback if value is None else value


def _metadata_token_balances(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    balances = metadata.get("token_balances", [])
    if not isinstance(balances, list):
        return []
    normalized: list[dict[str, Any]] = []
    for balance in balances:
        if not isinstance(balance, dict):
            continue
        usd = float(balance.get("usd") or balance.get("value_usd") or balance.get("valueUsd") or 0)
        if usd <= 0:
            continue
        token = str(balance.get("token") or balance.get("symbol") or balance.get("contractAddress") or "TOKEN")
        normalized.append({"token": token, "usd": usd})
    return normalized


def _selectors_from_transactions(txs: list[dict[str, Any]]) -> list[str]:
    selectors: list[str] = []
    seen: set[str] = set()
    for tx in txs:
        selector = str(tx.get("methodId") or tx.get("selector") or "").lower()
        if selector and selector not in seen:
            seen.add(selector)
            selectors.append(selector)
    return selectors


def _source_tags(source_code: dict[str, Any], txs: list[dict[str, Any]], token_txs: list[dict[str, Any]]) -> list[str]:
    tags = list(source_code.get("tags", []))
    if source_code.get("verified") is False:
        tags.append("unverified_contract")
    if len(txs) >= 100:
        tags.append("high_tx_count")
    if any(str(tx.get("methodId") or tx.get("selector") or "").lower() in {"0x414bf389", "0xfa461e33", "0x0d8f6a1c", "0x1b11d0ff", "0x10d1e85c"} for tx in txs):
        tags.append("flashloan_user")
    if any("router" in str(tx.get("to", "")).lower() for tx in token_txs):
        tags.append("dex_path_executor")
    return tags


def _is_verified_source(source_code: dict[str, Any]) -> bool | None:
    verified = source_code.get("verified")
    if isinstance(verified, bool):
        return verified
    if "SourceCode" in source_code or "source_code" in source_code:
        return True
    return None


def _normalize_first_result(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                return first
        if isinstance(result, dict):
            return result
        return payload
    return {}


def _normalize_result_list(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    result = payload.get("result", [])
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]
    return []


def _chain_explorer_config(config: dict[str, Any], chain: str) -> dict[str, Any]:
    explorers = config.get("live_explorers", {})
    chain_key = chain.lower()
    explorer = dict(explorers.get(chain_key, {}))
    env_prefix = f"SENTINEL_{chain_key.upper()}".replace("-", "_")
    api_keys = _ordered_unique(
        [
            *_env_values(f"{env_prefix}_EXPLORER_API_KEYS", f"{env_prefix}_SCAN_API_KEYS"),
            *_env_values(f"{env_prefix}_EXPLORER_API_KEY", f"{env_prefix}_SCAN_API_KEY"),
            *_config_values(explorer, "api_keys", "api_key"),
        ]
    )
    rpc_urls = _ordered_unique(
        [
            *_env_values(f"{env_prefix}_RPC_URLS"),
            *_env_values(f"{env_prefix}_RPC_URL"),
            *_config_values(explorer, "rpc_urls", "rpc_url"),
        ]
    )
    native_price = _env_first(f"{env_prefix}_NATIVE_PRICE_USD")
    if api_keys:
        explorer["api_keys"] = api_keys
        explorer["api_key"] = api_keys[0]
    if rpc_urls:
        explorer["rpc_urls"] = rpc_urls
        explorer["rpc_url"] = rpc_urls[0]
    if native_price:
        explorer["native_price_usd"] = native_price
    return explorer


def _closed_cluster_index(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    clusters: dict[str, dict[str, Any]] = {}
    for cluster in config.get("closed_project_clusters", []):
        cluster_id = str(cluster.get("id", "closed-project-cluster"))
        clusters[cluster_id] = cluster
    return clusters


def load_live_targets(path: str | Path) -> list[LiveTarget]:
    payload = json.loads(Path(path).read_text())
    entries = payload.get("targets", payload if isinstance(payload, list) else [])
    targets: list[LiveTarget] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        chain = str(item.get("chain", "")).lower()
        address = str(item.get("address", "")).lower()
        if chain and address:
            metadata = {key: value for key, value in item.items() if key not in {"chain", "address", "label"}}
            targets.append(LiveTarget(chain=chain, address=address, label=str(item.get("label", "")), metadata=metadata or None))
    return targets


def http_balance_fetcher(url_template: str) -> BalanceFetcher:
    def fetch(chain: str, address: str, explorer: dict[str, Any]) -> int:
        url = url_template.format(address=address, chain=chain, api_key=explorer.get("api_key", ""))
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getBalance",
            "params": [address, "latest"],
        }
        request = json.dumps(payload).encode("utf-8")
        import urllib.request

        req = urllib.request.Request(url, data=request, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        if isinstance(result, dict):
            hex_value = str(result.get("result", "0x0"))
            return int(hex_value, 16)
        return 0

    return fetch


def _cluster_id(item: dict[str, Any], closed_index: dict[str, dict[str, Any]]) -> str:
    deployer = str(item.get("deployer_address", "")).lower()
    funders = [str(address).lower() for address in item.get("funder_addresses", [])]
    treasuries = [str(address).lower() for address in item.get("treasury_addresses", [])]
    for cluster_id, cluster in closed_index.items():
        addresses = {
            *(str(address).lower() for address in cluster.get("deployer_addresses", [])),
            *(str(address).lower() for address in cluster.get("funder_addresses", [])),
            *(str(address).lower() for address in cluster.get("treasury_addresses", [])),
            *(str(address).lower() for address in cluster.get("project_addresses", [])),
        }
        if deployer in addresses or any(address in addresses for address in [*funders, *treasuries]):
            return cluster_id
    return str(item.get("funding_cluster_id", ""))


def _env_first(*names: str) -> str:
    import os

    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def _env_values(*names: str) -> list[str]:
    import os

    values: list[str] = []
    for name in names:
        values.extend(_split_rotation_values(os.environ.get(name, "")))
    return values


def _config_values(config: dict[str, Any], list_key: str, scalar_key: str) -> list[str]:
    values: list[str] = []
    raw_list = config.get(list_key, [])
    if isinstance(raw_list, list):
        values.extend(str(value).strip() for value in raw_list)
    elif raw_list:
        values.extend(_split_rotation_values(str(raw_list)))
    raw_scalar = config.get(scalar_key, "")
    if raw_scalar:
        values.append(str(raw_scalar).strip())
    return [value for value in values if value]


def _split_rotation_values(raw: str) -> list[str]:
    if not raw:
        return []
    text = raw.strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, list):
        return [str(value).strip() for value in parsed if str(value).strip()]
    return [value.strip() for value in text.replace("\n", ",").replace(" ", ",").split(",") if value.strip()]


def _ordered_unique(values: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def _rotation_values(config: dict[str, Any], list_key: str, scalar_key: str) -> list[str]:
    values = _ordered_unique(_config_values(config, list_key, scalar_key))
    return values or [""]


def _is_retryable_explorer_payload(payload: Any) -> bool:
    text = _payload_error_text(payload).lower()
    return any(
        marker in text
        for marker in (
            "rate limit",
            "rate-limit",
            "max rate",
            "too many requests",
            "limit reached",
            "temporarily unavailable",
            "timeout",
            "try again",
        )
    )


def _is_retryable_rpc_balance(balance: int | dict[str, Any]) -> bool:
    if not isinstance(balance, dict):
        return False
    text = _payload_error_text(balance).lower()
    return any(
        marker in text
        for marker in (
            "rate limit",
            "rate-limit",
            "too many requests",
            "limit reached",
            "temporarily unavailable",
            "timeout",
            "try again",
        )
    )


def _payload_error_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    parts: list[str] = []
    for key in ("status", "message", "result", "error"):
        value = payload.get(key)
        if isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts)
