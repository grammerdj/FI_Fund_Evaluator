"""
Import Statements Necessary for Yahoo Finance Information Retrieval
"""
import yfinance as yf
import pandas as pd
# -------------------------------------------#
"""
Class: Scraper
Purpose: To retrieve the historical data from Yahoo Finance on the Fixed Income funds
"""
class Scraper():

    def __init__(self):
        """
        Initializing the attributes: ticker, return dataframe
        """
        # Attribute Placeholders
        self.ticker = None
        self.prices = None

# -------------------------------------------#

    def get_data(self, ticker):
        """
        Retrives the historical data from Yahoo Finance
        """
        # Step 0: Validate Ticker Type
        assert type(ticker) == str, f"Invalid Ticker Symbol Type: {type(ticker)}"

        # Step 1: Read the Data Into a Ticker Instance
        self.ticker = yf.Ticker(ticker)
        self.prices = yf.download(ticker, period='max')

        # Step 2: Validate the Ticker Exists
        assert self.ticker.history(period = 'max').shape[0] > 0, f"{ticker} not found in YFinance"

# -------------------------------------------#
