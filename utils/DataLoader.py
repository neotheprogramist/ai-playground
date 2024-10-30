import ta.momentum
import ta.trend
import ta.volatility
import yfinance as yf
import ta
import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np

class DataLoader:
  def __init__(self, pair="BTC-USD", start='2022-01-01', end='2023-01-01', freq='1d'):
    self.pair = pair
    self.start = start
    self.end = end
    self.freq = freq
    self.scaler = StandardScaler()

    self.data = self.yfLoad()
    self.scaler.fit(self.data[:, 1:])
    self.scaled_data = self.scaler.fit_transform(self.data[:, 1:])

  def __len__(self):
      return len(self.data)
      
  def __getitem__(self, idx, col_idx=None):
      if col_idx is None:
        return self.data[idx]
      elif col_idx < len(list(self.data.columns)):
        return self.data[idx][col_idx]
      else:
        raise IndexError
    
  def yfLoad(self):
    df = yf.download([self.pair], start=self.start, end=self.end, interval=self.freq)
    
    df['next_day_reward'] = df['Adj Close'].pct_change().shift(-1)
    df['reward_day'] = df['Adj Close'].pct_change(1)
    
    rsi = ta.momentum.RSIIndicator(df['reward_day'], window=14)
    macd = ta.trend.MACD(df['reward_day'], window_slow=26, window_fast=12, window_sign=9)

    df['RSI'] = rsi.rsi()
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['Volume_day_pct_change'] = df['Volume'].pct_change(1)

    bollinger_lback = 20
    df["bollinger"] = df["reward_day"].ewm(bollinger_lback).mean()
    df["low_bollinger"] = df["bollinger"] - 2 * df["reward_day"].rolling(bollinger_lback).std()
    df["high_bollinger"] = df["bollinger"] + 2 * df["reward_day"].rolling(bollinger_lback).std()

    # Interpolation
    for c in df.columns:
      df[c] = df[c].interpolate('linear', limit_direction='both')

    # Drop NaNs
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    self.frame = df
    # drop yfinance fetched values, leave only indicators
    data = np.array(df.iloc[:, 6:])
    return data