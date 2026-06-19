<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_c7cbd4b8-634e-4670-8d4e-1d79e565d5bd?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0x73d8bd54f7cf5fab43fe4ef40a62d390644946db` does not appear anywhere in this repository — not in `state/`, `runs/`, `deepwiki_briefs/`, or `foundry_targets/`. All repository data uses placeholder addresses. The candidate brief itself contains critical data-quality problems that prevent any meaningful triage.

**Key disqualifying data issues:**
- `tvl_usd: 6.395501978040165e+33` (~$6.4 × 10³³) is a physically impossible value — it exceeds total global wealth by ~19 orders of magnitude. This is almost certainly a raw `uint256` token balance (e.g., in wei or token base units) that was never divided by the token's decimal factor before being stored as a USD figure. The real balance is unknown.
- `verified_source: null` — source code availability is unknown, no ABI, no selectors.
- `deployer_address: ""` — no deployer, no funding cluster, no deployment tx.
- `volume24h_usd: 0.0`, `liquidity_usd: 0.0`, `fdv_usd: 0.0` — no market activity signal.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
    "name": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh unverified Ethereum contract with an immediate balance spike and no source code. Tags indicate real token holdings. The reported TVL figure is a data artifact (raw uint256 balance without decimal normalization) so actual USD value at risk is unknown but non-zero. No selectors, deployer, proxy state, or transaction history are available to assess exploitability.",
  "live_context_required": [
    {
      "name": "real_token_balances",
      "reason": "The tvl_usd value of 6.395e+33 is a decimal-normalization artifact. Actual token addresses held, raw balances, and correct USD conversion are required to confirm real value at risk.",
      "command_or_source": "cast call 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db --rpc-url $ETH_RPC; etherscan token holdings lookup for address"
    },
    {
      "name": "source_code_or_bytecode_selectors",
      "reason": "verified_source is null. Without source or ABI, no value-moving selectors can be identified. Bytecode disassembly or 4byte.directory lookup is required.",
      "command_or_source": "cast code 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db --rpc-url $ETH_RPC | evmdis or heimdall-rs decompile"
    },
    {
      "name": "deployer_and_deployment_tx",
      "reason": "deployer_address is empty. Deployer identity and funding source are needed to assess whether this is a rug-redeploy, a known protocol, or a novel contract.",
      "command_or_source": "etherscan contract creation tx lookup for 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db"
    },
    {
      "name": "proxy_and_admin_state",
      "reason": "Unknown whether this is a proxy. If it is, the implementation address and any recent upgrades are critical to assess storage mismatch or unauthorized-upgrade risk.",
      "command_or_source": "cast storage 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "transaction_history",
      "reason": "volume24h_usd is 0.0 but balance_spike and immediate_balance_spike tags are set. Need to identify the funding transaction(s), any prior calls, and whether any bot has already interacted.",
      "command_or_source": "etherscan internal tx + normal tx list for 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or sweep (unverified contract with no access control evidence)",
    "missing access control on value-moving functions",
    "phantom accounting (fresh contract, unknown share/debt model)",
    "proxy or implementation storage mismatch"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown",
      "evidence": "verified_source is null; no ABI or bytecode analysis has been performed in this pipeline run",
      "why_it_matters": "No selector basis exists. All exploit family hypotheses are speculative until bytecode is recovered and disassembled."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Real token balance confirmed after decimal normalization",
      "At least one public selector that moves, releases, or claims value",
      "No caller restriction on that selector"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector enumeration from bytecode"
    ],
    "expected_gain": "Unknown — contingent on real balance confirmation and selector recovery"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Confirm real token balances and token addresses",
      "Recover selectors via bytecode disassembly",
      "Identify any proxy/implementation layout",
      "Pin fork block to current live state"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot construct until selectors and value-moving paths are known"
    ],
    "expected_assertions": [
      "BLOCKED — cannot define assertions without source or selector basis"
    ]
  },
  "rejection_reason": ""
}
```

**Summary:** The candidate cannot be promoted past `NEEDS_LIVE_CONTEXT`. The reported TVL is a data pipeline artifact (raw integer balance without decimal normalization), source code is absent, no selectors are known, and the deployer is unidentified. All five live-context items above must be resolved before a local proof attempt is meaningful. The hard rule "prefer REJECT over speculation" is satisfied here by `NEEDS_LIVE_CONTEXT` rather than `REJECT` because the balance-spike tags do indicate a real on-chain event worth one recon pass.