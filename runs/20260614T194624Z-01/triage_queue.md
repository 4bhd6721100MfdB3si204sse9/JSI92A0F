# Protocol Sentinel Triage Queue

| Rank | Score | Name | Type | Chain | Value | 24h % | Action | Reasons |
| --- | ---: | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | 137 | New Yield Migrator | unknown_protocol | bsc | 90000 | 0 | investigate_redeploy_funding_cluster | value_below_minimum:90000, unverified_contract:20, chain_weight:bsc:10, surface:vault:15, prior_project_closed:18, same_deployer_closed_project:22, funding_from_closed_project:24, suspected_rug_redeploy:28 |
| 2 | 85 | Unknown Spike Vault | unknown_protocol | base | 185000 | 420 | price_spike_recon_then_source_check | value_below_minimum:185000, chain_weight:base:8, surface:vault:15, latest_profile, high_tx_count, sudden_price_spike:18, unknown_protocol:10, price_spike_24h>=100:420 |
| 3 | 75 | DexPathExecutor Bot | bot_contract | bsc | 18000 | 0 | trace_bot_contract_then_target_protocols | value_below_minimum:18000, bot_contract:18, chain_weight:bsc:10, surface:router:11, verified_bot_contract, high_tx_count, flashloan_user, dex_path_executor |
| 4 | 70 | Unverified Funded Treasury | unverified_contract | bsc | 665000 | 0 | reverse_engineer_unverified_funded_contract | value_at_risk>=250000:665000, unverified_contract:20, chain_weight:bsc:10, surface:unverified:14, unknown_protocol:10 |

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
