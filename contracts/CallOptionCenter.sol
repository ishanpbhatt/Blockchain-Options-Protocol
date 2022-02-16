//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.10;

import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC721/ERC721.sol";
import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC20/ERC20.sol";
import "./RightToExecute.sol";
import "./RightToWrite.sol";

contract CallOptionCenter is IERC721Receiver {
    uint256 expirationDate;
    uint256 strikePrice;
    uint256 callAmount;

    RightToExecute RTE;
    RightToWrite RTW;

    mapping(uint256 => bool) bankTokenA;
    mapping(uint256 => bool) bankTokenB;

    ERC20 tokenA;
    ERC20 tokenB;

    constructor(
        uint256 _expirationDate,
        uint256 _strikePrice,
        uint256 _callAmount,
        address _tokenA,
        address _tokenB
    ) {
        expirationDate = _expirationDate;
        strikePrice = _strikePrice;
        callAmount = _callAmount;
        RTE = new RightToExecute(expirationDate, strikePrice, callAmount);
        RTW = new RightToWrite(expirationDate, strikePrice, callAmount);
        tokenA = ERC20(_tokenA);
        tokenB = ERC20(_tokenB);
    }

    function onERC721Received(
        address,
        address,
        uint256,
        bytes memory
    ) public virtual override returns (bytes4) {
        return this.onERC721Received.selector;
    }

    function getRightContractAddresses()
        public
        view
        returns (address, address)
    {
        return (address(RTE), address(RTW));
    }

    function mintContract() public returns (uint256) {
        require(
            tokenA.allowance(tx.origin, address(this)) >= callAmount,
            "Not Enough Allowance"
        );
        require(
            tokenA.balanceOf(tx.origin) >= callAmount,
            "Not enough balance"
        );
        tokenA.transferFrom(tx.origin, address(this), callAmount);
        uint256 counter = RTE.getLatestTokenId();
        bankTokenA[counter] = true;
        RTE.newMint();
        RTW.newMint();
        return counter;
    }

    function executeContract(uint256 tokenId) public {
        require(RTE.ownerOf(tokenId) == msg.sender, "Need to have RTE tokens");
        require(RTE.getApproved(tokenId) == address(this), "Not approved");
        require(block.timestamp < expirationDate, "Expired Contract");
        require(
            tokenB.balanceOf(msg.sender) >= strikePrice,
            "Not enough balance"
        );
        require(
            tokenB.allowance(msg.sender, address(this)) >
                callAmount * strikePrice,
            "Not enough allowance"
        );

        RTE.safeTransferFrom(msg.sender, address(this), tokenId);
        tokenA.transfer(msg.sender, callAmount);
        tokenB.transferFrom(
            msg.sender,
            address(this),
            strikePrice * callAmount
        );
        bankTokenA[tokenId] = false;
        bankTokenB[tokenId] = true;
    }

    function liquidateContract(uint256 tokenId) public {
        require(RTW.ownerOf(tokenId) == msg.sender, "Need to have RTW tokens");
        require(RTW.getApproved(tokenId) == address(this), "Not approved");
        require(
            block.timestamp > expirationDate || bankTokenB[tokenId] == true,
            "Not a withdrawal condition"
        );
        RTW.safeTransferFrom(msg.sender, address(this), tokenId);
        if (bankTokenA[tokenId]) {
            bankTokenA[tokenId] = false;
            tokenA.transfer(msg.sender, callAmount);
        }
        if (bankTokenB[tokenId]) {
            bankTokenB[tokenId] = false;
            tokenB.transfer(msg.sender, callAmount * strikePrice);
        }
    }
}
