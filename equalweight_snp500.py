"""
Nathan Scott
Equal Weight SNP500 Algorithm
Personal Project
Not for real-world use
"""

import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
import yfinance as yf
from io import StringIO


def fetch_snp500_stocklist():
    """Get a list of stocks on snp500"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    html_buffer = StringIO(response.text)
    tables = pd.read_html(html_buffer)

    # Extract the table with tickers
    sp500_table = tables[0]  # The first table contains the S&P 500 stocks
    sp500_tickers = sp500_table['Symbol'].tolist()  # Get the ticker column
    return sp500_tickers


def fetch_snp500_data(tickers):
    """Fetch stock market data for the stocks in tickers"""
    my_columns = ['Stock', 'Stock Price', 'Market Capitalisation', 'Number of Shares to Buy']
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data.append([ticker, info.get('currentPrice'), info.get('marketCap'), 'N/A'])
            print(ticker)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    final_dataframe = pd.DataFrame(data, columns=my_columns)
    return final_dataframe


def shares_to_buy(stock_data):
    """Calculate the number of shares to buy/sell"""
    # Prompt the user for portfolio size
    portfolio_recorded = False
    while not portfolio_recorded:
        portfolio_size = input("Enter the value of your portfolio:")
        try:
            val = float(portfolio_size)
            portfolio_recorded = True
        except ValueError:
            print("Thats not a number! Try again\n")
    print(f"Portfolio size recorded: {val}")

    # Determine number of shares to buy
    position_size = val / len(stock_data.index)
    for i in range(len(stock_data)):
        stock_price = stock_data.loc[i, 'Stock Price']
        if pd.notna(stock_price) and isinstance(stock_price, (int, float)):
            stock_data.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / stock_price)
        else:
            stock_data.loc[i, 'Number of Shares to Buy'] = 'N/A'
    print("Data recorded\n")
    return stock_data


def build_spreadsheet(final_data):
    """Write our final data to a csv file"""
    writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
    final_data.to_excel(writer, sheet_name='Recommended Trades', index=False)

    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    dollar_format = writer.book.add_format(
        {
            'num_format': '$0:00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    integer_format = writer.book.add_format(
        {
            'num_format': '0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    column_formats = {
        'A': ['Stock', string_format],
        'B': ['Stock Price', dollar_format],
        'C': ['Market Capitalisation', dollar_format],
        'D': ['Number of Shares to Buy', integer_format]
    }

    for column in column_formats.keys():
        writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
        writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

    writer.close()


sp_stocklist = fetch_snp500_stocklist()
stock_data = fetch_snp500_data(sp_stocklist)
final_stock_data = shares_to_buy(stock_data)
build_spreadsheet(final_stock_data)

