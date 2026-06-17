from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bot_runtime import batch_limit


DEFAULT_INPUT_DIRS = ["proof_gate_results", "deepwiki_candidates", "needs_local_proof", "deepwiki_briefs"]
MATERIALIZABLE_VERDICTS = {"NEEDS_LOCAL_PROOF", "HIGH_CONFIDENCE_CANDIDATE"}


def materialize_targets(input_dirs: list[str], output_dir: str, limit: int) -> list[Path]:
    candidates = _candidate_files(input_dirs)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for path in candidates[:batch_limit(limit)]:
        payload = _load_payload(path)
        if not _is_materializable(payload, path):
            continue
        candidate = normalize_candidate(payload, path)
        if not candidate["address"]:
            continue
        target_dir = output / f"{candidate['chain']}-{candidate['address'].lower()}"
        write_foundry_target(target_dir, candidate, payload, path)
        written.append(target_dir)

    if not written:
        raise FileNotFoundError("no materializable JSON candidates with chain/address found")
    return written


def normalize_candidate(payload: dict[str, Any], source: Path) -> dict[str, Any]:
    candidate = _payload_dict(payload, "candidate", "candidate_context")
    active_target = payload.get("active_target") if isinstance(payload.get("active_target"), dict) else {}
    raw_row = payload.get("raw_scored_row") if isinstance(payload.get("raw_scored_row"), dict) else {}
    score = payload.get("score") if isinstance(payload.get("score"), dict) else {}
    live_evidence = payload.get("live_evidence") if isinstance(payload.get("live_evidence"), dict) else {}
    value_at_risk = payload.get("value_at_risk") if isinstance(payload.get("value_at_risk"), dict) else {}

    chain = _first(candidate.get("chain"), active_target.get("chain"), payload.get("chain"), raw_row.get("chain"), "unknown")
    address = _first(candidate.get("address"), active_target.get("address"), payload.get("address"), raw_row.get("address"), "")
    name = _first(candidate.get("name"), payload.get("title"), raw_row.get("name"), source.stem)
    next_action = _first(score.get("next_action"), candidate.get("next_action"), raw_row.get("next_action"), payload.get("proof_route"), "")

    return {
        "schema_version": "foundry-materialized-target-v1",
        "name": name,
        "chain": str(chain).lower(),
        "address": str(address).lower(),
        "entity_type": _first(candidate.get("entity_type"), raw_row.get("entity_type"), ""),
        "category": _first(candidate.get("category"), raw_row.get("category"), ""),
        "source": _first(candidate.get("source"), raw_row.get("source"), ""),
        "source_file": str(source),
        "next_action": next_action,
        "score": _first(score.get("value"), payload.get("score"), raw_row.get("score"), 0),
        "value_at_risk": value_at_risk or {
            "usd": max(float(raw_row.get("liquidity_usd", 0) or 0), float(raw_row.get("tvl_usd", 0) or 0)),
            "liquidity_usd": raw_row.get("liquidity_usd", 0),
            "tvl_usd": raw_row.get("tvl_usd", 0),
        },
        "live_evidence": live_evidence or {
            "verified_source": raw_row.get("verified_source"),
            "deployer_address": raw_row.get("deployer_address", ""),
            "funding_cluster_id": raw_row.get("funding_cluster_id", ""),
            "tags": raw_row.get("tags", []),
        },
        "paid_scope_match": payload.get("paid_scope_match", ""),
        "hard_gates": payload.get("hard_gates", {}),
        "live_preconditions": payload.get("live_preconditions", []),
        "local_proof_required": payload.get("local_proof_required", {}),
    }


def write_foundry_target(target_dir: Path, candidate: dict[str, Any], payload: dict[str, Any], source: Path) -> None:
    (target_dir / "src" / "interfaces").mkdir(parents=True, exist_ok=True)
    (target_dir / "script").mkdir(parents=True, exist_ok=True)
    (target_dir / "test").mkdir(parents=True, exist_ok=True)
    (target_dir / "abis").mkdir(parents=True, exist_ok=True)

    (target_dir / "foundry.toml").write_text(_foundry_toml(candidate), encoding="utf-8")
    (target_dir / ".env.example").write_text(_env_example(candidate), encoding="utf-8")
    (target_dir / "addresses.json").write_text(json.dumps(_addresses(candidate), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_dir / "live_state.json").write_text(json.dumps(_live_state(candidate, payload, source), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_dir / "balances.json").write_text(json.dumps(_balances(candidate, payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_dir / "token_balances.json").write_text(json.dumps(_token_balances(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_dir / "proxy.json").write_text(json.dumps(_proxy(candidate, payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_dir / "abis" / "Target.json").write_text(json.dumps(_abi(payload), indent=2) + "\n", encoding="utf-8")
    (target_dir / "src" / "interfaces" / "ITarget.sol").write_text(_interface_sol(), encoding="utf-8")
    (target_dir / "script" / "Snapshot.s.sol").write_text(_snapshot_script(candidate), encoding="utf-8")
    (target_dir / "test" / "LiveStateProof.t.sol").write_text(_live_state_test(candidate), encoding="utf-8")
    (target_dir / "README.md").write_text(_readme(candidate), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Materialize staged Sentinel candidates into Foundry target repos.")
    parser.add_argument("--input-dir", action="append", default=DEFAULT_INPUT_DIRS)
    parser.add_argument("--output", default="foundry_targets")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)

    written = materialize_targets(args.input_dir, args.output, args.limit)
    print(f"foundry_targets={len(written)} output={args.output}")
    for path in written:
        print(path)
    return 0


def _candidate_files(input_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for directory in input_dirs:
        root = Path(directory)
        if root.exists():
            files.extend(root.glob("*.json"))
    return sorted(files)


def _load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_materializable(payload: dict[str, Any], path: Path) -> bool:
    if path.parent.name in {"deepwiki_briefs", "deepwiki_candidates"}:
        return True
    verdict = str(payload.get("verdict") or payload.get("deepwiki_verdict") or "").upper()
    return verdict in MATERIALIZABLE_VERDICTS


def _payload_dict(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _foundry_toml(candidate: dict[str, Any]) -> str:
    chain = _env_prefix(candidate["chain"])
    return f"""[profile.default]
src = "src"
test = "test"
script = "script"
out = "out"
libs = ["lib"]
solc_version = "0.8.24"
optimizer = true
optimizer_runs = 200
ffi = false

[rpc_endpoints]
{candidate["chain"]} = "${{{chain}_RPC_URL}}"
"""


def _env_example(candidate: dict[str, Any]) -> str:
    prefix = _env_prefix(candidate["chain"])
    return f"""# Copy to .env and fill the RPC URL before running forge.
CHAIN={candidate["chain"]}
TARGET_ADDRESS={candidate["address"]}
RPC_URL=
{prefix}_RPC_URL=
"""


def _addresses(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "chain": candidate["chain"],
        "target": candidate["address"],
        "name": candidate["name"],
        "next_action": candidate["next_action"],
    }


def _live_state(candidate: dict[str, Any], payload: dict[str, Any], source: Path) -> dict[str, Any]:
    return {
        "schema_version": "live-state-materialization-v1",
        "materialized_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(source),
        "candidate": candidate,
        "raw_candidate_payload": payload,
        "discovery_limitations": [
            "Mappings and private structs are not globally enumerable without known keys.",
            "Known keys should be recovered from events, calldata, public getters, and source logic.",
            "Run the Foundry fork test and Snapshot script against a real RPC URL to confirm current live values.",
        ],
    }


def _balances(candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("raw_scored_row") if isinstance(payload.get("raw_scored_row"), dict) else {}
    value = candidate.get("value_at_risk", {})
    return {
        "chain": candidate["chain"],
        "target": candidate["address"],
        "native_balance": {
            "wei": None,
            "usd_estimate": None,
            "source": "fill by running script/Snapshot.s.sol or live enrichment",
        },
        "value_at_risk": value,
        "liquidity_usd": raw.get("liquidity_usd", value.get("liquidity_usd")),
        "tvl_usd": raw.get("tvl_usd", value.get("tvl_usd")),
    }


def _token_balances(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("raw") if isinstance(payload.get("raw"), dict) else {}
    token_balances = raw.get("token_balances", [])
    if not token_balances:
        raw_row = payload.get("raw_scored_row") if isinstance(payload.get("raw_scored_row"), dict) else {}
        raw_source = raw_row.get("raw") if isinstance(raw_row.get("raw"), dict) else {}
        token_balances = raw_source.get("token_balances", [])
    return {"token_balances": token_balances, "source": "candidate payload or live enrichment"}


def _proxy(candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "chain": candidate["chain"],
        "target": candidate["address"],
        "eip1967_implementation_slot": "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
        "eip1967_admin_slot": "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103",
        "implementation": _nested_get(payload, ["active_target", "implementation"]) or _nested_get(payload, ["proxy", "implementation"]),
        "admin": _nested_get(payload, ["active_target", "admin"]) or _nested_get(payload, ["proxy", "admin"]),
        "source": "candidate payload if available; otherwise run cast storage against the listed slots",
    }


def _abi(payload: dict[str, Any]) -> Any:
    abi = _nested_get(payload, ["raw", "source_code", "ABI"]) or _nested_get(payload, ["raw_scored_row", "raw", "source_code", "ABI"])
    if isinstance(abi, str):
        try:
            return json.loads(abi)
        except json.JSONDecodeError:
            return []
    return abi if isinstance(abi, list) else []


def _interface_sol() -> str:
    return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface ITarget {}
"""


def _snapshot_script(candidate: dict[str, Any]) -> str:
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";

contract Snapshot is Script {{
    address internal constant TARGET = {candidate["address"]};

    function run() external view {{
        console2.log("chain", "{candidate["chain"]}");
        console2.log("target", TARGET);
        console2.log("code length", TARGET.code.length);
        console2.log("native balance", TARGET.balance);
    }}
}}
"""


def _live_state_test(candidate: dict[str, Any]) -> str:
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

contract LiveStateProofTest is Test {{
    address internal constant TARGET = {candidate["address"]};

    function setUp() public {{
        string memory rpcUrl = vm.envString("RPC_URL");
        vm.createSelectFork(rpcUrl);
    }}

    function testTargetHasCodeOnLiveFork() public view {{
        assertGt(TARGET.code.length, 0, "target has no code on selected fork");
    }}

    function testSnapshotNativeBalanceReadable() public view {{
        uint256 balance = TARGET.balance;
        assertGe(balance, 0);
    }}
}}
"""


def _readme(candidate: dict[str, Any]) -> str:
    return f"""# Foundry Target: {candidate["name"]}

Chain: `{candidate["chain"]}`
Target: `{candidate["address"]}`
Route: `{candidate["next_action"]}`

## Setup

```bash
forge install foundry-rs/forge-std
cp .env.example .env
# edit .env and set RPC_URL
forge test -vvv
forge script script/Snapshot.s.sol --rpc-url "$RPC_URL"
```

## What This Repo Contains

- `addresses.json`: target identity and route
- `live_state.json`: Sentinel/DeepWiki context and known live limitations
- `balances.json`: known value-at-risk data plus fields to fill from RPC
- `token_balances.json`: token balances from enrichment when available
- `proxy.json`: EIP-1967 implementation/admin slots and known proxy data
- `abis/Target.json`: verified ABI when available
- `test/LiveStateProof.t.sol`: first fork sanity checks
- `script/Snapshot.s.sol`: basic live snapshot script

## Important Limitation

Private mappings and structs cannot be fully enumerated from chain state unless keys are known. Recover keys from events, calldata, getters, source logic, and prior transactions, then add focused tests.
"""


def _nested_get(payload: dict[str, Any], path: list[str]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return ""


def _env_prefix(chain: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", chain.upper()).strip("_") or "CHAIN"


if __name__ == "__main__":
    sys.exit(main())
