import sys
import os 
from datetime import timedelta, date, datetime
from yahoofinancials import YahooFinancials

# Code for gathering the latest day
latest_day = date.today() - timedelta(days=1)
print(latest_day.strftime('%A'))
if latest_day.strftime('%A') == 'Saturday':
    latest_day = latest_day - timedelta(days=3)
elif latest_day.strftime('%A') == 'Sunday':
    latest_day = latest_day - timedelta(days=3)
latest_day_str = latest_day.strftime('%Y-%m-%d') 
day_before_latest = latest_day - timedelta(days=1)
if day_before_latest.strftime('%A') == "Sunday":
    day_before_latest = day_before_latest - timedelta(days=2)
day_before_latest_str = day_before_latest.strftime('%Y-%m-%d')
symbol = sys.argv[1]

symbol_yahoo_finance_interactor = YahooFinancials(symbol)
earnings_days_data = symbol_yahoo_finance_interactor.get_historical_price_data(day_before_latest_str, latest_day_str, 'daily')

symbol_file = os.getcwd() + "\\earnings_call_difference_data\\preferred\\%s.csv"%symbol
csv_file = open(symbol_file, "r") 
# print(csv_file.read())

lines = csv_file.readlines()
# print(lines)

absolute_diff = float(lines[7].rstrip().split(',')[1][:-1])
positive_diff = float(lines[8].rstrip().split(',')[1][:-1])
negative_diff = float(lines[9].rstrip().split(',')[1][:-1])

print("Absolute Difference Average: %f"% absolute_diff)
print("Positive Difference Average: %f"% positive_diff)
print("Negative Difference Average: %f"% negative_diff)
# print(earnings_days_data)
current_price = earnings_days_data[symbol]['prices'][0]['close']

print("Current Price: %f"%current_price)
lower_strike = (round((current_price - ((abs(negative_diff)/100)*current_price))*2))/2
higher_strike = (round((current_price + ((positive_diff/100)*current_price))*2))/2
print("Lower Strike: %f"%lower_strike)
print("Higher Strike: %f"%higher_strike)
csv_file.close()