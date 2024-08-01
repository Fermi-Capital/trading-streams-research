# cacl macd strategy output and return the result
import pandas as pd
import numpy as np
import requests

# get the max candles from the Kraken API
# make this macd a class so getting data and calculating the strategy can be done in one call
class MACD:
    def __init__(self, pair, interval):
        self.pair = pair
        self.interval = interval
        self.df = None
        
    def get_ohlc_data(self):
        url = "https://api.kraken.com/0/public/OHLC"
        querystring = {
            "pair": self.pair,
            "interval": self.interval
        }
        response = requests.request("GET", url, params=querystring)

        # parse the json response and create a dataframe
        data = response.json()
        df = pd.DataFrame(data['result']["SOLUSD"], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])

        #besides time and count are strings so we need to convert them to floats
        df['close'] = df['close'].astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['vwap'] = df['vwap'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['count'] = df['count'].astype(float)
        # create returns column
        df['returns'] = df['close'].pct_change()

        # assign to self.df
        self.df = df

    # calculate the MACD strategy
    def macdStrategy(self):
        # get the data
        self.get_ohlc_data()
        df = self.df

    
        # calculate the MACD strategy
        df['12ema'] = df['close'].ewm(span=12, adjust=False).mean()
        df['26ema'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['12ema'] - df['26ema']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['hist'] = df['macd'] - df['signal']

        df['position'] = np.where(df['macd'] > df['signal'], 1, 0)

        # retturn the most recent signal by date
        return {
            "last_signal":  df['position'].iloc[-1]
        }
