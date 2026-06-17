# Protocol Sentinel Triage Queue

| Rank | Score | Name | Type | Chain | Value | Action | Reasons |
| --- | ---: | --- | --- | --- | ---: | --- | --- |
| 1 | 89 | QuietBridge | protocol | base | 1900000 | recon_bravo_then_corecritical | value_at_risk>=1000000:1900000, chain_weight:base:8, surface:bridge:18, fresh_pair<=3d:3, latest_boost |
| 2 | 80 | DexPathExecutor Bot | bot_contract | bsc | 18000 | trace_bot_contract_then_target_protocols | value_below_minimum:18000, bot_contract:18, chain_weight:bsc:10, surface:bot:16, verified_bot_contract |
| 3 | 77 | FastReward Staking | protocol | bsc | 850000 | recon_bravo_then_corecritical | value_at_risk>=250000:850000, chain_weight:bsc:10, surface:vault:15, fresh_pair<=3d:1, latest_profile |
| 4 | 21 | Large Known Lending | protocol | ethereum | 400000000 | watch_mainstream | value_at_risk>=10000000:400000000, chain_weight:ethereum:5, surface:lending:16, mainstream_dampener>=100000000 |
| 5 | 15 | Tiny Meme Pool | protocol | polygon | 4000 | drop_low_value | value_below_minimum:4000, chain_weight:polygon:7, latest_profile, low_value_score_cap |

## Analyst Next Steps

1. Take the highest `recon_bravo_then_corecritical` item.
2. Resolve its real protocol contracts and live balances.
3. Run live recon into the 04-LIVE information path.
4. List callable entrypoints and asset-moving paths.
5. Prove the highest-risk mapped critical question before reporting.
6. For `trace_bot_contract_then_target_protocols`, trace counterparties, repeated targets, DEX paths, flashloan providers, and profit sinks before choosing a protocol to audit.
