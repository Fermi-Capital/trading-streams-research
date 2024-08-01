#!/usr/bin/env python
# ingest orderbook data from the Kraken API
# import streamOrderBook from ./stream/main.py
# stream order book data

from stream.main import streamOrderBook


def main():

    # stream order book data
    streamOrderBook()

if __name__ == "__main__":
    main()

