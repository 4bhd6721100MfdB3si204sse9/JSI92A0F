<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_57125ff2-f50b-4c02-bdd5-be5e38ce9a67?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0x61ed017468c8a3be3bac972b54fdae6eafcbcd79",
    "live_context_source": "explorer_snapshot (triage brief only — no Stage 3 live enrichment file present)",
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
    {
      "name": "real_token_value_confirmed",
      "status": "UNMET",
      "reason": "fdv_usd=0 and liquidity_usd=0 alongside a reported TVL of ~$314B is the canonical phantom-value signature. value_at_risk() returns max(liquidity_usd, tvl_usd), but the TVL figure is almost certainly a token-count multiplied by a stale or fabricated price. No token address, no balanceOf call, and no real on-chain liquidity figure has been provided. Extractable value is unconfirmed.",
      "required_command": "cast call 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79 'token()' --rpc-url $ETH_RPC; cast call 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79 'asset()' --rpc-url $ETH_RPC; check Etherscan token holdings tab"
    },
    {
      "name": "bytecode_selectors_enumerated",
      "status": "UNMET",
      "reason": "verified_source=null. No ABI, no selector list, no decompiled output. Without selectors, exact_code_path_or_selector_exists cannot be true and attacker_controls_trigger cannot be assessed.",
      "required_command": "cast code 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79 --rpc-url $ETH_RPC | heimdall decompile; or dedaub.com / ethervm.io"
    },
    {
      "name": "proxy_implementation_resolved",
      "status": "UNMET",
      "reason": "EIP-1967 implementation slot and admin slot have not been read. If this is a proxy, the logic contract may differ from the storage contract and may have separate access control.",
      "required_command": "cast storage 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $ETH_RPC; cast storage 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $ETH_RPC"
    },
    {
      "name": "deployer_and_funding_chain_identified",
      "status": "UNMET",
      "reason": "deployer_address is empty. Cluster risk (rug redeploy, closed-project redeploy) cannot be assessed. Funding source is unknown.",
      "required_command": "Etherscan contract creation tx for 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79; cast tx <creation_tx> --rpc-url $ETH_RPC"
    },
    {
      "name": "transaction_history_reviewed",
      "status": "UNMET",
      "reason": "volume24h_usd=0 but prior inflows may exist. No internal tx or token transfer history has been reviewed to confirm whether value-moving functions have been called or whether a bot is already sweeping.",
      "required_command": "Etherscan internal txs and token transfers for 0x61ed017468c8a3be3bac972b54fdae6eafcbcd79"
    }
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
    "attacker_gain": "unknown — no selector, no confirmed liquid balance",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot assess — no source, no ABI, no access-control logic visible"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Five hard gates fail simultaneously, making promotion impossible at this stage. (1) live_state_supports_preconditions=false: no Stage 3 live enrichment file was provided; the only input is the triage brief, which itself carried a NEEDS_LIVE_CONTEXT verdict. (2) exact_code_path_or_selector_exists=false: verified_source=null, no bytecode decompilation output, no ABI — no value-moving selector has been identified. (3) concrete_fund_or_reward_gain=false: fdv_usd=0 and liquidity_usd=0 alongside a $314B TVL is the phantom-value signature; value_at_risk() returns max(liquidity_usd, tvl_usd) and the TVL figure is unvalidated. (4) attacker_controls_trigger=false: without selectors, no callable entrypoint can be confirmed as attacker-reachable. (5) gain_is_beyond_entitlement=false: entitlement calculation requires source or decompiled logic, neither of which is available. Required next step: complete Stage 3 live enrichment — resolve token identities and real balances, decompile bytecode to enumerate selectors, read EIP-1967 proxy slots, identify deployer, and review transaction history — then re-enter the proof gate with a populated live context file."
}
```

**Why every failing gate maps directly to the pipeline state:**

- `live_state_supports_preconditions` — The prior triage verdict was `NEEDS_LIVE_CONTEXT`. That verdict is the pipeline's signal that Stage 3 has not run. [1](#0-0) 

- `exact_code_path_or_selector_exists` — `verified_source=null` is the direct cause. Without decompiled selectors there is no code path to evaluate. [2](#0-1) 

- `concrete_fund_or_reward_gain` — `value_at_risk()` returns `max(liquidity_usd, tvl_usd)`. Both `liquidity_usd` and `fdv_usd` are 0; the $314B TVL is unvalidated phantom value. [3](#0-2) 

- The `low_value_score_cap` in the scoring engine would cap this candidate at score ≤ 19 if `liquidity_usd` and `tvl_usd` are both confirmed zero after enrichment, regardless of the `hidden_high_value_contract` tag bonus. [4](#0-3) 

- The correct pipeline routing is back to Stage 3 (live enrichment → `state/latest_live_snapshot.json`) before re-entering Stage 6 (proof gate). [5](#0-4)

### Citations

**File:** deepwiki_prompts.py (L38-41)
```python
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** sentinel/models.py (L22-22)
```python
    verified_source: bool | None = None
```

**File:** sentinel/models.py (L36-37)
```python
    def value_at_risk(self) -> float:
        return max(self.liquidity_usd, self.tvl_usd)
```

**File:** sentinel/scoring.py (L175-177)
```python
    if value < low_value_floor:
        score = min(score, 19)
        reasons.append("low_value_score_cap")
```

**File:** HUNT_PLAN.md (L86-94)
```markdown
## Workflow

1. Discover protocols from live market and explorer data.
2. Filter to fund-extraction and reward-extraction candidates.
3. Refresh `live_targets.json` from the latest scored queue.
4. Build the live snapshot with explorer/RPC data.
5. Inspect balances, selectors, deployers, and funding clusters.
6. Prove the extraction path on a fork or live state.
7. Only then write a report or escalation note.
```