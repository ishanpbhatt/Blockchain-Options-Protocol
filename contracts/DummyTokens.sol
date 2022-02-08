pragma solidity ^0.8.10;

import "/Users/ishan/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.4.1/contracts/token/ERC20/ERC20.sol";

contract VarToken is ERC20 {
    constructor() public ERC20("VariableAsset", "VAR") {
        uint256 i = 10;
    }

    function mint(uint256 amount) public {
        _mint(tx.origin, amount);
    }
}

contract StableToken is ERC20 {
    constructor() public ERC20("StableAsset", "STBL") {
        uint256 i = 10;
    }

    function mint(uint256 amount) public {
        _mint(tx.origin, amount);
    }
}
