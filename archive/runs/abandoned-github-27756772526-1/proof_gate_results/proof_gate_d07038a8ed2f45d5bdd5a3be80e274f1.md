<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_101c341d-7958-4843-ad7f-39b4137777e3?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0x72a19342e8f1838460ebfccef09f6585e32db86e",
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
    "Verified source or decompiled bytecode with recovered selectors must be obtained before any precondition can be evaluated",
    "Proxy implementation slot (EIP-1967: 0x3608...2076) must be read to determine whether logic lives at a different address",
    "Admin/owner slot must be read to determine whether privileged roles are renounced or held by an EOA",
    "Token balance breakdown must be confirmed to identify which ERC-20(s) are held and in what amounts",
    "Deployment transaction and funding source must be traced to establish protocol identity",
    "Full transaction history must be reviewed to confirm the balance spike is real and no sweep has already occurred"
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token identity unconfirmed; ~$64.6M TVL reported but token(s) not identified",
    "attacker_gain": "unquantifiable — no selector or code path exists in available context",
    "victim_or_protocol_loss": "unquantifiable",
    "why_gain_exceeds_entitlement": "cannot be evaluated without a confirmed public drain path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "test/ForkDrain_0x72a1.t.sol",
    "setup": [
      "Fork Ethereum mainnet at current block",
      "Run heimdall-rs or panoramix against 0x72a19342e8f1838460ebfccef09f6585e32db86e to recover 4-byte selectors",
      "Read EIP-1967 impl slot (0x360894a13ba1a3210667c828492db98dca3e2076) — if non-zero, repeat decompilation on implementation address",
      "Read admin slot (0xb53127684a568b3173ae13b9f8a6016e243e63b6) and slot 0 to determine owner/admin state",
      "Enumerate token balances via Etherscan holdings tab or balanceOf calls",
      "Confirm balance spike is current and no prior sweep transaction has already drained the contract"
    ],
    "transaction_sequence": [
      "vm.prank(attacker)",
      "(bool ok,) = target.call(abi.encodeWithSelector(<recovered_drain_selector>, attacker));",
      "assertTrue(ok);"
    ],
    "expected_assertions": [
      "token.balanceOf(attacker) > 0 after call",
      "token.balanceOf(target) decreases by matching amount",
      "No revert due to access control or caller validation"
    ],
    "reject_if_assertion_fails": "If every recovered selector reverts with access-control errors for an unprivileged caller, or if no withdraw/claim/sweep-like selector exists in the bytecode, reject as unconfirmed speculation."
  },
  "rejection_reason": "Five of twelve hard gates are false. No verified source exists, no selectors have been recovered, no proxy or admin state has been read, and no live context was provided. The gate question cannot be answered — affirmatively or negatively — without at minimum bytecode decompilation and a proxy/admin slot read. The triage verdict of NEEDS_LIVE_CONTEXT has not been resolved; promoting to NEEDS_LOCAL_PROOF or HIGH_CONFIDENCE_CANDIDATE requires the six live-context items listed in the prior triage pass. Reject at this gate; re-submit with live context attached."
}
```

**Gate outcome:** `REJECT` — not because the target is low-value or uninteresting, but because the proof gate's hard requirements cannot be satisfied with the current evidence.

The blocking gates are:

| Gate | Status | Reason |
|---|---|---|
| `live_state_supports_preconditions` | false | No live context provided |
| `unprivileged_attacker` | false | No selector confirmed as callable by unprivileged caller |
| `attacker_controls_trigger` | false | No selector recovered from bytecode |
| `exact_code_path_or_selector_exists` | false | `verified_source: null`, no decompilation output |
| `concrete_fund_or_reward_gain` | false | No confirmed drain path |
| `gain_is_beyond_entitlement` | false | Follows from above |

The six `live_context_required` items from the triage pass must be completed and re-submitted before this gate can be re-evaluated. The proof gate schema [1](#0-0)  does not include `NEEDS_LIVE_CONTEXT` as a valid output verdict — the only correct output when hard gates are unresolvable is `REJECT`. [2](#0-1)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** deepwiki_prompts.py (L37-42)
```python
- Attacker must be unprivileged.
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.
```