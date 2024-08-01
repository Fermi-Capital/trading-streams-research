import pandas as pd
import numpy as np
import pywt
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import requests

class Wave_Strat:
    def __init__(self, pair, interval, signal_delay, prominence, distance, level):
        self.df = None
        self.pair = pair
        self.interval = interval
        self.signal_delay = signal_delay
        self.prominence = prominence
        self.distance = distance
        self.level = level
        self.denoised_close = None
        self.peaks = None
        self.valleys = None
        self.signals = None
        self.positions = None
        self.returns = None
        
        self.load_data()
        self.denoise_close()
        self.find_peaks_valleys()
        self.generate_signals()
        self.calculate_returns()

    # load the data via a def
    def load_data(self):
        # get data for the last 720 candles from kraken api
        url = "https://api.kraken.com/0/public/OHLC"
        querystring = {"pair": self.pair,"interval": self.interval}
        headers = {
        'Accept': 'application/json'
        }
        response = requests.request("GET", url, params=querystring)

        # parse the json response and create a dataframe
        data = response.json()
        df = pd.DataFrame(data['result'][self.pair], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])

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

        # assign the dataframe to the class variable
        self.df = df

    def denoise_close(self):
        # Wavelet denoising
        close = self.df['close'].values
        coeffs = pywt.wavedec(close, 'db8', level=self.level)
        coeffs[1:] = [pywt.threshold(i, value=0.05*max(i), mode='soft') for i in coeffs[1:]]
        self.denoised_close = pywt.waverec(coeffs, 'db8')
        self.df['denoised_close'] = self.denoised_close

    def find_peaks_valleys(self):
        # Find peaks and valleys
        self.peaks, _ = find_peaks(self.denoised_close, prominence=self.prominence, distance=self.distance)
        self.valleys, _ = find_peaks(-self.denoised_close, prominence=self.prominence, distance=self.distance)

    def generate_signals(self):
        # Generate buy/sell signals
        self.signals = pd.Series(index=self.df.index, data=0)
        self.signals.iloc[self.peaks] = -1  # Sell signal
        self.signals.iloc[self.valleys] = 1  # Buy signal
        
        # Adjust signals for delay
        self.signals = self.signals.shift(self.signal_delay)
        self.df['signal'] = self.signals

    def calculate_returns(self):
        # Calculate strategy returns
        self.positions = self.signals.cumsum()
        self.df['position'] = self.positions
        self.df['returns'] = self.df['close'].pct_change()
        self.df['strategy_returns'] = self.df['position'].shift(1) * self.df['returns']
        self.df['cumulative_returns'] = (1 + self.df['strategy_returns']).cumprod()

    def plot_signals(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.df['close'], label='Close Price')
        plt.scatter(self.df.index[self.df['signal'] == 1], self.df.loc[self.df['signal'] == 1, 'close'], 
                    marker='^', color='g', label='Buy Signal', s=100)
        plt.scatter(self.df.index[self.df['signal'] == -1], self.df.loc[self.df['signal'] == -1, 'close'], 
                    marker='v', color='r', label='Sell Signal', s=100)
        plt.scatter(self.df.index[self.peaks], self.denoised_close[self.peaks], color='r', label='Peaks')
        plt.scatter(self.df.index[self.valleys], self.denoised_close[self.valleys], color='g', label='Valleys')
        plt.title('Buy/Sell Signals')
        plt.legend()
        plt.show()

    def plot_peaks_valleys(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.denoised_close, label='Denoised Close')
        plt.scatter(self.df.index[self.peaks], self.denoised_close[self.peaks], color='r', label='Peaks')
        plt.scatter(self.df.index[self.valleys], self.denoised_close[self.valleys], color='g', label='Valleys')
        plt.title('Peaks and Valleys')
        plt.legend()
        plt.show()

    def plot_denoised_trend(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.df['close'], label='Original Close')
        plt.plot(self.df.index, self.denoised_close, label='Denoised Close')
        plt.title('Original vs Denoised Close Price')
        plt.legend()
        plt.show()

    def get_last_signal(self):
        last_signal = self.df['signal'].iloc[-1]
        
        # Find the last non-zero signal
        non_zero_signals = self.df['signal'][self.df['signal'] != 0]
        signal_type = None
        periods_since_last_signal = None
        if not non_zero_signals.empty:
            last_non_zero_signal = non_zero_signals.iloc[-1]
            last_non_zero_index = non_zero_signals.index[-1]
            periods_since_last_signal = len(self.df) - 1 - self.df.index.get_loc(last_non_zero_index)
            
            if last_non_zero_signal == 1:
                signal_type = 1
            else:
                signal_type = -1
        
        return {
            "last_signal": last_signal,
            "last_non_zero_position": signal_type,
            "periods_since_last_signal": periods_since_last_signal,
            "last_non_zero_close_price": self.df['close'].iloc[last_non_zero_index],
            "current_close_price": self.df['close'].iloc[-1]    
        }

    def plot_backtest_results(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Plot cumulative returns
        ax1.plot(self.df.index, self.df['cumulative_returns'], label='Strategy Returns')
        ax1.set_title('Cumulative Returns')
        ax1.legend()
        
        # Plot PnL
        pnl = (self.df['cumulative_returns'] - 1) * 100
        ax2.plot(self.df.index, pnl, label='PnL (%)')
        ax2.set_title('Profit and Loss (%)')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()





# ---- Execution ---- #
# strategy = Wave_Strat("SOLUSD", '1', signal_delay=5, prominence=6, distance=10, level=1)

# Plot results
# strategy.plot_signals()
# strategy.plot_peaks_valleys()
# strategy.plot_denoised_trend()
# strategy.plot_backtest_results()


# Get last signal
# print(strategy.get_last_signal())