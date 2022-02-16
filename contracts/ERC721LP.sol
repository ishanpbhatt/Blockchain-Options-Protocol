//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.10;

import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC721/ERC721.sol";
import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC20/ERC20.sol";

// TODO: Add fees to swaps
// This should be easy, just add param to constructor and take that amount off of
// the erc20 asset for each transaction
contract ERC721LP {
    ERC721 erc721Token;
    ERC20 erc20Token;

    mapping(address => uint256) poolShareMap;
    uint256 poolShares;

    uint256 public erc721Balance = 0;
    uint256[] erc721Array;
    uint256 public erc20Balance = 0;

    bool isStarted = false;

    constructor(address _erc721Token, address _erc20Token) {
        erc721Token = ERC721(_erc721Token);
        erc20Token = ERC20(_erc20Token);
    }

    function startPool(uint256[] memory erc721Ids, uint256 _erc20Balance)
        public
    {
        require(isStarted == false, "LP already started");
        require(
            erc20Token.balanceOf(msg.sender) >= _erc20Balance,
            "Not enough ERC20 Balance"
        );
        require(
            erc20Token.allowance(msg.sender, address(this)) >= _erc20Balance,
            "Not enough allowance"
        );
        for (uint256 i = 0; i < erc721Ids.length; i++) {
            require(
                erc721Token.ownerOf(erc721Ids[i]) == msg.sender,
                "Not the owner of the Right"
            );
            require(
                erc721Token.getApproved(erc721Ids[i]) == address(this),
                "Not approved"
            );
        }
        erc20Balance = _erc20Balance;
        erc20Token.transferFrom(msg.sender, address(this), _erc20Balance);

        for (uint256 i = 0; i < erc721Ids.length; i++) {
            erc721Array.push(erc721Ids[i]);
            erc721Token.transferFrom(msg.sender, address(this), erc721Ids[i]);
        }
        erc721Balance = erc721Ids.length;

        poolShares = erc721Balance * erc20Balance;
        poolShareMap[msg.sender] = poolShares;
        isStarted = true;
    }

    function getShares(address shareHolder) public view returns (uint256) {
        return poolShareMap[shareHolder];
    }

    function getTotalShares() public view returns (uint256) {
        return poolShares;
    }

    function getTotalBalances() public view returns (uint256, uint256) {
        return (erc20Balance, erc721Balance);
    }

    function addLiquidity(uint256[] memory erc721Ids, uint256 _erc20Balance)
        public
    {
        require(isStarted == true, "Pool not started yet");
        require(
            erc20Balance / erc721Balance == _erc20Balance / erc721Ids.length,
            "Need to satisfy the ratio of balance"
        );
        require(
            erc20Token.balanceOf(msg.sender) >= _erc20Balance,
            "Not enough ERC20 Balance"
        );
        require(
            erc20Token.allowance(msg.sender, address(this)) >= _erc20Balance,
            "Not enough allowance"
        );
        for (uint256 i = 0; i < erc721Ids.length; i++) {
            require(
                erc721Token.ownerOf(erc721Ids[i]) == msg.sender,
                "Not the owner of the Right"
            );
            require(
                erc721Token.getApproved(erc721Ids[i]) == address(this),
                "Not approved"
            );
        }
        uint256 newShares = erc721Ids.length * _erc20Balance;
        erc20Token.transferFrom(msg.sender, address(this), _erc20Balance);

        for (uint256 i = 0; i < erc721Ids.length; i++) {
            erc721Array.push(erc721Ids[i]);
            erc721Token.transferFrom(msg.sender, address(this), erc721Ids[i]);
        }
        erc721Balance += erc721Ids.length;
        erc20Balance += _erc20Balance;
        poolShareMap[msg.sender] += newShares;
        poolShares += newShares;
    }

    function removeLiquidity(uint256 shares) public {
        require(getShares(msg.sender) >= shares, "Not enough shares.");
        poolShareMap[msg.sender] -= shares;
        uint256 erc721Out = (erc721Balance * shares) / poolShares;
        uint256 erc20Out = (erc20Balance * shares) / poolShares;
        erc20Balance -= erc20Out;
        erc721Balance -= erc721Out;
        poolShares -= shares;

        for (uint256 i = 0; i < erc721Out; i++) {
            uint256 tokenId = erc721Array[erc721Array.length - 1];
            erc721Array.pop();
            erc721Token.approve(msg.sender, tokenId);
            erc721Token.safeTransferFrom(address(this), msg.sender, tokenId);
        }

        erc20Token.transfer(msg.sender, erc20Out);
    }

    function swapIn721(uint256[] memory erc721Ids) public {
        require(isStarted == true, "Pool not started yet");
        for (uint256 i = 0; i < erc721Ids.length; i++) {
            require(
                erc721Token.ownerOf(erc721Ids[i]) == msg.sender,
                "Not the owner of the Right"
            );
            require(
                erc721Token.getApproved(erc721Ids[i]) == address(this),
                "Not approved"
            );
        }
        uint256 post20Bal = poolShares / (erc721Ids.length + erc721Balance);
        uint256 erc20Out = erc20Balance - post20Bal;
        erc20Balance -= erc20Out;
        erc20Token.transfer(msg.sender, erc20Out);

        erc721Balance += erc721Ids.length;

        for (uint256 i = 0; i < erc721Ids.length; i++) {
            erc721Array.push(erc721Ids[i]);
            erc721Token.transferFrom(msg.sender, address(this), erc721Ids[i]);
        }
    }

    function swapIn20(uint256 tokenCount) public {
        require(isStarted == true, "Pool not started yet");
        require(
            erc20Token.balanceOf(msg.sender) >= tokenCount,
            "Not enough balance"
        );
        require(
            erc20Token.allowance(msg.sender, address(this)) >= tokenCount,
            "Not enough balance"
        );
        uint256 post721Bal = poolShares / (tokenCount + erc20Balance);
        uint256 erc721Out = erc721Balance - post721Bal;
        erc721Balance -= erc721Out;

        erc20Token.transferFrom(msg.sender, address(this), tokenCount);
        erc20Balance += tokenCount;

        for (uint256 i = 0; i < erc721Out; i++) {
            uint256 tokenId = erc721Array[erc721Array.length - 1];
            erc721Array.pop();
            erc721Token.approve(msg.sender, tokenId);
            erc721Token.safeTransferFrom(address(this), msg.sender, tokenId);
        }
    }
}
