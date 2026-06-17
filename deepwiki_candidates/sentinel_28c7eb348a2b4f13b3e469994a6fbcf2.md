<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_6b6da330-2f44-4305-b2de-69f2d71c49da?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The repository contains no stored data for this specific address. The triage must be based solely on the candidate brief. Here is the verdict:

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x7e58f160b5b77b8b24cd9900c09a3e730215ac47",
    "name": "0x7e58f160b5b77b8b24cd9900c09a3e730215ac47",
    "entity_type": "unknown_protocol",
    "next_action": "reverse_engineer_unverified_funded_contract",
    "score": 103
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with ~$1.78M TVL, no verified source, no deployer attribution, no transaction volume, and a confirmed balance spike. The combination of hidden_high_value_contract + unknown_verification_status + balance_spike on a zero-volume contract is consistent with a honeypot, a custodial sweep target, or an unguarded deposit receiver. No source or selectors are available to confirm or reject an unprivileged extraction path, so live recon is required before any proof attempt.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "verified_source is null; no function selectors, storage layout, or logic are known. Bytecode must be fetched and disassembled to identify value-moving public selectors (withdraw, claim, sweep, transfer, etc.) before any exploit hypothesis can be formed.",
      "command_or_source": "cast code 0x7e58f160b5b77b8b24cd9900c09a3e730215ac47 --rpc-url $BSC_RPC | evmdis / heimdall / panoramix"
    },
    {
      "name": "proxy_and_implementation_check",
      "reason": "Unknown whether the contract is a proxy. If EIP-1967 or EIP-897 slots are populated, the implementation address must be fetched and its bytecode recovered separately.",
      "command_or_source": "cast storage 0x7e58f160b5b77b8b24cd9900c09a3e730215ac47 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "deployer_address and funding_cluster_id are both empty. The deployer identity and funding source are needed to assess whether this is a redeployed rug, a known attacker cluster, or a legitimate protocol.",
      "command_or_source": "bscscan.com/address/0x7e58f160b5b77b8b24cd9900c09a3e730215ac47 -> Internal Txns tab; cast tx <creation_tx> --rpc-url $BSC_RPC"
    },
    {
      "name": "token_holdings_and_balance_breakdown",
      "reason": "TVL is $1.78M but liquidity_usd and fdv_usd are both 0. The exact token(s) held, their contract addresses, and whether they are stablecoins or protocol tokens must be confirmed to assess real extractable value.",
      "command_or_source": "bscscan.com/address/0x7e58f160b5b77b8b24cd9900c09a3e730215ac47#tokentxns; cast call <token> 'balanceOf(address)(uint256)' 0x7e58f160b5b77b8b24cd9900c09a3e730215ac47 --rpc-url $BSC_RPC"
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "reason": "volume24h_usd is 0.0 despite a large balance spike. Zero volume on a funded contract is anomalous. Transaction history must be checked to determine whether funds arrived in a single transfer, whether any withdrawals have been attempted, and whether any privileged callers have interacted.",
      "command_or_source": "bscscan.com/address/0x7e58f160b5b77b8b24cd9900c09a3e730215ac47#internaltx"
    },
    {
      "name": "owner_admin_slot_check",
      "reason": "If an owner or admin is set, determine whether it is an EOA, a multisig, or a contract, and whether any privileged selectors exist that an attacker could not call. This gates whether any identified value-moving function is actually unprivileged.",
      "command_or_source": "cast storage 0x7e58f160b5b77b8b24cd9900c09a3e730215ac47 0x0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting where deposits are accepted but withdrawal logic is absent or open"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not recovered",
      "evidence": "verified_source is null; no ABI, no selector list, no decompiled output available in the brief",
      "why_it_matters": "Without selectors, it is impossible to determine whether any public function can move the $1.78M balance to an arbitrary caller. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$1.78M in token value (confirmed by TVL tag)",
      "At least one public selector exists that transfers or releases tokens",
      "No access control guards that selector, or the guard is bypassable"
    ],
    "call_sequence": [
      "1. Recover bytecode and decompile to identify public selectors",
      "2. Identify any selector matching withdraw(uint256), claim(), sweep(address), transfer(address,uint256), or equivalent",
      "3. Call that selector with attacker address as recipient or beneficiary",
      "4. Confirm token balance transferred to attacker"
    ],
    "expected_gain": "Up to ~$1.78M in stablecoin or known-asset token balance held by the contract — contingent on selector recovery confirming an unguarded value-moving path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recovered ABI from bytecode decompilation",
      "Attacker EOA with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "Call identified value-moving selector from unprivileged EOA",
      "Assert attacker token balance increased",
      "Assert contract token balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker.balance(token) > 0 after call",
      "contract.balance(token) == 0 or reduced by attacker gain",
      "No revert from access control"
    ]
  },
  "rejection_reason": ""
}
```

**Rationale summary:**

The candidate is not rejected because the value signal ($1.78M, balance spike, fresh contract, zero volume) is material and consistent with a funded unguarded contract. It cannot advance to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because `verified_source` is `null`, no selectors are known, the deployer is unattributed, and no transaction pattern is available. Every field needed to form a concrete unprivileged extraction path is missing. The recommended `next_action` is `reverse_engineer_unverified_funded_contract` — recover bytecode, decompile selectors, trace deployer, confirm token holdings — before any proof attempt. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L376-378)
```markdown
reverse_engineer_unverified_funded_contract
-> selector/storage/proxy reconstruction before DeepWiki proof

```

**File:** deepwiki_prompts.py (L38-41)
```python
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** sentinel_deepwiki_schema.py (L7-48)
```python
TRIAGE_CONTRACT: dict[str, Any] = {
    "schema_version": "sentinel-triage-v1",
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "candidate": {
        "source_file": "",
        "chain": "",
        "address": "",
        "name": "",
        "entity_type": "",
        "next_action": "",
        "score": 0,
    },
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "why_this_target_matters": "",
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
    "suspected_exploit_families": [],
    "source_or_selector_basis": [
        {
            "selector_or_function": "",
            "evidence": "",
            "why_it_matters": "",
        }
    ],
    "attacker_path_hypothesis": {
        "actor": "unprivileged external user",
        "preconditions": [],
        "call_sequence": [],
        "expected_gain": "",
    },
    "local_proof_required": {
        "test_type": "fork | unit | invariant | fuzz | manual",
        "setup": [],
        "transaction_sequence": [],
        "expected_assertions": [],
    },
    "rejection_reason": "",
```