import unittest

from sentinel.sources import candidate_from_dict
from sentinel.verified_address_finder import find_verified_addresses, evaluate_verified_address


class VerifiedAddressFinderTest(unittest.TestCase):
    def test_promotes_verified_high_value_eth_bounty_target(self):
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "eth:0x111",
                "name": "Quiet Rewards Vault",
                "chain": "ethereum",
                "address": "0x1111111111111111111111111111111111111111",
                "entity_type": "contract",
                "category": "rewards",
                "tvl_usd": 1_500_000,
                "verified_source": True,
                "tags": ["under_the_radar"],
                "url": "https://etherscan.io/address/0x1111111111111111111111111111111111111111#code",
                "raw": {
                    "bounty_url": "https://example.org/security",
                    "source_url": "https://etherscan.io/address/0x1111111111111111111111111111111111111111#code",
                    "audit_evidence": "none_found",
                },
            }
        )

        finding = evaluate_verified_address(candidate)

        self.assertIsNotNone(finding)
        assert finding is not None
        self.assertEqual(finding.recommended_next_action, "shadow_value_verified_contract_recon")
        self.assertEqual(finding.chain, "ethereum")
        self.assertEqual(finding.confidence, "high")
        self.assertIn("verified_source", finding.reasons)
        self.assertIn("disclosure_path_present", finding.reasons)

    def test_requires_verified_source(self):
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:0x222",
                "name": "Unverified Funded Vault",
                "chain": "bsc",
                "address": "0x2222222222222222222222222222222222222222",
                "category": "vault",
                "tvl_usd": 2_000_000,
                "verified_source": False,
                "raw": {"bounty_url": "https://example.org/security"},
            }
        )

        self.assertIsNone(evaluate_verified_address(candidate))

    def test_requires_disclosure_path(self):
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:0x333",
                "name": "Quiet Vault No Security Page",
                "chain": "bsc",
                "address": "0x3333333333333333333333333333333333333333",
                "category": "vault",
                "tvl_usd": 2_000_000,
                "verified_source": True,
            }
        )

        self.assertIsNone(evaluate_verified_address(candidate))

    def test_quarantines_known_public_without_fresh_exception(self):
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:pancake",
                "name": "PancakeSwap Treasury Vault",
                "chain": "bsc",
                "address": "0x4444444444444444444444444444444444444444",
                "category": "vault",
                "tvl_usd": 10_000_000,
                "verified_source": True,
                "tags": ["popular_protocol"],
                "raw": {"bounty_url": "https://example.org/security"},
            }
        )

        finding = evaluate_verified_address(candidate)

        self.assertIsNotNone(finding)
        assert finding is not None
        self.assertEqual(finding.recommended_next_action, "known_public_quarantine")
        self.assertEqual(finding.known_public_risk, "high")

    def test_allows_fresh_unique_component_exception(self):
        candidate = candidate_from_dict(
            {
                "source": "test",
                "external_id": "bsc:fresh",
                "name": "PancakeSwap Fresh Migration Escrow",
                "chain": "bsc",
                "address": "0x5555555555555555555555555555555555555555",
                "category": "migration",
                "tvl_usd": 3_000_000,
                "verified_source": True,
                "tags": ["popular_protocol", "fresh_unique_component"],
                "raw": {"bounty_url": "https://example.org/security"},
            }
        )

        finding = evaluate_verified_address(candidate)

        self.assertIsNotNone(finding)
        assert finding is not None
        self.assertEqual(finding.recommended_next_action, "shadow_value_verified_contract_recon")

    def test_finder_sorts_promoted_before_quarantine(self):
        candidates = [
            candidate_from_dict(
                {
                    "source": "test",
                    "external_id": "bsc:known",
                    "name": "Uniswap Vault",
                    "chain": "bsc",
                    "address": "0x6666666666666666666666666666666666666666",
                    "category": "vault",
                    "tvl_usd": 9_000_000,
                    "verified_source": True,
                    "raw": {"bounty_url": "https://example.org/security"},
                }
            ),
            candidate_from_dict(
                {
                    "source": "test",
                    "external_id": "bsc:quiet",
                    "name": "Quiet Escrow",
                    "chain": "bsc",
                    "address": "0x7777777777777777777777777777777777777777",
                    "category": "escrow",
                    "tvl_usd": 1_000_000,
                    "verified_source": True,
                    "raw": {"bounty_url": "https://example.org/security"},
                }
            ),
        ]

        findings = find_verified_addresses(candidates)

        self.assertEqual(findings[0].address, "0x7777777777777777777777777777777777777777")
        self.assertEqual(findings[0].recommended_next_action, "shadow_value_verified_contract_recon")
        self.assertEqual(findings[1].recommended_next_action, "known_public_quarantine")


if __name__ == "__main__":
    unittest.main()
