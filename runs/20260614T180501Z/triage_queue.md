# Protocol Sentinel Triage Queue

| Rank | Score | Name | Chain | Value | Action | Reasons |
| --- | ---: | --- | --- | ---: | --- | --- |
| 1 | 89 | QuietBridge | base | 1900000 | recon_bravo_then_corecritical | value_at_risk>=1000000:1900000, chain_weight:base:8, surface:bridge:18, fresh_pair<=3d:3, latest_boost |
| 2 | 77 | FastReward Staking | bsc | 850000 | recon_bravo_then_corecritical | value_at_risk>=250000:850000, chain_weight:bsc:10, surface:vault:15, fresh_pair<=3d:1, latest_profile |
| 3 | 21 | Large Known Lending | ethereum | 400000000 | watch_mainstream | value_at_risk>=10000000:400000000, chain_weight:ethereum:5, surface:lending:16, mainstream_dampener>=100000000 |
| 4 | 15 | Tiny Meme Pool | polygon | 4000 | drop_low_value | value_below_minimum:4000, chain_weight:polygon:7, latest_profile |

## Analyst Next Steps

1. Take the highest `recon_bravo_then_corecritical` item.
2. Resolve its real protocol contracts and live balances.
3. Run live recon into the 04-LIVE information path.
4. List callable entrypoints and asset-moving paths.
5. Prove the highest-risk mapped critical question before reporting.
