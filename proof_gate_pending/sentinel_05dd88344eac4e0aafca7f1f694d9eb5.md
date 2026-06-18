<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_4ecfc96b-0786-42d0-bc14-d91c86ae42f8?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4` has no entry anywhere in the repository — no deepwiki brief, no scored run, no prior triage. The `deepwiki_candidates/` directory is empty and no run output references this address. The candidate brief itself carries `verified_source: null`, empty `deployer_address`, empty `funding_cluster_id`, and zero selector or proxy information. There is no basis to form an exploit hypothesis without live chain data.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4",
    "name": "0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 94
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with ~$403K TVL, immediate balance spike, no verified source, no known deployer, and no protocol identity. The combination of hidden_high_value_contract + balance_spike + unknown_verification_status on a high-weight chain (BSC:10) places it squarely in the funded-unverified-contract surface. Value is live and material, but zero selector, proxy, or deployer data is available to form an exploit path.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "No verified source exists. Bytecode must be fetched and decompiled (e.g. via Heimdall or 4byte.directory lookup) to enumerate public selectors and identify value-moving functions such as withdraw, claim, sweep, redeem, or migrate.",
      "command_or_source": "cast code 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 --rpc-url $BSC_RPC | heimdall decompile --stdin"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If a live implementation exists, it may expose additional or different selectors than the proxy shell. Storage slot reads are required before any selector analysis is meaningful.",
      "command_or_source": "cast storage 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $403K TVL is attributed to token balances (bluechip_token_balance, known_asset_balance tags), but the specific tokens and amounts are unknown. Identifying which tokens are held determines whether the balance is withdrawable principal or locked collateral.",
      "command_or_source": "BSCScan token holdings tab for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4, or cast call <token> 'balanceOf(address)(uint256)' 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 --rpc-url $BSC_RPC"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "deployer_address and funding_cluster_id are both empty. The deployer identity and funding source are required to assess whether this is a redeploy of a closed project, a known rug pattern, or a legitimate protocol. Without this, no cluster-based exploit hypothesis is possible.",
      "command_or_source": "BSCScan internal transactions for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 — identify creation tx, then trace deployer wallet history"
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "reason": "Zero volume24h and no tx history in the brief means it is unknown whether any public entrypoints have been called. Transaction history reveals whether the contract has been interacted with, which callers have touched it, and whether any value-moving selectors are reachable by an unprivileged caller.",
      "command_or_source": "BSCScan transactions tab for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, unstake, claim, liquidate, release, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source is null; unknown_verification_status tag present. No ABI, no selector list, no decompiled output available in the repository or brief.",
      "why_it_matters": "Without selectors, it is impossible to determine whether any public function can move the $403K balance to an arbitrary caller. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract bytecode must be recoverable and decompilable",
      "At least one public selector must exist that moves tokens or native value to a caller-controlled address",
      "No access control (owner check, whitelist, or merkle proof) must gate that selector"
    ],
    "call_sequence": [
      "UNKNOWN — selector enumeration required before any call sequence can be constructed"
    ],
    "expected_gain": "Up to ~$403K in bluechip token balance if an unrestricted sweep or withdraw selector exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Bytecode decompilation output identifying at least one value-moving selector",
      "Token balance confirmation via balanceOf calls"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot construct until selectors are recovered"
    ],
    "expected_assertions": [
      "attacker token balance increases by > 0 after call",
      "contract token balance decreases by matching amount",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate is not rejected because the live value (~$403K) is real and material, the `balance_spike` + `hidden_high_value_contract` signal combination is a genuine priority surface per the hunt plan, and the `unknown_verification_status` tag means the contract has not been ruled out as a funded-unverified target. However, `NEEDS_LOCAL_PROOF` cannot be issued because there is no source, no selector list, no deployer, no proxy state, and no transaction history — every field required to construct an exploit hypothesis is missing. The five live-context items above are the minimum required before this candidate can be re-triaged. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** HUNT_PLAN.md (L75-84)
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

**File:** blueprints/sentinel_fund_reward_discovery.json (L17-19)
```json
    "funded unverified contracts with public selectors",
    "proxy contracts with live funds or recent implementation changes",
    "bot-discovered target protocols repeatedly touched before profit sweeps"
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