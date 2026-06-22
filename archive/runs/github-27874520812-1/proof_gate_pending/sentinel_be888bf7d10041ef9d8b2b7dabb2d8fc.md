<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_29263551-b095-49e4-956f-9e1aae0e1ef5?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/018-bsc-0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b.json",
    "chain": "bsc",
    "address": "0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b",
    "name": "0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$550M in token value with no verified source, no known deployer, no selector inventory, and no protocol identity. The combination of hidden_high_value_contract, fresh_contract_large_token_balance, and unknown_verification_status at this TVL scale makes it a priority surface for unauthorized withdrawal or sweep paths. No triage decision beyond NEEDS_LIVE_CONTEXT is possible without bytecode, selectors, deployer lineage, and token breakdown.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_inventory",
      "reason": "Contract source is unverified or verification status is unknown. Decompiled selectors are required to identify any public value-moving entrypoints (withdraw, redeem, claim, sweep, release, migrate) before a proof path can be hypothesized.",
      "command_or_source": "cast code 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b --rpc-url $BSC_RPC | python3 -c 'import sys,evmdasm; [print(i) for i in evmdasm.disassemble(bytes.fromhex(sys.stdin.read().strip()[2:]))]' OR use heimdall-rs / panoramix to recover function selectors and approximate ABI"
    },
    {
      "name": "verification_status_and_source",
      "reason": "Tag is unknown_verification_status, not confirmed unverified. BSCScan may have partial or proxy-verified source. Source code would immediately reveal access control patterns, ownership, and value-moving logic.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "TVL of $550M is token-denominated (token_funded_contract tag, zero native liquidity_usd). The specific tokens held determine whether the balance is user-deposited principal, protocol-owned reserves, or a single large token transfer. This affects whether extraction would harm users.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "deployer_address_and_creation_tx",
      "reason": "deployer_address is empty. Deployer identity and funding source are required to detect rug-redeploy patterns, closed-project migrations, or known-bad actor clusters.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "recent_transaction_history_and_callers",
      "reason": "Zero volume24h_usd and zero liquidity_usd with $550M TVL is anomalous. Transaction history reveals whether the contract has ever been called, whether bots interact with it, and whether any withdrawal or claim patterns exist.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&sort=desc&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "proxy_and_implementation_slot_check",
      "reason": "Fresh contracts with large hidden balances are frequently proxy patterns. EIP-1967 and OpenZeppelin transparent proxy slots must be read to determine if an implementation contract holds the actual logic and whether it has been recently changed.",
      "command_or_source": "cast storage 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC && cast storage 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 0xb53127684a568b3173ae13b9f8a6016f243e3b8a --rpc-url $BSC_RPC"
    },
    {
      "name": "owner_or_admin_slot",
      "reason": "If an owner or admin exists, determining whether ownership is renounced or held by an EOA affects whether missing-access-control findings are exploitable by an unprivileged caller.",
      "command_or_source": "cast call 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 'owner()(address)' --rpc-url $BSC_RPC 2>/dev/null || cast storage 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 0x0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds",
    "phantom accounting where shares or debt are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selector inventory available",
      "evidence": "verified_source is null and unknown_verification_status tag is set; no ABI or decompiled output present in the brief",
      "why_it_matters": "Without a selector inventory, no specific value-moving entrypoint can be confirmed or ruled out. All exploit family hypotheses remain unanchored."
    },
    {
      "selector_or_function": "token transfer events (inferred from token_funded_contract tag)",
      "evidence": "Tags fresh_contract_large_token_balance and token_funded_contract indicate ERC-20 transfers into the contract; tvl_usd=$550M with liquidity_usd=0 and volume24h_usd=0",
      "why_it_matters": "Tokens were moved into this contract but no outbound activity is recorded. This pattern is consistent with a custody or escrow contract that may have a public release or claim path."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$550M in ERC-20 tokens confirmed by on-chain balance query",
      "At least one public selector exists that moves tokens to an arbitrary or caller-controlled address",
      "No access control gate (owner check, merkle proof, or deposit record) blocks the call"
    ],
    "call_sequence": [
      "UNKNOWN — requires decompiled selector inventory before a concrete call sequence can be constructed"
    ],
    "expected_gain": "Partial or full extraction of the ~$550M token balance to attacker-controlled address; exact asset and amount unknown until token breakdown and selectors are recovered"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block against $BSC_RPC",
      "Confirm token balances at 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b",
      "Recover ABI via heimdall-rs or panoramix decompilation of runtime bytecode",
      "Identify any selector matching withdraw/redeem/claim/sweep/release/migrate patterns",
      "Check proxy slots and resolve implementation if proxied"
    ],
    "transaction_sequence": [
      "PENDING selector recovery — populate after live context step above"
    ],
    "expected_assertions": [
      "attacker token balance after call > attacker token balance before call",
      "contract token balance decreases by attacker gain amount",
      "no privileged role was required to trigger the call"
    ]
  },
  "rejection_reason": ""
}
```

**Rationale for `NEEDS_LIVE_CONTEXT`:**

The candidate cannot be promoted to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because every required input for a concrete exploit hypothesis is absent:

| Required input | Status |
|---|---|
| Contract source / ABI | Unknown verification status — not confirmed available |
| Selector inventory | None |
| Deployer address | Empty |
| Funding cluster | Empty |
| Token breakdown | Not in brief |
| Proxy/impl state | Not checked |
| Transaction patterns | Zero volume, zero liquidity — anomalous but unexplained |

The $550M TVL with zero volume and zero liquidity at a fresh, hidden, unidentified contract is the primary signal that warrants continued investigation rather than rejection. The `recon_bravo_then_corecritical` next action assigned by the scoring engine is consistent with this verdict.