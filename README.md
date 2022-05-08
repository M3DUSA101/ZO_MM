# 01 Market Making Bot

This bot provides liquidity and performs market making activity on 01.xyz.



## Requirements

### Wallet
You need a local wallet on Solana blockchain. Check [here](https://docs.solana.com/wallet-guide) on hown to get started.
Once wallet is created, you need to enable margin facity on 01.xyz. You can read more about it [here](https://docs.01.xyz/guides/creating-margin-account). 

### Dependencies

Prefer python 3.10 environment for this bot. Please install 01 python SDK.

```bash
  pip install zo-sdk
```


    
## Bot Strategy and Execution

The bot runs in 3 modes:

1. **Simple bps**: This finds the mid price from orderbook, and places bid and ask quotes at specified bps difference (default is 5 bps).

2. **bps with bias**: Simple bps is direction neutral. This introduces a bias in sending quotes in particular direction and thus open possibility for momentum trading + market making at same time.

3. **Orderbook based**: This method looks at prevailing liquidity in orderbook to find right levels to place bid and ask orders. Such market making is aimed at capturing liquidation events.

Start using the bot by running the following command:

```python
python main.py
```

The bot will ask following questions to set the params:

1. *Select cluster: mainnet or devnet?* - Select the Solana cluster
2. *Select market* - Market you want bot to operate in
3. *Select margin coin* - Coin you want to use as margin
4. *Set replace frequency in seconds* - frequency at which bot will evaluate the positions and rebalance.
5. *select quoting method* - select one of the above three methods for quoting. This will be followed by setting params for the mode.

Post the questionaire, bot will take over and start market making in the mode.

Please use ```Ctrl+C``` to stop the bot at any time.

## Kill All

Incase of any fat-fingers, you can kill all the exsisting orders in the market by this command:
```python
python main.py KILL_ALL
```





## Authors

- [@M3DUSA101](https://github.com/M3DUSA101)

