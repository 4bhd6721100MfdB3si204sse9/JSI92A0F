<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_36955098-7e47-4860-b875-3f9251819dcb?mode=deep -->

The proof gate schema (`PROOF_GATE_CONTRACT` in `sentinel_deepwiki_schema.py`) only permits three verdicts: `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0)  `NEEDS_LIVE_CONTEXT` is a triage-stage verdict only and cannot pass through the proof gate. [2](#0-1) 

Per the hard rules, `NEEDS_LOCAL_PROOF` requires "enough source, selector, balance, or transaction evidence for a local proof attempt" — none of which exist here. [3](#0-2)  The `HUNT_PLAN.md` hard stop requires a proven unprivileged attacker, reproducible path, and gain beyond entitlement before promotion. [4](#0-3) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "live_context_source": "none — no live context file provided",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": true,
    "live_state_supports_preconditions": false,
    "unprivileged_attacker": false,
    "attacker_controls_trigger": false,
    "exact_code_path_or_selector_exists": false,
    "concrete_fund_or_reward_gain": false,
    "gain_is_beyond_entitlement": false,
    "not_dos_grief_or_liveness_only": true,
    "not_admin_governance_or_key_compromise": true,
    "not_external_dependency_only": true,
    "not_expected_behavior": true,
    "not_known_duplicate": true
  },
  "live_preconditions": [
    "Verified source or decompiled bytecode with enumerated public selectors must exist",
    "At least one selector must be identified that moves tokens or native value without access control",
    "Proxy implementation slot (EIP-1967 or EIP-897) must be checked and resolved if present",
    "Deployer address and funding trace must be confirmed",
    "Token balance breakdown (exact assets and amounts) must be confirmed on-chain",
    "Recent transaction history must be reviewed to confirm no sweep is already in progress"
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — stablecoin and native token balance inferred from tags only; no token identity or exact amounts confirmed",
    "attacker_gain": "unquantifiable — no selector or entrypoint identified",
    "victim_or_protocol_loss": "unquantifiable — no confirmed custodial relationship or depositor set",
    "why_gain_exceeds_entitlement": "cannot be stated — no source, ABI, or selector exists to establish any entitlement model"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "foundry_targets/bsc-0x28e2ea090877bf75740558f6bfb36a5ffee9e9df/ExploitTest.t.sol",
    "setup": [
      "Fork BSC mainnet at current block",
      "Decompile bytecode via heimdall-rs or Dedaub to enumerate public selectors",
      "Resolve proxy implementation slot 0x360894a13ba1a3210667c828492db98dca3e2076 and slot 0x0 (owner)",
      "Confirm token balances: token.balanceOf(target) for USDT, USDC, BUSD; address(target).balance for BNB",
      "Load decompiled ABI or manually craft calldata for any withdraw/claim/sweep selector found"
    ],
    "transaction_sequence": [
      "vm.prank(attacker) — call suspected withdrawal selector with attacker as recipient",
      "Assert attacker token balance increased",
      "Assert contract token balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker.balance > 0 after call",
      "contract.balance reduced by attacker gain",
      "call does not revert when msg.sender is an unprivileged EOA"
    ],
    "reject_if_assertion_fails": "If every value-moving selector reverts for an unprivileged caller, or if no such selector exists after full bytecode enumeration, reject permanently."
  },
  "rejection_reason": "The proof gate cannot be satisfied without live context. No verified source, no selectors, no deployer, no proxy state, and no transaction history were provided. The six hard gates that require live evidence (live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, concrete_fund_or_reward_gain, gain_is_beyond_entitlement) are all false. The candidate holds a real balance signal ($18.4M TVL) and is not rejected for lack of value — it is rejected at this gate because the proof gate requires a reproducible path against live or fork state, and no such path can be constructed without first completing the six live-context items listed in the triage output. Re-submit to the proof gate after bytecode decompilation, selector enumeration, proxy resolution, and balance confirmation are complete."
}
```

**Gate summary:** All six evidence-dependent hard gates are `false`. [5](#0-4)  The balance signal is real and the candidate is not permanently dead — it must complete the `live_context_required` steps from the triage stage before re-entering this gate. [6](#0-5)

### Citations

**File:** sentinel_deepwiki_schema.py (L54-54)
```python
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** sentinel_deepwiki_schema.py (L66-79)
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
    },
```

**File:** deepwiki_prompts.py (L38-41)
```python
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** HUNT_PLAN.md (L75-84)
```markdown
## Evidence Required

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy
```

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```