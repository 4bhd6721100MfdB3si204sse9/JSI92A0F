// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";

contract Snapshot is Script {
    address internal constant TARGET = 0x238a358808379702088667322f80ac48bad5e6c4;

    function run() external view {
        console2.log("chain", "bsc");
        console2.log("target", TARGET);
        console2.log("code length", TARGET.code.length);
        console2.log("native balance", TARGET.balance);
    }
}
