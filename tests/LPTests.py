from brownie import *
import time
"""
Setup
"""
# Deploy Contracts
present_time = time.time()
var_asset = VarToken.deploy({'from': accounts[0]})
stable_asset = StableToken.deploy({'from': accounts[0]})
calls_center = CallOptionCenter.deploy(present_time + 1000, 10, 10,
                                       var_asset.address, stable_asset.address, {"from": accounts[0]})

rte_address, rtw_address = calls_center.getRightContractAddresses.call({
                                                                       "from": accounts[0]})
rte_contract = RightToExecute.at(rte_address)
liq_pool = ERC721LP.deploy(
    rte_address, var_asset.address, {'from': accounts[0]})

# Fund Accounts
for i in range(9):
    var_asset.mint.transact(10000, {"from": accounts[i]})
    stable_asset.mint.transact(10000, {"from": accounts[i]})

# Initialize Pool
for token_id in range(50):
    var_asset.approve.transact(
        calls_center.address, 10**18, {'from': accounts[0]})
    calls_center.mintContract.transact({'from': accounts[0]})

    rte_contract.approve.transact(
        liq_pool.address, token_id, {"from": accounts[0]})

for token_id in range(50, 60):
    var_asset.approve.transact(
        calls_center.address, 10**18, {'from': accounts[1]})
    calls_center.mintContract.transact({'from': accounts[1]})

    rte_contract.approve.transact(
        liq_pool.address, token_id, {"from": accounts[1]})

for token_id in range(60, 70):
    var_asset.approve.transact(
        calls_center.address, 10**18, {'from': accounts[3]})
    calls_center.mintContract.transact({'from': accounts[3]})

    rte_contract.approve.transact(
        liq_pool.address, token_id, {"from": accounts[3]})


var_asset.approve.transact(
    liq_pool.address, 10**18, {'from': accounts[0]})
liq_pool.startPool.transact(
    [i for i in range(50)], 1000, {'from': accounts[0]})

# Ensure that the account has appropriate balances
assert 8500 == var_asset.balanceOf.call(
    accounts[0]), "Account Balance Incorrect"
assert liq_pool.address == rte_contract.ownerOf.call(
    25), "ERC-721 not transfered"

# Ensure that the pool has appropriate balances
assert 1000 == var_asset.balanceOf.call(liq_pool.address) == liq_pool.getTotalBalances.call()[
    0], "Incorrect ERC-20 Balance"
assert 50 == liq_pool.getTotalBalances.call()[1], "Incorrect ERC-721 Balance"

"""
Swap In ERC-20
"""
# Swap In ERC-20
var_asset.approve(liq_pool.address, 10**10, {'from': accounts[1]})
liq_pool.swapIn20.transact(100, {'from': accounts[1]})

# Ensure Pool Balances are updated
assert (1100, 45) == liq_pool.getTotalBalances.call(
), "Pool Balances not updated correctly"
assert (1100) == var_asset.balanceOf(
    liq_pool.address), "Incorrect var asset balance"

# Ensure User balances are updated
assert accounts[1] == rte_contract.ownerOf(
    48), "ERC-721 not transfered to user"
assert 9800 == var_asset.balanceOf(accounts[1])

# Swap In ERC-20
var_asset.approve(liq_pool.address, 10**10, {'from': accounts[2]})
liq_pool.swapIn20.transact(200, {'from': accounts[2]})

# Ensure Pool Balances are updated
assert (1300, 38) == liq_pool.getTotalBalances.call(
), "Pool Balances updated incorrectly"

# Ensure User Balances are updated
assert 9800 == var_asset.balanceOf(
    accounts[2]), "User balances updated incorrectly"

"""
Swap In ERC-721
"""
# Swap In Small amount of ERC-721
rte_contract.approve.transact(liq_pool.address, 61, {'from': accounts[3]})
liq_pool.swapIn721.transact([61], {'from': accounts[3]})

# Ensure Pool Balances are updated
assert (1266, 39) == liq_pool.getTotalBalances.call()
assert rte_contract.ownerOf(61) == liq_pool.address

# Ensure User balances are updated
assert 9934 == var_asset.balanceOf(accounts[3], {'from': accounts[3]})

# Swap In Larger amount of ERC-721
for i in range(62, 70):
    rte_contract.approve.transact(liq_pool.address, i, {'from': accounts[3]})
liq_pool.swapIn721.transact([i for i in range(62, 70)], {'from': accounts[3]})

# Ensure Pool Balances are updated
assert (1050, 47) == liq_pool.getTotalBalances.call()
assert rte_contract.ownerOf(65) == liq_pool.address

# Ensure User balances are updated
assert 10150 == var_asset.balanceOf(accounts[3], {'from': accounts[3]})

"""
Add Liquidity
"""
# Add Shares
for i in range(51, 55):
    rte_contract.approve.transact(liq_pool.address, i, {'from': accounts[1]})
liq_pool.addLiquidity.transact([51, 52, 53, 54], 88, {'from': accounts[1]})


assert 352 == liq_pool.getShares.call(accounts[1])
assert 49702 == liq_pool.getTotalShares.call()
assert (1138, 51) == liq_pool.getTotalBalances.call()

# Add again
for i in range(55, 57):
    rte_contract.approve.transact(liq_pool.address, i, {'from': accounts[1]})
liq_pool.addLiquidity.transact([55, 56], 44, {'from': accounts[1]})

assert 440 == liq_pool.getShares.call(accounts[1])
assert 49790 == liq_pool.getTotalShares.call()
assert (1182, 53) == liq_pool.getTotalBalances.call()

"""
Remove Liquidity
"""
# Remove Full Amount
liq_pool.removeLiquidity.transact(440, {'from': accounts[1]})
assert 0 == liq_pool.getShares.call(accounts[1])
assert 49350 == liq_pool.getTotalShares.call()
assert (1172, 53) == liq_pool.getTotalBalances.call()

# Remove Partial Amount
liq_pool.removeLiquidity.transact(20000, {'from': accounts[0]})
assert 30000 == liq_pool.getShares.call(accounts[0])
assert 29350 == liq_pool.getTotalShares.call()
assert (698, 32) == liq_pool.getTotalBalances.call()


def main():
    time.sleep(.1)
    print("All Tests Passed!")
