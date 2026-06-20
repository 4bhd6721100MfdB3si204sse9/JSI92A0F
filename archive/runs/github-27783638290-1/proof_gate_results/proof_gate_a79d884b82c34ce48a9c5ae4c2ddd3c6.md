<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_cb3ee202-d6d8-49f8-bb52-3bab82b238ab?mode=deep -->

The brief file `006-ethereum-0x26de7861e213a5351f6ed767d00e0839930e9ee1.json` does not exist in the repository's `deepwiki_briefs/` directory. [1](#0-0)  The proof gate schema defined in `sentinel_deepwiki_schema.py` has no `NEEDS_LIVE_CONTEXT` verdict — only `REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE`. [2](#0-1)  Every hard gate that requires source, selector, live balance confirmation, or a concrete fund-movement path is unresolvable from the provided candidate brief alone. [3](#0-2)  Per `HUNT_PLAN.md`, a candidate must not be promoted unless the proof shows an unprivileged attacker, a reproducible path, extraction of user funds or excess rewards, and gain beyond entitlement. [4](#0-3) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0x26de7861e213a5351f6ed767d00e0839930e9ee1",
    "live_context_source": "candidate brief only — no live context file provided",
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
    "Contract source or decompiled bytecode with at least one public value-moving selector identified",
    "ERC-20 token identity confirmed with non-zero real market liquidity (DEX pool depth > 0)",
    "Deployer address and funding trace recovered to rule out honeypot or self-minted token",
    "Transaction history showing at least one deposit or value-moving call to the contract",
    "Proxy slot check completed to determine whether an upgradeable implementation is live"
  ],
  "attacker_path": {
    "actor": "",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token identity unconfirmed; reported TVL of $1.89T is a data artifact (liquidity_usd: 0, volume24h_usd: 0)",
    "attacker_gain": "unknown — no selector or function identified that moves tokens to a caller-controlled address",
    "victim_or_protocol_loss": "unknown — no confirmed real-value asset held by the contract",
    "why_gain_exceeds_entitlement": "cannot be determined — no source, ABI, or selector basis exists to define entitlement or an extraction path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [
      "Obtain contract bytecode via cast code 0x26de7861e213a5351f6ed767d00e0839930e9ee1 --rpc-url $ETH_RPC",
      "Decompile bytecode with heimdall or panoramix to recover 4-byte selectors",
      "Cross-reference selectors against 4byte.directory for withdraw/claim/sweep/rescue matches",
      "Confirm ERC-20 token balances via balanceOf and verify real DEX pool depth for each token",
      "Check proxy storage slots 0x360894...2076 and 0x7050c9...2f for implementation address",
      "Trace deployer EOA from contract creation tx to identify funding cluster and rug-redeploy patterns"
    ],
    "transaction_sequence": [
      "Pin Ethereum fork to block at or after contract deployment",
      "vm.startPrank(attacker) — unprivileged EOA with no prior interaction with the contract",
      "target.call(abi.encodeWithSelector(<candidate_selector_from_decompilation>, attacker)) — attempt value-moving call",
      "Assert attacker token balance increased and contract token balance decreased"
    ],
    "expected_assertions": [
      "attacker token balance after > attacker token balance before",
      "contract token balance after < contract token balance before",
      "call did not revert with an access-control or ownership error"
    ],
    "reject_if_assertion_fails": "If no public value-moving selector is found in bytecode, or if all candidate selectors revert with access-control errors, or if token balances have zero real market liquidity, reject the candidate as a data artifact with no extractable value."
  },
  "rejection_reason": "All hard gates requiring live state evidence are unresolvable: (1) contract source is unverified and no selectors have been recovered from transactions or bytecode, blocking exact_code_path_or_selector_exists; (2) no live context file was provided, blocking live_state_supports_preconditions; (3) the reported $1.89T TVL is a data artifact — liquidity_usd and volume24h_usd are both zero, meaning no real market depth exists for the held tokens, blocking concrete_fund_or_reward_gain and gain_is_beyond_entitlement; (4) without selectors, deployer, or transaction history, no attacker path can be formed and attacker_controls_trigger cannot be satisfied. The candidate remains at NEEDS_LIVE_CONTEXT from triage. The proof gate has no NEEDS_LIVE_CONTEXT verdict; the correct gate outcome is REJECT pending completion of the five live_preconditions listed above, after which the candidate should be re-submitted to the proof gate with a populated live context file."
}
```

### Citations

**File:** deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json (L1-1)
```json
{
```

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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```