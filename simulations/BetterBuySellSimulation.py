from collections import deque
from datetime import datetime

class BuySellStrategy:
    def __init__(self, initial_balance, risk_level='medium', sell_all_threshold=0.001, alpha=0.1, window_size=10):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.crypto_held = 0
        self.risk_levels = {'low': 0.1, 'medium': 0.25, 'high': 0.5}
        self.sell_all_threshold = sell_all_threshold
        self.risk_factor = self.risk_levels.get(risk_level, 0.25)
        self.transaction_history = []
        self.alpha = alpha
        self.window_size = window_size
        self.price_window = deque(maxlen=window_size)
        self.ema_price = None
        self.min_trade_amount = 30
        self.min_crypto_amount = 0.001

    def _update_transaction_history(self, trade_amount=0.0, trade_price=0.0, traded_crypto=0.0):
        self.transaction_history.append({
            'balance': self.balance,
            'crypto_held': self.crypto_held,
            'trade_amount': trade_amount,
            'trade_price': trade_price,
            'traded_crypto': traded_crypto,
            'timestamp': len(self.transaction_history)
        })

    def update_ema(self, current_price):
        self.price_window.append(current_price)
        self.ema_price = sum(self.price_window) / len(self.price_window)
        
        if len(self.price_window) == self.window_size:
            weights = [(1 - self.alpha) ** i for i in range(self.window_size)]
            weights.reverse()
            weights_sum = sum(weights)
            normalized_weights = [w / weights_sum for w in weights]
            self.ema_price = sum(p * w for p, w in zip(self.price_window, normalized_weights))

    def interpret_action(self, action, current_price, current_rsi=None):
        trade_amount = 0.0
        traded_crypto = 0.0
        
        self.update_ema(current_price)
        
        if action == 1:
            if current_price <= self.ema_price:
                trade_amount = self.balance * self.risk_factor
                
                if trade_amount >= self.min_trade_amount and self.balance >= self.min_trade_amount:
                    crypto_to_buy = trade_amount / current_price
                    if crypto_to_buy >= self.min_crypto_amount:
                        self.balance -= trade_amount
                        self.crypto_held += crypto_to_buy
                        traded_crypto = crypto_to_buy
                    else:
                        trade_amount = 0.0
                else:
                    trade_amount = 0.0
            
        elif action == 2:
            if self.crypto_held > 0:
                price_diff_percent = ((current_price - self.ema_price) / self.ema_price) * 100
                
                if price_diff_percent >= 1.0:
                    sell_portion = 1.0
                elif price_diff_percent >= 0.5:
                    sell_portion = 0.75
                elif price_diff_percent >= 0.25:
                    sell_portion = 0.5
                elif price_diff_percent > 0:
                    sell_portion = 0.25
                else:
                    sell_portion = 0.1
                
                crypto_to_sell = self.crypto_held * sell_portion
                
                if (self.crypto_held - crypto_to_sell) < self.min_crypto_amount:
                    crypto_to_sell = self.crypto_held
                
                potential_trade_amount = crypto_to_sell * current_price
                if potential_trade_amount >= self.min_trade_amount and crypto_to_sell >= self.min_crypto_amount:
                    trade_amount = potential_trade_amount
                    self.balance += trade_amount
                    self.crypto_held -= crypto_to_sell
                    traded_crypto = crypto_to_sell
        
        self._update_transaction_history(trade_amount, current_price, traded_crypto)
        
        return traded_crypto
