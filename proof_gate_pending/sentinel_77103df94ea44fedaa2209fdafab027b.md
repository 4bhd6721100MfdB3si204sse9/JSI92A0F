<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_22e045fa-7f0c-442a-a439-b5e89347f580?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The contract `0xf8e349d1d827a6edf17ee673664cfad4ca78c533` does not appear anywhere in the Protocol Sentinel repository — no enrichment data, no source, no selectors, no deployer trace, and no chain scanner entry exist for it. [1](#0-0)  The repository's live state files only contain placeholder sample addresses. [2](#0-1) 

Given the candidate brief alone — `verified_source: null`, empty `deployer_address`, no selectors, no proxy state, and no transaction history — the correct verdict under the hard rules is `NEEDS_LIVE_CONTEXT`. [3](#0-2) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0xf8e349d1d827a6edf17ee673664cfad4ca78c533",
    "name": "0xf8e349d1d827a6edf17ee673664cfad4ca78c533",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 89
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with ~$540K TVL in stablecoins, an immediate balance spike, and no verified source. The combination of hidden_high_value_contract + unknown_verification_status + balance_spike on Ethereum is a high-signal pattern for an unguarded value-moving surface. No source, selectors, deployer, or proxy state are available to confirm or deny exploitability.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "verified_source is null and no ABI is known. Without selectors we cannot identify any value-moving entrypoints.",
      "command_or_source": "cast code 0xf8e349d1d827a6edf17ee673664cfad4ca78c533 --rpc-url $ETH_RPC | evmdis / heimdall / panoramix to recover function selectors and storage layout"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags include stablecoin_balance and known_asset_balance but the specific token(s) held are unknown. Need exact token addresses and amounts to assess claimability.",
      "command_or_source": "cast call <ERC20_TOKEN> 'balanceOf(address)(uint256)' 0xf8e349d1d827a6edf17ee673664cfad4ca78c533 --rpc-url $ETH_RPC; check Etherscan token holdings tab"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "deployer_address is empty. Deployer identity and funding source determine whether this is a rug-redeploy cluster, a protocol treasury, or an attacker-controlled honeypot.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block ...) ...) to find creation tx; trace deployer EOA on Etherscan internal txs"
    },
    {
      "name": "proxy_and_implementation_check",
      "reason": "unknown_verification_status combined with a large balance spike is a known proxy-with-live-funds pattern. Implementation slot must be checked.",
      "command_or_source": "cast storage 0xf8e349d1d827a6edf17ee673664cfad4ca78c533 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC (EIP-1967 impl slot)"
    },
    {
      "name": "transaction_history_and_callers",
      "reason": "No volume24h and no prior interaction data. Need to know whether any public selectors have been called, whether there are privileged-only paths, and whether bots have already touched this contract.",
      "command_or_source": "Etherscan internal transactions + normal transactions for 0xf8e349d1d827a6edf17ee673664cfad4ca78c533; check for repeated bot callers"
    },
    {
      "name": "access_control_on_value_moving_selectors",
      "reason": "Once selectors are recovered, each value-moving function (withdraw, redeem, claim, sweep, transfer) must be checked for msg.sender guards or merkle-proof requirements.",
      "command_or_source": "Decompile bytecode; attempt dry-run calls with cast call from an unprivileged address on a fork"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting (shares/debt created without matching assets)",
    "proxy or implementation storage mismatch exposing live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or ABI",
      "evidence": "verified_source: null; unknown_verification_status tag present",
      "why_it_matters": "Cannot enumerate callable entrypoints without bytecode decompilation. Any value-moving selector could be ungated."
    },
    {
      "selector_or_function": "ERC20 token transfer inbound",
      "evidence": "stablecoin_balance + known_asset_balance + token_funded_contract tags; TVL $540K",
      "why_it_matters": "Confirms real stablecoin value is held. If a public withdraw/sweep selector exists without access control, funds are directly extractable."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$540K in stablecoins (confirmed by tags)",
      "No verified source — access control on withdrawal paths is unknown",
      "Contract is fresh with an immediate balance spike — no established user base to front-run"
    ],
    "call_sequence": [
      "1. Recover selectors via bytecode decompilation",
      "2. Identify any withdraw(address,uint256), redeem(uint256), claim(), or sweep() selector",
      "3. Check whether selector requires msg.sender == owner or a merkle proof",
      "4. If ungated: call selector with attacker address as recipient on a mainnet fork",
      "5. Assert stablecoin balance transferred to attacker"
    ],
    "expected_gain": "Up to ~$540,091 in stablecoins if a public ungated withdrawal selector exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Ethereum mainnet at current block",
      "Confirm contract balance: cast balance + token balanceOf",
      "Decompile bytecode to recover selectors",
      "Identify value-moving selectors"
    ],
    "transaction_sequence": [
      "vm.startPrank(attacker) — unprivileged EOA",
      "Call recovered withdrawal/sweep selector with attacker as recipient",
      "Assert stablecoin.balanceOf(attacker) > 0 post-call"
    ],
    "expected_assertions": [
      "attacker stablecoin balance increases by contract's held amount",
      "contract stablecoin balance drops to zero",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Summary of why `NEEDS_LIVE_CONTEXT` and not a stronger verdict:**

The scoring signal is real — score 89, $540K stablecoins, Ethereum, balance spike, hidden/unverified contract. [4](#0-3)  However, the hard rules require that source, selectors, proxy/admin state, or transaction evidence be present before promoting to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE`. [5](#0-4)  None of those are available here — `verified_source` is null, `deployer_address` is empty, and no enrichment pass has been run against this address. The six live-context items above are the minimum required before a fork proof attempt is justified.

### Citations

**File:** state/ethereum_chain_scanner.json (L1-10)
```json
{
  "last_scanned_block": 100,
  "seen_contracts": {
    "0x1212121212121212121212121212121212121212": {
      "created_at_ms": null,
      "deployer": "",
      "deployment_tx": "0xtransfer01",
      "discovery_source": "erc20_transfer_log",
      "first_seen_block": 100,
      "last_seen_block": 100,
```

**File:** state/latest_deepwiki_briefs.json (L1-5)
```json
[
  "deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json",
  "deepwiki_briefs/002-bsc-0x5555555555555555555555555555555555555555.json",
  "deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json"
]
```

**File:** HUNT_PLAN.md (L12-18)
```markdown
## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.
```

**File:** HUNT_PLAN.md (L33-58)
```markdown
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

```

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L125-144)
```markdown
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

```