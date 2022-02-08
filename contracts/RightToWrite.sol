//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.10;

import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC721/ERC721.sol";

contract RightToWrite is ERC721 {
    uint256 expirationDate;
    uint256 strikePrice;
    uint256 callAmount;

    address owner;
    uint256 currTokenId = 0;
    mapping(address => uint256) tokenId;

    constructor(
        uint256 _expirationDate,
        uint256 _strikePrice,
        uint256 _callAmount
    ) ERC721("RTW", "WriteRight") {
        expirationDate = _expirationDate;
        strikePrice = _strikePrice;
        callAmount = _callAmount;
        owner = msg.sender;
    }

    function newMint() public {
        require(msg.sender == owner, "Can be called by only Call Factory");
        _mint(tx.origin, currTokenId);
        currTokenId += 1;
    }

    function getCurrTokenId() public view returns (uint256) {
        return currTokenId;
    }

    function getExpiration() public view returns (uint256) {
        return expirationDate;
    }

    function getStrikePrice() public view returns (uint256) {
        return strikePrice;
    }

    function getCallAmount() public view returns (uint256) {
        return callAmount;
    }
}
