<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_c68af2a8-e803-4308-a7c2-7a023327a177?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/003-ethereum-0x390f3595bca2df7d23783dfd126427cceb997bf4.json",
    "chain": "ethereum",
    "address": "0x390f3595bca2df7d23783dfd126427cceb997bf4",
    "name": "0x390f3595bca2df7d23783dfd126427cceb997bf4",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh unverified Ethereum contract holding ~$26M in stablecoins with an immediate balance spike. The combination of hidden_high_value_contract, unknown_verification_status, and stablecoin_balance tags indicates a live custody surface with no public source, no known selectors, and no deployer attribution — exactly the profile of a contract that may conceal value-moving paths from public review.",
  "live_context_required": [
    {
      "name": "verified_source_or_decompiled_bytecode",
      "reason": "Contract is unverified (verified_source: null). Without source or decompiled bytecode, no selectors, access control logic, or value-moving paths can be assessed. This is the single hardest blocker.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0x390f3595bca2df7d23783dfd126427cceb997bf4&apikey=$ETHERSCAN_KEY'; or: cast etherscan-source 0x390f3595bca2df7d23783dfd126427cceb997bf4 --chain mainnet; fallback: heimdall decompile $(cast code 0x390f3595bca2df7d23783dfd126427cceb997bf4 --rpc-url $ETH_RPC_URL)"
    },
    {
      "name": "public_selector_enumeration",
      "reason": "No ABI or selector list is present. Value-moving functions (withdraw, redeem, claim, sweep, migrate, transfer) cannot be identified or tested without selector recovery.",
      "command_or_source": "python3 -c \"import requests; bc=requests.get('https://api.etherscan.io/api?module=proxy&action=eth_getCode&address=0x390f3595bca2df7d23783dfd126427cceb997bf4&apikey=$ETHERSCAN_KEY').json()['result']; print(bc[:200])\"; then match 4-byte prefixes against https://www.4byte.directory/api/v1/signatures/?hex_signature=<sig>"
    },
    {
      "name": "proxy_and_implementation_slots",
      "reason": "If this is an EIP-1967 proxy, the implementation contract holds the actual logic. A proxy with live funds and a recently changed or unknown implementation is a direct escalation trigger.",
      "command_or_source": "cast storage 0x390f3595bca2df7d23783dfd126427cceb997bf4 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $ETH_RPC_URL; cast storage 0x390f3595bca2df7d23783dfd126427cceb997bf4 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $ETH_RPC_URL"
    },
    {
      "name": "deployer_address_and_funding_cluster",
      "reason": "Deployer field is empty. Deployer identity can reveal closed-project redeployment, rug-pattern reuse, or known-unsafe code lineage — all of which are direct score escalators per sentinel scoring rules.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0x390f3595bca2df7d23783dfd126427cceb997bf4&apikey=$ETHERSCAN_KEY'"
    },
    {
      "name": "token_balances_and_stablecoin_addresses",
      "reason": "Tags confirm stablecoin_balance and known_asset_balance but specific token contract addresses and exact amounts are not enumerated. Exact asset custody determines the extraction surface and victim pool.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=tokenlist&address=0x390f3595bca2df7d23783dfd126427cceb997bf4&apikey=$ETHERSCAN_KEY'; then: cast call <token_address> 'balanceOf(address)(uint256)' 0x390f3595bca2df7d23783dfd126427cceb997bf4 --rpc-url $ETH_RPC_URL"
    },
    {
      "name": "recent_transaction_and_event_history",
      "reason": "No transaction patterns, depositor count, or withdrawal activity is known. Transaction history distinguishes user-deposit custody (high extraction value) from single-funder treasury (lower unprivileged extraction surface).",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=txlist&address=0x390f3595bca2df7d23783dfd126427cceb997bf4&sort=asc&apikey=$ETHERSCAN_KEY'; cast logs --address 0x390f3595bca2df7d23783dfd126427cceb997bf4 --from-block earliest --rpc-url $ETH_RPC_URL"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, claim, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds",
    "phantom accounting where shares or debt are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — source unverified, no ABI available",
      "evidence": "verified_source: null; tags include unknown_verification_status and audit_hidden_contract; no selector data in candidate brief or any state file in the repository",
      "why_it_matters": "Any value-moving function could be public and caller-unchecked. Without selector recovery, no exploit family can be confirmed or ruled out."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$26M in stablecoins confirmed by live balance tags (stablecoin_balance, known_asset_balance, high_token_balance)",
      "Source is unverified — access control on any withdrawal, claim, or sweep function is unknown",
      "No deployer or funding cluster attribution — contract origin and code lineage are opaque",
      "Immediate balance spike pattern suggests funds arrived in a short window, consistent with a custody or distribution contract"
    ],
    "call_sequence": [
      "1. Recover bytecode via eth_getCode and decompile to enumerate 4-byte selectors",
      "2. Match selectors against known withdraw/redeem/claim/sweep/transfer signatures",
      "3. Identify any public selector that moves tokens to a caller-controlled address without an ownership or allowance check",
      "4. Call that selector from an unprivileged EOA with attacker address as recipient",
      "5. Receive stablecoin balance from contract"
    ],
    "expected_gain": "Up to ~$26M in stablecoins if a public unchecked value-moving selector exists — entirely unconfirmed without source or selector data"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Ethereum mainnet at current block with ETH_RPC_URL",
      "Confirm exact stablecoin token addresses and balances held by 0x390f3595bca2df7d23783dfd126427cceb997bf4",
      "Decompile bytecode and recover all 4-byte selectors",
      "Check EIP-1967 proxy slots; if proxy, fetch and decompile implementation",
      "Identify any withdraw/redeem/claim/sweep/transfer selector with no msg.sender restriction"
    ],
    "transaction_sequence": [
      "vm.startPrank(attacker) — fresh unprivileged EOA with no prior interaction",
      "Call identified value-moving selector with attacker as recipient argument",
      "Assert no revert",
      "Assert attacker stablecoin balance > 0"
    ],
    "expected_assertions": [
      "IERC20(stablecoin).balanceOf(attacker) > 0 after call",
      "IERC20(stablecoin).balanceOf(0x390f3595bca2df7d23783dfd126427cceb997bf4) decreased by attacker gain",
      "Call did not revert with access control error"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate scores `NEEDS_LIVE_CONTEXT` — not `REJECT` and not `NEEDS_LOCAL_PROOF` — for the following reasons:

**Why not REJECT:** The signal profile is genuinely interesting. ~$26M in stablecoins, a fresh unverified contract, an immediate balance spike, and the `hidden_high_value_contract` + `audit_hidden_contract` tag combination are exactly the pattern the hunt plan targets. [1](#0-0)  Rejecting on speculation alone would violate the "prefer REJECT over speculation" rule in the opposite direction — the rule means don't speculate toward a positive verdict, not that interesting unknowns should be discarded.

**Why not NEEDS_LOCAL_PROOF:** The brief contains zero source code, zero selectors, zero deployer data, zero proxy state, and zero transaction history. [2](#0-1)  Every field that would justify a local proof attempt is absent. A fork test cannot be written without at least one confirmed value-moving selector.

**Blocking gap:** `verified_source: null` combined with no ABI means the entire selector surface is dark. The `recon_bravo_then_corecritical` route requires normal protocol recon first, which means bytecode recovery and selector enumeration are the mandatory first step before any proof work. [3](#0-2)

### Citations

**File:** HUNT_PLAN.md (L59-67)
```markdown
## Triage Rule

Score only protocols that satisfy at least one of these:

1. user funds are already deposited on-chain
2. there is a live reward pool or claimable emission
3. there is a public withdraw/redeem/claim path
4. the protocol is newly deployed, unverified, or forked from a risky pattern
5. a bot or executor repeatedly reveals the same target path
```

**File:** HUNT_PLAN.md (L76-84)
```markdown

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy
```

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L370-384)
```markdown
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
```