# execute trades through the Kraken API
import requests
import json
import time

# get kraken signature function
from src.exchange.kraken.main import get_kraken_signature
# get order book
from src.execution.orderbook import OrderBook


# make this a class so getting data and calculating the strategy can be done in one call
class Account:
    def __init__(self, exchange="kraken"):
        self.exchange = exchange
        self.headers = get_kraken_signature

    def nonce(self):
        return str(int(time.time() * 1000))

    # get the balance
    def getBalances(self):
        url = "https://api.kraken.com/0/private/Balance"
        uri = "/0/private/Balance"
        payload = json.dumps({"nonce": self.nonce()})

        balances_response = requests.request(
            "POST", url, headers=self.headers(uri, payload), data=payload
        ).json()['result']

        # trade balances
        trade_balance_url = "https://api.kraken.com/0/private/TradeBalance"
        trade_balance_uri = "/0/private/TradeBalance"
        trade_balance_payload = json.dumps({"nonce": self.nonce(), "asset": "ZUSD"})

        trade_balances_response = requests.request(
            "POST", trade_balance_url, headers=self.headers(trade_balance_uri, trade_balance_payload), data=trade_balance_payload
        ).json()['result']

        # add the latest cost basis for each asset to the response from the getClosedOrders function
        closed_orders = self.getClosedOrders()
        # iterate through balances
        for asset in balances_response:
             # if the balance is float 0, skip the asset
            if float(balances_response[asset]) == 0:
                continue
            # replace each asset with a object that has the asset and the cost basis
            balances_response[asset] = {
                "balance": float(balances_response[asset]),
                "cost_basis": 0,
                "current_value_to_orderbook": 0
            }
            # get the cost basis for each asset from the last closed_buy order
            for order in closed_orders['closed_buy']:
                # match on if the order (SOLUSD) contains the asset (SOL)
                if asset in order[1]['descr']['pair']:
                    balances_response[asset]['cost_basis'] = float(order[1]['cost'])
                    break
            # get the current value of the asset to the orderbook bids, if the response is empty or the asset is not in the response, the value will be 0
            orderbook = OrderBook(f"{asset}USD")
            # make sure to have error handling if the asset is not in the response  
            try:
                orderbook_data = orderbook.orderBookData()
                # iterate through bid_quantities and subtract the balance from the bid_quantities to get the current value of the asset to the orderbook bids
                for i, bid_quantity in enumerate(orderbook_data['bid_quantities']):
                    if balances_response[asset]['balance'] > bid_quantity:
                        balances_response[asset]['current_value_to_orderbook'] += bid_quantity * orderbook_data['bid_prices'][i]
                        balances_response[asset]['balance'] -= bid_quantity
                    else:
                        balances_response[asset]['current_value_to_orderbook'] += balances_response[asset]['balance'] * orderbook_data['bid_prices'][i]
                        break
            except:
                balances_response[asset]['current_value_to_orderbook'] = 0
            
            # create fee and pnl_minus_fee if the asset is sold
            balances_response[asset]['fee'] = balances_response[asset]['current_value_to_orderbook'] * 0.004
            # pnl_minus_fee
            balances_response[asset]['pnl_minus_fee'] = balances_response[asset]['current_value_to_orderbook'] - balances_response[asset]['cost_basis'] - balances_response[asset]['fee']
            # after execution usd value
            balances_response[asset]['after_execution_usd_value'] = balances_response[asset]['current_value_to_orderbook'] - balances_response[asset]['fee']
        
        return {"balances": balances_response, "usd_trade_balance": trade_balances_response}

    def getAccountTradeVolume(self, pairs=None):
        """'
        pairs: comma separated pairs, e.g. "XXBT/ZUSD, XETH/ZEUR"
        """
        url = "https://api.kraken.com/0/private/TradeVolume"
        uri = "/0/private/TradeVolume"
        payload = json.dumps({"nonce": self.nonce(), "pair": pairs})

        response = requests.request(
            "POST", url, headers=self.headers(uri, payload), data=payload
        )

        return response
    
    def getClosedOrders(self):
        '''
        Get closed orders, sorted by time "closetm"
        Orders only placed on Kraken Pro are returned
        list with ['closed'] and ['closed_buy'] and ['closed_sell']
        '''
        url = "https://api.kraken.com/0/private/ClosedOrders"
        uri = "/0/private/ClosedOrders"
        payload = json.dumps({"nonce": self.nonce(), "trades": True,})

        response = requests.request(
            "POST", url, headers=self.headers(uri, payload), data=payload
        )

        # sort by time "closetm"
        response = response.json()
        response['result']['closed'] = sorted(response['result']['closed'].items(), key=lambda x: x[1]['closetm'], reverse=True)
        
        # add human readable time object at position x[1]['closetm']
        for x in response['result']['closed']:
            x[1]['nice-time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x[1]['closetm']))
        # split buy and sell orders into separate lists ['descr']['type']
        response['result']['closed_buy'] = [x for x in response['result']['closed'] if x[1]['descr']['type'] == 'buy']
        response['result']['closed_sell'] = [x for x in response['result']['closed'] if x[1]['descr']['type'] == 'sell']

        return response['result']
    

    def getAccountSummary(self):
        """
        Get account summary, combining balance, trade volume, fees, and average buy price of the assets
        """
        balances = self.getBalances()

        pairs = requests.request(
            "GET",
            "https://api.kraken.com/0/public/AssetPairs",
            headers={"Accept": "application/json"},
            data={},
        )
        pairs = pairs.json()["result"].keys()
        pairs = ",".join(pairs) 
        
        # trade_volume = self.getAccountTradeVolume(pairs).json()
        return {"account": balances}
