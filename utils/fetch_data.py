from enum import Enum
import yfinance as yf

class Api(Enum):
    YAHOO = 1

def fetch_data(api, stock_symbol, start, end, interval='1d'):
    '''
    Fetches data from Yahoo Finance API

    Parameters
    ----------
    api : Enum
        API to fetch the data
    stock_symbol : str
        Symbol of the stock
    start : str
        Start date of the data
    end : str
        End date of the data
    interval : str
        Interval of the data (default is '1d')

    Returns:
    data: DataFrame: Data of the stock
    '''
    
    if not isinstance(stock_symbol, str):
        raise ValueError("stock_symbol should be a string")
    
    if not isinstance(start, str):
        raise ValueError("start should be a string")
    
    if not isinstance(end, str):
        raise ValueError("end should be a string")
    
    if api == Api.YAHOO:
        return yf.download(stock_symbol, start=start, end=end, interval=interval)
    else:
        raise ValueError("Invalid API")