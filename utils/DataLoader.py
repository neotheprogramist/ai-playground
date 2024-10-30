import ta.momentum
import ta.trend
import ta.volatility
import yfinance as yf
import ta
import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np


class DataLoader:
    """
    A class used to load and preprocess financial data for a given trading pair.
    Attributes
    ----------
    pair : str
        The trading pair to load data for (default is "BTC-USD").
    start : str
        The start date for the data in 'YYYY-MM-DD' format (default is '2022-01-01').
    end : str
        The end date for the data in 'YYYY-MM-DD' format (default is '2023-01-01').
    freq : str
        The frequency of the data (default is '1d').
    scaler : StandardScaler
        An instance of StandardScaler used to scale the data.
    data : np.ndarray
        The raw data loaded from Yahoo Finance.
    scaled_data : np.ndarray
        The scaled version of the data.
    frame : pd.DataFrame
        The DataFrame containing the processed data with technical indicators.
    Methods
    -------
    __len__():
        Returns the length of the data.
    __getitem__(idx, col_idx=None):
        Returns the data at the specified index and column index.
    yfLoad():
        Loads data from Yahoo Finance, calculates technical indicators, and preprocesses the data.
    """

    def __init__(self, pair="BTC-USD", start="2022-01-01", end="2023-01-01", freq="1d"):
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
        """
        Downloads historical stock data using yfinance, calculates various technical indicators,
        and returns the processed data.

        The method performs the following steps:
        1. Downloads historical stock data for the specified pair, date range, and frequency.
        2. Calculates the next day's reward and the daily reward based on the adjusted close prices.
        3. Computes the Relative Strength Index (RSI) and Moving Average Convergence Divergence (MACD) indicators.
        4. Calculates the percentage change in volume on a daily basis.
        5. Computes Bollinger Bands using an exponential moving average and standard deviation.
        6. Interpolates missing values linearly in both directions.
        7. Replaces infinite values with NaNs and drops any remaining NaNs.
        8. Stores the processed DataFrame in the `self.frame` attribute.
        9. Returns a NumPy array containing only the calculated indicators.

        Returns:
            np.ndarray: A NumPy array containing the calculated technical indicators.
        """
        df = yf.download(
            [self.pair], start=self.start, end=self.end, interval=self.freq
        )

        df["next_day_reward"] = df["Adj Close"].pct_change().shift(-1)
        df["reward_day"] = df["Adj Close"].pct_change(1)

        rsi = ta.momentum.RSIIndicator(df["reward_day"], window=14)
        macd = ta.trend.MACD(
            df["reward_day"], window_slow=26, window_fast=12, window_sign=9
        )

        df["RSI"] = rsi.rsi()
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["Volume_day_pct_change"] = df["Volume"].pct_change(1)

        bollinger_lback = 20
        df["bollinger"] = df["reward_day"].ewm(bollinger_lback).mean()
        df["low_bollinger"] = (
            df["bollinger"] - 2 * df["reward_day"].rolling(bollinger_lback).std()
        )
        df["high_bollinger"] = (
            df["bollinger"] + 2 * df["reward_day"].rolling(bollinger_lback).std()
        )

        # Interpolation
        for c in df.columns:
            df[c] = df[c].interpolate("linear", limit_direction="both")

        # Drop NaNs
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)

        self.frame = df
        # drop yfinance fetched values, leave only indicators
        data = np.array(df.iloc[:, 6:])
        return data
