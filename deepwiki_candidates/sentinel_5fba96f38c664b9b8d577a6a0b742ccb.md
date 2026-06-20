<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_dc9da7e7-e031-4c2b-9635-2e48d9c8940e?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0x9996874dbd891c3ecd601eab79d51f92e92d50ee` does not appear anywhere in this repository. The `deepwiki_briefs/` directory contains only three placeholder entries with dummy addresses, and no run output references this contract. The triage below is based solely on the candidate brief provided, applying the schema from `sentinel_deepwiki_schema.py`. [1](#0-0) 

---

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "name": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified fresh contract on BSC holding ~$15.5M in stablecoins and known assets with zero on-chain volume, zero liquidity, and no deployer attribution. The combination of large balance, no source, and no protocol identity is consistent with a custody or escrow contract whose access controls are unknown. Without source or selectors, the attack surface is entirely opaque, but the value concentration alone warrants live recon before the window closes.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "No verified source exists. Raw bytecode must be fetched and run through a decompiler (e.g., heimdall-rs, panoramix, or whatsabi) to recover public selectors and reconstruct function signatures. Without this, no call path can be evaluated.",
      "command_or_source": "cast code 0x9996874dbd891c3ecd601eab79d51f92e92d50ee --rpc-url $BSC_RPC | heimdall decompile --stdin"
    },
    {
      "name": "proxy_slot_check",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If so, the implementation address holds the real logic and may have been recently swapped. A stale or malicious implementation behind a funded proxy is a direct extraction surface.",
      "command_or_source": "cast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags indicate stablecoin_balance and known_asset_balance but do not specify which tokens or amounts. Knowing the exact asset mix (USDT, USDC, BUSD, BNB) determines the realistic extraction ceiling and which transfer paths to test.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0x9996874dbd891c3ecd601eab79d51f92e92d50ee&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "reason": "Zero 24h volume but large balance suggests either a dormant escrow, a recently deployed contract not yet interacted with, or a contract whose interactions are internal/private. Tx history reveals whether any public selectors have been called, who the callers are, and whether a bot has already been sweeping.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x9996874dbd891c3ecd601eab79d51f92e92d50ee&sort=desc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "deployer_address_and_funding_path",
      "reason": "Deployer address is empty in the brief. Identifying the deployer reveals whether this contract is linked to a known protocol, a prior rug cluster, or a fresh anonymous actor. Funding path (which address sent the initial tokens) may reveal intent.",
      "command_or_source": "cast receipt $(cast tx-hash-from-creation 0x9996874dbd891c3ecd601eab79d51f92e92d50ee) --rpc-url $BSC_RPC | grep 'from'"
    },
    {
      "name": "admin_or_owner_slot",
      "reason": "If the contract has an owner or admin role, knowing whether that role is a multisig, an EOA, or address(0) determines whether access-controlled withdrawal functions are relevant to an unprivileged attacker.",
      "command_or_source": "cast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_function",
    "unauthorized_withdrawal_or_sweep",
    "proxy_implementation_mismatch_exposing_live_funds",
    "phantom_accounting_shares_or_debt_without_assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source is null; no ABI, no selector list, no decompiled output available in the brief or repository",
      "why_it_matters": "Cannot evaluate any call path without selectors. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "At least one public selector exists that moves tokens or native value",
      "That selector does not gate on msg.sender == owner or equivalent",
      "Contract holds the ~$15.5M balance directly (not as a pass-through with immediate revert)"
    ],
    "call_sequence": [
      "1. Recover selectors via bytecode decompilation",
      "2. Identify any withdraw(address,uint256), sweep(), claim(), redeem(), or transfer-wrapping function with no access check",
      "3. Call that function with attacker-controlled recipient",
      "4. Receive tokens to attacker address"
    ],
    "expected_gain": "Up to ~$15.5M in stablecoins/known assets if an unguarded withdrawal selector exists. Realistic partial extraction likely if only some token types are unguarded."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recovered ABI from decompilation step",
      "Attacker EOA with no prior relationship to the contract"
    ],
    "transaction_sequence": [
      "vm.startPrank(attacker)",
      "target.call(abi.encodeWithSelector(recoveredSelector, attacker, type(uint256).max))",
      "assertGt(IERC20(stablecoin).balanceOf(attacker), 0)"
    ],
    "expected_assertions": [
      "attacker stablecoin balance increases after call",
      "contract stablecoin balance decreases by matching amount",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

---

**Summary of verdict rationale:**

The candidate is not rejected because the value concentration (~$15.5M stablecoins on a fresh, unverified, zero-volume contract) is a genuine signal worth pursuing. It is not advanced to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because every hard gate is currently blocked by the same root cause: `verified_source: null` with no selector evidence. [2](#0-1) 

The six `live_context_required` items above are the minimum needed to unblock the next triage stage. If bytecode decompilation yields an unguarded value-moving selector, this candidate should be immediately re-triaged as `NEEDS_LOCAL_PROOF` with a BSC fork test. [3](#0-2)

### Citations

**File:** sentinel_deepwiki_schema.py (L7-49)
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
}
```

**File:** sentinel_deepwiki_schema.py (L66-78)
```python
    "hard_gates": {
        "current_live_target_only": False,
        "live_state_supports_preconditions": False,
        "unprivileged_attacker": False,
        "attacker_controls_trigger": False,
        "exact_code_path_or_selector_exists": False,
        "concrete_fund_or_reward_gain": False,
        "gain_is_beyond_entitlement": False,
        "not_dos_grief_or_liveness_only": False,
        "not_admin_governance_or_key_compromise": False,
        "not_external_dependency_only": False,
        "not_expected_behavior": False,
        "not_known_duplicate": False,
```

**File:** HUNT_PLAN.md (L12-18)
```markdown
## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.
```