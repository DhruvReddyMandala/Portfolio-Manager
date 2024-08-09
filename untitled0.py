

import pandas as pd
import requests
from datetime import datetime

class Portfolio:
    def __init__(self):
        self.portfolio = pd.DataFrame(columns=['Symbol', 'Shares', 'Purchase Price', 'Current Price', 'Dividends'])
        self.transaction_history = pd.DataFrame(columns=['Date', 'Symbol', 'Action', 'Shares', 'Price', 'Dividends'])

    def add_investment(self, symbol, shares, purchase_price, current_price, dividends=0):
        """Add a new investment to the portfolio."""
        new_investment = pd.DataFrame([[symbol, shares, purchase_price, current_price, dividends]],
                                      columns=['Symbol', 'Shares', 'Purchase Price', 'Current Price', 'Dividends'])
        self.portfolio = pd.concat([self.portfolio, new_investment], ignore_index=True)
        self.record_transaction('Buy', symbol, shares, purchase_price, dividends)

    def remove_investment(self, symbol):
        """Remove an investment from the portfolio based on the symbol."""
        shares_to_sell = self.portfolio[self.portfolio['Symbol'] == symbol]['Shares'].sum()
        if shares_to_sell > 0:
            self.record_transaction('Sell', symbol, shares_to_sell, self.portfolio[self.portfolio['Symbol'] == symbol]['Current Price'].values[0])
            self.portfolio = self.portfolio[self.portfolio['Symbol'] != symbol]

    def update_price(self, symbol, new_price):
        """Update the current price of an investment."""
        self.portfolio.loc[self.portfolio['Symbol'] == symbol, 'Current Price'] = new_price

    def add_dividends(self, symbol, amount_per_share):
        """Add dividends to an investment."""
        self.portfolio.loc[self.portfolio['Symbol'] == symbol, 'Dividends'] += amount_per_share
        self.record_transaction('Dividend', symbol, 0, 0, amount_per_share)

    def fetch_current_price(self, symbol):
        """Fetch the current price of the stock from an API."""
        api_key = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Replace with your actual API key
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'

        try:
            response = requests.get(url)
            data = response.json()
            print(data)  # Print the response to inspect its structure

            # Check if the expected key exists in the response
            if 'Time Series (1min)' not in data:
                raise KeyError("Key 'Time Series (1min)' not found in the response.")

            latest_time = max(data['Time Series (1min)'].keys())
            return float(data['Time Series (1min)'][latest_time]['1. open'])

        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
        except KeyError as e:
            print(f"KeyError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return None

    def calculate_total_value(self):
        """Calculate the total value of the portfolio."""
        self.portfolio['Value'] = self.portfolio['Shares'] * self.portfolio['Current Price']
        return self.portfolio['Value'].sum()

    def calculate_total_return(self):
        """Calculate the total return of the portfolio."""
        self.portfolio['Return'] = (self.portfolio['Current Price'] - self.portfolio['Purchase Price']) * self.portfolio['Shares']
        return self.portfolio['Return'].sum()

    def record_transaction(self, action, symbol, shares, price, dividends=0):
        """Record a transaction."""
        transaction = pd.DataFrame([[datetime.now(), symbol, action, shares, price, dividends]],
                                   columns=['Date', 'Symbol', 'Action', 'Shares', 'Price', 'Dividends'])
        self.transaction_history = pd.concat([self.transaction_history, transaction], ignore_index=True)

    def display_portfolio(self):
        """Display the current state of the portfolio."""
        return self.portfolio

    def display_transaction_history(self):
        """Display the transaction history."""
        return self.transaction_history

if __name__ == "__main__":
    my_portfolio = Portfolio()

    # Adding some investments
    my_portfolio.add_investment('NVDA', 100, 630, 100,000)
    my_portfolio.add_investment('GOOGL', 5, 2800, 2900)
    my_portfolio.add_investment('APPL', 100, 10, 150)

    # Display portfolio
    print("Portfolio:")
    print(my_portfolio.display_portfolio())

    # Calculate and display total value and return
    total_value = my_portfolio.calculate_total_value()
    total_return = my_portfolio.calculate_total_return()

    print(f"\nTotal Portfolio Value: ${total_value:.2f}")
    print(f"Total Portfolio Return: ${total_return:.2f}")

    # Fetch and update price
    current_price = my_portfolio.fetch_current_price('AAPL')
    if current_price is not None:
        my_portfolio.update_price('AAPL', current_price)
        print("\nUpdated Portfolio:")
        print(my_portfolio.display_portfolio())

    # Add dividends
    my_portfolio.add_dividends('APPL', 2.5)

    # Display updated transaction history
    print("\nTransaction History:")
    print(my_portfolio.display_transaction_history())

    # Recalculate and display updated total value and return
    total_value = my_portfolio.calculate_total_value()
    total_return = my_portfolio.calculate_total_return()

    print(f"\nUpdated Total Portfolio Value: ${total_value:.2f}")
    print(f"Updated Total Portfolio Return: ${total_return:.2f}")
