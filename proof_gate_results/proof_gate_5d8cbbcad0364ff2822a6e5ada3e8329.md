<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_d3b4ad5a-3bf1-479c-8b67-033e6ef7dd3a?mode=deep -->

The brief file `deepwiki_briefs/019-bsc-0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d.json` does not exist in the repository — only three placeholder/sample briefs are present.  The address `0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d` appears nowhere in the codebase. The proof gate hard rules require concrete live state; none exists here. [1](#0-0) 

The proof gate schema does not include `NEEDS_LIVE_CONTEXT` as a valid verdict — only `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [2](#0-1)  With every hard gate failing due to absent live context, the correct output is `REJECT`. [3](#0-2) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "bsc",
    "address": "0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d",
    "live_context_source": "none — deepwiki_briefs/019-bsc-0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d.json does not exist in the repository",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": false,
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
    "not_known_duplicate": false
  },
  "live_preconditions": [],
  "attacker_path": {
    "actor": "",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "",
    "attacker_gain": "",
    "victim_or_protocol_loss": "",
    "why_gain_exceeds_entitlement": ""
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "All hard gates fail. The candidate brief file (deepwiki_briefs/019-bsc-0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d.json) does not exist in the repository; the address appears nowhere in the codebase. No source code, verified ABI, selector inventory, proxy state, deployer identity, token breakdown, or transaction history is available. The upstream triage correctly assigned NEEDS_LIVE_CONTEXT. The proof gate cannot form a concrete exploit path — no selector, no code path, no confirmed live state. Return this candidate to the live-recon queue; re-submit to the proof gate only after bytecode recovery, proxy slot check, owner/admin slot check, token balance breakdown, creation-tx trace, and recent transaction pattern analysis are complete."
}
```

### Citations

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** deepwiki_prompts.py (L38-42)
```python
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.
```