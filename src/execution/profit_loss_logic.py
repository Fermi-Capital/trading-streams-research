    
class ProfitLossLogic:   
    def calculate_effective_price(self, prices, quantities, amount):
        """
        prices = [29900, 29850, 29800]  # USD
        quantities = [0.5, 0.3, 0.2]  # BTC
        amount = 0.7 # the amount of BTC to buy or sell
        """
        total_amount = 0
        total_value = 0
        for price, quantity in zip(prices, quantities):
            if amount <= 0:
                break
            if quantity <= amount:
                total_value += price * quantity
                total_amount += quantity
                amount -= quantity
            else:
                total_value += price * amount
                total_amount += amount
                amount = 0
        if total_amount == 0:
            return 0  # Avoid division by zero if no orders are available
        return total_value / total_amount

    def calculate_profit_or_loss_with_order_book(self, position_type, entry_price, amount, fee_percentage, bid_prices, bid_quantities, ask_prices, ask_quantities):
        '''
        position_type = 'long' or 'short'
        entry_price = 30000  # USD
        amount = 0.5  # BTC
        fee_percentage = 0.4% fee
        bid_prices = [29900, 29850, 29800]  # USD
        bid_quantities = [0.5, 0.3, 0.2]  # BTC
        ask_prices = [30050, 30100, 30150]  # USD
        ask_quantities = [0.4, 0.4, 0.2]  # BTC
    
        # Example usage with user inputs
        position_type = input("Enter the position type (long/short): ").strip().lower()
        entry_price = float(input("Enter the entry price (USD): "))
        amount = float(input("Enter the amount (BTC): "))
        fee_percentage = float(input("Enter the fee percentage: "))

        # Example bid and ask prices and quantities
        bid_prices = [29900, 29850, 29800]  # USD
        bid_quantities = [0.5, 0.3, 0.2]  # BTC
        ask_prices = [30050, 30100, 30150]  # USD
        ask_quantities = [0.4, 0.4, 0.2]  # BTC
        '''
        # Calculate the initial investment or revenue
        initial_value = entry_price * amount
        
        if position_type == 'long':
            # Calculate the effective selling price based on order book depth
            effective_price = self.calculate_effective_price(bid_prices, bid_quantities, amount)
        elif position_type == 'short':
            # Calculate the effective buying price based on order book depth
            effective_price = self.calculate_effective_price(ask_prices, ask_quantities, amount)
        else:
            raise ValueError("Invalid position type. Use 'long' or 'short'.")
        
        # Calculate the total amount before the fee
        total_amount = effective_price * amount
        
        # Calculate the total fee
        total_fee = total_amount * (fee_percentage / 100)
        
        # Calculate the net amount after subtracting the fee
        net_amount = total_amount - total_fee
        
        if position_type == 'long':
            # Calculate profit or loss for long position
            profit_or_loss = net_amount - initial_value
        elif position_type == 'short':
            # Calculate profit or loss for short position
            profit_or_loss = initial_value - net_amount
        
        return profit_or_loss
    
# # test it out 
# profit_loss_logic = ProfitLossLogic()
# profit_loss = profit_loss_logic.calculate_profit_or_loss_with_order_book('long', 29800, 1, 0.01, [29900, 29850, 29800], [1, 0.3, 0.2], [30050, 30100, 30150], [0.4, 0.4, 0.2])
# print(profit_loss, "fee", 30000 * 0.01)
