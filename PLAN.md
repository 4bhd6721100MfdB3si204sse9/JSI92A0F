# Defensive Protocol Discovery Plan

## Objective

Build a repeatable system that finds under-defended smart-contract protocols with meaningful user funds before attackers reach them.

The system should discover candidates from the same public surfaces attackers monitor, rank them by exploit opportunity, and produce a queue for live recon and proof-first auditing.

## Phase 1 - Discovery MVP

Status: implemented in this repository.

Inputs:

- DEX Screener latest token profiles.
- DEX Screener latest boosted tokens.
- DeFiLlama protocol list.
- Local sample fixtures for offline testing.
- Explorer/RPC-style contract snapshots.

Outputs:

- Scored JSON candidate list.
- CSV triage queue.
- Markdown analyst queue.

Core signals:

- New token/profile/pool activity.
- Liquidity or TVL above minimum threshold.
- Protocol category or name matching high-risk surfaces.
- Chain ecosystem where copy-fork and low-attention deployments are common.
- Low attention compared with value at risk.
- Unverified contracts holding meaningful funds.
- Unknown protocols with sudden price/liquidity spikes.
- Deployer or funding clusters linked to closed or abandoned projects.

## Phase 2 - Explorer Enrichment

Status: implemented as a fixture-backed collector in `sentinel/explorer.py`.

Add Etherscan-compatible collectors for:

- newly verified contracts
- contract creation transactions
- proxy implementation/admin reads
- token balances for contracts
- source-code keyword extraction
- deployer clustering
- bot smart contracts
- unverified funded contracts
- sudden price/liquidity spikes
- redeploy/funding links from closed projects

Current collector input:

```text
examples/explorer_snapshot.json
```

The live adapters should emit that same shape from explorer/RPC data so the scoring, queue, and tests stay stable.

Live adapter input:

```text
examples/live_targets.json
```

That file is the list of chain/address/label targets that the live adapter turns into the same snapshot format.

Target refresh command:

```text
python3 -m sentinel refresh-targets --latest --runs-dir runs --output examples/live_targets.json
```

This is the loop that turns the scored queue into the next live target list without hand-editing addresses.

Target refresh rule:

1. Pick the newest `runs/<timestamp>/candidates_scored.json`.
2. Keep only `investigate_redeploy_funding_cluster`, `reverse_engineer_unverified_funded_contract`, `price_spike_recon_then_source_check`, `trace_bot_contract_then_target_protocols`, and `recon_bravo_then_corecritical`.
3. Deduplicate by `chain:address`.
4. Write `examples/live_targets.json`.
5. Feed that file into `explorer_live`.

Required config:

- per-chain explorer base URL
- API key
- chain id
- safe rate limit

Bot contract signals:

- verified names containing bot, executor, arbitrage, sniper, keeper, liquidator, or MEV
- high transaction count relative to contract age
- flashloan callback usage
- repeated DEX/router paths
- profit sweeping to one or more EOAs
- repeated interaction with the same unknown protocol contracts
- same deployer creating multiple executor contracts

Bot contract output should not be treated as a final protocol target. It is a route-finder: trace the bot to discover which protocols, pools, vaults, bridges, or claims it is touching repeatedly.

Unverified funded contract signals:

- verified source is false or missing
- native/token balances exceed `min_unverified_value_usd`
- high-value deposits into contract shortly after deployment
- proxy-like storage or delegatecall behavior without verified implementation
- privileged caller or owner activity before/after deposits

Sudden-spike unknown protocol signals:

- 24h price change exceeds `price_spike_24h_pct`
- liquidity or TVL exceeds `min_spike_value_usd`
- unknown/low-attention source with new pool or boosted profile
- holder concentration or new treasury funding
- source verification missing or recently changed

Redeploy/funding-cluster signals:

- same deployer as a closed project
- funding from wallets associated with a closed project
- treasury migration into a new contract or pool
- repeated naming, website, deploy scripts, bytecode, or owner wallet patterns
- withdrawals or liquidity removals from old project followed by funding into a new one

## Phase 3 - On-Chain Recon Bridge

For every candidate above the score threshold:

1. Resolve protocol contracts.
2. Gather native and ERC20 balances.
3. Detect proxies and implementations.
4. Detect owner/admin/multisig/timelock roles.
5. Extract callable functions and value-moving paths.
6. Write a `bravo`-style live information folder.

For bot-contract candidates:

1. Trace recent transactions.
2. Extract target contracts called before profit sweep.
3. Group targets by protocol/address cluster.
4. Detect flashloan providers, DEX routers, and tokens used.
5. Promote the repeated target protocol into the normal recon queue.

For unverified funded contracts:

1. Identify native/ERC20 balances and recent depositors.
2. Recover function selectors from transaction calldata.
3. Check proxy slots, delegatecall patterns, and implementation addresses.
4. Cluster privileged callers, deployer, and funders.
5. Promote exploitable value-moving functions into proof work.

For redeploy/funding-cluster candidates:

1. Trace funding from the closed project to the new deployment.
2. Compare deployers, owners, treasuries, websites, names, and bytecode.
3. Identify where user funds are currently deposited.
4. Promote the live funded surface into recon and proof.

Output target:

```text
SINGULARITY/04-LIVE/information/<chain>-<protocol>/
```

## Phase 4 - Critical Pattern Mapping

Map each candidate to exploit families:

- reward accounting drift
- share/asset exchange-rate bugs
- oracle manipulation
- unchecked withdraw/redeem
- bridge/message validation mistakes
- unsafe claim logic
- fee-on-transfer accounting mismatch
- admin/proxy takeover
- stale state or missing sync logic
- external call/reentrancy value paths

Output:

```text
questionsCOREcritical candidate mapping
```

## Phase 5 - Proof-First Audit Queue

Only top-scoring candidates move into proof work.

Process:

```text
triage_queue.md
-> live recon
-> entrypoint inventory
-> corecritical proof
-> narrow PoC/test
-> responsible disclosure/report
```

Bot process:

```text
bot candidate
-> transaction trace
-> target protocol cluster
-> live recon on target protocol
-> corecritical proof
```

Unverified and redeploy process:

```text
funded unverified or redeploy-cluster candidate
-> balance and funding trace
-> selector/proxy/owner reconstruction
-> target protocol or contract selection
-> live recon
-> corecritical proof
```

Acceptance gate:

- real contract or reproducible fork target
- real value at risk
- concrete vulnerable path
- runnable proof or live-state proof

## Phase 6 - Continuous Operation

Run schedule:

- every 1-3 hours for DEX/new launch sources
- every 6-12 hours for DeFiLlama/TVL movement
- daily for full explorer source-code scans

State:

- dedupe known candidates
- track first seen / last seen
- track whether recon/proof/report was completed
- do not reopen candidates unless value or implementation changes

## Immediate Next Step

Add live chain adapters that build `explorer_snapshot` payloads from BscScan/Etherscan-compatible APIs plus RPC balance reads.
