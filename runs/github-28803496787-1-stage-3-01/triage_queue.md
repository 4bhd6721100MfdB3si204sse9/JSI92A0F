# Protocol Sentinel Triage Queue

| Rank | Score | Name | Type | Chain | Value | 24h % | Action | Reasons |
| --- | ---: | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | 116 | 0xaa390a37006e22b5775a34f2147f81ebd6a63641 | unknown_protocol | ethereum | 19564452307 | 0 | recon_bravo_then_corecritical | value_at_risk>=10000000:19564452307, chain_weight:ethereum:5, high_tx_count, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 2 | 116 | 0x99cd4ec3f88a45940936f469e4bb72a2a701eeb9 | unknown_protocol | ethereum | 18107795559 | 0 | recon_bravo_then_corecritical | value_at_risk>=10000000:18107795559, chain_weight:ethereum:5, high_tx_count, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 3 | 98 | 0x303d72b77efe73e07aacb9dbe58e794c3df48625 | unknown_protocol | ethereum | 8076774 | 0 | recon_bravo_then_corecritical | value_at_risk>=1000000:8076774, chain_weight:ethereum:5, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 4 | 94 | 0x278d858f05b94576c1e6f73285886876ff6ef8d2 | unknown_protocol | bsc | 766590 | 0 | recon_bravo_then_corecritical | value_at_risk>=250000:766590, chain_weight:bsc:10, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 5 | 94 | 0x519d281627c9f25636a041416707e6f1f4cf945f | unknown_protocol | bsc | 500567 | 0 | recon_bravo_then_corecritical | value_at_risk>=250000:500567, chain_weight:bsc:10, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 6 | 93 | 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b | unknown_protocol | bsc | 20622053 | 0 | recon_bravo_then_corecritical | value_at_risk>=10000000:20622053, chain_weight:bsc:10, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18 |
| 7 | 19 | 0x7ff1f30f6e7eec2ff3f0d1b60739115bdf88190f | known_protocol | ethereum | 21556952428 | 0 | watch_known_protocol | value_at_risk>=10000000:21556952428, chain_weight:ethereum:5, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20, known_public_protocol_quarantine |
| 8 | 19 | 0xc2eab7d33d3cb97692ecb231a5d0e4a649cb539d | known_protocol | ethereum | 6900338450 | 0 | watch_known_protocol | value_at_risk>=10000000:6900338450, chain_weight:ethereum:5, high_tx_count, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, balance_spike:20 |
| 9 | 19 | 0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b | known_protocol | ethereum | 4859934 | 0 | watch_known_protocol | value_at_risk>=1000000:4859934, chain_weight:ethereum:5, surface:flashloan:18, flashloan_user, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18 |
| 10 | 19 | 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 | known_protocol | bsc | 27856474 | 0 | watch_known_protocol | value_at_risk>=10000000:27856474, chain_weight:bsc:10, unknown_protocol:10, unfamiliar_contract:12, unknown_verification_status:8, hidden_high_value_contract:18, known_public_protocol_quarantine |

## Analyst Next Steps

1. Take the highest `recon_bravo_then_corecritical` item.
2. Resolve its real protocol contracts and live balances.
3. Run live recon into the 04-LIVE information path.
4. List callable entrypoints and asset-moving paths.
5. Prove the highest-risk mapped critical question before reporting.
6. For `trace_bot_contract_then_target_protocols`, trace counterparties, repeated targets, DEX paths, flashloan providers, and profit sinks before choosing a protocol to audit.
7. For `reverse_engineer_unverified_funded_contract`, recover selectors, storage/proxy shape, balances, and privileged callers before choosing a proof target.
8. For `price_spike_recon_then_source_check`, verify liquidity locks, holder concentration, admin permissions, and whether verified source exists.
9. For `investigate_redeploy_funding_cluster`, trace deployer/funder links to closed projects and promote the new funded contract or protocol cluster for audit.
