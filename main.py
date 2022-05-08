from zo import Zo
import time
import sys
import asyncio

class ZO_MarketMaker(Zo):
    
    def __init__(self, cluster, market, margin_coin):
        self.cluster = cluster,
        self.market = market,
        self.margin_coin = margin_coin
        
    async def connect_to_Zo(self):
        self.zo = await Zo.new(
            cluster=self.cluster[0])
        print("Connected to wallet address: ", self.zo.wallet.public_key)
     
    async def generate_quotes(self, method, bps=50, bias=.5):
        try:
            await mm.zo.refresh()
        except:
            print("error in refreshing")
        if(method=="simple_bps"):
            asks = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].asks]
            bids = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].bids]
            
            mid = (bids[0][0]+asks[0][0])/2
            
            bid_price = mid - 0.5 * mid * bps * 1e-4
            ask_price = mid + 0.5 * mid * bps * 1e-4
            
            return {'bid_price': bid_price, 'ask_price': ask_price}
        
        elif(method=="bias_bps"):
            asks = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].asks]
            bids = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].bids]
            
            mid = (bids[0][0]+asks[0][0])/2
            
            bid_price = mid - (1-bias) * mid * bps * 1e-4
            ask_price = mid + bias * mid * bps * 1e-4
            
            return {'bid_price': bid_price, 'ask_price': ask_price}
        
        elif(method=="orderbook"):
            asks = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].asks]
            bids = [[order.price, order.size] for order in self.zo.orderbook[self.market[0]].bids]
            
            bid_price = np.sum([bid[0]*bid[1] for bid in bids])/np.sum([bid[1] for bid in bids])
            ask_price = np.sum([ask[0]*ask[1] for ask in asks])/np.sum([ask[1] for ask in asks])
            
            return {'bid_price': bid_price, 'ask_price': ask_price}
    
    async def send_new_orders(self, quotes):
        
        try:

            #get margin
            margin = self.zo.balance[self.margin_coin]

            # Use only 95% of margin while placing order
            bid_quote_size = ( margin / 2 ) * 0.95 / quotes['bid_price']
            ask_quote_size = ( margin / 2 ) * 0.95 / quotes['ask_price']

            #existing inventory
            position = self.zo.position[self.market].size

            if(position < 0):
                bid_quote_size = bid_quote_size + position

            elif(position > 0):
                ask_quote_size = ask_quote_size + position

            #get orders    
            orders = self.zo.orders[self.market]

            #cancel exsisting orders
            for order in orders:
                await zo.cancel_order_by_client_id(order.client_order_id, symbol=self.market)

            #place new orders
            await zo.place_order(bid_quote_size, quotes['bid_quote_size'], 'bid', symbol=self.market, order_type="limit", client_id=1)
            await zo.place_order(bid_quote_size, quotes['ask_quote_size'], 'ask', symbol=self.market, order_type="limit", client_id=2)
        
        except Exception as e:
            print("Error in sending new orders")
            print(e)
            
            
    async def kill_all(self):
        try:
            await mm.zo.refresh()

            #get orders    
            orders = self.zo.orders[self.market]

            #cancel exsisting orders
            for order in orders:
                await zo.cancel_order_by_client_id(order.client_order_id, symbol=self.market)

        except Exception as e:
            print("Error in sending Kill All")
            print(e)
            

            
if __name__ == "__main__":

    print("Zo Market Maker Started!")

    s = ""
    while(s not in ['mainnet', 'devnet']):
        s = input("Select cluster: mainnet or devnet? \n")
    cluster = s

    while((s not in ['BTC-PERP', 'SOL-PERP', 'DOGE-PERP', 'SOL-SQUARE'])):
        s = input("Select market: BTC-PERP / SOL-PERP / DOGE-PERP / SOL-SQUARE? \n")
    market = s
    
    while((s not in ['USDC', 'SOL', 'BTC', 'SRM'])):
        s = input("Select margin coin: USDC / SOL / BTC / SRM \n")
    margin_coin = s
    
    s = input("Set replace frequency in seconds: ")
    replace_freq = int(s)
    
    if(str(sys.argv[1])=='KILL_ALL'):
        mm = ZO_MarketMaker(cluster, market, margin_coin)
        asyncio.run(mm.connect_to_Zo())
        asyncio.run(mm.kill_all())
        sys.exit(0)
    
    s = input("Start market making? y/n")
    
    if(s=="y"):
        mm = ZO_MarketMaker(cluster, market, margin_coin)
        asyncio.run(mm.connect_to_Zo())
    else:
        sys.exit(0)
        
    print("Market Stats for :", market)
    
    index_price = mm.zo.markets[mm.market[0]].index_price
    mark_price = mm.zo.markets[mm.market[0]].mark_price
    funding_rate = mm.zo.markets[mm.market[0]].funding_rate
    
    print("\nIndex Price for :", index_price)
    print("Market Price for :", mark_price)
    print("Funding  Price for :", funding_rate)
    print("BIDS: \n")
    print([[order.price, order.size] for order in mm.zo.orderbook[mm.market[0]].bids][:5], "\n")
    
    
    print("ASKS: \n")
    print([[order.price, order.size] for order in mm.zo.orderbook[mm.market[0]].asks][:5], "\n\n\n")
    
    
    
    while((s not in ['simple_bps', 'bias_bps', 'orderbook_liquidity'])):
        s = input("select quoting method: simple_bps, bias_bps, orderbook_liquidity?")
    method = s
    bps=0
    bias=0
    if(method=="simple_bps" or method == "bias_bps"):
        s = input("Quote with how many bps? (default 5bps)")
        if(s!=""):
            bps = int(s)
        else:
            bps = 5
            
    if(method =="bias_bps"):
        s = input("How much bias between 0 to 1? 0 -> Bearish and 1-> Bullish")
        bias = float(s)
    
    quotes = asyncio.run(mm.generate_quotes(method=method, bps=bps, bias=bias))
    print("Current quotes: bid: ", quotes['bid_price'], " ask: ", quotes['ask_price'])
    
    while(True):
        quotes = asyncio.run(mm.generate_quotes(method=method, bps=bps, bias=bias))
        print("Current quotes: bid: ", quotes['bid_price'], " ask: ", quotes['ask_price'])
        print("sending orders")
        asyncio.run(mm.send_new_orders(quotes))
        print("Waiting for ", replace_freq, " seconds")
        time.sleep(replace_freq)
        continue