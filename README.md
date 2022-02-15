# Tokenized Options Protocol

- The protocol provides a decentralized way to trade, write, and sell covered options including puts and calls. It serves as an alternatives to current DeFi offerings which rely on pooling assets in the form of option vaults. The goal of this protocol would be to make options trading accessible to retail crypto investors
- Users will primarily interact with a central smart contract that handles transactions and minting of options contracts and liquidity pools to sell or buy options
- When an option contract is “minted” by an individual, they will be given two NFTs (ERC-721) tokens that compose the contract and the collateral for the covered call or put is deposited into the protocol’s smart contract. One of these will be a RTE (right to execute) token and the other will be a RTW (right to write/withdraw). Each RTE and RTW will store the strike price, expiration date, and the amount of stock (coin asset).
- A RTE gives the holder the ability before the expiration date the right to exchange from the smart contract’s protocol a pre-listed amount of tokens for the amount of assets that the writer deposited into the protocol.
- The RTW gives the holder the ability to either withdraw specified deposited assets from the protocol or if the option is not executed, can withdraw the original deposit after option expiration.
- RTEs and RTWs can be traded in liquidity pools allowing for fast, seamless trading experience that will keep gas fees low. Although they are NFTs, they can be traded like tokens because one RTE is no better than the other (assuming option details are the same). The challenge with these liquidity pools is that they are a little different than

### Liquidity Pool

- There is a balance of NFT tokens that is stored in a storage array that gets pushed and popped
- The fungible ERC-20 token will get stored normally (as they are in other LPs)
- LPs can withdraw liquidity at a given moment for percentage of the fund that they put in
- LPs will earn some kind of reward in governance token and swap fees
