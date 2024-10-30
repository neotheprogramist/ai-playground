from matplotlib import pyplot as plt


def plot_buy_and_sell(data):
    """
    Plots the closing prices of the stock along with buy and sell signals.
    Buy signals are represented by green dots and sell signals are represented by red dots.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the closing prices and buy/sell signals.
        It should have the following columns: 'Close' and 'Action'.
        'Action' column should have values 0, 1, or 2.
        0: Buy Signal
        1: Hold Signal
        2: Sell Signal

    Returns
    -------
    None
    """

    # Check if 'Close' column exists
    check_close_column(data)

    # Check if 'Action' column exists
    check_action_column(data)

    # Get buy and sell signals
    buy_signals = data[data['Action'] == 0]
    sell_signals = data[data['Action'] == 2]

    # Plot the closing prices
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue', linewidth=1.5)

    # Plot buy signals (green dots)
    plt.scatter(buy_signals.index, buy_signals['Close'], color='green', label='Buy Signal', marker='o', s=10)

    # Plot sell signals (red dots)
    plt.scatter(sell_signals.index, sell_signals['Close'], color='red', label='Sell Signal', marker='o', s=10)

    # Adding labels and legend
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title('Stock Price with Buy and Sell Signals')
    plt.legend()
    plt.grid(True)
    plt.show()

def check_close_column(dataframe):
    if 'Close' not in dataframe.columns:
        raise ValueError("Error: Column 'Close' does not exist in the DataFrame.")
    
def check_action_column(dataframe):
    if 'Action' not in dataframe.columns:
        raise ValueError("Error: Column 'Action' does not exist in the DataFrame.")