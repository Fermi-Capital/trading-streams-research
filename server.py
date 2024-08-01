# import macd strategy
from src.account.main import Account
from src.strategies.ema import EMA
from src.execution.main import OrderExecution
from src.strategies.pv_wave import Wave_Strat
import time
from colored import Fore, Back, Style

# run the ema strategy every 5 secs afte the top of the unix time minute and return the current result to see if the signal is buy or sell
def run_ema(pair="SOLUSD", interval="1", short_period=12, long_period=26):
    while True:
        # retry logic if error getting from the api in the ema strategy
        try:
            ema = EMA(pair, interval)
            ema_data = ema.emaStrategy(short_period, long_period)
            # get all the retun data from the ema strategy
            position = ema_data["position"]
            pair = ema_data["pair"]
            # time = ema_data["time"]
            nice_time = ema_data["nice-time"]
            short_ema = ema_data["short_ema"]
            long_ema = ema_data["long_ema"]
            execute_order = ema_data["execute_order"]
            print(f"position!!!!! {position}")
            # print(signal)
            # Use colorlog to print the result in color of the latest row in the dataframe
            if position == 1:
                print(f"Trade signal BUY |{pair}|--> time: {nice_time}, short_period: {short_ema}, long_period: {long_ema}, execute_order: {execute_order}")

                if execute_order:
                    order_execution = OrderExecution()
                    order = order_execution.executeOrder("market", "buy", "0.05", pair)
                    print(order)
            else:
                # color the print output
                print(f"Trade signal SELL |{pair}|--> time: {nice_time}, short_period: {short_ema}, long_period: {long_ema}, execute_order: {execute_order}")
                
                if execute_order:
                    order_execution = OrderExecution()
                    order = order_execution.executeOrder("market", "sell", "0.05", pair)
                    print(order)
            # poll every 5 seconds after 1 whole unix time minute so at 1:00:05, 1:01:05, 1:02:05, etc
            time.sleep(5 - time.time() % 5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5 - time.time() % 5)
            continue

# run the wave strategy every 5 secs and return the current result to see if the signal is buy or sell
def run_wave(base, quote, interval, size):
    # make size a str
    size = str(size)
    # new string by concatenating the base and quote strings
    asset = base + quote
    while True:
        # include try catch logic to retry if error and buy/sell execution
        try:
            # get account data
            account = Account()
            account_data = account.getAccountSummary()

            # get the account balanace for base asset, if falsy then no balance
            balance = 0 if type(account_data['account']['balances'][base]) == str else account_data['account']['balances'][base]['balance']
            is_balance = False if type(account_data['account']['balances'][base]) == str  else True
            # print('Balance Already!' if is_balance else 'No Balance Yet!')


            # ----------------- Wave Strategy - from peaks_valley.py -----------------
            # signal = Wave_Strategy(asset, interval, level=1, prominence=1.1, distance=10)
            # signal.load_data()  # df should be your up-to-date price data
            # signal.identify_peaks_valleys()
            # signal.generate_positions()

            # run new
            strategy = Wave_Strat(asset, interval, signal_delay=0, prominence=1.1, distance=10, level=1)
            latest_signal = strategy.get_last_signal()
            last_signal = latest_signal["last_signal"]
            last_non_zero_position = latest_signal["last_non_zero_position"]
            periods_since_last_signal = latest_signal["periods_since_last_signal"]
            last_non_zero_close_price = latest_signal["last_non_zero_close_price"]
            current_close_price = latest_signal["current_close_price"]

            print(f"{Style.reset}----------------- Trade Update -----------------")
            print(f"{Back.green if last_non_zero_position == 1 else Back.red}base asset balance: {balance}")
            print(f"Periods since last signal: {periods_since_last_signal}")
            print(f"current close price: {current_close_price}")
            print(f"last non zero close price: {last_non_zero_close_price}")
            print(f"Current UTC time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
            print(f"latest signal: {last_signal}")


# if the latest signal is a buy and the base balance is 0 then execute a buy order
            if last_non_zero_position == 1 and is_balance == False:
                print(f"Trade signal BUY: {last_non_zero_position}")
                order_execution = OrderExecution()
                order = order_execution.executeOrder("market", "buy", size, asset)
                print(order)
                print(f'{Style.reset}-----------------------------------------------{Style.reset}')
# if the latest signal is a sell and the base balance is not 0 then execute a sell order
            elif last_non_zero_position == -1 and is_balance:
                print(f"Trade signal SELL: {last_non_zero_position}")
                order_execution = OrderExecution()
                order = order_execution.executeOrder("market", "sell", size, asset)
                print(order)
                print(f'{Style.reset}-----------------------------------------------{Style.reset}')
            else:
                print("No signal - HOLD - Already in Trade")
                print(f'{Style.reset}-----------------------------------------------{Style.reset}')
            time.sleep(3)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
            continue

run_wave('SOL', 'USD', '1', 0.05)