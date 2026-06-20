<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_ac9c1000-412c-4eb6-8c90-e27ac9f9794e?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0xabe0e16758e0ec57848a092285ace3b384c58d88",
    "live_context_source": "none — no live context file provided",
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
    "not_dos_grief_or_liveness_only": true,
    "not_admin_governance_or_key_compromise": true,
    "not_external_dependency_only": true,
    "not_expected_behavior": true,
    "not_known_duplicate": true
  },
  "live_preconditions": [
    "Bytecode must be recovered and selectors decoded via 4byte.directory or decompiler (Dedaub, Panoramix, Heimdall) before any value-moving function can be identified",
    "EIP-1967 / EIP-897 proxy implementation slot must be checked — real logic may reside at a different address",
    "Token balance breakdown must confirm which assets constitute the reported ~$11.3 M TVL and whether they are transferable by the contract",
    "Transaction history must confirm at least one public selector has been called by an external EOA, ruling out a pure honeypot or owner-only contract",
    "Deployer funding chain must be traced to determine whether this contract belongs to a known protocol cluster or a pattern of draining sister contracts"
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token composition of ~$11.3 M TVL not confirmed",
    "attacker_gain": "unknown — no value-moving selector identified",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "unknown — no entitlement logic recoverable without source or ABI"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "All exploit-critical hard gates fail. The contract is unverified (verified_source: null), no ABI or selector list exists anywhere in the repository, and no live context file was supplied. The proof-gate schema requires exact_code_path_or_selector_exists, live_state_supports_preconditions, attacker_controls_trigger, concrete_fund_or_reward_gain, and gain_is_beyond_entitlement to all be true before a non-REJECT verdict is possible. None of these can be evaluated without first completing the five live_context_required recon steps carried forward from the prior NEEDS_LIVE_CONTEXT triage verdict. Per HUNT_PLAN.md hard stop: do not report a candidate unless the proof shows an unprivileged attacker, a reproducible path, extraction of user funds or excess rewards, and gain beyond entitlement. None of those conditions are met. Re-submit after bytecode recovery, selector decoding, proxy-slot inspection, balance breakdown, and transaction-history analysis are complete."
}
```

**Gate outcome summary:**

Seven of the twelve hard gates are `false`. The five that pass (`not_dos_grief_or_liveness_only` through `not_known_duplicate`) are trivially true only because there is no evidence of anything — they cannot carry the verdict.

The blocking gates and what is needed to clear each:

| Blocked gate | What clears it |
|---|---|
| `exact_code_path_or_selector_exists` | Bytecode decompilation + selector recovery |
| `live_state_supports_preconditions` | Live context file with confirmed balances and callable selectors |
| `attacker_controls_trigger` | At least one public value-moving selector callable by an EOA |
| `concrete_fund_or_reward_gain` | Confirmed token amounts moveable via the exploit path |
| `gain_is_beyond_entitlement` | Entitlement logic recovered from source or decompiled output |

The prior triage correctly assigned `NEEDS_LIVE_CONTEXT`. The proof gate cannot advance past `REJECT` until all five `live_context_required` recon steps from that triage are completed and their outputs are attached as a live context file. [1](#0-0) [2](#0-1)

### Citations

**File:** HUNT_PLAN.md (L110-115)
```markdown
Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement
```

**File:** sentinel_deepwiki_schema.py (L52-79)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "gate_question": (
        "Does this exact current protocol, with current live state, allow an "
        "unprivileged attacker to extract funds or rewards beyond entitlement?"
    ),
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "active_target": {
        "chain": "",
        "address": "",
        "live_context_source": "",
        "live_context_is_current": False,
    },
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