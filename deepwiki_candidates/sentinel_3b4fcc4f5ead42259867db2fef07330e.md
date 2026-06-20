<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_f453aa6f-1162-4805-bf6c-b59aebe7bed0?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/002-bsc-0x92b7807bf19b7dddf89b706143896d05228f3121.json",
    "chain": "bsc",
    "address": "0x92b7807bf19b7dddf89b706143896d05228f3121",
    "name": "0x92b7807bf19b7dddf89b706143896d05228f3121",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 113
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with $36.4M TVL and an immediate balance spike, tagged as hidden_high_value_contract and audit_hidden_contract with no verified source. The combination of large stablecoin/token balance, unknown verification status, and zero on-chain volume suggests funds are parked rather than actively used, which is a pattern consistent with custody contracts, migrators, or unverified vaults that may lack access controls. No source, no deployer, and no selectors are available in this pass, so no exploit family can be confirmed without live recon.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "verified_source is null and unknown_verification_status is set. Without source or decompiled bytecode, no public selectors, access-control patterns, or value-moving functions can be identified. This is the single hardest blocker.",
      "command_or_source": "cast code 0x92b7807bf19b7dddf89b706143896d05228f3121 --rpc-url $BSC_RPC | python3 -c 'import sys,evmdasm; evmdasm.disassemble(bytes.fromhex(sys.stdin.read().strip()[2:]))' OR fetch from https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x92b7807bf19b7dddf89b706143896d05228f3121"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "If the contract is an EIP-1967 or EIP-897 proxy, the logic lives at a different address. A proxy with a recently swapped implementation and live funds is a high-priority escalation path.",
      "command_or_source": "cast storage 0x92b7807bf19b7dddf89b706143896d05228f3121 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  # EIP-1967 impl slot"
    },
    {
      "name": "deployer_address_and_creation_tx",
      "reason": "deployer_address is empty in the brief. The deployer identity and funding source are needed to detect closed-project redeployment, rug-redeploy patterns, or known-bad actor clusters.",
      "command_or_source": "https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x92b7807bf19b7dddf89b706143896d05228f3121"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "TVL is $36.4M but the specific tokens held are unknown. Identifying whether these are stablecoins (USDT/USDC/BUSD), LP tokens, or protocol-specific tokens determines which withdrawal or redeem paths are worth probing.",
      "command_or_source": "https://api.bscscan.com/api?module=account&action=tokenlist&address=0x92b7807bf19b7dddf89b706143896d05228f3121"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero volume24h_usd with a large balance spike is anomalous. Reviewing inbound/outbound transactions reveals whether funds arrived in a single sweep (custody/migrator pattern), whether any withdrawal attempts have been made, and whether a bot is repeatedly interacting.",
      "command_or_source": "https://api.bscscan.com/api?module=account&action=txlist&address=0x92b7807bf19b7dddf89b706143896d05228f3121&sort=desc&page=1&offset=50"
    },
    {
      "name": "admin_and_owner_slot_scan",
      "reason": "If source is unavailable, scanning common owner/admin storage slots (slot 0, Ownable pattern, OpenZeppelin AccessControl DEFAULT_ADMIN_ROLE) can reveal whether privileged roles are set to zero address or a known EOA, which affects whether missing-access-control paths are reachable by an unprivileged caller.",
      "command_or_source": "cast storage 0x92b7807bf19b7dddf89b706143896d05228f3121 0 --rpc-url $BSC_RPC && cast storage 0x92b7807bf19b7dddf89b706143896d05228f3121 0xb53127684a568b3173ae13b9f8a6016f243e3b8a --rpc-url $BSC_RPC  # OZ ProxyAdmin slot"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_function",
    "unauthorized_withdrawal_or_sweep",
    "proxy_implementation_mismatch_with_live_funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source is null; unknown_verification_status tag is set. No ABI, selector list, or decompiled output is available in this pass.",
      "why_it_matters": "Without selectors, no specific call path can be constructed. All exploit family assignments above are hypotheses only, not confirmed paths."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds $36.4M in tokens (confirmed by TVL signal)",
      "At least one public or externally callable function exists that moves tokens out",
      "That function either has no access control or has a bypassable guard"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector extraction from bytecode or verified source",
      "Hypothetical: call withdraw(address,uint256) or sweep(address) or claim() with attacker-controlled recipient",
      "Receive tokens to attacker address"
    ],
    "expected_gain": "Up to $36.4M in stablecoin or token value if a public sweep or withdraw selector exists without access control — unconfirmed until selectors are resolved"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Pin BSC fork to block where balance spike is confirmed",
      "Identify token addresses held by the contract",
      "Decompile bytecode to extract callable selectors",
      "Identify any withdraw, sweep, claim, redeem, or release selectors"
    ],
    "transaction_sequence": [
      "vm.createSelectFork(BSC_RPC, SPIKE_BLOCK)",
      "Call each candidate value-moving selector from an unprivileged address",
      "Assert attacker token balance increases and contract balance decreases"
    ],
    "expected_assertions": [
      "attackerTokenBalance > 0 after call",
      "contractTokenBalance < pre-call balance",
      "No revert from access control"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** `NEEDS_LIVE_CONTEXT` — not `REJECT` and not `NEEDS_LOCAL_PROOF`.

The $36.4M TVL with an immediate balance spike on a fresh, unverified, zero-volume BSC contract is a pattern that warrants recon. However, `verified_source` is `null` and no deployer, selectors, proxy state, or token breakdown are available in this pass. Per the hard rules, a local proof attempt cannot be structured without at least one confirmed value-moving selector. The six live-context items above — bytecode/selector extraction first, then proxy check and deployer trace — are the minimum needed to either escalate to `NEEDS_LOCAL_PROOF` or reject. [1](#0-0) [2](#0-1)

### Citations

**File:** HUNT_PLAN.md (L75-85)
```markdown
## Evidence Required

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy

```

**File:** sentinel_deepwiki_schema.py (L7-49)
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
}
```