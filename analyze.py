from yahoofinancials import YahooFinancials
from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date
import matplotlib.pyplot as plts
import requests
import os

api_key = os.getenv('td_api_key')

# Return info as map

class LineGraph:
	def __init__(x_axis, title):
		self.x_axis = x_axis
		self.title = title

		self.x_len = len(x_axis)

	def addLine(symbol, data ,color):
		if len(data) == self.x_len:
			plt.plot(y_axis, data, color='g')

	def show():
		plt.show()

# ENTER: TSLA;DAY1-DAY2;9:30-16,16-20|4-9:30,9:30-16;30m
# RETURN: [1,2,2,2]
class PriceDifferenceRetriever:
	def __init__(self, time_str):
		self.retrieveDay = __timeStringParser(time_str)

	def __timeStringParser(self, time_str):
		days_times = time_str.split(";")
		timeframe = days_times[1].split("-")
		start_date = datetime.strptime(timeframe[0], '%Y%m%d')
		end_date = datetime.strptime(timeframe[1], '%Y%m%d')
		end_date = end_date + datetime.timedelta(days=1) # last day is not inclusive
		intraday_timeframes = days_times[2].split("|")
		for daydata in days:
			getPrices


def afterMarketCallDifferenceStrategy(date):


def beforeMarketCallDifferenceStrategy(date):
	day_before = date - 1 
	"TSLA;%s-%s-%s;9:30-20|4-9:30,9:30-16,16-20|4-9:30,9:30-16;30m"

def 
# This strategy is to simply compare during day movement, after market movement, and 
# before market movement the next day for earnings calls after market hours.
# Then compare it against intraday ,movement the next day, once at 12pm and once at 4pm
# The output of the data will look like this:
# TSLA 2/5/19
# Change during the day: 5%
# Change after hours: -16%
# Change before hours: -2%
# Change next day: -2%
def Strategy1():
	["intraday", "post-market", "pre-market", "intra-day"]

start_date = date(2018, 6, 13)
end_date = date(2019, 8, 14)
cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates", start_date, end_date)
cp.loadCached(True)
print(cp.earnings_map['AAPL'])

#TIME FRAME: "DAY:(9:30-16,16-20);DAY:(4-9:30,9:30-16)"
# "DIFFERENCE"
	

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