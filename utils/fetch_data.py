from enum import Enum
import yfinance as yf
from typing import Union
from pandas import DataFrame

class Api(Enum):
    YAHOO = 1

def fetch_data(
    api: Api,
    stock_symbol: str,
    start: str,
    end: str,
    interval: str = '1d'
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
    
        Returns
        -------
        DataFrame
            OHLCV data for the requested stock

        Raises
        ------
        ValueError
            If parameters are invalid or API is not supported
        RuntimeError
            If data fetching fails

        Examples
        --------
        >>> data = fetch_data(Api.YAHOO, "AAPL", "2023-01-01", "2023-12-31")
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
            return data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data: {str(e)}") from e
    else:
        raise ValueError("Invalid API")
    
from datetime import datetime

def _is_valid_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False