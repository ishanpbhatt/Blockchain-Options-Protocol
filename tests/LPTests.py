from brownie import *
import time


# Init a Call Option Center
present_time = time.time()
var_asset = VarToken.deploy({'from': accounts[0]})
stable_asset = StableToken.deploy({'from': accounts[0]})
calls_center = CallOptionCenter.deploy(present_time + 1000, 10, 10,
                                       var_asset.address, stable_asset.address, {"from": accounts[0]})

# Fund accounts
for i in range(9):
    var_asset.mint.transact(10000, {"from": accounts[i]})
    stable_asset.mint.transact(10000, {"from": accounts[i]})

var_token_pre_execute = var_asset.balanceOf.call(
    accounts[0], {"from": accounts[0]})

# Init a LP Contract
rte_address, rtw_address = calls_center.getRightContractAddresses.call({
                                                                       "from": accounts[0]})
rte_contract = RightToExecute.at(rte_address)
liq_pool = ERC721LP.deploy(
    rte_address, var_asset.address, {'from': accounts[0]})

# Fund the liquidity pool and start it
for token_id in range(10):
    var_asset.approve.transact(
        calls_center.address, 10**18, {'from': accounts[0]})
    calls_center.mintContract.transact({'from': accounts[0]})

    rte_contract.approve.transact(
        liq_pool.address, token_id, {"from": accounts[0]})

var_asset.approve.transact(
    liq_pool.address, 10**18, {'from': accounts[0]})
liq_pool.startPool.transact(
    [i for i in range(10)], 100, {'from': accounts[0]})

var_token_post_execute = var_asset.balanceOf.call(
    accounts[0], {"from": accounts[0]})

assert var_token_pre_execute == 10000
assert var_token_post_execute == 9800

# Swap in erc20 for the erc721
erc20_bal, erc721_bal = liq_pool.getTotalBalances.call({"from": accounts[0]})
print("Balances: " + str([erc20_bal, erc721_bal]))

var_asset.approve(liq_pool.address, 10**10, {"from": accounts[1]})
liq_pool.swapIn20.transact(10, {"from": accounts[1]})

# Ensure that two RTEs are swapped out to the right address
assert rte_contract.ownerOf.call(
    9, {"from": accounts[1]}) == accounts[1].address, "erc721 improperly transferd"

erc20_bal, erc721_bal = liq_pool.getTotalBalances.call({"from": accounts[0]})
assert [110, 9] == [erc20_bal, erc721_bal], "Unexpected balances"


# Swap in erc721 for erc20 token
erc20_bal, erc721_bal = liq_pool.getTotalBalances.call({"from": accounts[0]})
print([erc20_bal, erc721_bal])
print(var_asset.balanceOf.call(accounts[2].address))
var_asset.approve.transact(calls_center.address, 10**10, {"from": accounts[2]})
calls_center.mintContract.transact({'from': accounts[2]})
rte_contract.approve.transact(
    liq_pool.address, 10, {"from": accounts[2]})

erc20_bal, erc721_bal = liq_pool.getTotalBalances.call({"from": accounts[0]})
print([erc20_bal, erc721_bal])

liq_pool.swapIn721.transact([10], {"from": accounts[2]})

# Ensure balance updates for the pool
erc20_bal, erc721_bal = liq_pool.getTotalBalances.call({"from": accounts[0]})
print([erc20_bal, erc721_bal])
# Ensure balance updates for the user
assert 10000 == var_asset.balanceOf.call(
    accounts[2].address), 'incorrect balance'
# Ensure token ownership updates for the user

assert rte_contract.ownerOf(
    10) == liq_pool.address, "unexpected token ownership"

# Add liquidity tests
# Make sure balances update for the pool
# Make sure balances update for the user
# Make sure the total number of shares updates

# Remove liquidity tests
# Make sure balances update for the pool
# Make sure balances update for the user
# Make sure the total number of shares updates


def main():
    time.sleep(.1)
    print("All Tests Passed!")
