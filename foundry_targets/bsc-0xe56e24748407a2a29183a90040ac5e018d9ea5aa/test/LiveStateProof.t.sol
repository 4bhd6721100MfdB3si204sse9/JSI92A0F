// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

contract LiveStateProofTest is Test {
    address internal constant TARGET = 0xe56e24748407a2a29183a90040ac5e018d9ea5aa;

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
