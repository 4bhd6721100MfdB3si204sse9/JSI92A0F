from __future__ import annotations

import json
import os
import hashlib
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from .models import Candidate


JsonRpcCaller = Callable[[str, str, list[Any]], Any]
ExplorerFetcher = Callable[[str], Any]


BOT_KEYWORDS = (
    "arbitrage",
    "bot",
    "executor",
    "flashloan",
    "keeper",
    "liquidator",
    "mev",
    "sniper",
)
DEX_KEYWORDS = ("swap", "router", "uniswap", "sushiswap", "curve", "balancer", "1inch", "pancake")
REWARD_KEYWORDS = ("reward", "staking", "farm", "claim", "emission", "distributor")
VAULT_KEYWORDS = ("vault", "strategy", "share", "asset", "yield")
DEFAULT_KNOWN_PUBLIC_PROTOCOL_KEYWORDS = (
    "aave",
    "balancer",
    "biswap",
    "compound",
    "curve",
    "frax",
    "lido",
    "pancake",
    "pancakeswap",
    "stargate",
    "sushiswap",
    "uniswap",
    "venus",
    "yearn",
)
DEFAULT_KNOWN_PUBLIC_PROTOCOL_SOURCE_MARKERS = (
    "copyright (c) 2024 pancakeswap",
    "pancakeswap infinity",
)
ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
CHAIN_ADDRESS_URLS = {
    "ethereum": "https://etherscan.io/address/{address}",
    "bsc": "https://bscscan.com/address/{address}",
}
KNOWN_CHAIN_TOKENS = {
    "ethereum": {
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {"symbol": "USDC", "decimals": 6, "price_usd": 1.0, "kind": "stablecoin"},
        "0xdac17f958d2ee523a2206206994597c13d831ec7": {"symbol": "USDT", "decimals": 6, "price_usd": 1.0, "kind": "stablecoin"},
        "0x6b175474e89094c44da98b954eedeac495271d0f": {"symbol": "DAI", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0x853d955acef822db058eb8505911ed77f175b99e": {"symbol": "FRAX", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0x83f20f44975d03b1b09e64809b757c47f942beea": {"symbol": "sDAI", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {"symbol": "WETH", "decimals": 18, "price_usd": "native", "kind": "bluechip"},
        "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {"symbol": "WBTC", "decimals": 8, "price_usd": 0.0, "kind": "bluechip"},
        "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": {"symbol": "stETH", "decimals": 18, "price_usd": "native", "kind": "bluechip"},
        "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": {"symbol": "wstETH", "decimals": 18, "price_usd": "native", "kind": "bluechip"},
    },
    "bsc": {
        "0x55d398326f99059ff775485246999027b3197955": {"symbol": "USDT", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": {"symbol": "USDC", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0xe9e7cea3dedca5984780bafc599bd69add087d56": {"symbol": "BUSD", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0xc5f0f7b66764f6ec8c8dff7ba683102295e16409": {"symbol": "FDUSD", "decimals": 18, "price_usd": 1.0, "kind": "stablecoin"},
        "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c": {"symbol": "WBNB", "decimals": 18, "price_usd": "native", "kind": "bluechip"},
        "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c": {"symbol": "BTCB", "decimals": 18, "price_usd": 0.0, "kind": "bluechip"},
        "0x2170ed0880ac9a755fd29b2688956bd959f933f8": {"symbol": "ETH", "decimals": 18, "price_usd": 0.0, "kind": "bluechip"},
    },
}


@dataclass(frozen=True)
class Deployment:
    address: str
    deployer: str
    tx_hash: str
    block_number: int
    timestamp_ms: int | None
    value_wei: int
    discovery_source: str = "contract_creation"
    seed_token_addresses: tuple[str, ...] = ()


@dataclass(frozen=True)
class KnownContract:
    address: str
    deployer: str
    first_seen_block: int
    timestamp_ms: int | None = None


@dataclass(frozen=True)
class Funding:
    address: str
    value_wei: int
    is_eoa: bool


@dataclass(frozen=True)
class TokenHolding:
    token_address: str
    symbol: str
    decimals: int
    balance_raw: int
    balance: float
    price_usd: float
    price_source: str
    asset_kind: str
    value_usd: float


def load_ethereum_chain_candidates(
    config: dict[str, Any],
    limit: int,
    rpc_call: JsonRpcCaller | None = None,
    fetch_json: ExplorerFetcher | None = None,
) -> list[Candidate]:
    scanner = EthereumChainScanner("ethereum", "ethereum_chain_scanner", config, rpc_call=rpc_call, fetch_json=fetch_json)
    return scanner.scan(limit)


def load_bsc_chain_candidates(
    config: dict[str, Any],
    limit: int,
    rpc_call: JsonRpcCaller | None = None,
    fetch_json: ExplorerFetcher | None = None,
) -> list[Candidate]:
    scanner = EthereumChainScanner("bsc", "bsc_chain_scanner", config, rpc_call=rpc_call, fetch_json=fetch_json)
    return scanner.scan(limit)


class EthereumChainScanner:
    def __init__(
        self,
        chain: str,
        source_name: str,
        config: dict[str, Any],
        rpc_call: JsonRpcCaller | None = None,
        fetch_json: ExplorerFetcher | None = None,
    ) -> None:
        self.chain = chain
        self.source_name = source_name
        self.env_prefix = "BSC" if chain == "bsc" else chain.upper()
        self.config = config
        source_config = dict(config.get("sources", {}).get(source_name, {}))
        self.source_config = source_config
        self.rpc_call = rpc_call or self._rpc_call
        self.fetch_json = fetch_json or self._fetch_json
        explorer_config = dict(config.get("live_explorers", {}).get(chain, {}))
        self.rpc_urls = _rotation_values(
            os.environ.get(f"SENTINEL_{self.env_prefix}_RPC_URLS", ""),
            os.environ.get(f"SENTINEL_{self.env_prefix}_RPC_URL", ""),
            source_config.get("rpc_urls", []),
            source_config.get("rpc_url", ""),
            explorer_config.get("rpc_urls", []),
            explorer_config.get("rpc_url", ""),
        )
        self.api_keys = _rotation_values(
            os.environ.get(f"SENTINEL_{self.env_prefix}_EXPLORER_API_KEYS", ""),
            os.environ.get(f"SENTINEL_{self.env_prefix}_EXPLORER_API_KEY", ""),
            source_config.get("api_keys", []),
            source_config.get("api_key", ""),
            explorer_config.get("api_keys", []),
            explorer_config.get("api_key", ""),
        )
        self.explorer = explorer_config
        self.state_path = Path(str(os.environ.get(f"SENTINEL_{self.env_prefix}_SCANNER_STATE_PATH") or source_config.get("state_path") or f"state/{source_name}.json"))
        self.native_price_usd = _float_first(
            os.environ.get(f"SENTINEL_{self.env_prefix}_NATIVE_PRICE_USD", ""),
            source_config.get("native_price_usd", ""),
            self.explorer.get("native_price_usd", ""),
            0,
        )

    def scan(self, limit: int) -> list[Candidate]:
        if not self.rpc_urls:
            return []
        state = self._load_state()
        first_run_blocks = int(self.source_config.get("first_run_blocks", self.source_config.get("recent_blocks", 250)) or 250)
        incremental_blocks = int(self.source_config.get("recent_blocks", 250) or 250)
        remembered_raw = self.source_config.get("remembered_contracts_per_run", 25)
        remembered_limit = int(remembered_raw if remembered_raw is not None else 25)
        max_contracts = min(int(self.source_config.get("max_contracts", limit) or limit), limit)
        raw_transfer_limit = self.source_config.get("max_transfer_recipients", max_contracts)
        max_transfer_recipients = int(raw_transfer_limit if raw_transfer_limit is not None else max_contracts)
        if max_contracts <= 0:
            return []

        latest = int(str(self._rpc("eth_blockNumber", [])), 16)
        last_scanned = int(state.get("last_scanned_block", 0) or 0)
        if last_scanned > 0:
            first_block = min(last_scanned + 1, latest)
            if first_block > latest:
                first_block = max(latest - incremental_blocks + 1, 0)
        else:
            first_block = max(latest - first_run_blocks + 1, 0)

        deployments = self._recent_deployments(first_block, latest, max_contracts)
        transfer_recipients = self._transfer_log_deployments(first_block, latest, max_transfer_recipients)
        remembered = self._remembered_deployments(state, remembered_limit)
        deployments = _dedupe_deployments([*deployments, *transfer_recipients, *remembered])
        candidates: list[Candidate] = []
        for deployment in deployments:
            previous_record = state.get("seen_contracts", {}).get(deployment.address.lower(), {})
            try:
                candidate = self._candidate_from_deployment(deployment, previous_record if isinstance(previous_record, dict) else {})
            except (RuntimeError, TimeoutError, OSError):
                continue
            if candidate is not None:
                candidates.append(candidate)
                self._record_candidate(state, candidate)
        state["last_scanned_block"] = max(latest, int(state.get("last_scanned_block", 0) or 0))
        self._save_state(state)
        return candidates

    def _recent_deployments(self, first: int, latest: int, max_contracts: int) -> list[Deployment]:
        deployments: list[Deployment] = []
        max_receipt_checks = int(self.source_config.get("max_deployment_receipt_checks", 250) or 250)
        receipt_checks = 0
        for block_number in range(latest, first - 1, -1):
            block = self._rpc("eth_getBlockByNumber", [hex(block_number), True])
            if not isinstance(block, dict):
                continue
            timestamp_ms = _hex_to_int(block.get("timestamp")) * 1000 if block.get("timestamp") else None
            txs = block.get("transactions", [])
            if not isinstance(txs, list):
                continue
            for tx in txs:
                if not isinstance(tx, dict) or tx.get("to") not in ("0x", "", None):
                    continue
                if receipt_checks >= max_receipt_checks:
                    return deployments
                receipt_checks += 1
                receipt = self._rpc("eth_getTransactionReceipt", [tx.get("hash")])
                if not isinstance(receipt, dict):
                    continue
                address = str(receipt.get("contractAddress") or "").lower()
                if not address:
                    continue
                deployments.append(
                    Deployment(
                        address=address,
                        deployer=str(tx.get("from") or "").lower(),
                        tx_hash=str(tx.get("hash") or ""),
                        block_number=block_number,
                        timestamp_ms=timestamp_ms,
                        value_wei=_hex_to_int(tx.get("value")),
                    )
                )
                if len(deployments) >= max_contracts:
                    return deployments
        return deployments

    def _transfer_log_deployments(self, first: int, latest: int, max_recipients: int) -> list[Deployment]:
        if max_recipients <= 0:
            return []
        chunk_size = int(self.source_config.get("transfer_log_chunk_size", 100) or 100)
        deployments: list[Deployment] = []
        seen: set[str] = set()
        start = first
        while start <= latest and len(deployments) < max_recipients:
            end = min(start + chunk_size - 1, latest)
            logs = self._transfer_logs(start, end)
            for log in logs:
                if not isinstance(log, dict):
                    continue
                topics = log.get("topics", [])
                if not isinstance(topics, list) or len(topics) < 3:
                    continue
                recipient = _topic_address(str(topics[2]))
                token = str(log.get("address") or "").lower()
                if not recipient or not token or recipient in seen:
                    continue
                if self._eth_get_code(recipient) in {"0x", "0x0", ""}:
                    continue
                seen.add(recipient)
                deployments.append(
                    Deployment(
                        address=recipient,
                        deployer="",
                        tx_hash=str(log.get("transactionHash") or ""),
                        block_number=_hex_to_int(log.get("blockNumber")),
                        timestamp_ms=None,
                        value_wei=0,
                        discovery_source="erc20_transfer_log",
                        seed_token_addresses=(token,),
                    )
                )
                if len(deployments) >= max_recipients:
                    break
            start = end + 1
        return deployments

    def _transfer_logs(self, first: int, latest: int) -> list[dict[str, Any]]:
        try:
            payload = self._rpc(
                "eth_getLogs",
                [
                    {
                        "fromBlock": hex(first),
                        "toBlock": hex(latest),
                        "topics": [ERC20_TRANSFER_TOPIC],
                    }
                ],
            )
        except (RuntimeError, TimeoutError, OSError):
            return []
        return payload if isinstance(payload, list) else []

    def _remembered_deployments(self, state: dict[str, Any], limit: int) -> list[Deployment]:
        if limit <= 0:
            return []
        contracts = state.get("seen_contracts", {})
        if not isinstance(contracts, dict):
            return []
        ranked = sorted(
            (item for item in contracts.items() if isinstance(item[1], dict)),
            key=lambda item: float(item[1].get("max_value_usd", 0) or 0),
            reverse=True,
        )
        deployments: list[Deployment] = []
        for address, payload in ranked[:limit]:
            deployments.append(
                Deployment(
                    address=str(address).lower(),
                    deployer=str(payload.get("deployer", "")).lower(),
                    tx_hash=str(payload.get("deployment_tx", "")),
                    block_number=int(payload.get("first_seen_block", 0) or 0),
                    timestamp_ms=int(payload["created_at_ms"]) if payload.get("created_at_ms") else None,
                    value_wei=0,
                    discovery_source=str(payload.get("discovery_source", "remembered")),
                    seed_token_addresses=tuple(str(token).lower() for token in payload.get("token_addresses", []) if str(token).strip()),
                )
            )
        return deployments

    def _record_candidate(self, state: dict[str, Any], candidate: Candidate) -> None:
        contracts = state.setdefault("seen_contracts", {})
        if not isinstance(contracts, dict):
            contracts = {}
            state["seen_contracts"] = contracts
        current = contracts.get(candidate.address, {})
        if not isinstance(current, dict):
            current = {}
        value = float(candidate.tvl_usd or 0)
        first_seen = int(current.get("first_seen_block", candidate.raw.get("deployment_block", 0)) or 0)
        contracts[candidate.address] = {
            "deployer": candidate.deployer_address,
            "first_seen_block": first_seen,
            "last_seen_block": int(candidate.raw.get("deployment_block", first_seen) or first_seen),
            "created_at_ms": candidate.created_at_ms,
            "deployment_tx": candidate.raw.get("deployment_tx", ""),
            "discovery_source": candidate.raw.get("discovery_source", ""),
            "token_addresses": [
                str(item.get("token_address", "")).lower()
                for item in candidate.raw.get("token_balances", [])
                if isinstance(item, dict) and item.get("token_address")
            ],
            "max_value_usd": max(float(current.get("max_value_usd", 0) or 0), value),
            "last_value_usd": value,
            "tags": candidate.tags,
            "updated_at_block": int(state.get("last_scanned_block", 0) or 0),
        }

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"last_scanned_block": 0, "seen_contracts": {}}
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"last_scanned_block": 0, "seen_contracts": {}}
        if not isinstance(payload, dict):
            return {"last_scanned_block": 0, "seen_contracts": {}}
        payload.setdefault("last_scanned_block", 0)
        payload.setdefault("seen_contracts", {})
        return payload

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _candidate_from_deployment(self, deployment: Deployment, previous_record: dict[str, Any] | None = None) -> Candidate | None:
        previous_record = previous_record or {}
        balance_wei = self._eth_get_balance(deployment.address)
        source = self._source_code(deployment.address)
        txs = self._txlist(deployment.address)
        token_txs = self._tokentx(deployment.address)
        token_holdings = self._erc20_holdings(deployment.address, token_txs, deployment.seed_token_addresses)
        source_text = _source_text(source)
        contract_name = _contract_name(source) or deployment.address
        verified = _is_verified(source)
        incoming_funders = self._incoming_funders(txs, deployment.address)
        cluster_match = _cluster_match(deployment.deployer, [funder.address for funder in incoming_funders], self.config)
        code = self._eth_get_code(deployment.address)
        known_public_reason = self._known_public_protocol_reason(deployment.address, code)
        popular_protocol_hint = self._popular_protocol_hint(contract_name, source_text)
        balance_eth = balance_wei / 10**18
        native_usd = balance_eth * self.native_price_usd if self.native_price_usd else 0.0
        token_usd = sum(holding.value_usd for holding in token_holdings)
        total_usd = native_usd + token_usd
        previous_value_usd = _float_from_any(previous_record.get("last_value_usd", 0))
        tags = self._tags(
            deployment,
            native_usd,
            token_usd,
            total_usd,
            previous_value_usd,
            verified,
            contract_name,
            source_text,
            txs,
            incoming_funders,
            cluster_match,
            token_holdings,
            known_public_reason,
            popular_protocol_hint,
        )
        entity_type = self._entity_type(tags, verified)

        return Candidate(
            source=self.source_name,
            external_id=f"{self.chain}:{deployment.address}",
            name=contract_name,
            chain=self.chain,
            entity_type=entity_type,
            address=deployment.address,
            category=_category(tags, source_text, contract_name),
            url=CHAIN_ADDRESS_URLS.get(self.chain, "{address}").format(address=deployment.address),
            tvl_usd=total_usd,
            verified_source=verified,
            deployer_address=deployment.deployer,
            funding_cluster_id=cluster_match.get("cluster_id", ""),
            created_at_ms=deployment.timestamp_ms,
            tags=tags,
            raw={
                "deployment_tx": deployment.tx_hash,
                "deployment_block": deployment.block_number,
                "discovery_source": deployment.discovery_source,
                "deployment_value_wei": str(deployment.value_wei),
                "native_balance_wei": str(balance_wei),
                "native_balance_eth": balance_eth,
                "native_balance_usd": native_usd,
                "native_price_usd": self.native_price_usd,
                "token_balances": [
                    {
                        "token_address": holding.token_address,
                        "symbol": holding.symbol,
                        "decimals": holding.decimals,
                        "balance_raw": str(holding.balance_raw),
                        "balance": holding.balance,
                        "price_usd": holding.price_usd,
                        "price_source": holding.price_source,
                        "asset_kind": holding.asset_kind,
                        "value_usd": holding.value_usd,
                    }
                    for holding in token_holdings
                ],
                "token_balance_usd": token_usd,
                "total_value_usd": total_usd,
                "previous_value_usd": previous_value_usd,
                "incoming_funders": [
                    {"address": funder.address, "value_wei": str(funder.value_wei), "is_eoa": funder.is_eoa}
                    for funder in incoming_funders
                ],
                "cluster_match": cluster_match,
                "tx_count": len(txs),
                "verified_source": verified,
                "contract_name": contract_name,
                "known_public_protocol_reason": known_public_reason,
                "popular_protocol_hint_reason": popular_protocol_hint,
            },
        )

    def _tags(
        self,
        deployment: Deployment,
        native_usd: float,
        token_usd: float,
        total_usd: float,
        previous_value_usd: float,
        verified: bool | None,
        contract_name: str,
        source_text: str,
        txs: list[dict[str, Any]],
        incoming_funders: list[Funding],
        cluster_match: dict[str, str],
        token_holdings: list[TokenHolding],
        known_public_reason: str,
        popular_protocol_hint: str,
    ) -> list[str]:
        text = f"{contract_name} {source_text}".lower()
        target_min_usd = float(self.source_config.get("target_min_value_usd", self.config.get("min_value_usd", 200_000)) or 200_000)
        high_tx_threshold = int(self.source_config.get("high_tx_count", 50) or 50)
        tags = ["known_public_protocol", "popular_protocol"] if known_public_reason else ["unknown_protocol"]
        if popular_protocol_hint and not known_public_reason:
            tags.extend(["popular_protocol_name_hint", "possible_protocol_impersonation"])
        if deployment.discovery_source == "erc20_transfer_log":
            tags.append("token_funded_contract")
        else:
            tags.append("fresh_deployment")
        if not known_public_reason and _is_unfamiliar_contract(deployment.address, contract_name, source_text, verified):
            tags.append("unfamiliar_contract")
        if not known_public_reason and verified is None:
            tags.append("unknown_verification_status")
        if native_usd >= target_min_usd:
            tags.extend(["high_native_balance", "fresh_contract_large_balance"])
        if token_usd >= target_min_usd:
            tags.extend(["high_token_balance", "fresh_contract_large_token_balance", "fresh_contract_large_balance"])
        if total_usd >= target_min_usd:
            tags.append("high_total_balance")
        if any(holding.price_source == "known_asset" and holding.value_usd >= target_min_usd for holding in token_holdings):
            tags.append("known_asset_balance")
        if any(holding.asset_kind == "stablecoin" and holding.value_usd >= target_min_usd for holding in token_holdings):
            tags.append("stablecoin_balance")
        if any(holding.asset_kind == "bluechip" and holding.value_usd >= target_min_usd for holding in token_holdings):
            tags.append("bluechip_token_balance")
        if _wei_usd(deployment.value_wei, self.native_price_usd) >= target_min_usd:
            tags.append("funded_on_deploy")
        if verified is False:
            tags.append("unverified_contract")
        if len(txs) >= high_tx_threshold:
            tags.append("high_tx_count")
        if (
            not known_public_reason
            and total_usd >= target_min_usd
            and (verified is False or verified is None or "unfamiliar_contract" in tags)
        ):
            tags.extend(["hidden_high_value_contract", "audit_hidden_contract"])
        if (
            not known_public_reason
            and total_usd >= target_min_usd
            and len(txs) >= high_tx_threshold
            and (verified is False or verified is None or "unfamiliar_contract" in tags)
        ):
            tags.extend(["probable_bot_contract", "high_balance_bot_candidate"])
        if _contains_any(text, BOT_KEYWORDS):
            tags.extend(["bot_contract", "verified_bot_contract"])
        if _contains_any(text, DEX_KEYWORDS):
            tags.append("dex_path_executor")
        if "flashloan" in text or "flash loan" in text:
            tags.append("flashloan_user")
        if _contains_any(text, REWARD_KEYWORDS):
            tags.extend(["active_reward_pool", "reward_pool"])
            if total_usd >= target_min_usd and ("claim" in text or "claimable" in text):
                tags.append("large_claimable_rewards")
        if _contains_any(text, VAULT_KEYWORDS):
            tags.append("vault_exchange_rate")
        if any(funder.is_eoa and _wei_usd(funder.value_wei, self.native_price_usd) >= target_min_usd for funder in incoming_funders):
            tags.append("fresh_contract_funded_by_large_eoa")
        if _has_immediate_balance_spike(total_usd, previous_value_usd, self.config, self.source_config):
            tags.extend(["immediate_balance_spike", "balance_spike"])
        if cluster_match.get("deployer_cluster_id"):
            tags.extend(["prior_project_closed", "same_deployer_closed_project", "suspected_rug_redeploy"])
        if cluster_match.get("funder_cluster_id"):
            tags.extend(["prior_project_closed", "funding_from_closed_project", "suspected_rug_redeploy"])
        return sorted(set(tags))

    def _entity_type(self, tags: list[str], verified: bool | None) -> str:
        tag_set = set(tags)
        if "known_public_protocol" in tag_set:
            return "known_protocol"
        if "bot_contract" in tag_set or "probable_bot_contract" in tag_set or "dex_path_executor" in tag_set and "high_tx_count" in tag_set:
            return "bot_contract"
        if verified is False and ("high_native_balance" in tag_set or "high_token_balance" in tag_set or "high_total_balance" in tag_set):
            return "unverified_contract"
        return "unknown_protocol"

    def _known_public_protocol_reason(self, address: str, code: str = "") -> str:
        address_lc = address.lower()
        known_entry = _known_public_protocol_entry(self.config, self.chain, address_lc)
        if known_entry:
            protocol = str(known_entry.get("protocol", "known")).strip() or "known"
            component = str(known_entry.get("component", "contract")).strip() or "contract"
            return f"known_public_protocol_address:{protocol}:{component}:{address_lc}"
        bytecode_entry = _known_public_protocol_bytecode_entry(self.config, self.chain, code)
        if bytecode_entry:
            protocol = str(bytecode_entry.get("protocol", "known")).strip() or "known"
            component = str(bytecode_entry.get("component", "bytecode")).strip() or "bytecode"
            runtime_hash = _runtime_bytecode_hash(code)
            return f"known_public_protocol_bytecode:{protocol}:{component}:{runtime_hash}"
        if address_lc in _legacy_known_public_protocol_addresses(self.config, self.chain):
            return f"known_public_protocol_address:{address_lc}"
        return ""

    def _popular_protocol_hint(self, contract_name: str, source_text: str) -> str:
        name_text = contract_name.lower()
        for keyword in _known_public_protocol_keywords(self.config):
            if keyword and keyword in name_text:
                return f"popular_protocol_name_hint:{keyword}"

        lowered_source = source_text.lower()
        for marker in _known_public_protocol_source_markers(self.config):
            if marker and marker in lowered_source:
                return f"popular_protocol_source_marker_hint:{marker}"
        return ""

    def _eth_get_balance(self, address: str) -> int:
        return int(str(self._rpc("eth_getBalance", [address, "latest"])), 16)

    def _eth_get_code(self, address: str) -> str:
        return str(self._rpc("eth_getCode", [address, "latest"]) or "0x")

    def _incoming_funders(self, txs: list[dict[str, Any]], address: str) -> list[Funding]:
        funders: dict[str, int] = {}
        target = address.lower()
        for tx in txs:
            if str(tx.get("to") or "").lower() != target:
                continue
            value = str(tx.get("value") or "0")
            try:
                value_wei = int(value)
            except ValueError:
                value_wei = 0
            if value_wei <= 0:
                continue
            funder = str(tx.get("from") or "").lower()
            if funder:
                funders[funder] = funders.get(funder, 0) + value_wei
        return [
            Funding(address=funder, value_wei=value_wei, is_eoa=self._eth_get_code(funder) in {"0x", "0x0", ""})
            for funder, value_wei in funders.items()
        ]

    def _source_code(self, address: str) -> dict[str, Any]:
        url_template = str(self.explorer.get("source_code_url", ""))
        if not url_template:
            return {}
        payload = self._explorer_json(url_template, address)
        return _first_result(payload)

    def _txlist(self, address: str) -> list[dict[str, Any]]:
        url_template = str(self.explorer.get("txlist_url", ""))
        if not url_template:
            return []
        payload = self._explorer_json(url_template, address)
        result = payload.get("result") if isinstance(payload, dict) else []
        return result if isinstance(result, list) else []

    def _tokentx(self, address: str) -> list[dict[str, Any]]:
        url_template = str(self.explorer.get("tokentx_url", ""))
        if not url_template:
            return []
        payload = self._explorer_json(url_template, address)
        result = payload.get("result") if isinstance(payload, dict) else []
        return result if isinstance(result, list) else []

    def _erc20_holdings(self, address: str, token_txs: list[dict[str, Any]], seed_tokens: Iterable[str] = ()) -> list[TokenHolding]:
        max_tokens_raw = self.source_config.get("max_token_contracts", 20)
        max_tokens = int(max_tokens_raw if max_tokens_raw is not None else 20)
        token_meta: dict[str, dict[str, Any]] = {}
        for token in seed_tokens:
            token_address = str(token).lower()
            if token_address:
                token_meta[token_address] = {"contractAddress": token_address}
        for tx in token_txs:
            token = str(tx.get("contractAddress") or "").lower()
            if not token or token in token_meta:
                continue
            token_meta[token] = tx
            if len(token_meta) >= max_tokens:
                break

        holdings: list[TokenHolding] = []
        for token, meta in token_meta.items():
            balance_raw = self._erc20_balance_of(token, address)
            if balance_raw <= 0:
                continue
            known = _known_token(self.chain, token, self.native_price_usd)
            if meta.get("tokenDecimal") is not None:
                decimals = _int_from_any(meta.get("tokenDecimal"), default=18)
            elif known:
                decimals = _int_from_any(known.get("decimals"), default=18)
            else:
                decimals = self._erc20_decimals(token)
            if meta.get("tokenSymbol") or meta.get("symbol"):
                symbol = str(meta.get("tokenSymbol") or meta.get("symbol"))
            elif known:
                symbol = str(known.get("symbol") or token)
            else:
                symbol = self._erc20_symbol(token) or token
            balance = balance_raw / 10**decimals if decimals >= 0 else float(balance_raw)
            known_price = _float_from_any(known.get("price_usd", 0) if known else 0)
            if known_price > 0:
                price_usd = known_price
                price_source = "known_asset"
                asset_kind = str(known.get("kind") or "")
            else:
                price_usd = self._token_price_usd(token)
                price_source = "dexscreener" if price_usd else ""
                asset_kind = str(known.get("kind") or "") if known else ""
            value_usd = balance * price_usd if price_usd else 0.0
            holdings.append(
                TokenHolding(
                    token_address=token,
                    symbol=symbol,
                    decimals=decimals,
                    balance_raw=balance_raw,
                    balance=balance,
                    price_usd=price_usd,
                    price_source=price_source,
                    asset_kind=asset_kind,
                    value_usd=value_usd,
                )
            )
        return holdings

    def _erc20_balance_of(self, token: str, holder: str) -> int:
        holder_word = holder.lower().removeprefix("0x").rjust(64, "0")
        data = "0x70a08231" + holder_word
        try:
            result = self._rpc("eth_call", [{"to": token, "data": data}, "latest"])
        except (RuntimeError, TimeoutError, OSError):
            return 0
        return _hex_to_int(result)

    def _erc20_decimals(self, token: str) -> int:
        try:
            result = self._rpc("eth_call", [{"to": token, "data": "0x313ce567"}, "latest"])
        except (RuntimeError, TimeoutError, OSError):
            return 18
        value = _hex_to_int(result)
        return value if 0 <= value <= 255 else 18

    def _erc20_symbol(self, token: str) -> str:
        try:
            result = str(self._rpc("eth_call", [{"to": token, "data": "0x95d89b41"}, "latest"]) or "")
        except (RuntimeError, TimeoutError, OSError):
            return ""
        return _decode_abi_string(result)

    def _token_price_usd(self, token: str) -> float:
        url = f"https://api.dexscreener.com/token-pairs/v1/{self.chain}/{token}"
        try:
            payload = self.fetch_json(url)
        except (RuntimeError, TimeoutError, OSError):
            return 0.0
        pairs = payload if isinstance(payload, list) else []
        prices = []
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            try:
                price = float(pair.get("priceUsd") or 0)
            except (TypeError, ValueError):
                price = 0.0
            if price > 0:
                prices.append(price)
        return max(prices) if prices else 0.0

    def _explorer_json(self, url_template: str, address: str) -> dict[str, Any]:
        if not self.api_keys:
            return {}
        for api_key in self.api_keys:
            url = url_template.format(address=address, chain=self.chain, api_key=api_key)
            try:
                payload = self.fetch_json(url)
            except (RuntimeError, TimeoutError, OSError):
                continue
            if isinstance(payload, dict):
                return payload
        return {}

    def _rpc(self, method: str, params: list[Any]) -> Any:
        last_error: Exception | None = None
        for url in self.rpc_urls:
            try:
                return self.rpc_call(url, method, params)
            except (RuntimeError, TimeoutError, OSError) as exc:
                last_error = exc
                continue
        if last_error is not None:
            raise last_error
        raise RuntimeError("no Ethereum RPC URL configured")

    def _rpc_call(self, url: str, method: str, params: list[Any]) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "protocol-sentinel/0.1 defensive-research",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"rpc failed for {method}: {exc}") from exc
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"rpc failed for {method}: {result['error']}")
        return result.get("result") if isinstance(result, dict) else None

    def _fetch_json(self, url: str) -> Any:
        request = urllib.request.Request(url, headers={"User-Agent": "protocol-sentinel/0.1 defensive-research", "Accept": "application/json"})
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


def _rotation_values(*values: Any) -> list[str]:
    output: list[str] = []
    for value in values:
        if isinstance(value, list):
            output.extend(str(item).strip() for item in value if str(item).strip())
            continue
        text = str(value or "").strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            output.extend(str(item).strip() for item in parsed if str(item).strip())
        else:
            output.extend(part.strip() for part in text.replace("\n", ",").replace(" ", ",").split(",") if part.strip())
    deduped: list[str] = []
    seen: set[str] = set()
    for value in output:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _dedupe_deployments(deployments: list[Deployment]) -> list[Deployment]:
    deduped: list[Deployment] = []
    seen: set[str] = set()
    for deployment in deployments:
        key = deployment.address.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(deployment)
    return deduped


def _float_first(*values: Any) -> float:
    for value in values:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    return 0.0


def _float_from_any(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _hex_to_int(value: Any) -> int:
    if value in (None, "", "0x"):
        return 0
    text = str(value)
    return int(text, 16) if text.startswith("0x") else int(text)


def _topic_address(topic: str) -> str:
    text = topic.lower().removeprefix("0x")
    if len(text) < 40:
        return ""
    return "0x" + text[-40:]


def _decode_abi_string(value: str) -> str:
    text = value.removeprefix("0x")
    if not text:
        return ""
    try:
        if len(text) == 64:
            return bytes.fromhex(text).rstrip(b"\x00").decode("utf-8", errors="ignore").strip()
        if len(text) >= 128:
            length = int(text[64:128], 16)
            data = text[128:128 + length * 2]
            return bytes.fromhex(data).decode("utf-8", errors="ignore").strip()
    except ValueError:
        return ""
    return ""


def _int_from_any(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _first_result(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    result = payload.get("result")
    if isinstance(result, list) and result and isinstance(result[0], dict):
        return result[0]
    if isinstance(result, dict):
        return result
    return {}


def _contract_name(source: dict[str, Any]) -> str:
    return str(source.get("ContractName") or source.get("contractName") or source.get("name") or "").strip()


def _source_text(source: dict[str, Any]) -> str:
    parts = [
        source.get("ContractName", ""),
        source.get("SourceCode", ""),
        source.get("ABI", ""),
    ]
    return " ".join(str(part) for part in parts if part)


def _is_verified(source: dict[str, Any]) -> bool | None:
    if not source:
        return None
    if "SourceCode" in source:
        return bool(str(source.get("SourceCode") or "").strip())
    return None


def _cluster_match(deployer: str, funders: Iterable[str], config: dict[str, Any]) -> dict[str, str]:
    deployer = deployer.lower()
    funder_set = {funder.lower() for funder in funders}
    match = {"cluster_id": "", "deployer_cluster_id": "", "funder_cluster_id": ""}
    for cluster in config.get("closed_project_clusters", []):
        cluster_id = str(cluster.get("id", ""))
        addresses = {
            *(str(address).lower() for address in cluster.get("deployer_addresses", [])),
            *(str(address).lower() for address in cluster.get("funder_addresses", [])),
            *(str(address).lower() for address in cluster.get("treasury_addresses", [])),
            *(str(address).lower() for address in cluster.get("project_addresses", [])),
        }
        if deployer in addresses:
            match["cluster_id"] = match["cluster_id"] or cluster_id
            match["deployer_cluster_id"] = cluster_id
        if funder_set.intersection(addresses):
            match["cluster_id"] = match["cluster_id"] or cluster_id
            match["funder_cluster_id"] = cluster_id
    return match


def _wei_usd(value_wei: int, native_price_usd: float) -> float:
    if value_wei <= 0 or native_price_usd <= 0:
        return 0.0
    return value_wei / 10**18 * native_price_usd


def _known_token(chain: str, token: str, native_price_usd: float) -> dict[str, Any]:
    metadata = KNOWN_CHAIN_TOKENS.get(chain, {}).get(token.lower())
    if not metadata:
        return {}
    resolved = dict(metadata)
    if resolved.get("price_usd") == "native":
        resolved["price_usd"] = native_price_usd
    return resolved


def _known_public_protocol_entry(config: dict[str, Any], chain: str, address: str) -> dict[str, Any]:
    address_lc = address.lower().strip()
    if not address_lc:
        return {}
    for entry in _known_public_protocol_entries(config):
        if str(entry.get("chain", "")).lower().strip() == chain.lower() and str(entry.get("address", "")).lower().strip() == address_lc:
            return entry
    return {}


def _known_public_protocol_bytecode_entry(config: dict[str, Any], chain: str, code: str) -> dict[str, Any]:
    runtime_hash = _runtime_bytecode_hash(code)
    if not runtime_hash:
        return {}
    for entry in _known_public_protocol_entries(config):
        if str(entry.get("chain", "")).lower().strip() != chain.lower():
            continue
        entry_hash = str(entry.get("runtime_bytecode_hash", "")).lower().strip()
        if entry_hash and entry_hash == runtime_hash:
            return entry
    return {}


def _runtime_bytecode_hash(code: str) -> str:
    normalized = str(code or "").lower().strip()
    if normalized in {"", "0x"}:
        return ""
    normalized = normalized.removeprefix("0x")
    try:
        raw = bytes.fromhex(normalized)
    except ValueError:
        return ""
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _known_public_protocol_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    registry_path = str(config.get("known_public_protocol_registry", "")).strip()
    entries: list[dict[str, Any]] = []
    if registry_path:
        try:
            payload = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            payload = {}
        raw_entries = payload.get("entries", []) if isinstance(payload, dict) else []
        if isinstance(raw_entries, list):
            entries.extend(entry for entry in raw_entries if isinstance(entry, dict))
    inline_entries = config.get("known_public_protocol_entries", [])
    if isinstance(inline_entries, list):
        entries.extend(entry for entry in inline_entries if isinstance(entry, dict))
    return entries


def _legacy_known_public_protocol_addresses(config: dict[str, Any], chain: str) -> set[str]:
    raw = config.get("known_public_protocol_addresses", {})
    values: list[Any]
    if isinstance(raw, dict):
        values = list(raw.get(chain, [])) + list(raw.get(chain.lower(), []))
    elif isinstance(raw, list):
        values = raw
    else:
        values = []
    return {str(value).lower().strip() for value in values if str(value).strip()}


def _known_public_protocol_keywords(config: dict[str, Any]) -> tuple[str, ...]:
    values = config.get("known_public_protocol_keywords", DEFAULT_KNOWN_PUBLIC_PROTOCOL_KEYWORDS)
    if not isinstance(values, list):
        return DEFAULT_KNOWN_PUBLIC_PROTOCOL_KEYWORDS
    return tuple(str(value).lower().strip() for value in values if str(value).strip())


def _known_public_protocol_source_markers(config: dict[str, Any]) -> tuple[str, ...]:
    values = config.get("known_public_protocol_source_markers", DEFAULT_KNOWN_PUBLIC_PROTOCOL_SOURCE_MARKERS)
    if not isinstance(values, list):
        return DEFAULT_KNOWN_PUBLIC_PROTOCOL_SOURCE_MARKERS
    return tuple(str(value).lower().strip() for value in values if str(value).strip())


def _is_unfamiliar_contract(address: str, contract_name: str, source_text: str, verified: bool | None) -> bool:
    if verified is False or verified is None:
        return True
    normalized_name = contract_name.lower().strip()
    if not normalized_name or normalized_name == address.lower():
        return True
    return not source_text.strip()


def _has_immediate_balance_spike(
    total_usd: float,
    previous_value_usd: float,
    config: dict[str, Any],
    source_config: dict[str, Any],
) -> bool:
    min_spike_usd = float(source_config.get("balance_spike_min_usd", config.get("balance_spike_min_usd", 200_000)) or 200_000)
    multiplier = float(source_config.get("balance_spike_multiplier", config.get("balance_spike_multiplier", 5)) or 5)
    if total_usd < min_spike_usd:
        return False
    if previous_value_usd <= 0:
        return True
    return total_usd >= previous_value_usd * multiplier and total_usd - previous_value_usd >= min_spike_usd


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)


def _category(tags: list[str], source_text: str, contract_name: str) -> str:
    text = f"{contract_name} {source_text}".lower()
    if "bot_contract" in tags:
        return "mev bot executor"
    if "reward_pool" in tags:
        return "reward staking pool"
    if "unverified_contract" in tags:
        return "unverified funded contract"
    if _contains_any(text, VAULT_KEYWORDS):
        return "vault"
    return "fresh contract"
