import json
import tempfile
import unittest
from pathlib import Path

from sentinel.chain_scanner import load_bsc_chain_candidates, load_ethereum_chain_candidates


class EthereumChainScannerTest(unittest.TestCase):
    def test_scanner_classifies_fresh_contract_surfaces(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        config["sources"]["ethereum_chain_scanner"] = {
            "enabled": True,
            "recent_blocks": 1,
            "max_contracts": 5,
            "max_token_contracts": 5,
            "max_transfer_recipients": 5,
            "transfer_log_chunk_size": 1,
            "target_min_value_usd": 200_000,
            "high_tx_count": 2,
            "native_price_usd": 3000,
            "rpc_urls": ["https://rpc.example"],
            "api_keys": ["explorer-key"],
        }

        candidates = load_ethereum_chain_candidates(
            config,
            limit=7,
            rpc_call=_fake_rpc,
            fetch_json=_fake_explorer,
        )

        by_address = {candidate.address: candidate for candidate in candidates}
        unverified = by_address["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
        bot = by_address["0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"]
        reward = by_address["0xcccccccccccccccccccccccccccccccccccccccc"]
        redeploy = by_address["0xdddddddddddddddddddddddddddddddddddddddd"]
        token_heavy = by_address["0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"]
        log_funded = by_address["0x1212121212121212121212121212121212121212"]
        stablecoin_funded = by_address["0x3434343434343434343434343434343434343434"]

        self.assertEqual(unverified.entity_type, "unverified_contract")
        self.assertFalse(unverified.verified_source)
        self.assertIn("unverified_contract", unverified.tags)
        self.assertIn("high_native_balance", unverified.tags)
        self.assertEqual(unverified.tvl_usd, 300_000)

        self.assertEqual(bot.entity_type, "bot_contract")
        self.assertIn("high_tx_count", bot.tags)
        self.assertIn("dex_path_executor", bot.tags)
        self.assertIn("flashloan_user", bot.tags)

        self.assertIn("reward_pool", reward.tags)
        self.assertIn("large_claimable_rewards", reward.tags)

        self.assertEqual(redeploy.funding_cluster_id, "closed-yield-cluster-001")
        self.assertIn("same_deployer_closed_project", redeploy.tags)
        self.assertIn("funding_from_closed_project", redeploy.tags)
        self.assertIn("suspected_rug_redeploy", redeploy.tags)
        self.assertIn("fresh_contract_funded_by_large_eoa", redeploy.tags)

        self.assertEqual(token_heavy.tvl_usd, 250_000)
        self.assertIn("high_token_balance", token_heavy.tags)
        self.assertIn("fresh_contract_large_token_balance", token_heavy.tags)
        self.assertNotIn("high_native_balance", token_heavy.tags)
        self.assertEqual(token_heavy.raw["token_balances"][0]["symbol"], "RISK")

        self.assertEqual(log_funded.tvl_usd, 240_000)
        self.assertIn("token_funded_contract", log_funded.tags)
        self.assertIn("high_token_balance", log_funded.tags)
        self.assertNotIn("fresh_deployment", log_funded.tags)
        self.assertEqual(log_funded.raw["token_balances"][0]["symbol"], "LOG")

        self.assertEqual(stablecoin_funded.tvl_usd, 250_000)
        self.assertIn("token_funded_contract", stablecoin_funded.tags)
        self.assertIn("known_asset_balance", stablecoin_funded.tags)
        self.assertIn("stablecoin_balance", stablecoin_funded.tags)
        self.assertIn("high_token_balance", stablecoin_funded.tags)
        self.assertEqual(stablecoin_funded.raw["token_balances"][0]["symbol"], "USDC")
        self.assertEqual(stablecoin_funded.raw["token_balances"][0]["price_source"], "known_asset")
        self.assertEqual(stablecoin_funded.raw["token_balances"][0]["asset_kind"], "stablecoin")

    def test_scanner_persists_cursor_and_rechecks_remembered_contracts(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "ethereum_chain_scanner.json"
            config["sources"]["ethereum_chain_scanner"] = {
                "enabled": True,
                "recent_blocks": 1,
                "first_run_blocks": 3,
                "max_contracts": 1,
                "max_transfer_recipients": 0,
                "remembered_contracts_per_run": 1,
                "target_min_value_usd": 200_000,
                "native_price_usd": 3000,
                "rpc_urls": ["https://rpc.example"],
                "api_keys": ["explorer-key"],
                "state_path": str(state_path),
            }

            first = load_ethereum_chain_candidates(config, limit=1, rpc_call=_stateful_rpc, fetch_json=_fake_explorer)
            self.assertEqual([candidate.address for candidate in first], ["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])
            state = json.loads(state_path.read_text())
            self.assertEqual(state["last_scanned_block"], 100)
            self.assertIn("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", state["seen_contracts"])

            second = load_ethereum_chain_candidates(config, limit=1, rpc_call=_stateful_rpc, fetch_json=_fake_explorer)
            addresses = [candidate.address for candidate in second]
            self.assertIn("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", addresses)
            state = json.loads(state_path.read_text())
            self.assertEqual(state["last_scanned_block"], 100)
            self.assertGreaterEqual(
                state["seen_contracts"]["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]["max_value_usd"],
                300_000,
            )

    def test_bsc_scanner_finds_known_stablecoin_contract_without_explorer_key(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            config["sources"]["bsc_chain_scanner"] = {
                "enabled": True,
                "recent_blocks": 1,
                "max_contracts": 1,
                "max_token_contracts": 5,
                "max_transfer_recipients": 2,
                "transfer_log_chunk_size": 1,
                "target_min_value_usd": 200_000,
                "native_price_usd": 600,
                "rpc_urls": ["https://bsc-rpc.example"],
                "state_path": str(Path(tmp) / "bsc_chain_scanner.json"),
            }

            candidates = load_bsc_chain_candidates(config, limit=2, rpc_call=_fake_bsc_rpc, fetch_json=_unexpected_fetch)

        by_address = {candidate.address: candidate for candidate in candidates}
        stablecoin_funded = by_address["0x5656565656565656565656565656565656565656"]

        self.assertEqual(stablecoin_funded.source, "bsc_chain_scanner")
        self.assertEqual(stablecoin_funded.chain, "bsc")
        self.assertEqual(stablecoin_funded.url, "https://bscscan.com/address/0x5656565656565656565656565656565656565656")
        self.assertEqual(stablecoin_funded.tvl_usd, 250_000)
        self.assertIn("token_funded_contract", stablecoin_funded.tags)
        self.assertIn("known_asset_balance", stablecoin_funded.tags)
        self.assertIn("stablecoin_balance", stablecoin_funded.tags)
        self.assertEqual(stablecoin_funded.raw["token_balances"][0]["symbol"], "USDT")
        self.assertEqual(stablecoin_funded.raw["token_balances"][0]["price_source"], "known_asset")


def _fake_rpc(_url, method, params):
    if method == "eth_blockNumber":
        return "0x64"
    if method == "eth_getBlockByNumber":
        return {
            "timestamp": "0x67748580",
            "transactions": [
                {"hash": "0x01", "from": "0x1111111111111111111111111111111111111111", "to": None, "value": "0xde0b6b3a7640000"},
                {"hash": "0x02", "from": "0x2222222222222222222222222222222222222222", "to": None, "value": "0x0"},
                {"hash": "0x03", "from": "0x3333333333333333333333333333333333333333", "to": None, "value": "0x0"},
                {"hash": "0x04", "from": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "to": None, "value": "0x0"},
                {"hash": "0x05", "from": "0x5555555555555555555555555555555555555555", "to": None, "value": "0x0"},
            ],
        }
    if method == "eth_getTransactionReceipt":
        receipts = {
            "0x01": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "0x02": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "0x03": "0xcccccccccccccccccccccccccccccccccccccccc",
            "0x04": "0xdddddddddddddddddddddddddddddddddddddddd",
            "0x05": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        }
        return {"contractAddress": receipts[params[0]]}
    if method == "eth_getBalance":
        balances = {
            "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa": 100 * 10**18,
            "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb": 12 * 10**18,
            "0xcccccccccccccccccccccccccccccccccccccccc": 80 * 10**18,
            "0xdddddddddddddddddddddddddddddddddddddddd": 75 * 10**18,
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": 0,
            "0x1212121212121212121212121212121212121212": 0,
            "0x3434343434343434343434343434343434343434": 0,
        }
        return hex(balances[params[0]])
    if method == "eth_getCode":
        codes = {
            "0x4444444444444444444444444444444444444444": "0x",
            "0x5555555555555555555555555555555555555555": "0x6000",
            "0xcccccccccccccccccccccccccccccccccccccccc": "0x",
            "0x1212121212121212121212121212121212121212": "0x6000",
            "0x3434343434343434343434343434343434343434": "0x6000",
        }
        return codes.get(params[0], "0x")
    if method == "eth_call":
        token = params[0]["to"]
        data = params[0]["data"]
        if token == "0x9999999999999999999999999999999999999999":
            if data == "0x313ce567":
                return hex(18)
            if data == "0x95d89b41":
                return _abi_string("RISK")
            return hex(1000 * 10**18)
        if token == "0x8888888888888888888888888888888888888888":
            if data == "0x313ce567":
                return hex(18)
            if data == "0x95d89b41":
                return _abi_string("LOG")
            return hex(2000 * 10**18)
        if token == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":
            return hex(250_000 * 10**6)
        return "0x0"
    if method == "eth_getLogs":
        return [
            {
                "address": "0x8888888888888888888888888888888888888888",
                "topics": [
                    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                    _topic("0xffffffffffffffffffffffffffffffffffffffff"),
                    _topic("0x1212121212121212121212121212121212121212"),
                ],
                "transactionHash": "0xtransfer01",
                "blockNumber": "0x64",
            },
            {
                "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "topics": [
                    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                    _topic("0xffffffffffffffffffffffffffffffffffffffff"),
                    _topic("0x3434343434343434343434343434343434343434"),
                ],
                "transactionHash": "0xtransfer02",
                "blockNumber": "0x64",
            }
        ]
    raise AssertionError(f"unexpected rpc method {method}")


def _stateful_rpc(_url, method, params):
    if method == "eth_blockNumber":
        return "0x64"
    if method == "eth_getBlockByNumber":
        block_number = int(params[0], 16)
        if block_number == 100:
            return {
                "timestamp": "0x67748580",
                "transactions": [
                    {"hash": "0x01", "from": "0x1111111111111111111111111111111111111111", "to": None, "value": "0x0"}
                ],
            }
        return {"timestamp": "0x67748580", "transactions": []}
    return _fake_rpc(_url, method, params)


def _fake_bsc_rpc(_url, method, params):
    if method == "eth_blockNumber":
        return "0xc8"
    if method == "eth_getBlockByNumber":
        return {"timestamp": "0x67748580", "transactions": []}
    if method == "eth_getLogs":
        return [
            {
                "address": "0x55d398326f99059ff775485246999027b3197955",
                "topics": [
                    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                    _topic("0xffffffffffffffffffffffffffffffffffffffff"),
                    _topic("0x5656565656565656565656565656565656565656"),
                ],
                "transactionHash": "0xbsc-transfer01",
                "blockNumber": "0xc8",
            }
        ]
    if method == "eth_getCode":
        if params[0] == "0x5656565656565656565656565656565656565656":
            return "0x6000"
        return "0x"
    if method == "eth_getBalance":
        return "0x0"
    if method == "eth_call":
        token = params[0]["to"]
        if token == "0x55d398326f99059ff775485246999027b3197955":
            return hex(250_000 * 10**18)
        return "0x0"
    raise AssertionError(f"unexpected bsc rpc method {method}")


def _unexpected_fetch(url):
    raise AssertionError(f"unexpected fetch {url}")


def _fake_explorer(url):
    if "getsourcecode" in url:
        if "aaaaaaaa" in url:
            return {"result": [{"ContractName": "", "SourceCode": ""}]}
        if "bbbbbbbb" in url:
            return {
                "result": [
                    {
                        "ContractName": "FlashloanArbitrageExecutor",
                        "SourceCode": "contract FlashloanArbitrageExecutor { function swap() external {} }",
                    }
                ]
            }
        if "cccccccc" in url:
            return {
                "result": [
                    {
                        "ContractName": "ClaimableRewardPool",
                        "SourceCode": "contract ClaimableRewardPool { function claim() external {} }",
                    }
                ]
            }
        if "eeeeeeee" in url:
            return {"result": [{"ContractName": "TokenHeavyVault", "SourceCode": "contract TokenHeavyVault {}"}]}
        return {"result": [{"ContractName": "RedeployedVault", "SourceCode": "contract RedeployedVault {}"}]}
    if "txlist" in url:
        if "bbbbbbbb" in url:
            return {
                "result": [
                    {"from": "0x4444444444444444444444444444444444444444", "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "value": "1"},
                    {"from": "0x5555555555555555555555555555555555555555", "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "value": "2"},
                ]
            }
        if "dddddddd" in url:
            return {
                "result": [
                    {"from": "0xcccccccccccccccccccccccccccccccccccccccc", "to": "0xdddddddddddddddddddddddddddddddddddddddd", "value": "70000000000000000000"}
                ]
            }
        return {"result": []}
    if "tokentx" in url:
        if "eeeeeeee" in url:
            return {
                "result": [
                    {
                        "contractAddress": "0x9999999999999999999999999999999999999999",
                        "tokenSymbol": "RISK",
                        "tokenDecimal": "18",
                        "from": "0xffffffffffffffffffffffffffffffffffffffff",
                        "to": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    }
                ]
            }
        return {"result": []}
    if "token-pairs/v1/ethereum/0x9999999999999999999999999999999999999999" in url:
        return [{"priceUsd": "250"}]
    if "token-pairs/v1/ethereum/0x8888888888888888888888888888888888888888" in url:
        return [{"priceUsd": "120"}]
    return {"result": []}


def _topic(address: str) -> str:
    return "0x" + address.removeprefix("0x").rjust(64, "0")


def _abi_string(value: str) -> str:
    raw = value.encode().hex()
    padded_len = (len(raw) + 63) // 64 * 64
    return "0x" + "20".rjust(64, "0") + hex(len(value))[2:].rjust(64, "0") + raw.ljust(padded_len, "0")


if __name__ == "__main__":
    unittest.main()
