# Protocol Sentinel Triage Queue

| Rank | Score | Name | Chain | Value | Action | Reasons |
| --- | ---: | --- | --- | ---: | --- | --- |
| 1 | 38 | SPCX69 | solana | 94667 | recon_bravo_then_corecritical | value_at_risk>=minimum:94667, fresh_pair<=3d:2, latest_boost |
| 2 | 23 | LayerZero V2 | ethereum | 7583345774 | watch_mainstream | value_at_risk>=10000000:7583345774, chain_weight:ethereum:5, surface:bridge:18, mainstream_dampener>=100000000 |
| 3 | 21 | Aave V3 | ethereum | 11828950643 | watch_mainstream | value_at_risk>=10000000:11828950643, chain_weight:ethereum:5, surface:lending:16, mainstream_dampener>=100000000 |
| 4 | 19 | UFC White House | solana | 18960 | drop_low_value | value_below_minimum:18960, fresh_pair<=3d:0, latest_profile, high_liquidity_to_fdv:0.26, low_value_score_cap |
| 5 | 19 | TCGData | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_profile, low_value_score_cap |
| 6 | 19 | I am a fucking architect | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_profile, low_value_score_cap |
| 7 | 19 | Wokius Maximus | ethereum | 8136 | drop_low_value | value_below_minimum:8136, chain_weight:ethereum:5, fresh_pair<=3d:0, latest_profile, high_liquidity_to_fdv:0.42 |
| 8 | 19 | sims | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_profile, low_value_score_cap |
| 9 | 19 | Buongiorno | ethereum | 3791 | drop_low_value | value_below_minimum:3791, chain_weight:ethereum:5, fresh_pair<=3d:0, latest_profile, high_liquidity_to_fdv:0.45 |
| 10 | 19 | michaelseacrest15 | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_profile, low_value_score_cap |
| 11 | 19 | Dreaming Big | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_profile, low_value_score_cap |
| 12 | 19 | TaoOS | ethereum | 6070 | drop_low_value | value_below_minimum:6070, chain_weight:ethereum:5, fresh_pair<=3d:0, latest_profile, high_liquidity_to_fdv:0.90 |
| 13 | 19 | Religion | solana | 21437 | drop_low_value | value_below_minimum:21437, fresh_pair<=3d:0, latest_profile, high_liquidity_to_fdv:0.22, low_value_score_cap |
| 14 | 19 | BABY KINS | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_boost, low_value_score_cap |
| 15 | 19 | Highway on Solana | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:2, latest_boost, low_value_score_cap |
| 16 | 19 | LiquidPool | solana | 10585 | drop_low_value | value_below_minimum:10585, fresh_pair<=3d:0, latest_boost, high_liquidity_to_fdv:0.61, low_value_score_cap |
| 17 | 19 | PumpTown | solana | 11214 | drop_low_value | value_below_minimum:11214, fresh_pair<=3d:0, latest_boost, high_liquidity_to_fdv:0.44, low_value_score_cap |
| 18 | 19 | QUOKKA | solana | 0 | drop_low_value | value_below_minimum:0, fresh_pair<=3d:0, latest_boost, low_value_score_cap |
| 19 | 19 | Fight House | solana | 30371 | drop_low_value | value_below_minimum:30371, fresh_pair<=3d:0, latest_boost, high_liquidity_to_fdv:0.23, low_value_score_cap |
| 20 | 19 | Lido | ethereum | 14822733001 | watch_mainstream | value_at_risk>=10000000:14822733001, chain_weight:ethereum:5, surface:staking:14, mainstream_dampener>=100000000 |
| 21 | 19 | Bybit | ethereum | 13904893251 | watch_mainstream | value_at_risk>=10000000:13904893251, chain_weight:ethereum:5, surface:stake:14, mainstream_dampener>=100000000 |
| 22 | 19 | SSV Network | ethereum | 12224474246 | watch_mainstream | value_at_risk>=10000000:12224474246, chain_weight:ethereum:5, surface:staking:14, mainstream_dampener>=100000000 |
| 23 | 18 | Alpie | solana | 128280 | watch | value_at_risk>=minimum:128280, latest_boost |
| 24 | 18 | WBTC | bitcoin | 7317939832 | watch_mainstream | value_at_risk>=10000000:7317939832, surface:bridge:18, mainstream_dampener>=100000000 |
| 25 | 10 | ANDY | solana | 0 | drop_low_value | value_below_minimum:0, latest_boost, low_value_score_cap |
| 26 | 5 | Binance CEX | ethereum | 140161946025 | watch_mainstream | value_at_risk>=10000000:140161946025, chain_weight:ethereum:5, mainstream_dampener>=100000000 |
| 27 | 5 | OKX | ethereum | 21781833454 | watch_mainstream | value_at_risk>=10000000:21781833454, chain_weight:ethereum:5, mainstream_dampener>=100000000 |
| 28 | 0 | Bitfinex | bitcoin | 16879987165 | watch_mainstream | value_at_risk>=10000000:16879987165, mainstream_dampener>=100000000 |
| 29 | 0 | Robinhood | bitcoin | 11301131022 | watch_mainstream | value_at_risk>=10000000:11301131022, mainstream_dampener>=100000000 |

## Analyst Next Steps

1. Take the highest `recon_bravo_then_corecritical` item.
2. Resolve its real protocol contracts and live balances.
3. Run live recon into the 04-LIVE information path.
4. List callable entrypoints and asset-moving paths.
5. Prove the highest-risk mapped critical question before reporting.
