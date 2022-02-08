from secrets import token_bytes
from brownie import *
import time


# Init a Call Option Center
present_time = time.time()
var_asset = VarToken.deploy({'from': accounts[0]})
stable_asset = StableToken.deploy({'from': accounts[0]})
calls_center = CallOptionCenter.deploy(present_time + 1000, 100, 10,
                                       var_asset.address, stable_asset.address, {"from": accounts[0]})

# Fund accounts
for i in range(9):
    var_asset.mint.transact(100, {"from": accounts[i]})
    stable_asset.mint.transact(10000, {"from": accounts[i]})


def main():
    tx_rept = calls_center.getRightContractAddresses.transact(
        {"from": accounts[0]})
    rte_contract = RightToExecute.at(tx_rept.return_value[0])
    rtw_contract = RightToWrite.at(tx_rept.return_value[1])

    var_token_pre_balance = var_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})
    stable_token_pre_balance = stable_asset.balanceOf.call(accounts[0],
                                                           {"from": accounts[0]})

    var_asset.approve.transact(
        calls_center.address, 10**10, {"from": accounts[0]})
    tx_rept = calls_center.mintContract.transact({"from": accounts[0]})
    token_id = tx_rept.return_value

    var_token_post_mint = var_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})
    stable_token_post_mint = stable_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})

    try:
        rtw_contract.approve.transact(
            calls_center.address, token_id, {"from": accounts[0]})
        calls_center.liquidateContract.transact(
            token_id, {"from": accounts[0]})
    except:
        print('\033[1m' + "Early Liquidation Displays Expected Behavior!\n")

    # Execute RTE token
    stable_asset.approve.transact(
        calls_center.address, 10**10, {"from": accounts[0]})
    rte_contract.approve.transact(
        calls_center.address, token_id, {"from": accounts[0]})
    calls_center.executeContract.transact(token_id, {"from": accounts[0]})

    var_token_post_execute = var_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})
    stable_token_post_execute = stable_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})

    try:
        stable_asset.approve.transact(
            calls_center.address, 10**10, {"from": accounts[0]})
        rte_contract.approve.transact(
            calls_center.address, token_id, {"from": accounts[0]})
    except:
        print('\033[1m' + "Repeat Execution Displays Expected Behavior!\n")

    # Liquidate RTW token
    rtw_contract.approve.transact(
        calls_center.address, token_id, {"from": accounts[0]})
    calls_center.liquidateContract.transact(token_id, {"from": accounts[0]})

    var_token_post_liquid = var_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})
    stable_token_post_liquid = stable_asset.balanceOf.call(
        accounts[0], {"from": accounts[0]})

    try:
        rtw_contract.approve.transact(
            calls_center.address, token_id, {"from": accounts[0]})
        calls_center.liquidateContract.transact(
            token_id, {"from": accounts[0]})
    except:
        print('\033[1m' + "Repeat Liquidation Displays Expected Behavior!\n")

    print("Balances of account[0] before purchases were made:")
    print(var_token_pre_balance)
    print(stable_token_pre_balance)
    print("\nBalances of account[0] after contracts were minted:")
    print(var_token_post_mint)
    print(stable_token_post_mint)
    print("\nBalances of account[0] after contracts were exectued (RTE):")
    print(var_token_post_execute)
    print(stable_token_post_execute)
    print("\nBalances of account[0] after contracts were executed (RTW):")
    print(var_token_post_liquid)
    print(stable_token_post_liquid)
    time.sleep(1)
