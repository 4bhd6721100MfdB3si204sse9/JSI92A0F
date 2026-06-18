// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface Vm {
    function envOr(string calldata name, string calldata defaultValue) external returns (string memory);
    function createSelectFork(string calldata url) external returns (uint256);
    function prank(address msgSender) external;
    function expectRevert() external;
}

interface IVault {
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
}

contract VaultLiveAuthTest {
    Vm internal constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    IVault internal constant vault = IVault(0x238a358808379702088667322f80aC48bAd5e6c4);
    address internal constant EXPECTED_OWNER = 0xfa206DAB60c014bEb6833004D8848910165e6047;
    address internal constant ATTACKER = address(0xBEEF);
    address internal constant BSC_USDT = 0x55d398326f99059fF775485246999027B3197955;

    function setUp() public {
        string memory rpcUrl = vm.envOr("RPC_URL", "");
        if (bytes(rpcUrl).length == 0) rpcUrl = vm.envOr("BSC_RPC_URL", "");
        vm.createSelectFork(rpcUrl);
    }

    function testLiveIdentityAndOwnerContract() public view {
        require(address(vault).code.length > 0, "vault has no code");
        require(EXPECTED_OWNER.code.length > 0, "owner is not contract");
        require(vault.owner() == EXPECTED_OWNER, "unexpected owner");
    }

    function testUnprivilegedCannotRegisterApp() public {
        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.registerApp(ATTACKER);
    }

    function testUnprivilegedOperatorApprovalIsSelfScoped() public {
        vm.prank(ATTACKER);
        bool ok = vault.setOperator(address(0xCAFE), true);
        require(ok, "setOperator failed");
        require(vault.isOperator(ATTACKER, address(0xCAFE)), "operator not set for caller");
        require(!vault.isOperator(EXPECTED_OWNER, address(0xCAFE)), "operator leaked to owner scope");
    }

    function testDirectValueMovingSelectorsNeedLockerOrBalanceContext() public {
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
    }

    function testSurplusTokenTransfersDoNotBypassBalanceOrAllowance() public {
        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.transfer(address(0xCAFE), BSC_USDT, 1);

        vm.prank(ATTACKER);
        vm.expectRevert();
        vault.transferFrom(EXPECTED_OWNER, ATTACKER, BSC_USDT, 1);
    }

    function testLiveReadStateIsReachable() public view {
        vault.getLocker();
        vault.getUnsettledDeltasCount();
        vault.getVaultReserve();
        vault.isAppRegistered(ATTACKER);
    }
}
