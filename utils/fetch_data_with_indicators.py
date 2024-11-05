from enum import Enum
import numpy as np
import yfinance as yf
from typing import Union
from pandas import DataFrame
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from datetime import datetime

class Api(Enum):
    YAHOO = 1

def fetch_data_with_indicators(
    api: Api,
    stock_symbol: str,
    start: str,
    end: str,
    interval: str = '1d',
    indicators: None | list[str] = None
) -> DataFrame:
    '''
        Fetches data from Yahoo Finance API
    
        Parameters
        ----------
        api : Api
            API to fetch the data
        stock_symbol : str
            Symbol of the stock
        start : str
            Start date of the data in YYYY-MM-DD format
        end : str
            End date of the data in YYYY-MM-DD format
        interval : str
            Interval of the data (default is '1d')
        indicators : None | list[str]
            List of indicators to add to the data (default is None)
            Supported indicators: 'RSI', 'MACD', 'EMA_{window}'
    
        Returns
        -------
        DataFrame
            Dataframe containing the fetched data
            
        Raises
        ------
        ValueError
            If parameters are invalid or API is not supported
        RuntimeError
            If data fetching fails

        Examples
        --------
        >>> data = fetch_data(Api.YAHOO, "AAPL", "2023-01-01", "2023-12-31", "1d", ["RSI"])
     '''
    
    if not isinstance(stock_symbol, str):
        raise ValueError("stock_symbol should be a string")
    if not stock_symbol.strip():
        raise ValueError("stock_symbol cannot be empty")
    
    if not isinstance(start, str):
        raise ValueError("start should be a string")
    if not _is_valid_date_format(start):
        raise ValueError("start date must be in YYYY-MM-DD format")
    
    if not isinstance(end, str):
        raise ValueError("end should be a string")
    if not _is_valid_date_format(end):
        raise ValueError("end date must be in YYYY-MM-DD format")

    valid_intervals = {'1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'}
    if interval not in valid_intervals:
        raise ValueError(f"interval must be one of {valid_intervals}")

    if api == Api.YAHOO:
        try:
            data = yf.download(stock_symbol, start=start, end=end, interval=interval)
            if data.empty:
                raise ValueError(f"No data available for {stock_symbol} between {start} and {end}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data: {str(e)}") from e
    else:
        raise ValueError("Invalid API")
    
    if indicators is None:
        return data
    
    dropna_elements = []
    
    indicators = [indicator.upper() for indicator in indicators]
    for indicator in indicators:
        if indicator == 'RSI':
            data = add_rsi(data)
            dropna_elements.append('RSI')
        elif indicator == 'MACD':
            data = add_macd(data)
            dropna_elements.extend(['MACD_LINE', 'MACD_SIGNAL', 'MACD_HIST'])
        elif indicator.startswith('EMA'):
            window = int(indicator.split('_')[1])
            data = add_ema(data, window)
            dropna_elements.append(f'EMA_{window}')
        else:
            raise ValueError(f"Invalid indicator: {indicator}")
    
    data = data.dropna(subset=dropna_elements)
    
    return data


def _is_valid_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
def add_rsi(data: DataFrame) -> DataFrame:
    """Add Relative Strength Index (RSI) to the data."""
    data['RSI'] = RSIIndicator(data['Close']).rsi()
    
    return data

def add_macd(data: DataFrame) -> DataFrame:
    """Add Moving Average Convergence Divergence (MACD) to the data."""
    macd = MACD(data['Close'])
    data['MACD_LINE'] = macd.macd()
    data['MACD_SIGNAL'] = macd.macd_signal()
    data['MACD_HIST'] = macd.macd_diff()

    return data

def add_ema(data: DataFrame, window: int) -> DataFrame:
    """Add Exponential Moving Average (EMA) to the data."""
    data[f'EMA_{window}'] = EMAIndicator(data['Close'], window=window).ema_indicator()
    
    return data