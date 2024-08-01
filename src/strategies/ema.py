# based off of R%D/ema.ipynb file I've found in the repository.
import pandas as pd
import numpy as np
import requests

# lets create a class for the EMA strategy
class EMA:
    def __init__(self, pair, interval):
        self.pair = pair
        self.interval = interval
        
    def get_ohlc_data(self):
        url = "https://api.kraken.com/0/public/OHLC"
        querystring = {
            "pair": self.pair,
            "interval": self.interval
        }
        response = requests.request("GET", url, params=querystring)
        data = response.json()
        return data

    # calculate the EMA strategy
    def emaStrategy(self, short_period, long_period):
        # get the data
        data = self.get_ohlc_data()
        df = pd.DataFrame(data['result'][self.pair])
        df.columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        # all values from the api are strings besides time and count so we need to convert them to float
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['vwap'] = df['vwap'].astype(float)
        df['volume'] = df['volume'].astype(float)

        # order by time 
        df = df.sort_values(by='time', ascending=True)
        # convert time to datetime and set it as index
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        # add back time to the dataframe
        df['time'] = df.index
        # make human readable time
        df['nice-time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
        # calculate the EMA strategy
        df['short_ema'] = df['close'].ewm(span=short_period).mean()
        df['long_ema'] = df['close'].ewm(span=long_period).mean()
        # print latest short and long period
      
        df['position'] = np.where(df['short_ema'] > df['long_ema'], 1, 0)
        print(short_period, long_period, df['short_ema'].iloc[1], df['long_ema'].iloc[1])
    
        # format json to the following:
        # include position long/short
        # asset pair
        # time and nice-time
        # short_period
        # long_period
        # execute order True/False meaning buy/sell if position switches from 0 to 1 or 1 to 0 from last candle to current candle
        return {
            'position': df['position'].iloc[0],
            'pair': self.pair,
            'time': df['time'].iloc[0],
            'nice-time': df['nice-time'].iloc[0],
            'short_ema': df['short_ema'].iloc[0],
            'long_ema': df['long_ema'].iloc[0],
            # if the position changes from 0 to 1 or 1 to 0 then execute the order, if 3 are the same then don't execute the order
            'execute_order': df['position'].iloc[0] != df['position'].iloc[1] 
        } 

