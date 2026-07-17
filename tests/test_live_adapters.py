import json
import os
import tempfile
import unittest
from pathlib import Path

from sentinel.live_adapters import LiveTarget, _chain_explorer_config, build_explorer_snapshot, load_live_targets
from sentinel.sources import load_explorer_snapshot_from_snapshot


class LiveAdapterTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(Path("config/sentinel.json").read_text())

    def test_load_live_targets_reads_target_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = _write_fixture_targets(tmp)
            targets = load_live_targets(str(target_path))

        self.assertEqual(len(targets), 4)
        self.assertEqual(targets[0], LiveTarget(chain="bsc", address="0x5555555555555555555555555555555555555555", label="Unverified Funded Treasury"))

    def test_build_snapshot_uses_balance_and_explorer_fetchers(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = _write_fixture_targets(tmp)
            targets = load_live_targets(str(target_path))
        snapshot = build_explorer_snapshot(
            targets,
            self.config,
            fetch_json=_fake_explorer_fetch_json,
            fetch_balance=_fake_balance_fetch,
        )

        contracts = {item["address"]: item for item in snapshot["contracts"]}
        self.assertEqual(contracts["0x5555555555555555555555555555555555555555"]["native_balance_usd"], 210000)
        self.assertEqual(contracts["0x5555555555555555555555555555555555555555"]["verified_source"], False)
        self.assertIn("flashloan_user", contracts["0x4444444444444444444444444444444444444444"]["tags"])
        self.assertEqual(contracts["0x7777777777777777777777777777777777777777"]["funding_cluster_id"], "closed-yield-cluster-001")
        self.assertEqual(contracts["0x6666666666666666666666666666666666666666"]["price_change_24h_pct"], 420)

    def test_snapshot_round_trip_produces_expected_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = _write_fixture_targets(tmp)
            targets = load_live_targets(str(target_path))
        snapshot = build_explorer_snapshot(
            targets,
            self.config,
            fetch_json=_fake_explorer_fetch_json,
            fetch_balance=_fake_balance_fetch,
        )
        candidates = load_explorer_snapshot_from_snapshot(snapshot, self.config, 25)

        actions = {candidate.name: candidate.entity_type for candidate in candidates}
        self.assertEqual(actions["Unverified Funded Treasury"], "unverified_contract")
        self.assertEqual(actions["Unknown Spike Vault"], "unknown_protocol")
        self.assertEqual(actions["New Yield Migrator"], "unknown_protocol")
        self.assertEqual(actions["DexPathExecutor Bot"], "bot_contract")

    def test_snapshot_round_trip_preserves_nested_target_value_metadata(self):
        targets = [
            LiveTarget(
                chain="bsc",
                address="0x8888888888888888888888888888888888888888",
                label="Nested Metadata Vault",
                metadata={
                    "metadata": {
                        "entity_type": "unknown_protocol",
                        "tvl_usd": 75_000,
                        "next_action": "recon_bravo_then_corecritical",
                        "tags": ["unknown_protocol", "unfamiliar_contract", "hidden_high_value_contract"],
                    },
                    "tags": ["balance_spike"],
                },
            )
        ]
        snapshot = build_explorer_snapshot(
            targets,
            self.config,
            fetch_json=_fake_explorer_fetch_json,
            fetch_balance=lambda *_args: {"wei": 0, "usd": 0},
        )

        contract = snapshot["contracts"][0]
        self.assertEqual(contract["value_at_risk_usd"], 75_000)
        self.assertEqual(contract["tvl_usd"], 75_000)
        self.assertIn("balance_spike", contract["tags"])
        candidates = load_explorer_snapshot_from_snapshot(snapshot, self.config, 25)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].entity_type, "unknown_protocol")

    def test_default_explorer_urls_use_etherscan_v2_chainids(self):
        ethereum = _chain_explorer_config(self.config, "ethereum")
        bsc = _chain_explorer_config(self.config, "bsc")
        base = _chain_explorer_config(self.config, "base")

        self.assertIn("/v2/api?chainid=1&", ethereum["source_code_url"])
        self.assertIn("/v2/api?chainid=56&", bsc["source_code_url"])
        self.assertIn("/v2/api?chainid=8453&", base["source_code_url"])
        self.assertIn("module=account&action=txlist", bsc["txlist_url"])
        self.assertIn("module=account&action=tokentx", ethereum["tokentx_url"])

    def test_build_snapshot_preserves_target_when_explorer_fetch_fails(self):
        targets = [LiveTarget(chain="ethereum", address="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", label="Failing")]

        snapshot = build_explorer_snapshot(
            targets,
            self.config,
            fetch_json=lambda _url: (_ for _ in ()).throw(RuntimeError("temporary explorer timeout")),
            fetch_balance=lambda *_args: 0,
        )

        self.assertEqual(len(snapshot["contracts"]), 1)
        self.assertEqual(snapshot["contracts"][0]["verified_source"], None)
        self.assertEqual(snapshot["contracts"][0]["tx_count_24h"], 0)

    def test_build_snapshot_preserves_target_when_optional_tx_fetch_fails(self):
        targets = [LiveTarget(chain="ethereum", address="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", label="Partial")]

        def fetch_json(url: str):
            if "getsourcecode" in url:
                return {"result": [{"ContractName": "Partial", "SourceCode": "contract Partial {}", "ABI": "[]"}]}
            raise RuntimeError("temporary explorer timeout")

        snapshot = build_explorer_snapshot(targets, self.config, fetch_json=fetch_json, fetch_balance=lambda *_args: 0)

        self.assertEqual(len(snapshot["contracts"]), 1)
        self.assertEqual(snapshot["contracts"][0]["verified_source"], True)
        self.assertEqual(snapshot["contracts"][0]["tx_count_24h"], 0)

    def test_chain_explorer_config_accepts_environment_overrides(self):
        old_env = dict(os.environ)
        os.environ["SENTINEL_BSC_EXPLORER_API_KEY"] = "bsc-key"
        os.environ["SENTINEL_BSC_RPC_URL"] = "https://rpc.example"
        os.environ["SENTINEL_BSC_NATIVE_PRICE_USD"] = "612.5"
        try:
            explorer = _chain_explorer_config(self.config, "bsc")
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(explorer["api_key"], "bsc-key")
        self.assertEqual(explorer["rpc_url"], "https://rpc.example")
        self.assertEqual(explorer["native_price_usd"], "612.5")

    def test_chain_explorer_config_accepts_rotation_environment_overrides(self):
        old_env = dict(os.environ)
        os.environ["SENTINEL_BSC_EXPLORER_API_KEYS"] = "bsc-key-1,bsc-key-2\nbsc-key-3"
        os.environ["SENTINEL_BSC_EXPLORER_API_KEY"] = "bsc-key-4"
        os.environ["SENTINEL_BSC_RPC_URLS"] = '["https://rpc-1.example", "https://rpc-2.example"]'
        os.environ["SENTINEL_BSC_RPC_URL"] = "https://rpc-3.example"
        try:
            explorer = _chain_explorer_config(self.config, "bsc")
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(explorer["api_keys"], ["bsc-key-1", "bsc-key-2", "bsc-key-3", "bsc-key-4"])
        self.assertEqual(explorer["api_key"], "bsc-key-1")
        self.assertEqual(explorer["rpc_urls"], ["https://rpc-1.example", "https://rpc-2.example", "https://rpc-3.example"])
        self.assertEqual(explorer["rpc_url"], "https://rpc-1.example")

    def test_explorer_api_keys_rotate_on_rate_limit_and_fetch_failure(self):
        config = json.loads(json.dumps(self.config))
        config["live_explorers"]["bsc"]["api_keys"] = ["rate-limited-key", "broken-key", "good-key"]
        targets = [LiveTarget(chain="bsc", address="0x5555555555555555555555555555555555555555", label="Rotated")]
        attempted_keys = []

        def fetch_json(url: str):
            attempted_keys.append(url.rsplit("apikey=", 1)[1])
            if "rate-limited-key" in url:
                return {"status": "0", "message": "NOTOK", "result": "Max rate limit reached"}
            if "broken-key" in url:
                raise RuntimeError("network failure")
            return _fake_explorer_fetch_json(url)

        snapshot = build_explorer_snapshot(targets, config, fetch_json=fetch_json, fetch_balance=_fake_balance_fetch)

        self.assertEqual(snapshot["contracts"][0]["name"], "Rotated")
        self.assertIn("rate-limited-key", attempted_keys)
        self.assertIn("broken-key", attempted_keys)
        self.assertIn("good-key", attempted_keys)

    def test_rpc_urls_rotate_on_balance_fetch_failure(self):
        config = json.loads(json.dumps(self.config))
        config["live_explorers"]["bsc"]["rpc_urls"] = ["https://dead-rpc.example", "https://good-rpc.example"]
        targets = [LiveTarget(chain="bsc", address="0x5555555555555555555555555555555555555555", label="RPC Rotated")]
        attempted_rpc_urls = []

        def fetch_balance(chain: str, address: str, explorer: dict[str, object]):
            attempted_rpc_urls.append(str(explorer["rpc_url"]))
            if explorer["rpc_url"] == "https://dead-rpc.example":
                raise RuntimeError("rpc rate limit")
            return {"wei": 3 * 10**18, "usd": 123}

        snapshot = build_explorer_snapshot(targets, config, fetch_json=_fake_explorer_fetch_json, fetch_balance=fetch_balance)

        self.assertEqual(snapshot["contracts"][0]["native_balance_usd"], 123)
        self.assertEqual(attempted_rpc_urls, ["https://dead-rpc.example", "https://good-rpc.example"])


def _write_fixture_targets(directory: str) -> Path:
    path = Path(directory) / "live_targets.json"
    path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "chain": "bsc",
                        "address": "0x5555555555555555555555555555555555555555",
                        "label": "Unverified Funded Treasury",
                    },
                    {
                        "chain": "base",
                        "address": "0x6666666666666666666666666666666666666666",
                        "label": "Unknown Spike Vault",
                        "price_change_24h_pct": 420,
                    },
                    {
                        "chain": "bsc",
                        "address": "0x7777777777777777777777777777777777777777",
                        "label": "New Yield Migrator",
                    },
                    {
                        "chain": "bsc",
                        "address": "0x4444444444444444444444444444444444444444",
                        "label": "DexPathExecutor Bot",
                        "tags": ["flashloan_user"],
                    },
                ]
            }
        )
    )
    return path


def _fake_explorer_fetch_json(url: str):
    if "getsourcecode" in url:
        if "555555" in url:
            return {
                "result": [
                    {
                        "ContractName": "UnverifiedFundedTreasury",
                        "SourceCode": "",
                        "ABI": "",
                        "ContractType": "treasury",
                        "verified": False,
                    }
                ]
            }
        if "666666" in url:
            return {
                "result": [
                    {
                        "ContractName": "UnknownSpikeVault",
                        "SourceCode": "contract UnknownSpikeVault {}",
                        "ABI": "[]",
                        "ContractType": "vault",
                        "verified": True,
                    }
                ]
            }
        if "777777" in url:
            return {
                "result": [
                    {
                        "ContractName": "NewYieldMigrator",
                        "SourceCode": "",
                        "ABI": "",
                        "ContractType": "migrator",
                        "verified": False,
                        "deployer_address": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                        "funder_addresses": ["0xcccccccccccccccccccccccccccccccccccccccc"],
                        "treasury_addresses": ["0xdddddddddddddddddddddddddddddddddddddddd"],
                    }
                ]
            }
        if "888888" in url:
            return {
                "result": [
                    {
                        "ContractName": "NestedMetadataVault",
                        "SourceCode": "contract NestedMetadataVault {}",
                        "ABI": "[]",
                        "ContractType": "vault",
                        "verified": True,
                    }
                ]
            }
        return {
            "result": [
                {
                    "ContractName": "DexPathExecutorBot",
                    "SourceCode": "contract DexPathExecutorBot {}",
                    "ABI": "[]",
                    "ContractType": "executor",
                    "verified": True,
                }
            ]
        }
    if "txlist" in url:
        if "444444" in url:
            return {
                "result": [
                    {"methodId": "0x414bf389", "to": "PancakeSwapV2 Router"},
                    {"methodId": "0xfa461e33", "to": "PancakeSwapV3 Router"},
                    {"methodId": "0x12345678", "to": "ProfitSweep"},
                ]
            }
        if "666666" in url:
            return {
                "result": [
                    {"methodId": "0x9abcdef0", "to": "new-pool-router"},
                    {"methodId": "0x9abcdef0", "to": "new-pool-router"},
                ]
            }
        if "777777" in url:
            return {"result": [{"methodId": "0x9abcdef0", "to": "migrator"}]}
        return {"result": [{"methodId": "0x9abcdef0", "to": "treasury"}]}
    if "tokentx" in url:
        if "555555" in url:
            return {
                "result": [
                    {"tokenSymbol": "USDT", "usdValue": 455000},
                ]
            }
        if "666666" in url:
            return {
                "result": [
                    {"tokenSymbol": "BASE", "usdValue": 980000},
                ]
            }
        return {"result": []}
    return {"result": []}


def _fake_balance_fetch(chain: str, address: str, explorer: dict[str, object]) -> int:
    if address == "0x5555555555555555555555555555555555555555":
        return {"wei": 210000 * 10**18, "usd": 210000}
    if address == "0x6666666666666666666666666666666666666666":
        return {"wei": 0, "usd": 0}
    if address == "0x7777777777777777777777777777777777777777":
        return {"wei": 0, "usd": 0}
    return {"wei": 0, "usd": 0}


if __name__ == "__main__":
    unittest.main()
