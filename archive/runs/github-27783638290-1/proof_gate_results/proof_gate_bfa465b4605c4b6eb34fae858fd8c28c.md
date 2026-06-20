<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_918e69b7-1104-43bf-8f57-d362db8c038a?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35",
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
    "not_dos_grief_or_liveness_only": false,
    "not_admin_governance_or_key_compromise": false,
    "not_external_dependency_only": false,
    "not_expected_behavior": false,
    "not_known_duplicate": true
  },
  "live_preconditions": [],
  "attacker_path": {
    "actor": "unknown — no selector or source basis",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token composition unconfirmed",
    "attacker_gain": "unquantifiable — no value-moving selector identified",
    "victim_or_protocol_loss": "unquantifiable",
    "why_gain_exceeds_entitlement": "cannot be established without a confirmed selector and access-control analysis"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Candidate entered the proof gate with triage verdict NEEDS_LIVE_CONTEXT and zero live data attached. All hard gates that require an exact code path (exact_code_path_or_selector_exists), confirmed preconditions (live_state_supports_preconditions), attacker-controlled trigger (attacker_controls_trigger), and concrete gain (concrete_fund_or_reward_gain, gain_is_beyond_entitlement) are false. No verified source, no recovered selectors, no deployer identity, no proxy/admin slot state, no token breakdown, and no transaction calldata patterns are present. The $8.7M stablecoin balance confirms the target is worth pursuing, but no exploit hypothesis can be formed or gated without first completing the six live-context collection steps listed in the triage output: (1) source code or bytecode selector recovery, (2) EIP-1967/EIP-897 proxy slot reads, (3) ERC-20 token balance enumeration, (4) deployer address and creation tx lookup, (5) recent transaction calldata for selector recovery, (6) owner/admin storage slot reads. Re-submit to the proof gate only after at least steps 1, 2, and 5 are satisfied."
}
```

**Gate outcome: REJECT — missing live context blocks all hard gates.**

The candidate is not rejected on merit. It is rejected because the proof gate cannot evaluate any hard gate without selector, source, proxy, or deployer data. The triage stage correctly flagged `NEEDS_LIVE_CONTEXT`; that work was not completed before this gate was entered.

The six blocking gaps, in priority order:

| # | Gap | Blocking gate |
|---|-----|---------------|
| 1 | No source / no recovered selectors | `exact_code_path_or_selector_exists` |
| 2 | No proxy/implementation slot state | `live_state_supports_preconditions` |
| 3 | No transaction calldata patterns | `attacker_controls_trigger` |
| 4 | No token breakdown | `concrete_fund_or_reward_gain` |
| 5 | No deployer identity | `not_admin_governance_or_key_compromise` |
| 6 | No owner/admin slot reads | `not_admin_governance_or_key_compromise` |

Re-entry path: complete the live-context commands from the triage output (bytecode decompilation via `heimdall`/`whatsabi`, proxy slot reads via `cast storage`, tx calldata pull via Etherscan API), then re-submit to the proof gate with a populated `live_context` block. [1](#0-0)

### Citations

**File:** PLAN.md (L149-155)
```markdown
For unverified funded contracts:

1. Identify native/ERC20 balances and recent depositors.
2. Recover function selectors from transaction calldata.
3. Check proxy slots, delegatecall patterns, and implementation addresses.
4. Cluster privileged callers, deployer, and funders.
5. Promote exploitable value-moving functions into proof work.
```