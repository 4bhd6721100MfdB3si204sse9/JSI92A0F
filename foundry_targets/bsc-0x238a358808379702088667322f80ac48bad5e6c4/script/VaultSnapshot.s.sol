// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IVault {
    function owner() external view returns (address);
    function getLocker() external view returns (address);
    function getUnsettledDeltasCount() external view returns (uint256);
    function getVaultReserve() external view returns (address currency, uint256 amount);
}

contract VaultSnapshot {
    IVault internal constant vault = IVault(0x238a358808379702088667322f80aC48bAd5e6c4);

    function run() external view {
        address owner = vault.owner();
        address locker = vault.getLocker();
        uint256 unsettled = vault.getUnsettledDeltasCount();
        (address reserveCurrency, uint256 reserveAmount) = vault.getVaultReserve();

        owner;
        locker;
        unsettled;
        reserveCurrency;
        reserveAmount;
    }
}
