"""
Nathan Scott
Extracting Market Data
Personal Project
Not for real world use
"""

import pandas as pd
import requests
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
    updated_sp500_tickers = [item.replace('.', '-') for item in sp500_tickers]
    return updated_sp500_tickers


# def fetch_snp500_data(tickers):
#     """Fetch stock market data for the stocks in tickers"""
#     my_columns = ['Stock', 'Stock Price', 'Previous Close', 'Overnight Price Return', 'Market Capitalisation',
#                   'Trailing Price to Earnings Ratio', 'Number of Shares to Buy']
#     data = []
#     for ticker in tickers:
#         try:
#             stock = yf.Ticker(ticker)
#             info = stock.info
#             overnight_price_change = info.get('currentPrice') / info.get('previousClose')
#             data.append([ticker, info.get('currentPrice'), info.get('previousClose'), overnight_price_change,
#                          info.get('marketCap'),
#                          info.get('trailingPE'), 'N/A'])
#         except Exception as e:
#             print(f"Error fetching data for {ticker}: {e}")
#     final_dataframe = pd.DataFrame(data, columns=my_columns)
#     return final_dataframe


def calculate_price_returns(stock_info):
    """Calculate the price return percentage for 12, 6, 3 and 1 months"""
    # historic_price = stock_info.history(period="1y")
    # # print(historic_price)
    # if len(historic_price) < 252:
    #     print("Not enough data")
    #     return False
    try:
        historic_price = stock_info.history(period="1y")
        today_price = stock_info.info.get('currentPrice')
        one_month_price = historic_price['Close'].iloc[-22]
        three_month_price = historic_price['Close'].iloc[-66]
        six_month_price = historic_price['Close'].iloc[-126]
        twelve_month_price = historic_price['Close'].iloc[0]

        one_month_return = (today_price - one_month_price) / one_month_price
        three_month_return = (today_price - three_month_price) / three_month_price
        six_month_return = (today_price - six_month_price) / six_month_price
        twelve_month_return = (today_price - twelve_month_price) / twelve_month_price

        results = [twelve_month_return, six_month_return, three_month_return, one_month_return]
    except:
        results = False

    return results


def fetch_snp500_data(tickers):
    """Fetch stock market data for the stocks in tickers"""
    my_columns = ['Stock',
                  'Stock Price',
                  'Market Capitalisation',
                  'Number of Shares to Buy',
                  'One-Year Price Return',
                  'One-Year Return Percentile',
                  'Six-Month Price Return',
                  'Six-Month Return Percentile',
                  'Three-Month Price Return',
                  'Three-Month Return Percentile',
                  'One-Month Price Return',
                  'One-Month Return Percentile',
                  'HQM Score',
                  'Trailing Price to Earnings Ratio']
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price_returns = calculate_price_returns(stock)
            if price_returns:
                data.append([ticker, info.get('currentPrice'), info.get('marketCap'), 'N/A',
                             price_returns[0], 'N/A', price_returns[1], 'N/A',
                             price_returns[2], 'N/A', price_returns[3], 'N/A',
                             'N/A', info.get('trailingPE')])
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    final_dataframe = pd.DataFrame(data, columns=my_columns)
    return final_dataframe


def build_spreadsheet(final_data):
    """Write the data to a CSV file"""
    file_name = 'snp500_marketdata.csv'

    # Write the data to a CSV file
    final_data.to_csv(file_name, index=False)


def extract_market_data():
    """Extract market data"""
    stocks_list = fetch_snp500_stocklist()
    stock_datasheet = fetch_snp500_data(stocks_list)
    build_spreadsheet(stock_datasheet)
