"""
Nathan Scott
Quantitative Momentum Strategy
Personal Project
Not for real world use
"""

import numpy as np
import os
import pandas as pd
import xlsxwriter
import math
from scipy import stats
from statistics import mean
from extract_market_data import extract_market_data


def retrieve_data():
    """Check for CSV file and process its data"""
    filename = "snp500_marketdata.csv"

    # Check if file in directory
    if not os.path.exists(filename):
        extract_market_data()

    data = pd.read_csv(filename)
    return data


def calc_momentum_percentile(data):
    """Calculate the momentum percentiles for the given data"""
    time_periods = [
        "One-Year",
        "Six-Month",
        "Three-Month",
        "One-Month"
    ]

    for row in data.index:
        for time_period in time_periods:
            data.loc[row, f'{time_period} Return Percentile'] = (
                    stats.percentileofscore(
                        data[f'{time_period} Price Return'],
                        data.loc[row, f'{time_period} Price Return'])/100)

    for time_period in time_periods:
        print(data[f'{time_period} Return Percentile'])

    for row in data.index:
        momentum_percentiles = []
        for time_period in time_periods:
            momentum_percentiles.append(data.loc[row, f'{time_period} Return Percentile'])
        data.loc[row, 'HQM Score'] = mean(momentum_percentiles)

    data.sort_values(by="HQM Score", ascending=False)
    return data[:51]


def shares_to_buy(stock_dataframe):
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
    position_size = val / len(stock_dataframe.index)
    for i in range(len(stock_dataframe)):
        stock_price = stock_dataframe.loc[i, 'Stock Price']
        if pd.notna(stock_price) and isinstance(stock_price, (int, float)):
            stock_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / stock_price)
        else:
            stock_dataframe.loc[i, 'Number of Shares to Buy'] = 'N/A'
    return stock_dataframe


def build_spreadsheet(final_data):
    """Write our final data to a csv file"""
    writer = pd.ExcelWriter('quantitative_momentum_recommended_trades.xlsx', engine='xlsxwriter')
    final_data.to_excel(writer, sheet_name='Momentum Strategy', index=False)

    background_color = '#ffffff'
    font_color = '#000000'

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
            'num_format': '0.000',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
    percent_format = writer.book.add_format(
        {
            'num_format': '0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    column_formats = {
        'A': ['Stock', string_format],
        'B': ['Stock Price', dollar_format],
        'C': ['Market Capitalisation', dollar_format],
        'D': ['Number of Shares to Buy', integer_format],
        'E': ['One-Year Price Return', percent_format],
        'F': ['One-Year Return Percentile', percent_format],
        'G': ['Six-Month Price Return', percent_format],
        'H': ['Six-Month Return Percentile', percent_format],
        'I': ['Three-Month Price Return', percent_format],
        'J': ['Three-Month Return Percentile', percent_format],
        'K': ['One-Month Price Return', percent_format],
        'L': ['One-Month Return Percentile', percent_format],
        'M': ['HQM Score', integer_format],
        'N': ['Trailing Price to Earnings Ratio', dollar_format]
    }

    for column in column_formats.keys():
        writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
        writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_format)

    writer.close()


stock_data = retrieve_data()
momentum_percentile_data = calc_momentum_percentile(stock_data)
final_stock_data = shares_to_buy(momentum_percentile_data)
build_spreadsheet(final_stock_data)
