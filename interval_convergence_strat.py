
from src.account.main import Account
# from src.execution.main import OrderExecution
from src.strategies.pv_wave import Wave_Strat
from src.strategies.macd import MACD
import time
from colored import Fore, Back, Style

# run the Wave_Strat every 10 seconds to find the last non-zero signal for several candle intervals
# run it for 1, 5, 15, 30, 60, 240, 1440

# the def will take a map of the intervals and the prominence value for the wave strat
signal_map = {
    "1": 1.6,
    "5": 3,
    "15": 5,
    "30": 7,
    "60": 8,
    "240": 17,
    # "1440": 0.0
}

# def should also take the asset "SOLUSD"

def run_wave(base, quote, signal_map):
    # make size a str
    # size = str(size)
    # new string by concatenating the base and quote strings
    asset = base + quote
    while True:
        # include try catch logic to retry if error and buy/sell execution
        try:
            # get account data
            # account = Account()
            # account_data = account.getAccountSummary()
            # get the last non-zero signal for each interval
            print(f"{Back.black}----------------- Trade Update -----------------{Style.reset}")
            for interval, prominence in signal_map.items():
                # run new wave strat for each interval
                strategy = Wave_Strat(asset, interval, signal_delay=0, prominence=prominence, distance=10, level=1)
                latest_signal = strategy.get_last_signal()
                last_signal = latest_signal["last_signal"]
                last_non_zero_position = latest_signal["last_non_zero_position"]
                periods_since_last_signal = latest_signal["periods_since_last_signal"]
                last_non_zero_close_price = latest_signal["last_non_zero_close_price"]
                current_close_price = latest_signal["current_close_price"]
                # run macd strategy for each interval
                macd = MACD(asset, interval)
                macd_signal = macd.macdStrategy()
                last_macd_signal = macd_signal["last_signal"]



                print(f"{Back.green if last_non_zero_position == 1 else Back.red}({interval} Minute Candle) Last PV Signal: ({last_non_zero_position}): { "Buy" if last_non_zero_position > 0 else 'Sell' }{Style.reset} ---- {Back.green if last_macd_signal == 1 else Back.red}Last MACD Signal: ({last_macd_signal}){Style.reset}")

            print(f"current close price: ${current_close_price}")
            print(f"Current UTC time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
            # poll every 10 seconds
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
            continue


run_wave("SOL", "USD", signal_map)