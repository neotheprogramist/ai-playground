from matplotlib import pyplot as plt
import pandas as pd

def plot_data_with_rsi(data: pd.DataFrame):
    """
    Plots the Close Price and Relative Strength Index (RSI) of the stock.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the Close Price and RSI values.
        It should have the following columns: 'Close' and 'RSI'.
        
    Returns
    -------
    None
    """
    
    buy_signals = data[data['Action'] == 1]
    sell_signals = data[data['Action'] == 2]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

    ax1.plot(data['Close'], label='Close Price')
        # Plot buy signals (green dots)
    ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', label='Buy Signal', marker='o', s=10)

    # Plot sell signals (red dots)
    ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', label='Sell Signal', marker='o', s=10)
    ax1.set_title('Close Price')
    ax1.set_ylabel('Price')
    ax1.legend()

    ax2.plot(data['RSI'], label='RSI', color='orange')
    ax2.axhline(70, linestyle='--', color='red', label='Overbought')
    ax2.axhline(30, linestyle='--', color='green', label='Oversold')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI')
    ax2.legend()

    plt.tight_layout()
    plt.show()
    plt.close()