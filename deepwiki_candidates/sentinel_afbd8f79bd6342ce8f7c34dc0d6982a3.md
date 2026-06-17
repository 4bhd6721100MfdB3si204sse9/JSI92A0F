<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_80162736-30be-44cb-818b-36f50104ddfa?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0x1715a3e4a142d8b698131108995174f37aeba10d` has no entry in the repository's chain scanner state, no deepwiki brief, and no verified source anywhere in the codebase. The scoring reasons (`unfamiliar_contract:12`, `unknown_verification_status:8`, `hidden_high_value_contract:18`, `balance_spike:20`) are chain-scanner heuristics with no underlying source or selector data to analyze. Without bytecode selectors, deployer identity, or proxy shape, no exploit path can be constructed or rejected on merit.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x1715a3e4a142d8b698131108995174f37aeba10d",
    "name": "0x1715a3e4a142d8b698131108995174f37aeba10d",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified Ethereum contract holding ~$14.87M in stablecoins with an immediate balance spike and no public identity. The combination of hidden_high_value_contract, balance_spike, and unknown_verification_status on a stablecoin-funded address is a high-signal pattern for either a custodial contract with missing access control or a covert protocol with unguarded withdrawal paths. No source, selectors, deployer, or proxy data are available to confirm or reject exploitability.",
  "live_context_required": [
    {
      "name": "bytecode_selectors",
      "reason": "Contract is unverified. Selectors must be recovered from deployed bytecode to identify any public value-moving functions (withdraw, redeem, claim, sweep, transfer, execute). Without selectors, no exploit path can be evaluated.",
      "command_or_source": "cast code 0x1715a3e4a142d8b698131108995174f37aeba10d --rpc-url $ETH_RPC | heimdall decompile --stdin  OR  upload bytecode to dedaub.com/decompile  OR  query 4byte.directory for recovered selectors"
    },
    {
      "name": "deployer_and_deployment_tx",
      "reason": "Deployer address and deployment transaction are both empty in the brief. Deployer identity is needed to trace funding origin, identify related contracts, and assess whether this is a rug-redeploy or known-bad cluster.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) | grep contractAddress) --rpc-url $ETH_RPC  OR  Etherscan API: https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0x1715a3e4a142d8b698131108995174f37aeba10d"
    },
    {
      "name": "token_balances_and_token_addresses",
      "reason": "Tags confirm stablecoin_balance and high_token_balance but no token addresses are listed. Need exact token contracts and amounts to confirm $14.87M TVL composition and identify which assets are at risk.",
      "command_or_source": "Etherscan token holdings tab: https://etherscan.io/address/0x1715a3e4a142d8b698131108995174f37aeba10d#tokentxns  OR  cast call <token> 'balanceOf(address)(uint256)' 0x1715a3e4a142d8b698131108995174f37aeba10d --rpc-url $ETH_RPC"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Hidden high-value contracts are frequently transparent or UUPS proxies. If an implementation slot is set, the implementation contract may be separately verifiable or have a different access control surface.",
      "command_or_source": "cast storage 0x1715a3e4a142d8b698131108995174f37aeba10d 0x360894a13ba1a3210667c828492db98dca3e2076ecc42df388eaa5cf4d00edd --rpc-url $ETH_RPC  AND  cast storage 0x1715a3e4a142d8b698131108995174f37aeba10d 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c --rpc-url $ETH_RPC"
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "reason": "balance_spike and immediate_balance_spike tags indicate funds arrived suddenly. Transaction history reveals whether any outbound calls have occurred, who the callers are, and whether a sweep or drain pattern is already in progress.",
      "command_or_source": "Etherscan internal txns: https://etherscan.io/address/0x1715a3e4a142d8b698131108995174f37aeba10d#internaltx  OR  cast logs --address 0x1715a3e4a142d8b698131108995174f37aeba10d --from-block earliest --rpc-url $ETH_RPC"
    },
    {
      "name": "access_control_owner_or_admin_slot",
      "reason": "If the contract has an owner or admin, knowing whether that slot is set to a known EOA, multisig, or zero address determines whether privileged functions are reachable by an unprivileged caller.",
      "command_or_source": "cast storage 0x1715a3e4a142d8b698131108995174f37aeba10d 0x0 --rpc-url $ETH_RPC  AND  try common owner selectors: cast call 0x1715a3e4a142d8b698131108995174f37aeba10d 'owner()(address)' --rpc-url $ETH_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "proxy implementation mismatch exposing live funds",
    "phantom accounting where tokens are held without tracked shares"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not decompiled",
      "evidence": "verified_source is null; no ABI, no selectors, no source in repository or brief",
      "why_it_matters": "Cannot confirm or reject any exploit family without knowing what public functions exist"
    },
    {
      "selector_or_function": "balance_spike / immediate_balance_spike tags",
      "evidence": "Chain scanner detected a sudden large token inflow to a fresh, unidentified contract",
      "why_it_matters": "Sudden inflow to an unverified contract is consistent with a custodial or escrow pattern where a withdrawal function may exist without caller restrictions"
    },
    {
      "selector_or_function": "stablecoin_balance / known_asset_balance tags",
      "evidence": "Contract holds recognized stablecoin assets worth ~$14.87M",
      "why_it_matters": "Stablecoins are directly extractable if any transfer or withdraw selector is callable without authentication"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes a public or externally callable withdraw/sweep/transfer function",
      "No msg.sender check or the check is bypassable"
    ],
    "call_sequence": [
      "UNKNOWN — selectors must be recovered before a call sequence can be constructed"
    ],
    "expected_gain": "Up to ~$14.87M in stablecoins if an unguarded value-moving selector exists; unquantifiable until bytecode is decompiled"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Pin Ethereum mainnet fork to a recent block where the balance spike is confirmed",
      "Identify token addresses and confirm balances via balanceOf calls",
      "Decompile bytecode and recover all public selectors",
      "Attempt owner()/admin() calls to determine access control state"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot construct transaction sequence without selectors"
    ],
    "expected_assertions": [
      "BLOCKED — cannot assert gain without knowing callable functions"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:** The signal profile (large stablecoin balance, immediate spike, hidden/unverified, Ethereum mainnet) is genuinely interesting and warrants live recon. However, every required input for a proof attempt — selectors, deployer, proxy shape, token list, caller history — is absent from the brief and the repository. `NEEDS_LIVE_CONTEXT` is the only defensible verdict. The six live-context items above are the minimum needed to either promote to `NEEDS_LOCAL_PROOF` or reject. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** sentinel/scoring.py (L102-105)
```python
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
```

**File:** sentinel_deepwiki_schema.py (L7-48)
```python
TRIAGE_CONTRACT: dict[str, Any] = {
    "schema_version": "sentinel-triage-v1",
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "candidate": {
        "source_file": "",
        "chain": "",
        "address": "",
        "name": "",
        "entity_type": "",
        "next_action": "",
        "score": 0,
    },
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "why_this_target_matters": "",
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
    "suspected_exploit_families": [],
    "source_or_selector_basis": [
        {
            "selector_or_function": "",
            "evidence": "",
            "why_it_matters": "",
        }
    ],
    "attacker_path_hypothesis": {
        "actor": "unprivileged external user",
        "preconditions": [],
        "call_sequence": [],
        "expected_gain": "",
    },
    "local_proof_required": {
        "test_type": "fork | unit | invariant | fuzz | manual",
        "setup": [],
        "transaction_sequence": [],
        "expected_assertions": [],
    },
    "rejection_reason": "",
```

**File:** state/ethereum_chain_scanner.json (L1-30)
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
      "last_value_usd": 240000.0,
      "max_value_usd": 240000.0,
      "tags": [
        "fresh_contract_large_balance",
        "fresh_contract_large_token_balance",
        "high_token_balance",
        "high_total_balance",
        "token_funded_contract",
        "unknown_protocol",
        "vault_exchange_rate"
      ],
      "token_addresses": [
        "0x8888888888888888888888888888888888888888"
      ],
      "updated_at_block": 100
    },
    "0x3434343434343434343434343434343434343434": {
      "created_at_ms": null,
      "deployer": "",
      "deployment_tx": "0xtransfer02",
```