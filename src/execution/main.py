# execute trades through the Kraken API
import requests
import json
import time
# get kraken signature function
from src.exchange.kraken.main import get_kraken_signature

# make this a class so getting data and calculating the strategy can be done in one call
class OrderExecution: 
    def __init__(self, exchange='kraken'):
        self.exchange = exchange
        self.headers = get_kraken_signature

    def nonce(self):
        return str(int(time.time() * 1000))
    
    # execute order through the Kraken API
    def executeOrder(self, order_type, type, volume, pair, price=None):

        url = "https://api.kraken.com/0/private/AddOrder"
        uri = "/0/private/AddOrder"

        payload = json.dumps({
            "nonce": self.nonce(),
            "ordertype": order_type,
            "type": type,
            "volume": volume,
            "pair": pair,
        })

        if order_type == "limit":
            payload = json.dumps({
                "nonce": self.nonce(),
                "ordertype": order_type,
                "type": type,
                "volume": volume,
                "pair": pair,
                "price": price
            })

        response = requests.request("POST", url, headers=self.headers(uri, payload), data=payload)

        return response.json()