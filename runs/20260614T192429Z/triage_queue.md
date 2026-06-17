# Protocol Sentinel Triage Queue

| Rank | Score | Name | Type | Chain | Value | 24h % | Action | Reasons |
| --- | ---: | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | 147 | New Yield Migrator | unknown_protocol | bsc | 90000 | 0 | investigate_redeploy_funding_cluster | value_below_minimum:90000, unverified_contract:20, chain_weight:bsc:10, surface:vault:15, unknown_protocol:10 |
| 2 | 89 | QuietBridge | protocol | base | 1900000 | 0 | recon_bravo_then_corecritical | value_at_risk>=1000000:1900000, chain_weight:base:8, surface:bridge:18, fresh_pair<=3d:3, latest_boost |
| 3 | 80 | DexPathExecutor Bot | bot_contract | bsc | 18000 | 0 | trace_bot_contract_then_target_protocols | value_below_minimum:18000, bot_contract:18, chain_weight:bsc:10, surface:bot:16, verified_bot_contract |
| 4 | 77 | FastReward Staking | protocol | bsc | 850000 | 0 | recon_bravo_then_corecritical | value_at_risk>=250000:850000, chain_weight:bsc:10, surface:vault:15, fresh_pair<=3d:1, latest_profile |
| 5 | 77 | Unknown Spike Vault | unknown_protocol | base | 180000 | 420 | price_spike_recon_then_source_check | value_below_minimum:180000, chain_weight:base:8, surface:vault:15, latest_profile, sudden_price_spike:18 |
| 6 | 70 | Unverified Funded Treasury | unverified_contract | bsc | 640000 | 0 | reverse_engineer_unverified_funded_contract | value_at_risk>=250000:640000, unverified_contract:20, chain_weight:bsc:10, surface:unverified:14, unknown_protocol:10 |
| 7 | 21 | Large Known Lending | protocol | ethereum | 400000000 | 0 | watch_mainstream | value_at_risk>=10000000:400000000, chain_weight:ethereum:5, surface:lending:16, mainstream_dampener>=100000000 |
| 8 | 15 | Tiny Meme Pool | protocol | polygon | 4000 | 0 | drop_low_value | value_below_minimum:4000, chain_weight:polygon:7, latest_profile, low_value_score_cap |

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
