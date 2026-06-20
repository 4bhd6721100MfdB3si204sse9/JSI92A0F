<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_72a024be-7454-435f-a097-84f0c6d72eac?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "live_context_source": "none — candidate brief only, no RPC or explorer data attached",
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
    "verified_source or decompiled bytecode with recovered public selectors must exist before this gate can be re-entered",
    "at least one selector must be identified that moves tokens or native value without an access check",
    "live balance confirmation via BSC RPC or BscScan token list must show funds still present at evaluation block",
    "proxy slot check (EIP-1967 slot 0x360894...) must be run to determine whether logic address differs from storage address",
    "deployer and funding-path attribution must be resolved to confirm no admin-only withdrawal is the only path"
  ],
  "attacker_path": {
    "actor": "unprivileged external EOA",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token mix unresolved; brief tags stablecoin_balance and known_asset_balance without specifying assets or amounts",
    "attacker_gain": "unquantifiable — no selector exists to route a call through",
    "victim_or_protocol_loss": "unquantifiable",
    "why_gain_exceeds_entitlement": "cannot be evaluated without a confirmed call path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "tests/fork/bsc_0x9996874dbd891c3ecd601eab79d51f92e92d50ee.t.sol",
    "setup": [
      "BSC mainnet fork pinned to current block",
      "ABI recovered from bytecode decompilation (heimdall-rs, panoramix, or whatsabi) — this step must complete before the test file can be written",
      "attacker EOA with no prior relationship to the contract",
      "token balance snapshot of contract before call"
    ],
    "transaction_sequence": [
      "vm.startPrank(attacker)",
      "target.call(abi.encodeWithSelector(recoveredSelector, attacker, type(uint256).max))",
      "assertGt(IERC20(resolvedStablecoin).balanceOf(attacker), 0)"
    ],
    "expected_assertions": [
      "attacker token balance increases after call",
      "contract token balance decreases by matching amount",
      "call does not revert due to access control or ownership check"
    ],
    "reject_if_assertion_fails": "if all recovered selectors revert with access-control errors or no value-moving selector exists, close as REJECT with reason: no_unguarded_withdrawal_path"
  },
  "rejection_reason": "All value-path hard gates fail. verified_source is null and no bytecode decompilation output was attached, so exact_code_path_or_selector_exists is false. Without at least one confirmed public selector that moves value, live_state_supports_preconditions, attacker_controls_trigger, concrete_fund_or_reward_gain, and gain_is_beyond_entitlement are all false. The prior triage stage correctly classified this as NEEDS_LIVE_CONTEXT; it was promoted to the proof gate before the six required live-context steps were completed. Re-enter this gate only after bytecode decompilation yields a confirmed value-moving selector with no access check."
}
```

**Gate outcome: REJECT — premature promotion.**

The candidate arrived at the proof gate still carrying a `NEEDS_LIVE_CONTEXT` blocker. Five of the twelve hard gates fail on the same root cause: `verified_source: null` with no decompiled selector output attached. [1](#0-0) 

The proof gate cannot synthesize selectors or live state. The six `live_context_required` commands from the prior triage stage must be executed first. Once bytecode decompilation produces at least one value-moving selector with no `msg.sender` guard, re-submit with that selector evidence and the gate can be re-evaluated. [2](#0-1)

### Citations

**File:** HUNT_PLAN.md (L12-18)
```markdown
## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.
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