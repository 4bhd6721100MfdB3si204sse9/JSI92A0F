<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_184fcbe5-d9cd-40e3-a775-9aa50c42ae06?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "ethereum_chain_scanner",
    "chain": "ethereum",
    "address": "0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c",
    "name": "0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 98
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract holding ~$2.78M in token value with an immediate balance spike, unverified source, no deployer attribution, and no transaction volume. The combination of hidden_high_value_contract, audit_hidden_contract, and token_funded_contract tags on an unverified contract with this balance level is a high-priority surface for unauthorized withdrawal or sweep. No source code or ABI is available, so no selector-level exploit hypothesis can be formed without live recon.",
  "live_context_required": [
    {
      "name": "bytecode_selectors",
      "reason": "Contract is unverified. Need 4-byte selectors from deployed bytecode to identify any public value-moving functions (withdraw, redeem, claim, sweep, transfer, etc.).",
      "command_or_source": "cast code 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c --rpc-url $ETH_RPC | python3 -c \"import sys,re; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b)-8,2) if b[i:i+2]=='63']\" # or use heimdall / etherface / 4byte.directory decompiler"
    },
    {
      "name": "token_composition",
      "reason": "TVL is entirely token-based (token_funded_contract, high_token_balance). Need exact token addresses, amounts, and USD values to confirm live extractable value and identify asset type (stablecoin, bluechip, governance token).",
      "command_or_source": "cast call <token_address> 'balanceOf(address)(uint256)' 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c --rpc-url $ETH_RPC  # repeat for each token found via Etherscan token holdings tab"
    },
    {
      "name": "deployer_and_creation_tx",
      "reason": "Deployer address is empty in the brief. Deployer identity is needed to check for cluster risk, prior closed projects, or known attacker/rug patterns.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) | grep -i 'creates') --rpc-url $ETH_RPC  # or: Etherscan contract creation tab for 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c"
    },
    {
      "name": "transaction_history",
      "reason": "volume24h_usd is 0 but balance_spike and immediate_balance_spike tags are set. Need to confirm whether the spike was a single large inbound transfer with no outbound activity, or whether there are any calls to value-moving selectors.",
      "command_or_source": "https://etherscan.io/address/0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c#internaltx  # review all internal txs and token transfers"
    },
    {
      "name": "proxy_check",
      "reason": "Contract may be a proxy (EIP-1967 or EIP-897). If it is, the implementation address and any admin/upgrade state must be fetched before selector analysis is meaningful.",
      "command_or_source": "cast storage 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC  # EIP-1967 impl slot; also check 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f for beacon"
    },
    {
      "name": "decompiled_source",
      "reason": "Without verified source, a decompiler output (Panoramix, Dedaub, or Heimdall) is required to identify function signatures, access control patterns, and any owner/admin checks on value-moving paths.",
      "command_or_source": "https://app.dedaub.com/decompile?address=0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c&network=ethereum  # or: heimdall decompile 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized_withdrawal_or_sweep",
    "missing_access_control_on_value_moving_functions",
    "phantom_accounting_shares_without_assets",
    "proxy_implementation_storage_mismatch"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — unverified bytecode",
      "evidence": "verified_source is null; unknown_verification_status tag present; no ABI or source available from the brief",
      "why_it_matters": "Cannot confirm or deny the existence of public withdraw/claim/sweep selectors without decompilation. This is the primary blocker for forming a concrete exploit hypothesis."
    },
    {
      "selector_or_function": "ERC20 token inflow (inferred from token_funded_contract tag)",
      "evidence": "Tags include token_funded_contract, high_token_balance, fresh_contract_large_token_balance, immediate_balance_spike. TVL is $2,782,986 with zero volume.",
      "why_it_matters": "Tokens were transferred into the contract shortly after deployment with no outbound activity. If the contract lacks access control on a transfer/withdraw function, the full token balance may be extractable by any caller."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes a public or externally callable selector that moves tokens to an arbitrary recipient or msg.sender",
      "No owner/admin check guards the value-moving function",
      "Tokens remain in the contract at time of call"
    ],
    "call_sequence": [
      "1. Decompile bytecode to recover selectors",
      "2. Identify any withdraw(address,uint256), claim(), sweep(), or transfer() variant with no access control",
      "3. Call the selector directly from an unprivileged EOA on a mainnet fork",
      "4. Assert token balance of attacker increases by contract holdings"
    ],
    "expected_gain": "Up to ~$2,782,986 in token value if a public sweep or withdraw path exists with no access control — unconfirmed until selectors are recovered"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Ethereum mainnet at current block",
      "Confirm token balances of 0xd40f8aeb4f574f67377009d2a27003ddae8bfc7c via balanceOf calls",
      "Recover selectors via bytecode decompilation",
      "Identify candidate value-moving selectors with no apparent access control"
    ],
    "transaction_sequence": [
      "vm.startPrank(address(0xdeadbeef))  // unprivileged attacker",
      "target.call(abi.encodeWithSelector(<candidate_selector>, attacker, amount))  // attempt withdrawal",
      "assertGt(token.balanceOf(attacker), 0)  // confirm gain"
    ],
    "expected_assertions": [
      "Attacker token balance increases after call",
      "Contract token balance decreases by matching amount",
      "No revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The contract scores 98 and carries ~$2.78M in token value with an immediate balance spike on a fresh, unverified Ethereum contract. That combination clears the value threshold and matches the `fund_extraction` paid scope.

However, the brief contains **zero selector, source, or ABI information**. The `verified_source` field is `null`, the deployer address is empty, and no transaction volume exists. Under the hard rules, this is the canonical `NEEDS_LIVE_CONTEXT` pattern: the value signal is real, but no exploit hypothesis can be formed without first recovering bytecode selectors and confirming token composition.

The six live-context items above are ordered by priority. Bytecode decompilation and token composition are the critical-path blockers — if decompilation reveals a public `withdraw` or `sweep` selector with no access control guard, this immediately escalates to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** sentinel/chain_scanner.py (L459-466)
```python
        if deployment.discovery_source == "erc20_transfer_log":
            tags.append("token_funded_contract")
        else:
            tags.append("fresh_deployment")
        if native_usd >= target_min_usd:
            tags.extend(["high_native_balance", "fresh_contract_large_balance"])
        if token_usd >= target_min_usd:
            tags.extend(["high_token_balance", "fresh_contract_large_token_balance", "fresh_contract_large_balance"])
```

**File:** sentinel/scoring.py (L27-29)
```python
    elif value >= 1_000_000:
        score += 25
        reasons.append(f"value_at_risk>=1000000:{value:.0f}")
```

**File:** HUNT_PLAN.md (L108-115)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement
```