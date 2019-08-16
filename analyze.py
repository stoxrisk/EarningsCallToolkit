from yahoofinancials import YahooFinancials
from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date
import requests
import os

api_key = os.getenv('td_api_key')

# Return info as map

earnings_cache = {}

class EarningsData:

	def __init__(self, timeframe, ticker, numEarningsCalls):
		self.timeframe = timeframe
		self.ticker = ticker

	def dayBefore(self):
		pass

	def dayBeforeChange(self):
		pass

	def afterHours(self):
		pass

	def afterHoursChange(self):
		pass

	def dayAfter(self):
		pass

	def dayAfterChange(self):
		pass

class Strategy1():
	def __init__():
		pass

start_date = date(2018, 6, 13)
end_date = date(2019, 8, 14)
cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates", start_date, end_date)
cp.loadCached(True)
print(cp.earnings_map['AAAP'])

# Desired return output
# ---------------------------- 
# TSLA 2/5/19
# Change during the day: 5%
# Change after hours: -16%
# Change next day: -2%
# ----------------------------
# Also present a visualization

# Consider surprise factor?

# Pull from list of tickets

# for ticker in tickers:
# 	data = EarningsData('5m', ticker, 4)
# 	print('')

# START_DATE = datetime.date(2004, 9, 25)
# END_DATE = datetime.date(2004, 10, 8)
# day = datetime.timedelta(days=1)

# while START_DATE <= END_DATE:
#     print START_DATE.strftime('%Y.%m.%d')
#     START_DATE = START_DATE + day

# yahoo_financials = YahooFinancials(ticker)