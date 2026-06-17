# Protocol Sentinel DeepWiki Workflow Plan

## Review Summary

`MKSIIQO` is the workflow model to copy. It is a numbered GitHub Actions DeepWiki bot with:

- a project blueprint loaded into every prompt
- rotating DeepWiki repository URLs through `repositories.json`
- `BOT_SMOKE_LIMIT` and `chain_next` dispatch inputs
- staged output folders instead of direct validation
- a DeepWiki proof gate that asks one exact live-state question
- JSON schemas for scanner/proof-gate output
- `workflow_chain.py` to verify stage outputs and dispatch the next workflow

`maker` is the discovery engine to wrap. It already has:

- `python3 -m sentinel discover`
- live target refresh from the newest scored queue
- fixture-backed explorer/RPC snapshot enrichment
- scored outputs in `runs/<timestamp>/`
- actions for bot contracts, unverified funded contracts, sudden spikes, redeploy clusters, and normal recon
- a fund/reward extraction hunt plan with the same hard proof gate used in MKSIIQO

The right direction is not to replace Sentinel. The right direction is to turn Sentinel into Stage 1-3 of a DeepWiki workflow, then reuse the MKSIIQO style for prompt routing, proof gating, smoke runs, repository rotation, and staged outputs.

## Target Architecture

```text
live discovery sources
-> Sentinel scored queue
-> live target refresh
-> explorer/RPC enrichment snapshot
-> DeepWiki candidate brief
-> DeepWiki candidate triage
-> DeepWiki proof gate with live context
-> local bravo/prove/corecritical workflow
-> report only confirmed issues
```

DeepWiki should never mark a candidate final. It should only classify and produce proof-ready work:

- `REJECT`
- `NEEDS_LIVE_CONTEXT`
- `NEEDS_LOCAL_PROOF`
- `HIGH_CONFIDENCE_CANDIDATE`

Final confirmation remains local: code review, fork/live proof, or a runnable PoC.

## Folder Layout To Add In `maker`

```text
.github/workflows/
  1_sentinel_discover.yml
  2_refresh_live_targets.yml
  3_enrich_live_targets.yml
  4_build_deepwiki_briefs.yml
  5_run_deepwiki_triage.yml
  6_run_deepwiki_proof_gate.yml
  7_export_local_proof_queue.yml
  8_cleanup_state.yml

blueprints/
  sentinel_fund_reward_discovery.json

deepwiki_briefs/
deepwiki_pending/
deepwiki_candidates/
needs_live_context/
needs_local_proof/
deepwiki_unknown/
rejected_by_deepwiki/
proof_gate_pending/
proof_gate_results/
local_proof_queue/
state/
```

The `runs/<timestamp>/` folders should remain the raw Sentinel history. DeepWiki-facing folders should hold only normalized, smaller artifacts that are easy for GitHub workflows to batch and commit.

## Workflow Stages

### Stage 1 - Sentinel Discovery

Run:

```bash
python3 -m sentinel discover --source all --limit "${SENTINEL_LIMIT:-100}" --output runs
```

Output:

- `runs/<timestamp>/candidates_scored.json`
- `runs/<timestamp>/triage_queue.csv`
- `runs/<timestamp>/triage_queue.md`

Required upgrade:

- add workflow inputs for `source`, `limit`, `smoke_limit`, and `chain_next`
- make `BOT_SMOKE_LIMIT` map to Sentinel `--limit`
- commit only the new run folder

### Stage 2 - Refresh Live Targets

Run:

```bash
python3 -m sentinel refresh-targets --latest --runs-dir runs --output examples/live_targets.json
```

Output:

- `examples/live_targets.json`

Required upgrade:

- also write `state/latest_targets.json`
- include rank, score, action, source, and reasons in metadata
- preserve target action priority:
  - `investigate_redeploy_funding_cluster`
  - `reverse_engineer_unverified_funded_contract`
  - `price_spike_recon_then_source_check`
  - `trace_bot_contract_then_target_protocols`
  - `recon_bravo_then_corecritical`

### Stage 3 - Live Enrichment

Run:

```bash
python3 -m sentinel discover --source explorer_live --input examples/live_targets.json --limit "${SENTINEL_LIMIT:-50}"
```

Output:

- enriched `runs/<timestamp>/candidates_scored.json`
- enriched `triage_queue.*`
- `state/latest_live_snapshot.json`

Required upgrade:

- persist the raw explorer snapshot separately before scoring
- include commands/API URLs used, block number, chain id, balance source, and timestamp
- mark stale live data as unusable after a configured TTL

### Stage 4 - Build DeepWiki Candidate Briefs

Add a script:

```text
run_build_deepwiki_briefs.py
```

It should convert top enriched candidates into one JSON brief per candidate:

```text
deepwiki_briefs/<rank>-<chain>-<address>.json
```

Each brief must include:

- candidate identity and source
- score, action, and scoring reasons
- live balances/value at risk
- verified/unverified source status
- proxy/admin/implementation status if known
- deployer/funder/treasury cluster evidence
- top selectors and recent transaction patterns
- bot counterparties and profit sinks when relevant
- why this candidate matters for fund/reward extraction
- exact local proof questions to answer

### Stage 5 - DeepWiki Candidate Triage

Copy the MKSIIQO pattern:

- `bot_blueprint.py`
- `bot_runtime.py`
- `deepwiki_triage.py`
- Selenium driver wrapper
- `repositories.json` rotation
- smoke batching

Add Sentinel-specific prompts in a new module:

```text
deepwiki_prompts.py
```

DeepWiki should answer:

```text
Does this live candidate likely expose a concrete unprivileged path to extract funds or rewards beyond entitlement, or should it be rejected before local proof?
```

Routes:

- `REJECT` -> `rejected_by_deepwiki/` only when `SAVE_REJECTED_DEEPWIKI=1`
- `NEEDS_LIVE_CONTEXT` -> `needs_live_context/`
- `NEEDS_LOCAL_PROOF` -> `needs_local_proof/`
- `HIGH_CONFIDENCE_CANDIDATE` -> `deepwiki_candidates/`
- parse failure -> `deepwiki_unknown/`

### Stage 6 - DeepWiki Proof Gate

Reuse MKSIIQO's exact gate:

```text
Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?
```

Input folders:

- `needs_local_proof/*.json`
- `deepwiki_candidates/*.json`

Output contract:

```text
proof-gate-v1
```

Hard gates:

- current live target only
- unprivileged attacker
- attacker-controlled trigger
- exact code path or selector exists
- concrete fund/reward gain
- gain beyond entitlement
- live state supports the preconditions
- not admin/governance/key compromise
- not DoS/grief/liveness only
- not external dependency only
- not expected behavior or known duplicate

### Stage 7 - Export Local Proof Queue

Add:

```text
run_export_local_proof_queue.py
```

It should produce:

```text
local_proof_queue/<rank>-<chain>-<project>.md
```

Each item should include:

- candidate summary
- target contracts
- live balances
- selected entrypoints/selectors
- suspected exploit family
- exact fork/live commands to run
- expected assertion
- suggested next command:
  - `bravo <project>`
  - `list entrypoints`
  - `prove corecritical`
  - `prove critical`

### Stage 8 - Cleanup And State

Maintain:

- `state/seen_candidates.json`
- `state/rejected_candidates.json`
- `state/proof_queue_index.json`
- `state/source_health.json`

Rules:

- dedupe by `chain:address`
- reopen only if value, implementation, proxy, source verification, or score changed materially
- do not reopen unchanged low-signal candidates
- preserve first seen, last seen, max score, max value, and last action

## DeepWiki Repository Setup

Use the MKSIIQO setup model:

- keep a source repository for the real tool
- create rotating clone repositories for DeepWiki indexing
- store resulting URLs in `repositories.json`
- filter URLs so only the expected Sentinel repo slug is used
- keep `MAX_REPO` in the Sentinel blueprint
- preserve `workflow_dispatch` inputs:
  - `smoke_limit`
  - `chain_next`

The workflow chain should verify real outputs before dispatching the next numbered workflow. A stage with no expected output should stop with a clear log, not silently continue.

## Discovery Upgrade Plan

### Add Better Sources

Priority sources to add:

- Etherscan-compatible contract creation scans for BSC, Ethereum, Base, Arbitrum, Polygon, Avalanche, Optimism, Linea, Scroll, Mantle, Blast
- Blockscout-compatible scans for chains where Etherscan-style APIs are weak
- verified-contract feeds: newly verified contracts, newly changed source, proxy implementation changes
- internal transaction contract creation feeds
- DEX Screener pair search by high 24h volume and high liquidity-to-FDV
- GeckoTerminal new pools as a second market source
- DeFiLlama yield pools and emissions data, not just protocol TVL
- token holder concentration and LP lock/burn status
- proxy/admin monitoring from EIP-1967 slots
- event-based claim/reward/deposit/withdraw activity

### Add More Candidate Classes

Add scoring classes for:

- proxy implementation changed while funds remain in old accounting state
- verified source recently changed after deposits
- high-value contracts with only selector-level public usage and no verified ABI
- reward pools with large claimable balance and low staker count
- vaults with large asset/share imbalance
- bridges with paused/failed message queues and live escrow funds
- routers/migrators with approvals from many users
- token distributors with unclaimed allocation and weak proof/snapshot logic
- fee splitters and reward managers with public `claim`, `distribute`, `sync`, `harvest`, or `sweep`
- lending markets with thin liquidity, stale oracle updates, or new collateral listings
- strategy wrappers with public rebalance/harvest/withdraw paths
- contracts funded by exploit-linked, abandoned, or closed-project wallets
- bot-discovered target protocols where the bot repeatedly profits from the same target cluster

### Add Risk Features

Score these features:

- live native/ERC20 balance in the contract
- value locked in child contracts, pools, gauges, or escrow
- claimable reward pool size
- number of unique depositors or holders
- recent deposits before verification
- source unverified, partial, proxy-only, or implementation missing
- public value-moving selectors seen in transactions
- owner/admin is EOA or recently changed
- timelock absent or delay too short
- implementation slot changed recently
- repeated failed transactions around claim/withdraw/redeem
- high volume with low liquidity
- liquidity-to-FDV abnormality
- fresh deployment with high value
- high bot interaction count
- same deployer/funder as closed project

### Add Negative Filters

Reduce noise by dampening:

- large mainstream protocols unless a fresh implementation/listing/reward change exists
- CEX wallets
- pure memecoins without protocol custody
- low-liquidity tokens below floor
- admin-only issues without user-triggered extraction
- theoretical math issues without live funds
- DoS/liveness-only candidates
- contracts with value only in unrelated subsidies and no user/reward pool exposure

### Add Smart Routing

Map `next_action` to proof route:

```text
recon_bravo_then_corecritical
-> normal protocol recon

trace_bot_contract_then_target_protocols
-> trace counterparties first, then promote repeated target protocols

reverse_engineer_unverified_funded_contract
-> selector/storage/proxy reconstruction before DeepWiki proof

price_spike_recon_then_source_check
-> source, admin, holder, LP-lock, and value custody checks first

investigate_redeploy_funding_cluster
-> funder/deployer migration trace before normal recon
```

Add new routes:

```text
proxy_change_live_funds
reward_pool_claimability_check
bridge_escrow_message_validation_check
approval_router_drain_surface
vault_share_asset_invariant_check
lending_oracle_liquidation_check
```

## Implementation Order

1. Copy only the reusable MKSIIQO workflow pieces into `maker`: runtime limit, triage routing, workflow chain, blueprint loader, and proof-gate schema.
2. Create `blueprints/sentinel_fund_reward_discovery.json`.
3. Add `run_build_deepwiki_briefs.py` and tests for brief generation from `candidates_scored.json`.
4. Add Sentinel DeepWiki prompt/schema modules.
5. Add workflows 1-4 and verify they run without Selenium first.
6. Add workflows 5-6 using the MKSIIQO Selenium DeepWiki runner and staging folders.
7. Add local proof queue export.
8. Add persistent state and dedupe/reopen rules.
9. Add live source adapters one chain at a time, starting with BSC and Base.
10. Expand scoring with proxy, reward, bridge, router, vault, lending, and bot-target features.
11. Run a smoke chain with `smoke_limit=1`.
12. Inspect staged outputs and tune prompts before enabling full-chain dispatch.

## First Smoke Test

```bash
python3 -m sentinel discover --source sample --limit 10
python3 -m sentinel refresh-targets --latest --runs-dir runs --output examples/live_targets.json
python3 -m sentinel discover --source explorer_snapshot --input examples/explorer_snapshot.json --limit 10
python3 run_build_deepwiki_briefs.py --latest --limit 1
```

Then run GitHub workflows manually:

```text
1_sentinel_discover.yml smoke_limit=1 chain_next=true
```

Expected safe result:

- a new run folder exists
- one live target list exists
- one DeepWiki brief exists
- DeepWiki output is staged, not validated
- proof gate produces proof-ready JSON, not a final report

## Success Criteria

The conversion is complete when:

- Sentinel can run fully from GitHub Actions
- DeepWiki sees the latest Sentinel candidate briefs
- output folders match the MKSIIQO staged workflow model
- no workflow writes directly to final validation/report folders
- smoke mode can walk the chain end to end
- local proof queue contains exact runnable next steps
- high-value unfamiliar contracts, bot targets, unverified funded contracts, redeploy clusters, reward pools, vaults, bridges, routers, and proxy-change candidates are all represented in scoring

