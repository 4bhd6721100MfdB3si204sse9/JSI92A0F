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
                "tvl_usd": 220_000,
                "tags": ["verified_bot_contract", "flashloan_user", "dex_path_executor"],
                "raw": {
                    "behavior": "flashloan swap callback profit sweep"
                },
            }
        )

        scored = score_candidate(candidate, config)

        self.assertGreaterEqual(scored.score, config["queue_threshold"])
        self.assertEqual(scored.next_action, "trace_bot_contract_then_target_protocols")

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
