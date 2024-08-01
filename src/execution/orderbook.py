# get current order book data from the Kraken API for a specific pair
import requests

class OrderBook:
    def __init__(self, pair):
        self.pair = pair

    def get_order_book_data(self):
        url = "https://api.kraken.com/0/public/Depth"
        querystring = {
            "pair": self.pair
        }
        response = requests.request("GET", url, params=querystring)
        data = response.json()
        # format the data to floats
        data['result'][self.pair]['asks'] = [[float(ask[0]), float(ask[1])] for ask in data['result'][self.pair]['asks']]
        data['result'][self.pair]['bids'] = [[float(bid[0]), float(bid[1])] for bid in data['result'][self.pair]['bids']]
        return data

    # get the current order book data
    def orderBookData(self):
        """
        Get the current order book data from the Kraken API for a specific pair.
        returns
        bid_prices = [29900, 29850, 29800]  # USD
        bid_quantities = [0.5, 0.3, 0.2]  # BTC
        ask_prices = [30050, 30100, 30150]  # USD
        ask_quantities = [0.4, 0.4, 0.2]  # BTC
        spread = 150
        spread_percentage = 0.5
        """
        data = self.get_order_book_data()
        # calculate the spread 
        ask = data['result'][self.pair]['asks'][0][0]
        bid = data['result'][self.pair]['bids'][0][0]
        spread = ask - bid
        data['result'][self.pair]['spread'] = spread
        # calculate the spread percentage
        spread_percentage = spread / ask * 100
        data['result'][self.pair]['spread_percentage'] = spread_percentage

        # format to return
        data = {
            'bid_prices': [bid[0] for bid in data['result'][self.pair]['bids']],
            'bid_quantities': [bid[1] for bid in data['result'][self.pair]['bids']],
            'ask_prices': [ask[0] for ask in data['result'][self.pair]['asks']],
            'ask_quantities': [ask[1] for ask in data['result'][self.pair]['asks']],
            'spread': spread,
            'spread_percentage': spread_percentage
        }

        return data
