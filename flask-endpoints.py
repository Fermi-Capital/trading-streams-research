from flask import Flask

# import macd strategy
from src.strategies.macd import MACD
from src.account.main import Account
from src.execution.main import OrderExecution

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Private API"

# summary of the account, volume, fees, balances and average buy price of the assets
@app.route("/account")
def account():
    # get api keys from .env file
    account = Account()
    account_data = account.getAccountSummary()
    # print(account_data['balance'])
    return account_data

@app.route("/closed-orders")
def closed_orders():
    account = Account()
    closed_orders = account.getClosedOrders()
    return closed_orders

@app.route("/macd")
def macd():
    macd = MACD("SOLUSD", "1")
    macd_data = macd.macdStrategy().to_json(orient='records')
    return macd_data

# order execution
@app.route("/execute-order")
def execute_order():
    order_execution = OrderExecution()
    order = order_execution.executeOrder("market", "buy", "0.05", "SOLUSD")
    return order
