import json
import unittest
from pathlib import Path

from sentinel.scoring import score_candidate
from sentinel.sources import candidate_from_dict


class ScoringTest(unittest.TestCase):
    def test_high_value_bridge_is_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "base:test",
                "name": "New Bridge Vault",
                "chain": "base",
                "category": "bridge",
                "tvl_usd": 2_000_000,
                "tags": ["latest_boost"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "recon_bravo_then_corecritical")

    def test_low_value_candidate_is_dropped(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:low",
                "name": "Tiny Pool",
                "chain": "bsc",
                "liquidity_usd": 1000,
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "drop_low_value")
        self.assertLess(scored.score, config["queue_threshold"])

    def test_mainstream_defillama_protocol_is_watch_not_recon(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "defillama_protocols",
                "external_id": "large-known",
                "name": "Large Known Lending",
                "chain": "ethereum",
                "category": "lending",
                "tvl_usd": 400_000_000,
                "tags": ["defillama"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch_mainstream")

    def test_known_public_protocol_is_quarantined_not_recon(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "known_protocol",
                "external_id": "bsc:0x238a358808379702088667322f80ac48bad5e6c4",
                "name": "Pancakeswap: Infinity Vault",
                "chain": "bsc",
                "category": "vault",
                "tvl_usd": 184_000_000,
                "verified_source": True,
                "tags": [
                    "known_public_protocol",
                    "popular_protocol",
                    "high_token_balance",
                    "stablecoin_balance",
                    "vault_exchange_rate",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch_known_protocol")
        self.assertLess(scored.score, config["queue_threshold"])
        self.assertIn("known_public_protocol_quarantine", scored.reasons)

    def test_popular_protocol_name_hint_is_quarantined(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:fake-uniswap",
                "name": "Uniswap Rewards Vault",
                "chain": "bsc",
                "category": "vault",
                "tvl_usd": 750_000,
                "verified_source": True,
                "tags": [
                    "unknown_protocol",
                    "popular_protocol_name_hint",
                    "possible_protocol_impersonation",
                    "hidden_high_value_contract",
                    "immediate_balance_spike",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch_known_protocol")
        self.assertLess(scored.score, config["queue_threshold"])

    def test_bot_contract_with_activity_is_trace_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "bot_contract",
                "external_id": "bsc:bot",
                "name": "Flashloan Arbitrage Executor",
                "chain": "bsc",
                "category": "mev bot",
                "tvl_usd": 320_000,
                "tags": ["verified_bot_contract", "flashloan_user", "dex_path_executor"],
                "raw": {
                    "behavior": "flashloan swap callback profit sweep"
                },
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "trace_bot_contract_then_target_protocols")

    def test_bot_contract_below_50k_is_watch_only(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "bot_contract",
                "external_id": "bsc:mid-bot",
                "name": "Flashloan Arbitrage Executor",
                "chain": "bsc",
                "category": "mev bot",
                "tvl_usd": 25_000,
                "tags": ["verified_bot_contract", "flashloan_user", "dex_path_executor"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch_bot_contract")
        self.assertLess(scored.score, config["queue_threshold"])

    def test_low_value_bot_contract_is_watch_only(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "bot_contract",
                "external_id": "bsc:low-bot",
                "name": "Tiny Executor Bot",
                "chain": "bsc",
                "category": "bot",
                "tvl_usd": 100,
                "tags": ["verified_bot_contract"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch_bot_contract")
        self.assertLess(scored.score, config["queue_threshold"])

    def test_unverified_contract_with_funds_is_reverse_engineering_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "unverified_contract",
                "external_id": "bsc:unverified",
                "name": "Unverified Funded Treasury",
                "chain": "bsc",
                "category": "unverified treasury",
                "tvl_usd": 640_000,
                "verified_source": False,
                "tags": ["unknown_protocol"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "reverse_engineer_unverified_funded_contract")

    def test_unknown_protocol_price_spike_is_recon_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "unknown_protocol",
                "external_id": "base:spike",
                "name": "Unknown Spike Vault",
                "chain": "base",
                "category": "vault",
                "liquidity_usd": 220_000,
                "price_change_24h_pct": 420,
                "tags": ["unknown_protocol", "latest_profile"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "price_spike_recon_then_source_check")

    def test_chain_scanner_unknown_without_unfamiliar_or_spike_signal_is_watch(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:verified-known-shape",
                "name": "Verified Treasury",
                "chain": "bsc",
                "category": "treasury",
                "tvl_usd": 5_000_000,
                "verified_source": True,
                "tags": ["unknown_protocol", "high_total_balance", "stablecoin_balance"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "watch")

    def test_chain_scanner_unverified_below_value_floor_is_watch(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unverified_contract",
                "external_id": "bsc:small-unverified",
                "name": "Unverified Funded Contract",
                "chain": "bsc",
                "category": "unverified treasury",
                "tvl_usd": 25_000,
                "verified_source": False,
                "tags": ["unknown_protocol", "unverified_contract", "high_total_balance"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertEqual(scored.next_action, "drop_low_value")
        self.assertLess(scored.score, config["queue_threshold"])

    def test_chain_scanner_unfamiliar_balance_spike_is_recon_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:unfamiliar-spike",
                "name": "0xabc",
                "chain": "bsc",
                "category": "fresh contract",
                "tvl_usd": 1_500_000,
                "verified_source": None,
                "tags": [
                    "unknown_protocol",
                    "unfamiliar_contract",
                    "unknown_verification_status",
                    "immediate_balance_spike",
                    "high_total_balance",
                    "stablecoin_balance",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "recon_bravo_then_corecritical")

    def test_chain_scanner_hidden_unknown_at_300k_is_recon_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:hidden-unknown",
                "name": "0xhidden",
                "chain": "bsc",
                "category": "fresh contract",
                "tvl_usd": 300_000,
                "verified_source": None,
                "tags": [
                    "unknown_protocol",
                    "unfamiliar_contract",
                    "unknown_verification_status",
                    "hidden_high_value_contract",
                    "high_total_balance",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "recon_bravo_then_corecritical")

    def test_chain_scanner_high_balance_probable_bot_is_trace_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "bot_contract",
                "external_id": "bsc:probable-bot",
                "name": "0xprobablebot",
                "chain": "bsc",
                "category": "fresh contract",
                "tvl_usd": 350_000,
                "verified_source": None,
                "tags": [
                    "unknown_protocol",
                    "unfamiliar_contract",
                    "unknown_verification_status",
                    "hidden_high_value_contract",
                    "probable_bot_contract",
                    "high_balance_bot_candidate",
                    "high_tx_count",
                    "high_total_balance",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "trace_bot_contract_then_target_protocols")

    def test_closed_project_redeploy_cluster_is_investigation_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:cluster",
                "name": "New Yield Migrator",
                "chain": "bsc",
                "category": "migrator vault",
                "liquidity_usd": 220_000,
                "verified_source": False,
                "tags": [
                    "unknown_protocol",
                    "prior_project_closed",
                    "same_deployer_closed_project",
                    "funding_from_closed_project",
                    "suspected_rug_redeploy",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "investigate_redeploy_funding_cluster")

    def test_proxy_change_with_live_funds_is_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "base:proxy-change",
                "name": "Live Proxy Vault",
                "chain": "base",
                "category": "vault proxy",
                "tvl_usd": 900_000,
                "tags": ["proxy_impl_changed", "live_proxy_funds"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "proxy_change_live_funds")

    def test_reward_pool_claimability_is_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:reward-pool",
                "name": "Claimable Reward Pool",
                "chain": "bsc",
                "category": "reward staking",
                "tvl_usd": 420_000,
                "tags": ["active_reward_pool", "large_claimable_rewards"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "reward_pool_claimability_check")

    def test_shadow_value_verified_contract_is_recon_queue(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:shadow-vault",
                "name": "Silent Yield Reward Vault",
                "chain": "bsc",
                "category": "reward vault",
                "tvl_usd": 1_250_000,
                "verified_source": True,
                "tags": [
                    "unknown_protocol",
                    "under_the_radar",
                    "low_public_attention",
                    "no_audit_found",
                    "not_defillama_top",
                    "vault",
                    "reward_pool",
                    "stablecoin_balance",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "shadow_value_verified_contract_recon")
        self.assertIn("shadow_value_verified_contract:30", scored.reasons)

    def test_shadow_value_requires_verified_source(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "bsc_chain_scanner",
                "entity_type": "unknown_protocol",
                "external_id": "bsc:shadow-unverified",
                "name": "Silent Yield Reward Vault",
                "chain": "bsc",
                "category": "reward vault",
                "tvl_usd": 1_250_000,
                "verified_source": False,
                "tags": [
                    "unknown_protocol",
                    "under_the_radar",
                    "low_public_attention",
                    "no_audit_found",
                    "vault",
                    "reward_pool",
                ],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertNotEqual(scored.next_action, "shadow_value_verified_contract_recon")
        self.assertNotIn("shadow_value_verified_contract:30", scored.reasons)


    def test_bridge_escrow_validation_is_queued(self):
        config = json.loads(Path("config/sentinel.json").read_text())
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:bridge-escrow",
                "name": "Bridge Escrow",
                "chain": "bsc",
                "category": "bridge",
                "tvl_usd": 1_500_000,
                "tags": ["bridge_escrow", "message_validation"],
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "bridge_escrow_message_validation_check")


if __name__ == "__main__":
    unittest.main()
