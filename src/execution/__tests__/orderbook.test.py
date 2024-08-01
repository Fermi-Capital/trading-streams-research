from ..orderbook import OrderBook 

# write tests for the orderBookData function
def test_orderBookData(self):
    data = self.orderBookData()
    assert isinstance(data['bid_prices'], list)
    assert isinstance(data['bid_quantities'], list)
    assert isinstance(data['ask_prices'], list)
    assert isinstance(data['ask_quantities'], list)
    assert isinstance(data['spread'], float)
    assert isinstance(data['spread_percentage'], float)
    print("All tests pass")
    return True

# test the orderBookData function
orderbook = OrderBook("SOLUSD")
test_orderBookData(orderbook)
