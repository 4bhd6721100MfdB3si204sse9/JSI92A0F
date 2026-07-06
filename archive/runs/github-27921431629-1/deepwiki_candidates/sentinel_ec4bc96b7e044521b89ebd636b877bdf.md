<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_e2686189-253e-49ca-98a4-43fdc0109efe?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1` has no existing entry in the codebase — this is a net-new candidate from the explorer snapshot. Based on the brief and the triage rules defined in the codebase, here is the triage output: [1](#0-0) [2](#0-1) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/001-bsc-0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1.json",
    "chain": "bsc",
    "address": "0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1",
    "name": "0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 113
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with ~$100.9M in token value, an immediate balance spike, and unknown verification status. No source, no selectors, no deployer, and no transaction history are available in the brief. The combination of hidden_high_value_contract + unknown_verification_status + balance_spike on a fresh contract is a high-priority surface for unauthorized withdrawal or missing access control on value-moving functions. The value at risk is large enough to justify full live recon before any proof attempt.",
  "live_context_required": [
    {
      "name": "contract_bytecode_and_selector_recovery",
      "reason": "No source code or ABI is available. Bytecode must be fetched and 4-byte selectors extracted to identify any public value-moving functions (withdraw, claim, sweep, redeem, transfer, migrate).",
      "command_or_source": "cast code 0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1 --rpc-url $BSC_RPC | python3 -c 'import sys; b=bytes.fromhex(sys.stdin.read().strip()[2:]); [print(b[i:i+4].hex()) for i in range(len(b)-3) if b[i]==0x63 or True]' # or use heimdall / 4byte.directory lookup"
    },
    {
      "name": "bscscan_source_and_proxy_check",
      "reason": "verified_source is null. Must confirm whether source is verified, whether the contract is a proxy (EIP-1967 / EIP-897), and if so, what the implementation address is.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1&apikey={api_key}'"
    },
    {
      "name": "deployer_address_and_deployment_tx",
      "reason": "deployer_address is empty. The deployer identity and deployment transaction are needed to check for closed-project links, funding cluster membership, and whether the same deployer has a history of rug redeployments.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1&sort=asc&page=1&offset=5&apikey={api_key}'"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $100.9M TVL is token-denominated (high_token_balance tag). The specific tokens held, their amounts, and how they arrived (direct transfer, deposit function, or airdrop) determine whether there is a claimable or withdrawable surface.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1&sort=desc&page=1&offset=50&apikey={api_key}'"
    },
    {
      "name": "recent_transaction_history_and_callers",
      "reason": "volume24h_usd is 0.0, suggesting no recent interaction — but this must be confirmed. If the contract has never been called after funding, it may be a custody or escrow contract with no public withdrawal path yet. If it has been called, the callers and selectors used reveal the live attack surface.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1&sort=desc&page=1&offset=50&apikey={api_key}'"
    },
    {
      "name": "proxy_implementation_and_admin_slots",
      "reason": "If the contract is a proxy, the implementation address and admin slot must be read to determine whether the implementation exposes public value-moving selectors or has recently changed.",
      "command_or_source": "cast storage 0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC && cast storage 0x6a7054e68b9335c31b75a4c67d2d6b5c819119b1 0xb53127684a568b3173ae13b9f8a6016f243e3b8a --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, unstake, claim, liquidate, release, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds",
    "phantom accounting where shares, debt, or rewards are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not yet recovered",
      "evidence": "verified_source is null; no ABI or selector list is present in the brief. The contract is tagged unknown_verification_status and unfamiliar_contract.",
      "why_it_matters": "Without selectors, no concrete exploit path can be formed. Selector recovery is the mandatory first step before any proof attempt."
    },
    {
      "selector_or_function": "inferred: withdraw / claim / sweep / transfer (class)",
      "evidence": "token_funded_contract + fresh_contract_large_token_balance + immediate_balance_spike tags indicate tokens were deposited into this contract shortly after deployment. Contracts of this shape commonly expose a withdrawal or claim entrypoint.",
      "why_it_matters": "If a public withdraw/claim selector exists without caller validation, an unprivileged attacker could drain the full token balance."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$100.9M in tokens (confirmed by TVL figure)",
      "Contract exposes at least one public selector that moves tokens to a caller-controlled address",
      "No access control (owner check, whitelist, merkle proof, or timelock) guards the value-moving function"
    ],
    "call_sequence": [
      "1. Recover selectors from bytecode (heimdall or 4byte.directory)",
      "2. Identify any withdraw(address,uint256), claim(), sweep(address), or transfer(address,uint256) selectors",
      "3. Call the selector from an unprivileged EOA on a BSC fork",
      "4. Assert attacker token balance increases and contract balance decreases"
    ],
    "expected_gain": "Up to ~$100.9M in tokens if a public unguarded withdrawal path exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at the current block using cast or anvil --fork-url $BSC_RPC",
      "Confirm contract token balances match the $100.9M TVL figure",
      "Recover and decode all 4-byte selectors from the contract bytecode",
      "Identify the token contract addresses held by the target"
    ],
    "transaction_sequence": [
      "Attempt each value-moving selector (withdraw, claim, sweep, redeem, transfer) from an unprivileged address",
      "If a proxy is detected, repeat against the implementation address",
      "Record token balance delta for attacker and contract after each call"
    ],
    "expected_assertions": [
      "attacker.tokenBalance(token) > 0 after call",
      "target.tokenBalance(token) < pre-call balance",
      "call does not revert with access control error"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** The $100.9M value at risk is real and the tag profile (`hidden_high_value_contract`, `balance_spike`, `unknown_verification_status`, `fresh_contract_large_token_balance`) is a high-priority Sentinel surface. However, the brief contains zero source, zero selectors, no deployer, and no transaction history. The hard rules require `NEEDS_LIVE_CONTEXT` when "proxy/admin state, selectors, claimability, or source details are missing" — all four are missing here. [3](#0-2)  The mandatory next step is bytecode selector recovery and BSCScan enrichment before any local proof attempt is warranted. [4](#0-3)

### Citations

**File:** deepwiki_prompts.py (L36-42)
```python
## Hard Rules
- Attacker must be unprivileged.
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.
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

**File:** HUNT_PLAN.md (L77-84)
```markdown
Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy
```