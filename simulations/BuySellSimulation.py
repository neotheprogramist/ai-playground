# simulations/BuySellSimulation.py
class BuySellInParts:
    def __init__(self, initial_balance, risk_level='medium', sell_all_threshold=0.001):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.crypto_held = 0
        self.risk_levels = {
            'low': 0.1,
            'medium': 0.25,
            'high': 0.5
        }
        self.sell_all_threshold = sell_all_threshold
        self.risk_factor = self.risk_levels.get(risk_level, 0.25)
        self.transaction_history = []
   
        self._update_transaction_history(trade_amount=0.0, trade_price=0.0)
        
    def _update_transaction_history(self, trade_amount=0.0, trade_price=0.0, traded_crypto=0.0):
        self.transaction_history.append({
            'balance': self.balance,
            'crypto_held': self.crypto_held,
            'trade_amount': trade_amount,
            'trade_price': trade_price,
            'traded_crypto': traded_crypto,
            'timestamp': len(self.transaction_history)
        })
        
    def interpret_action(self, action, current_price, current_step):
        trade_amount = 0.0
        traded_crypto = 0.0
        
        if action == 1:  # Buy
            if self.balance > self.initial_balance * 0.5:
                trade_amount = self.balance * self.risk_factor
                crypto_to_buy = trade_amount / current_price
                self.balance -= trade_amount
                self.crypto_held += crypto_to_buy
                traded_crypto = crypto_to_buy
                
        elif action == 2:  # Sell
            if self.crypto_held > self.sell_all_threshold:
                crypto_to_sell = self.crypto_held * self.risk_factor
            elif self.crypto_held < self.sell_all_threshold and self.crypto_held > 0:
                crypto_to_sell = self.crypto_held
            else:
                crypto_to_sell = 0.0
            
            if crypto_to_sell > 0:
                trade_amount = crypto_to_sell * current_price
                self.balance += trade_amount
                self.crypto_held -= crypto_to_sell
                traded_crypto = crypto_to_sell
            
        self._update_transaction_history(trade_amount, current_price, traded_crypto)
        
        return traded_crypto
