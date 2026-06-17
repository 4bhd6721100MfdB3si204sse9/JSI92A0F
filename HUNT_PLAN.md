# Fund And Reward Extraction Hunt Plan

## Goal

Find protocols where an unprivileged actor can extract user funds or rewards beyond entitlement.

This hunt excludes generic bugs, nuisance liveness issues, and cosmetic failures. The target class is only:

- unauthorized or excessive withdrawal of user principal or pooled value
- reward capture beyond what the actor is entitled to receive

## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.

## High-Value Surfaces

Prioritize protocols with these shapes:

- vaults and share-based pools
- staking and reward-distribution contracts
- lending markets and liquidation paths
- bridges and cross-chain claim or release paths
- migrators, routers, and strategy wrappers
- claim contracts, airdrop distributors, and vesting contracts
- reward managers, fee splitters, and emission controllers
- bots or executors that repeatedly touch the same protocol and reveal the extraction route

## Fund Extraction Patterns

Look for paths where a caller can move or realize user principal:

- withdraw, redeem, unstake, claim, liquidate, or sweep functions
- share-price drift or exchange-rate mismatch
- rounding favoring the attacker on repeat calls
- deposit/withdraw asymmetry
- phantom accounting where shares are issued without matching assets
- missing access control on release, sweep, rescue, or migration functions
- allowance, permit, or approval bugs that let funds move from users
- bridge message validation gaps that unlock user value

## Reward Extraction Patterns

Look for paths where a caller can capture more rewards than their share:

- early entry into a reward pool before snapshot or cooldown
- repeated claim windows from one position
- reward index desynchronization
- stale accumulator state
- zero-stake or dust-stake reward capture
- front-run or back-run of reward updates
- flashloan-amplified reward capture
- wrapper or proxy custody that lets one user capture another user’s reward

## Triage Rule

Score only protocols that satisfy at least one of these:

1. user funds are already deposited on-chain
2. there is a live reward pool or claimable emission
3. there is a public withdraw/redeem/claim path
4. the protocol is newly deployed, unverified, or forked from a risky pattern
5. a bot or executor repeatedly reveals the same target path

Reject candidates that only show:

- theoretical math issues without value movement
- liveness or UX friction without extraction
- admin-only misuse unless the admin key compromise is part of the proof

## Evidence Required

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy

## Workflow

1. Discover protocols from live market and explorer data.
2. Filter to fund-extraction and reward-extraction candidates.
3. Refresh `live_targets.json` from the latest scored queue.
4. Build the live snapshot with explorer/RPC data.
5. Inspect balances, selectors, deployers, and funding clusters.
6. Prove the extraction path on a fork or live state.
7. Only then write a report or escalation note.

## Scoring Bias

Increase priority for:

- high TVL or high pooled balances
- active reward emissions
- recent deployment with no verified source
- proxy/admin-controlled value movement
- repeated bot interaction
- closed-project redeploy patterns
- sudden price/liquidity spikes around a new or unknown protocol

## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

