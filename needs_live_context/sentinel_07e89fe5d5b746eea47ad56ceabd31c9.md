<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_65ffd771-3314-4ab5-8525-b0ab79d2a25e?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b` does not appear anywhere in the repository. The codebase contains only placeholder/sample contracts. No source, ABI, selectors, deployer, or transaction data for this candidate exists in the repo. The verdict must be `NEEDS_LIVE_CONTEXT` — the $17.4M balance is notable but there is zero selector or source basis to form an exploit hypothesis.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b",
    "name": "0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract holding ~$17.4M in token value with no known protocol identity, no verified source, no deployer attribution, and no transaction history available in the codebase. The combination of large balance, hidden identity, and zero public context matches the highest-risk surface for unauthorized withdrawal or sweep paths.",
  "live_context_required": [
    {
      "name": "Contract bytecode and selector recovery",
      "reason": "Source is unverified and unknown. No ABI, function selectors, or logic is available. Cannot assess any value-moving path without first recovering the public interface.",
      "command_or_source": "cast code 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b --rpc-url $BSC_RPC | python3 -c 'import sys,re; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b)-8,2) if re.match(\"[0-9a-f]{8}\",b[i:i+8])]' | sort -u"
    },
    {
      "name": "Proxy detection and implementation address",
      "reason": "Contract may be a proxy (EIP-1967, EIP-897, or custom). If so, the implementation holds the real logic and may have been recently swapped, exposing live funds.",
      "command_or_source": "cast storage 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC && cast storage 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url $BSC_RPC"
    },
    {
      "name": "Token balances held by the contract",
      "reason": "TVL of $17.4M is attributed to token holdings, not native BNB. The specific tokens, their amounts, and whether they are user deposits or protocol-owned reserves determines the real attack surface.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b&sort=desc&apikey=$BSCSCAN_KEY' | jq '.result[:20]'"
    },
    {
      "name": "Deployer address and funding chain",
      "reason": "Deployer is unknown. Tracing the deployer reveals whether this is a redeployed rug, a known protocol's satellite contract, or a novel unknown entity. Funding cluster membership changes the risk profile significantly.",
      "command_or_source": "cast tx $(cast rpc eth_getTransactionByBlockNumberAndIndex $(cast rpc eth_getCode 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b latest) 0x0 --rpc-url $BSC_RPC) --rpc-url $BSC_RPC | grep 'from'"
    },
    {
      "name": "Transaction history and caller pattern",
      "reason": "Zero 24h volume reported. Need to confirm whether the contract has ever been called, whether deposits and withdrawals are balanced, and whether any privileged sweep or drain transactions have already occurred.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b&sort=desc&apikey=$BSCSCAN_KEY' | jq '.result[:30] | map({hash,from,to,input:.input[:10],value})"
    },
    {
      "name": "Admin or owner slot",
      "reason": "If the contract has an owner or admin, determining whether that role is a multisig, EOA, or zero address affects whether access-control bypass is in scope.",
      "command_or_source": "cast call 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b 'owner()(address)' --rpc-url $BSC_RPC 2>/dev/null || cast storage 0x5faf1dfc1e933daaa92cfbd165cbf6acf2d42c3b 0x0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or sweep (missing access control on value-moving selectors)",
    "phantom accounting (shares or debt created without matching assets)",
    "proxy or implementation mismatch exposing live funds",
    "missing or bypassable access control on claim, redeem, or migrate functions"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no source or ABI available",
      "evidence": "verified_source is null; unknown_verification_status tag present; no bytecode or selector data exists in the repository or candidate brief",
      "why_it_matters": "Without selectors, no call sequence can be constructed and no exploit family can be confirmed. All hypotheses below are speculative pending bytecode recovery."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract has at least one public or external value-moving selector with no caller check",
      "Token balance (~$17.4M) is accessible via that selector rather than locked behind admin-only logic",
      "Contract is not a pure admin treasury with no user-facing withdrawal surface"
    ],
    "call_sequence": [
      "1. Recover selectors from bytecode via 4byte.directory or brute-force",
      "2. Identify any withdraw(), redeem(), claim(), sweep(), or migrate() selector",
      "3. Attempt call with attacker address as sole argument or with no arguments",
      "4. Observe token transfer event in return trace"
    ],
    "expected_gain": "Up to $17,439,091 in token value if an unchecked withdrawal path exists — unquantifiable until selectors are recovered"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recovered ABI from bytecode decompilation (e.g., Panoramix, Dedaub, or heimdall-rs)",
      "Attacker account with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "Identify value-moving selector from decompiled output",
      "Call selector from unprivileged EOA",
      "Assert token balance of attacker increases and contract balance decreases"
    ],
    "expected_assertions": [
      "attacker.balance(token) > 0 after call",
      "contract.balance(token) < pre-call balance",
      "No revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Key basis for `NEEDS_LIVE_CONTEXT` over `REJECT`:** The $17.4M balance on a fresh, unverified, identity-unknown BSC contract is a genuine signal. The tags `hidden_high_value_contract`, `audit_hidden_contract`, and `unknown_verification_status` together indicate this is not a known benign protocol. However, without bytecode, selectors, deployer identity, or any transaction history, there is no source or selector basis to advance to `NEEDS_LOCAL_PROOF`. The six live-context items above are the minimum required before any proof work is meaningful.