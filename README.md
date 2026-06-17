# Protocol Sentinel

Protocol Sentinel is a defensive discovery pipeline for finding under-watched smart-contract protocols before attackers do.

The first goal is not full auditing. The first goal is a ranked queue:

```text
new/unknown protocol with value
-> score by attacker-interest signals
-> write a triage queue
-> run live recon and critical proof workflow on the top items
```

## Quick Start

Run the offline sample pipeline:

```bash
python3 -m sentinel discover --source sample --limit 25
```

Run all enabled live sources:

```bash
python3 -m sentinel discover --source all --limit 50
```

Run the explorer/RPC-style enrichment fixture:

```bash
python3 -m sentinel discover --source explorer_snapshot --input examples/explorer_snapshot.json
```

Run the live adapter against a target list:

```bash
python3 -m sentinel discover --source explorer_live --input examples/live_targets.json
```

Refresh the live target list from a scored queue:

```bash
python3 -m sentinel refresh-targets --latest --runs-dir runs --output examples/live_targets.json
```

Outputs are written to `runs/<timestamp>/`:

- `candidates_scored.json`
- `triage_queue.csv`
- `triage_queue.md`

## Sources In The MVP

- `sample`: local fixture for verification.
- `dexscreener_profiles`: latest token profiles from DEX Screener.
- `dexscreener_boosts`: latest boosted tokens from DEX Screener.
- `defillama_protocols`: protocol TVL list from DeFiLlama.
- `explorer_snapshot`: JSON snapshot of contract balances, source verification, selectors, deployers, funders, tx activity, and price/liquidity movement.
- `explorer_live`: target list for live explorer/RPC fetches that emit the same snapshot shape.

The current explorer collector is fixture-backed so the analysis is deterministic and testable. Live explorer/RPC adapters should write the same snapshot shape before scoring.

The live workflow is:

```text
discover -> refresh-targets -> explorer_live -> triage_queue -> recon/proof
```

Bot smart contracts are included as first-class candidates through `entity_type: "bot_contract"`. They use a separate lower value floor because the useful signal is often activity, target selection, flashloan usage, and DEX execution paths rather than TVL held inside the bot.

The MVP also supports:

- `entity_type: "unverified_contract"` for contracts holding meaningful funds without verified source.
- `entity_type: "unknown_protocol"` for new or low-attention protocols with sudden price/liquidity expansion.
- deployer/funding-cluster signals for teams or wallets that closed one project and appear to fund a new one.

## Triage Rule

The queue is ranked by:

- value at risk
- freshness
- attacker-relevant surface keywords
- low-attention / high-value gap
- chain risk weight
- live recon need

The default value floor is `$250,000` in liquidity or TVL. Lower `min_value_usd` in `config/sentinel.json` when you want earlier but noisier discovery.

The top queue items should then go through the established audit flow:

```text
bravo <project>
list entrypoints
prove corecritical
prove critical
report only confirmed issues
```

Bot-contract queue items use a different first step:

```text
trace bot contract
-> identify repeated target protocols
-> identify DEX/flashloan/profit paths
-> choose the vulnerable protocol surface
-> then run bravo/prove on that protocol
```

Other special actions:

```text
reverse_engineer_unverified_funded_contract
-> recover selectors/storage/proxy shape
-> identify privileged callers and withdrawal paths
-> then choose a proof target

price_spike_recon_then_source_check
-> verify source, liquidity locks, holder concentration, admin powers
-> then run protocol recon if real funds are exposed

investigate_redeploy_funding_cluster
-> trace deployer/funder links to closed projects
-> identify whether user funds moved into the new project
-> then audit the new funded surface
```
