from __future__ import annotations

import argparse
import ast
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TARGET = "0x238a358808379702088667322f80ac48bad5e6c4"
TARGET_CHECKSUM = "0x238a358808379702088667322f80aC48bAd5e6c4"
OWNER = "0xfa206DAB60c014bEb6833004D8848910165e6047"
PROJECT_NAME = f"bsc-{TARGET}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a live Foundry target for PancakeSwap Infinity Vault.")
    parser.add_argument("--target-html", default="/private/tmp/bscscan-0x238a.html")
    parser.add_argument("--owner-html", default="/private/tmp/bscscan-owner.html")
    parser.add_argument("--output", default=f"foundry_targets/{PROJECT_NAME}")
    args = parser.parse_args()

    target_html = Path(args.target_html).read_text(encoding="utf-8")
    owner_html = Path(args.owner_html).read_text(encoding="utf-8")
    output = Path(args.output)

    contract_json = _extract_editor_contract_json(target_html)
    owner_contract_json = _extract_editor_contract_json(owner_html)
    abi = _extract_abi(target_html)
    owner_abi = _extract_abi(owner_html)
    recent_txs = _extract_quick_export(target_html, "quickExportCsvData")
    recent_internal_txs = _extract_quick_export(target_html, "quickExportInternalTxsData")

    _write_foundry_project(output, contract_json, owner_contract_json, abi, owner_abi, recent_txs, recent_internal_txs)
    print(f"prepared={output}")
    print(f"sources={len(contract_json.get('sources', {}))}")
    print(f"abi_entries={len(abi)}")
    print(f"recent_txs={len(recent_txs)}")
    print(f"recent_internal_txs={len(recent_internal_txs)}")
    return 0


def _extract_editor_contract_json(page: str) -> dict[str, Any]:
    decoded = _extract_js_string_assignment(page, "var editor_contractJsonData")
    decoded = _strip_js_only_json_escapes(decoded)
    return json.loads(decoded)


def _extract_abi(page: str) -> list[dict[str, Any]]:
    match = re.search(r"<pre id='js-copytextarea2'.*?>(.*?)</pre>", page, flags=re.DOTALL)
    if not match:
        return []
    return json.loads(html.unescape(match.group(1)))


def _extract_quick_export(page: str, variable: str) -> list[dict[str, Any]]:
    try:
        decoded = _extract_js_string_assignment(page, f"const {variable}")
    except ValueError:
        return []
    return json.loads(decoded)


def _extract_js_string_assignment(page: str, assignment_prefix: str) -> str:
    marker = f"{assignment_prefix} = '"
    start = page.find(marker)
    if start < 0:
        raise ValueError(f"{assignment_prefix} not found")
    start += len(marker)
    end = page.find("'\n        var editor_activeFile", start)
    if end < 0:
        end = page.find("'\r\n        var editor_activeFile", start)
    if end < 0:
        end = page.find("';\n", start)
    if end < 0:
        end = page.find("';", start)
    if end < 0:
        raise ValueError(f"{assignment_prefix} terminator not found")
    return _decode_js_single_quoted(page[start:end])


def _decode_js_single_quoted(raw: str) -> str:
    # BscScan embeds JSON inside JavaScript single-quoted strings. Python's
    # literal parser handles the JS-style escapes we need here, including \'.
    return ast.literal_eval("'" + raw.replace("\\\n", "") + "'")


def _strip_js_only_json_escapes(value: str) -> str:
    return re.sub(r'\\([^"\\/bfnrtu])', r"\1", value)


def _write_foundry_project(
    output: Path,
    contract_json: dict[str, Any],
    owner_contract_json: dict[str, Any],
    abi: list[dict[str, Any]],
    owner_abi: list[dict[str, Any]],
    recent_txs: list[dict[str, Any]],
    recent_internal_txs: list[dict[str, Any]],
) -> None:
    (output / "src").mkdir(parents=True, exist_ok=True)
    (output / "test").mkdir(parents=True, exist_ok=True)
    (output / "script").mkdir(parents=True, exist_ok=True)
    (output / "abis").mkdir(parents=True, exist_ok=True)
    (output / "source-artifacts" / "owner").mkdir(parents=True, exist_ok=True)
    (output / "live-context").mkdir(parents=True, exist_ok=True)

    for source_path, source in sorted(contract_json.get("sources", {}).items()):
        content = source.get("content", "")
        destination = output / source_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    for source_path, source in sorted(owner_contract_json.get("sources", {}).items()):
        content = source.get("content", "")
        destination = output / "source-artifacts" / "owner" / source_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    settings = _load_settings(contract_json)
    (output / "foundry.toml").write_text(_foundry_toml(settings), encoding="utf-8")
    (output / ".env.example").write_text(_env_example(), encoding="utf-8")
    (output / "remappings.txt").write_text(_remappings(settings), encoding="utf-8")
    (output / "abis" / "Vault.json").write_text(json.dumps(abi, indent=2) + "\n", encoding="utf-8")
    (output / "abis" / "OwnerGnosisSafeProxy.json").write_text(json.dumps(owner_abi, indent=2) + "\n", encoding="utf-8")
    (output / "source-artifacts" / "bscscan-contract-json.json").write_text(
        json.dumps(contract_json, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "source-artifacts" / "owner" / "bscscan-contract-json.json").write_text(
        json.dumps(owner_contract_json, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "live-context" / "recent-transactions.json").write_text(
        json.dumps(recent_txs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "live-context" / "recent-internal-transactions.json").write_text(
        json.dumps(recent_internal_txs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "addresses.json").write_text(json.dumps(_addresses(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "live-context" / "setup-summary.md").write_text(_setup_summary(abi, recent_txs), encoding="utf-8")
    (output / "README.md").write_text(_readme(), encoding="utf-8")
    (output / "test" / "VaultLiveAuth.t.sol").write_text(_live_auth_test(), encoding="utf-8")
    (output / "script" / "VaultSnapshot.s.sol").write_text(_snapshot_script(), encoding="utf-8")

    html_dir = output / "source-artifacts" / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    for source, name in [("/private/tmp/bscscan-0x238a.html", "vault-bscscan.html"), ("/private/tmp/bscscan-owner.html", "owner-bscscan.html")]:
        source_path = Path(source)
        if source_path.exists():
            shutil.copyfile(source_path, html_dir / name)


def _load_settings(contract_json: dict[str, Any]) -> dict[str, Any]:
    settings_source = contract_json.get("sources", {}).get("settings.json", {}).get("content", "{}")
    try:
        return json.loads(settings_source)
    except json.JSONDecodeError:
        return {}


def _foundry_toml(settings: dict[str, Any]) -> str:
    optimizer = settings.get("optimizer", {})
    runs = optimizer.get("runs", 25666)
    via_ir = str(bool(settings.get("viaIR", True))).lower()
    evm_version = settings.get("evmVersion", "cancun")
    return f"""[profile.default]
src = "src"
test = "test"
script = "script"
out = "out"
libs = ["lib"]
solc_version = "0.8.26"
evm_version = "{evm_version}"
optimizer = true
optimizer_runs = {runs}
via_ir = {via_ir}
ffi = false

[rpc_endpoints]
bsc = "${{BSC_RPC_URL}}"
"""


def _env_example() -> str:
    return f"""CHAIN=bsc
TARGET_ADDRESS={TARGET}
OWNER_ADDRESS={OWNER}
RPC_URL=
BSC_RPC_URL=
BSCSCAN_API_KEY=
"""


def _remappings(settings: dict[str, Any]) -> str:
    remappings = settings.get("remappings", [])
    if not remappings:
        remappings = ["@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/"]
    return "\n".join(remappings) + "\n"


def _addresses() -> dict[str, Any]:
    return {
        "chain": "bsc",
        "target": TARGET_CHECKSUM,
        "target_label": "Pancakeswap: Infinity Vault",
        "contract_name": "Vault",
        "owner": OWNER,
        "owner_label": "GnosisSafeProxy / Safe owner contract",
        "bscscan": f"https://bscscan.com/address/{TARGET}",
        "owner_bscscan": f"https://bscscan.com/address/{OWNER}",
    }


def _setup_summary(abi: list[dict[str, Any]], recent_txs: list[dict[str, Any]]) -> str:
    functions = [entry for entry in abi if entry.get("type") == "function"]
    interesting = {"take", "clear", "transfer", "transferFrom", "settle", "settleFor", "mint", "burn", "collectFee", "setOperator", "registerApp"}
    methods: dict[str, dict[str, int]] = {}
    for tx in recent_txs:
        method = str(tx.get("Method", "unknown"))
        status = "success" if str(tx.get("Status", "")).lower() == "success" else "revert"
        methods.setdefault(method, {"success": 0, "revert": 0})[status] += 1
    return f"""# Live Setup Summary

- generated_at: `{datetime.now(timezone.utc).isoformat()}`
- target: `{TARGET_CHECKSUM}`
- label: `Pancakeswap: Infinity Vault`
- contract: `Vault`
- owner: `{OWNER}`
- owner contract: `GnosisSafeProxy`
- source: BscScan HTML embedded verified source, because anonymous Etherscan v2 API returned `Missing/Invalid API Key`.
- abi_functions: `{len(functions)}`
- priority_selectors_present: `{", ".join(sorted(name for name in interesting if any(f.get("name") == name for f in functions)))}`

## Recent Method Counts

```json
{json.dumps(methods, indent=2, sort_keys=True)}
```

## Next Audit Focus

The current code model is PancakeSwap Infinity Vault accounting. Public `take`, `clear`, `mint`, `burn`, `collectFee`, `settle`, and transfer methods exist, but exploitability depends on locker/app/operator state and whether a caller can create positive currency deltas beyond entitlement.
"""


def _readme() -> str:
    return f"""# PancakeSwap Infinity Vault Live Foundry Target

Target: `{TARGET_CHECKSUM}`
Owner: `{OWNER}` (`GnosisSafeProxy`)
Chain: `bsc`

This folder is a live Foundry project for the BSC PancakeSwap Infinity Vault. The verified Vault source and ABI were extracted from the BscScan page HTML and stored locally so fork tests can be added without depending on the explorer UI.

## Files

- `src/`: verified Vault source tree from BscScan.
- `source-artifacts/`: raw BscScan contract JSON, copied HTML evidence, and owner proxy source.
- `abis/Vault.json`: live verified ABI.
- `live-context/recent-transactions.json`: recent BscScan transaction table snapshot.
- `test/VaultLiveAuth.t.sol`: first fork tests for live authorization boundaries.
- `script/VaultSnapshot.s.sol`: live read-only snapshot helper.

## Run

```bash
cp .env.example .env
# set RPC_URL or BSC_RPC_URL to a BSC mainnet RPC
forge test -vvv
forge script script/VaultSnapshot.s.sol --rpc-url "$RPC_URL"
```
"""


def _live_auth_test() -> str:
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface Vm {{
    function envOr(string calldata name, string calldata defaultValue) external returns (string memory);
    function createSelectFork(string calldata url) external returns (uint256);
    function prank(address msgSender) external;
    function expectRevert() external;
}}

interface IVault {{
    function owner() external view returns (address);
    function getLocker() external view returns (address);
    function getUnsettledDeltasCount() external view returns (uint256);
    function getVaultReserve() external view returns (address currency, uint256 amount);
    function isAppRegistered(address app) external view returns (bool);
    function isOperator(address owner, address operator) external view returns (bool);
    function setOperator(address operator, bool approved) external returns (bool);
    function registerApp(address app) external;
    function take(address currency, address to, uint256 amount) external;
    function clear(address currency, uint256 amount) external;
    function collectFee(address currency, uint256 amount, address recipient) external;
    function mint(address to, address currency, uint256 amount) external;
    function burn(address from, address currency, uint256 amount) external;
    function settle() external payable returns (uint256);
    function settleFor(address recipient) external payable returns (uint256);
    function transfer(address receiver, address currency, uint256 amount) external returns (bool);
    function transferFrom(address sender, address receiver, address currency, uint256 amount) external returns (bool);
}}

contract VaultLiveAuthTest {{
    Vm internal constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    IVault internal constant vault = IVault({TARGET_CHECKSUM});
    address internal constant EXPECTED_OWNER = {OWNER};
    address internal constant ATTACKER = address(0xBEEF);
    address internal constant BSC_USDT = 0x55d398326f99059fF775485246999027B3197955;

    function setUp() public {{
        string memory rpcUrl = vm.envOr("RPC_URL", "");
        if (bytes(rpcUrl).length == 0) rpcUrl = vm.envOr("BSC_RPC_URL", "");
        vm.createSelectFork(rpcUrl);
    }}

    function testLiveIdentityAndOwnerContract() public view {{
        require(address(vault).code.length > 0, "vault has no code");
        require(EXPECTED_OWNER.code.length > 0, "owner is not contract");
        require(vault.owner() == EXPECTED_OWNER, "unexpected owner");
    }}

    function testUnprivilegedCannotRegisterApp() public {{
        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.registerApp(ATTACKER);
    }}

    function testUnprivilegedOperatorApprovalIsSelfScoped() public {{
        vm.prank(ATTACKER);
        bool ok = vault.setOperator(address(0xCAFE), true);
        require(ok, "setOperator failed");
        require(vault.isOperator(ATTACKER, address(0xCAFE)), "operator not set for caller");
        require(!vault.isOperator(EXPECTED_OWNER, address(0xCAFE)), "operator leaked to owner scope");
    }}

    function testDirectValueMovingSelectorsNeedLockerOrBalanceContext() public {{
        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.take(BSC_USDT, ATTACKER, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.clear(BSC_USDT, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.collectFee(BSC_USDT, 1, ATTACKER);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.mint(ATTACKER, BSC_USDT, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.burn(ATTACKER, BSC_USDT, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.settle();

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.settleFor(ATTACKER);
    }}

    function testSurplusTokenTransfersDoNotBypassBalanceOrAllowance() public {{
        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.transfer(address(0xCAFE), BSC_USDT, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.transferFrom(EXPECTED_OWNER, ATTACKER, BSC_USDT, 1);
    }}

    function testLiveReadStateIsReachable() public view {{
        vault.getLocker();
        vault.getUnsettledDeltasCount();
        vault.getVaultReserve();
        vault.isAppRegistered(ATTACKER);
    }}
}}
"""


def _snapshot_script() -> str:
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IVault {{
    function owner() external view returns (address);
    function getLocker() external view returns (address);
    function getUnsettledDeltasCount() external view returns (uint256);
    function getVaultReserve() external view returns (address currency, uint256 amount);
}}

contract VaultSnapshot {{
    IVault internal constant vault = IVault({TARGET_CHECKSUM});

    function run() external view {{
        address owner = vault.owner();
        address locker = vault.getLocker();
        uint256 unsettled = vault.getUnsettledDeltasCount();
        (address reserveCurrency, uint256 reserveAmount) = vault.getVaultReserve();

        owner;
        locker;
        unsettled;
        reserveCurrency;
        reserveAmount;
    }}
}}
"""


if __name__ == "__main__":
    raise SystemExit(main())
