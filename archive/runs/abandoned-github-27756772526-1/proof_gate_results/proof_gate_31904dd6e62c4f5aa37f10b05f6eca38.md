<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_586c60a1-98ec-4f86-891a-1cafadb299e1?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9",
    "live_context_source": "deepwiki_briefs/bsc-0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9.json",
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
    "verified_source or recovered bytecode selectors must be available before any exploit family can be confirmed",
    "at least one public value-moving selector (withdraw, sweep, claim, transfer variant) must exist and be identified",
    "that selector must have no meaningful access control guarding it",
    "contract must not be a honeypot that reverts on non-owner callers after appearing callable",
    "token identity and balance composition must be confirmed to establish real asset value at risk"
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token identity not confirmed; brief reports ~$284,725 high_token_balance tag only",
    "attacker_gain": "unquantifiable — no selector, no ABI, no source; no entry point confirmed",
    "victim_or_protocol_loss": "unquantifiable — same blocker",
    "why_gain_exceeds_entitlement": "cannot be asserted without a confirmed code path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "foundry_targets/test/LiveStateProof_bsc_0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9.t.sol",
    "setup": [
      "BSC mainnet fork at current block",
      "Recover 4-byte selectors from bytecode: cast code 0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9 --rpc-url $BSC_RPC | python3 -c \"import sys,re; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(0,len(b)-8,2) if re.match(r'[0-9a-f]{8}',b[i:i+8])]\" | sort -u",
      "Check EIP-1967 proxy slot: cast storage 0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC",
      "Identify held tokens via BscScan ERC-20 transfer events",
      "Probe owner/admin: cast call 0x7f9bd73e51e66e0b2c7a87db0ca530a11eb7a7e9 'owner()(address)' --rpc-url $BSC_RPC",
      "Trace deployer and funding cluster via BscScan 'Contract Creator' field"
    ],
    "transaction_sequence": [
      "Only constructable after selector recovery — no sequence can be specified without a confirmed entry point"
    ],
    "expected_assertions": [
      "attacker.balance(token) > 0 after call",
      "contract.balance(token) < pre-call value",
      "tx does not revert"
    ],
    "reject_if_assertion_fails": "If no unguarded value-moving selector is found after full bytecode analysis, or if every candidate selector reverts for unprivileged callers, reject permanently."
  },
  "rejection_reason": "Hard gates 'live_state_supports_preconditions', 'unprivileged_attacker', 'attacker_controls_trigger', 'exact_code_path_or_selector_exists', 'concrete_fund_or_reward_gain', and 'gain_is_beyond_entitlement' are all false. No live context was supplied to this gate pass. verified_source is null, no selectors or ABI are known, and no deployer or proxy state has been resolved. The triage verdict of NEEDS_LIVE_CONTEXT has not been resolved before this gate was invoked. The proof gate schema does not include NEEDS_LIVE_CONTEXT as a valid output verdict; the correct gate output is REJECT until the five live_context_required steps from triage are completed and re-submitted with a populated live context block. Re-queue after: (1) bytecode selector extraction, (2) proxy slot check, (3) token balance composition, (4) deployer trace, (5) owner/admin probe."
}
```

**Gate rationale (non-JSON summary):**

The proof gate schema (`PROOF_GATE_CONTRACT` in `sentinel_deepwiki_schema.py`) does not carry `NEEDS_LIVE_CONTEXT` as a valid verdict — only `REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0) 

Six of the twelve hard gates fail simultaneously. The blocking condition is that `verified_source` is `null` and no live context block was provided to this gate invocation, so `exact_code_path_or_selector_exists`, `attacker_controls_trigger`, `concrete_fund_or_reward_gain`, `gain_is_beyond_entitlement`, `live_state_supports_preconditions`, and `unprivileged_attacker` cannot be set to `true`. [2](#0-1) 

Per the hard rules in `deepwiki_prompts.py`, `NEEDS_LIVE_CONTEXT` is a triage-stage verdict, not a proof-gate verdict. The gate must `REJECT` and re-queue the candidate after the five live recon steps listed in `live_context_required` are executed and their output is attached as a populated live context block. [3](#0-2)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
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