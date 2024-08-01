#!/usr/bin/env python
from websockets.sync.client import connect
import json
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
	"%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
	datefmt=None,
	reset=True,
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	},
	secondary_log_colors={},
	style='%'
))

logger = colorlog.getLogger('example')
logger.addHandler(handler)

asset = "ETH/USD"

def streamTrades():
    with connect("wss://ws.kraken.com/v2") as websocket:
        websocket.send(json.dumps({
            "method": "subscribe",
            "params": {
                "channel": "trade",
                "symbol": [
                    asset
                ],
            }
        }))
        message = websocket.recv()
        logger.critical(f"Received Trade: {message}")
# keep the connection open
        while True:
            message = websocket.recv()
            logger.debug(f"Trade error: {message}")

# stream order book
def streamOrderBook():
    with connect("wss://ws.kraken.com/v2") as websocket:
        websocket.send(json.dumps({
            "method": "subscribe",
            "params": {
                "channel": "book",
                "symbol": [
                    asset
                ],
            }
        }))
        message = websocket.recv()
        logger.warning(f"Received OrderBook Update: {message}")
# keep the connection open
        while True:
            message = websocket.recv()
            logger.debug(f"OrderBook error: {message}")

# start streaming of trades and order book
streamTrades()

