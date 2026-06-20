<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_49707462-d6f5-4060-af9c-b05dc9760835?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

Based on the candidate brief and repository context, the contract has no verified source, no deployer, no selectors, and no protocol identity — only a massive TVL spike. The hard rules require `NEEDS_LIVE_CONTEXT` here: the value is real and the tags are high-signal, but no exploit path can be hypothesized without bytecode, selectors, or source.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/ethereum-0x01989c93890aed05a63d179b03424997075b6acf.json",
    "chain": "ethereum",
    "address": "0x01989c93890aed05a63d179b03424997075b6acf",
    "name": "0x01989c93890aed05a63d179b03424997075b6acf",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified Ethereum contract with ~$4.07B TVL and an immediate balance spike. No deployer, no source, no selectors, and no protocol identity are on record. The combination of hidden_high_value_contract + balance_spike + unknown_verification_status on a contract of this size is the highest-priority recon signal in the Sentinel scoring model. If any public value-moving selector exists without access control, the exposure is catastrophic.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "No ABI or function selectors are known. Bytecode must be fetched and decompiled (e.g., via Heimdall, Panoramix, or 4byte.directory lookup) to identify any public withdraw, redeem, claim, sweep, transfer, or migrate selectors before any exploit hypothesis can be formed.",
      "command_or_source": "cast code 0x01989c93890aed05a63d179b03424997075b6acf --rpc-url $ETH_RPC | heimdall decompile --stdin"
    },
    {
      "name": "proxy_and_implementation_detection",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If so, the implementation address holds the actual logic and may be separately unverified or point to a known vulnerable contract.",
      "command_or_source": "cast storage 0x01989c93890aed05a63d179b03424997075b6acf 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "deployer_address_and_funding_source",
      "reason": "deployer_address is empty in the brief. The deployer identity and the funding transaction chain are required to determine whether this is a known-protocol escrow, a bridge relay, a rug-redeploy, or a novel custody contract.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) --rpc-url $ETH_RPC) --rpc-url $ETH_RPC  # or Etherscan creation tx lookup for 0x01989c93890aed05a63d179b03424997075b6acf"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The brief reports token_funded_contract and high_token_balance but does not identify which tokens or amounts. The specific token(s) determine whether the balance is user principal, protocol-owned liquidity, or a bridge escrow — each implying a different exploit surface.",
      "command_or_source": "Etherscan token holdings tab for 0x01989c93890aed05a63d179b03424997075b6acf, or DeFiLlama /protocol endpoint if the contract is indexed."
    },
    {
      "name": "recent_transaction_history_and_caller_set",
      "reason": "Zero volume24h_usd but a large balance spike implies funds arrived and have not moved. Inspecting the inbound transactions reveals whether this is a one-time deposit (bridge, escrow, multisig) or an active pool. Outbound calls reveal which selectors are live and whether bots are already probing it.",
      "command_or_source": "Etherscan internal transactions + normal transactions for 0x01989c93890aed05a63d179b03424997075b6acf, last 500 txns."
    },
    {
      "name": "etherscan_verification_and_source_code",
      "reason": "verified_source is null (not false — status is unknown). A direct Etherscan API check may reveal partial or full source that the Sentinel enrichment pass missed.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0x01989c93890aed05a63d179b03424997075b6acf&apikey=$ETHERSCAN_KEY'"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_shares_without_assets",
    "proxy_implementation_storage_mismatch"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI available",
      "evidence": "verified_source is null; no selectors have been extracted from bytecode in this pass.",
      "why_it_matters": "Without selectors, no exploit path can be confirmed or rejected. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "At least one public selector exists that moves tokens or ETH out of the contract.",
      "That selector does not enforce msg.sender == owner or equivalent access control.",
      "The ~$4.07B token balance is withdrawable by an arbitrary caller or by a caller who can satisfy a weak precondition (e.g., holding any amount of a share token)."
    ],
    "call_sequence": [
      "UNKNOWN — call sequence cannot be constructed until selectors are extracted from bytecode."
    ],
    "expected_gain": "Up to ~$4.07B in token value if a public unrestricted sweep or withdraw selector exists. Actual gain depends on token identity and liquidity."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Ethereum mainnet at the block where the balance spike occurred.",
      "Load the contract bytecode and decompiled ABI into the test environment.",
      "Identify the token(s) held and their Etherscan-confirmed balances.",
      "Construct an attacker EOA with no prior relationship to the contract."
    ],
    "transaction_sequence": [
      "BLOCKED — transaction sequence cannot be specified until live context (selectors, source) is retrieved."
    ],
    "expected_assertions": [
      "assertGt(token.balanceOf(attacker), 0) after calling the suspected sweep/withdraw selector.",
      "assertEq(token.balanceOf(contract), 0) or materially reduced after the call.",
      "No revert due to access control."
    ]
  },
  "rejection_reason": ""
}
```

**Why `NEEDS_LIVE_CONTEXT` and not `REJECT`:**

The brief has five simultaneous high-signal tags (`balance_spike`, `immediate_balance_spike`, `hidden_high_value_contract`, `audit_hidden_contract`, `unknown_verification_status`) on a contract with ~$4B TVL and zero volume. That pattern — large silent balance, no public identity, unverified — is exactly the shape of an unguarded escrow or a custody contract with a missing access check. The `HUNT_PLAN.md` scoring bias explicitly elevates "recent deployment with no verified source" and "sudden liquidity spike around an unknown protocol." [1](#0-0) 

The blocker is purely informational: without bytecode selectors or source, the gate question cannot be answered in either direction. [2](#0-1) 

The six `live_context_required` items above are the minimum needed to advance this to `NEEDS_LOCAL_PROOF` or `REJECT`. [3](#0-2)

### Citations

**File:** HUNT_PLAN.md (L12-18)
```markdown
## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.
```

**File:** HUNT_PLAN.md (L99-106)
```markdown

- high TVL or high pooled balances
- active reward emissions
- recent deployment with no verified source
- proxy/admin-controlled value movement
- repeated bot interaction
- closed-project redeploy patterns
- sudden price/liquidity spikes around a new or unknown protocol
```

**File:** sentinel_deepwiki_schema.py (L21-27)
```python
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
```