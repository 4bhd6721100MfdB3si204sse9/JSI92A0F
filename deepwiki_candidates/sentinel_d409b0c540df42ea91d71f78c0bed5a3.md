<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_93dc8cfd-a88c-4071-bdf3-7efd8c584fb3?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/23-bsc-0x9996874dbd891c3ecd601eab79d51f92e92d50ee.json",
    "chain": "bsc",
    "address": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "name": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "A fresh, unverified BSC contract holds approximately $15.7M in stablecoins and known assets with zero 24h volume and no public protocol identity. The combination of hidden_high_value_contract, unknown_verification_status, and stablecoin_balance on a fresh deployment is a high-priority surface for unauthorized withdrawal or sweep paths. No source, no selectors, no deployer, and no proxy state are available — live recon is required before any exploit hypothesis can be formed.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "Contract is unverified. Without ABI or decompiled selectors we cannot identify any value-moving functions (withdraw, sweep, claim, redeem, transfer, rescue, etc.).",
      "command_or_source": "cast code 0x9996874dbd891c3ecd601eab79d51f92e92d50ee --rpc-url $BSC_RPC | python3 -c 'import sys,evmdasm; print(evmdasm.disassemble(bytes.fromhex(sys.stdin.read().strip()[2:])))' ; OR use heimdall-rs / panoramix to recover selectors and function signatures from bytecode"
    },
    {
      "name": "proxy_slot_check",
      "reason": "Fresh unverified contracts with large balances are frequently proxy contracts. A proxy pointing to a vulnerable or attacker-controlled implementation would be immediately exploitable.",
      "command_or_source": "cast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  # EIP-1967 logic slot\ncast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0xb53127684a568b3173ae13b9f8a6016f243e3b8a --rpc-url $BSC_RPC  # EIP-1967 admin slot\ncast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url $BSC_RPC  # OpenZeppelin legacy proxy slot"
    },
    {
      "name": "erc20_token_balances",
      "reason": "Tags confirm stablecoin_balance and known_asset_balance. We need the exact token addresses and amounts to understand what is extractable and whether any token has a public transfer or sweep path.",
      "command_or_source": "Use BscScan token holdings API: https://api.bscscan.com/api?module=account&action=tokenlist&address=0x9996874dbd891c3ecd601eab79d51f92e92d50ee&apikey=$BSCSCAN_KEY\nOR: cast call <token_address> 'balanceOf(address)(uint256)' 0x9996874dbd891c3ecd601eab79d51f92e92d50ee --rpc-url $BSC_RPC"
    },
    {
      "name": "deployer_address_and_funding_history",
      "reason": "Deployer address is missing from the brief. Identifying the deployer reveals whether this is a redeploy from a closed project, a known scam cluster, or a legitimate protocol. Funding source reveals whether user deposits are already inside.",
      "command_or_source": "BscScan creation tx: https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x9996874dbd891c3ecd601eab79d51f92e92d50ee&apikey=$BSCSCAN_KEY\nThen trace deployer wallet: cast tx <creation_tx_hash> --rpc-url $BSC_RPC"
    },
    {
      "name": "recent_transaction_calldata_patterns",
      "reason": "With zero 24h volume but $15.7M TVL, recent historical transactions may reveal which selectors have been called, who the depositors are, and whether any withdrawal or admin calls have been made.",
      "command_or_source": "BscScan tx list: https://api.bscscan.com/api?module=account&action=txlist&address=0x9996874dbd891c3ecd601eab79d51f92e92d50ee&sort=desc&apikey=$BSCSCAN_KEY\nExtract 4-byte selectors from input fields and resolve via https://www.4byte.directory/"
    },
    {
      "name": "owner_admin_role_slots",
      "reason": "If an owner or admin role exists and is set to a zero address, a dead address, or is publicly callable for initialization, an unprivileged attacker may be able to claim ownership and sweep funds.",
      "command_or_source": "cast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x0 --rpc-url $BSC_RPC  # slot 0 (common owner slot)\ncast call 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 'owner()(address)' --rpc-url $BSC_RPC\ncast call 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 'admin()(address)' --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds",
    "phantom accounting where shares, debt, or rewards are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source, no recovered selectors",
      "evidence": "verified_source is null; unknown_verification_status tag is set; no ABI or bytecode analysis has been performed in this pass",
      "why_it_matters": "Without selectors we cannot confirm whether any public value-moving function exists. This is the primary blocker for forming a concrete exploit hypothesis."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Selectors must be recovered from bytecode or calldata to identify any public withdraw, sweep, claim, or transfer function",
      "Proxy implementation address (if any) must be resolved to check for authorization gaps",
      "Owner/admin slot must be checked for zero address or uninitialized state that allows takeover"
    ],
    "call_sequence": [
      "BLOCKED — no call sequence can be constructed without selector recovery"
    ],
    "expected_gain": "Unknown — up to $15,712,243 in stablecoins and known assets if a public value-moving path exists without access control"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block with --fork-url $BSC_RPC",
      "Confirm token balances at 0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
      "Recover and resolve all 4-byte selectors from bytecode",
      "Identify proxy implementation if applicable"
    ],
    "transaction_sequence": [
      "BLOCKED — populate after selector recovery and proxy resolution"
    ],
    "expected_assertions": [
      "BLOCKED — populate after live context is gathered"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate scores 93 and holds ~$15.7M in stablecoins on BSC, which is a meaningful value-at-risk. However, every field that would allow a concrete exploit hypothesis is missing:

- `verified_source` is `null` — no ABI, no function names, no logic visible
- `deployer_address` is empty — no provenance, no cluster linkage
- `funding_cluster_id` is empty — no redeploy signal
- `volume24h_usd` is 0 — no recent calldata to mine for selectors
- No proxy/admin state, no selector list, no token addresses

The hard rules require preferring `REJECT` over speculation, and `NEEDS_LOCAL_PROOF` only when selector/balance/source evidence is sufficient for a fork test. Neither condition is met. The contract is interesting enough to warrant live recon (large stablecoin balance, fresh, hidden, unverified) but not enough to attempt a proof without first running the six live-context queries above.

The `recon_bravo_then_corecritical` next action from the scoring engine is consistent with this verdict. [1](#0-0) [2](#0-1)

### Citations

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L195-201)
```markdown
Routes:

- `REJECT` -> `rejected_by_deepwiki/` only when `SAVE_REJECTED_DEEPWIKI=1`
- `NEEDS_LIVE_CONTEXT` -> `needs_live_context/`
- `NEEDS_LOCAL_PROOF` -> `needs_local_proof/`
- `HIGH_CONFIDENCE_CANDIDATE` -> `deepwiki_candidates/`
- parse failure -> `deepwiki_unknown/`
```

**File:** HUNT_PLAN.md (L59-74)
```markdown
## Triage Rule

Score only protocols that satisfy at least one of these:

1. user funds are already deposited on-chain
2. there is a live reward pool or claimable emission
3. there is a public withdraw/redeem/claim path
4. the protocol is newly deployed, unverified, or forked from a risky pattern
5. a bot or executor repeatedly reveals the same target path

Reject candidates that only show:

- theoretical math issues without value movement
- liveness or UX friction without extraction
- admin-only misuse unless the admin key compromise is part of the proof

```