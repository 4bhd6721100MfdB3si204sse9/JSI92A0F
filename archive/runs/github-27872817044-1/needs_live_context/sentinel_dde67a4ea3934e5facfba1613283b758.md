<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_59d6551f-4a2d-49a6-b657-37e94e666f25?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/ethereum-0x73d8bd54f7cf5fab43fe4ef40a62d390644946db.json",
    "chain": "ethereum",
    "address": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
    "name": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with ~$11.66M TVL, an immediate balance spike, and no verified source. The combination of high_token_balance, balance_spike, and unknown_verification_status on a fresh contract is a high-signal pattern for either a custody/vault contract with missing access control or a migrator that received user funds. Without source or selectors, no exploit path can be confirmed, but the value at risk justifies full recon before rejection.",
  "live_context_required": [
    {
      "name": "bytecode_decompilation_and_selector_extraction",
      "reason": "verified_source is null and no ABI is available. Decompiling the deployed bytecode and resolving 4byte selectors is the minimum required to identify any public value-moving functions (withdraw, claim, sweep, redeem, transfer, etc.).",
      "command_or_source": "cast code 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db --rpc-url $ETH_RPC | python3 -c 'import sys; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b),8) if i+8<=len(b)]' | sort -u  # then resolve via https://www.4byte.directory or heimdall-rs decompile"
    },
    {
      "name": "proxy_slot_check",
      "reason": "If the contract is an EIP-1967 or EIP-897 proxy, the implementation address determines the actual code surface. A recent implementation upgrade on a funded proxy is a critical escalation signal.",
      "command_or_source": "cast storage 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC  # EIP-1967 impl slot; also check 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f for beacon"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "deployer_address is empty in the brief. The deployer identity and the funding transaction(s) that caused the balance spike are needed to determine whether this is a migrator receiving user funds, a treasury deposit, or an attacker-controlled honeypot.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) --rpc-url $ETH_RPC) --rpc-url $ETH_RPC  # or query Etherscan API: https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0x73d8bd54f7cf5fab43fe4ef40a62d390644946db&apikey=$ETHERSCAN_KEY"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "TVL is $11.66M but liquidity_usd and fdv_usd are both 0. The value is entirely in token holdings. Identifying which tokens, their quantities, and who transferred them reveals whether this is a legitimate protocol deposit or an anomalous custody event.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=tokentx&address=0x73d8bd54f7cf5fab43fe4ef40a62d390644946db&sort=asc&apikey=$ETHERSCAN_KEY'"
    },
    {
      "name": "recent_transaction_history",
      "reason": "volume24h_usd is 0.0, meaning no recent swap/interaction volume is recorded. Checking raw transaction history reveals whether any callers have already interacted with value-moving selectors, which would confirm those selectors exist and are reachable.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=txlist&address=0x73d8bd54f7cf5fab43fe4ef40a62d390644946db&sort=asc&apikey=$ETHERSCAN_KEY'"
    },
    {
      "name": "owner_or_admin_slot",
      "reason": "If the contract has an owner/admin, determining whether it is a known EOA, multisig, or zero address affects whether access-controlled withdrawal paths are in scope.",
      "command_or_source": "cast call 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db 'owner()(address)' --rpc-url $ETH_RPC; cast storage 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db 0 --rpc-url $ETH_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_shares_without_assets",
    "proxy_implementation_mismatch_exposing_live_funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or ABI",
      "evidence": "verified_source is null; unknown_verification_status tag present; no URL or deployer address in the brief",
      "why_it_matters": "Without selectors, no specific exploit path can be constructed. All exploit family hypotheses remain conditional on bytecode decompilation results."
    },
    {
      "selector_or_function": "balance_spike / immediate_balance_spike (heuristic tags)",
      "evidence": "Tags fresh_contract_large_balance, fresh_contract_large_token_balance, immediate_balance_spike, and high_token_balance all fire simultaneously on a fresh contract",
      "why_it_matters": "Immediate large token inflows to a fresh unverified contract match the pattern of custody contracts, migrators, or airdrop distributors — all surfaces where missing access control on claim/withdraw/sweep functions has historically led to fund extraction."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$11.66M in tokens (confirmed by TVL signal)",
      "At least one public selector exists that moves tokens out of the contract",
      "That selector does not enforce msg.sender == owner or equivalent access control",
      "Contract is not a honeypot with a revert trap on non-owner callers"
    ],
    "call_sequence": [
      "1. Resolve public selectors via bytecode decompilation",
      "2. Identify any withdraw(address,uint256), claim(address), sweep(address), or transfer-delegating function with no access check",
      "3. Call that function with attacker-controlled recipient address",
      "4. Receive tokens from contract balance"
    ],
    "expected_gain": "Up to ~$11.66M in token value if a public unrestricted withdrawal path exists — unquantifiable until selectors are known"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Pin Ethereum mainnet fork at a recent block where contract balance is confirmed",
      "Load contract ABI from decompilation output",
      "Fund attacker address with enough ETH for gas"
    ],
    "transaction_sequence": [
      "attacker calls identified value-moving selector with attacker address as recipient",
      "assert attacker token balance increased",
      "assert contract token balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker.tokenBalance > 0 after call",
      "contract.tokenBalance < pre-call balance",
      "no revert on unprivileged caller"
    ]
  },
  "rejection_reason": ""
}
```

**Basis for `NEEDS_LIVE_CONTEXT`:**

The candidate scores high on value-at-risk signals (score 108, $11.66M TVL, `balance_spike`, `hidden_high_value_contract`) but every field that would allow selector-level analysis is absent: `verified_source` is `null`, `deployer_address` is empty, there is no ABI, no URL, and no transaction volume. [1](#0-0) 

Per the hard rules, `NEEDS_LIVE_CONTEXT` is the correct verdict when "live balances, proxy/admin state, selectors, claimability, or source details are missing." [2](#0-1)  The six `live_context_required` items above are the minimum recon steps before this can be escalated to `NEEDS_LOCAL_PROOF`. [3](#0-2)

### Citations

**File:** deepwiki_prompts.py (L39-40)
```python
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
```

**File:** sentinel_deepwiki_schema.py (L21-27)
```python
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
```