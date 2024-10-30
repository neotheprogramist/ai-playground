import yfinance as yf

def fetch_data(stock_symbol, start, end):
    data = yf.download(stock_symbol, start=start, end=end)

    return data