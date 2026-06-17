// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

contract LiveStateProofTest is Test {
    address internal constant TARGET = 0x238a358808379702088667322f80ac48bad5e6c4;

    function setUp() public {
        string memory rpcUrl = vm.envString("RPC_URL");
        vm.createSelectFork(rpcUrl);
    }

    function testTargetHasCodeOnLiveFork() public view {
        assertGt(TARGET.code.length, 0, "target has no code on selected fork");
    }

    function testSnapshotNativeBalanceReadable() public view {
        uint256 balance = TARGET.balance;
        assertGe(balance, 0);
    }
}
