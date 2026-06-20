<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_0c0f3728-e8fa-438d-b7e4-7801787fb507?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0xe5ce5bc4785cd2a246151364f5a190cee3fdb142",
    "live_context_source": "candidate brief only — no separate live context provided",
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
    "Contract bytecode must be fetched and decompiled to enumerate public selectors — not yet done.",
    "Proxy implementation address must be resolved (EIP-1967 slot check) — not yet done.",
    "Token holdings must be identified to confirm the $366K TVL denomination and withdrawal path — not yet done.",
    "Deployer and transaction history must be reviewed to distinguish a live multi-user protocol from a single-EOA honeypot — not yet done.",
    "Owner/admin storage slot must be read to determine whether privileged guards are effectively absent — not yet done."
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token identity not confirmed",
    "attacker_gain": "unknown — no selector confirmed",
    "victim_or_protocol_loss": "unknown — no call path confirmed",
    "why_gain_exceeds_entitlement": "cannot be evaluated without a confirmed selector and entitlement model"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Hard gate exact_code_path_or_selector_exists fails. The contract at 0xe5ce5bc4785cd2a246151364f5a190cee3fdb142 is unverified (verified_source: null). No bytecode decompilation has been performed, no public selectors have been identified, and no live context was supplied. Without at least one confirmed value-moving selector callable by an unprivileged address, the gate question cannot be answered affirmatively. Five blocking live-context steps remain outstanding: bytecode decompilation, proxy implementation resolution, token balance identification, deployer/transaction history review, and access-control slot read. Re-submit after those steps complete and a concrete selector is confirmed."
}
```

**Why REJECT and not NEEDS_LOCAL_PROOF:**

The `proof-gate-v1` schema only permits `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0)  `NEEDS_LIVE_CONTEXT` is a triage-stage verdict only. [2](#0-1) 

`NEEDS_LOCAL_PROOF` requires enough source, selector, balance, or transaction evidence for a local proof attempt. [3](#0-2)  None of that evidence exists here — the contract is unverified, no bytecode has been decompiled, and no selectors are known. The hard gate `exact_code_path_or_selector_exists` is definitively false, which alone is sufficient to block promotion. [4](#0-3) 

Per the hunt plan's hard stop rule, a candidate must not be promoted unless a reproducible path and extraction of user funds or excess rewards can be shown. [5](#0-4)  The five outstanding live-context steps from the triage stage must complete before this candidate can re-enter the proof gate.

### Citations

**File:** sentinel_deepwiki_schema.py (L9-9)
```python
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** sentinel_deepwiki_schema.py (L54-54)
```python
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** sentinel_deepwiki_schema.py (L71-71)
```python
        "exact_code_path_or_selector_exists": False,
```

**File:** deepwiki_prompts.py (L40-41)
```python
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** HUNT_PLAN.md (L109-116)
```markdown

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```