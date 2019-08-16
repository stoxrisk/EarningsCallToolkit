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
class IntraDayToolkit:
	def __init__(self, api_key):
		print("sda")
		self.td_api = TDAmeritradeAPI(api_key)
		print("sda2")
		
	def retrieveSelectedTimesDifferences(self, dates, times, ticker, candlestick):
		start_date = datetime.strptime(dates[0], '%Y%m%d')
		end_date = datetime.strptime(dates[len(dates)-1], '%Y%m%d')
		# Translate candlestick
		if candlestick == "30m":
			freq_type = "minute"
			freq_num = "30"
		# Convert to miliseconds for api call
		start_date = start_date.timestamp() * 1000
		end_date = end_date.timestamp() * 1000
		# Get all the data for this ticker
		data_return = td_api.getPrices(ticker, freq_type, freq_num, start_date, end_date).content
		print(data_return)
		# for daydata in days:

	def priceDifferenceBetweenTimes(candle1, candle2):
		pass
	



def afterMarketCallDifferenceStrategy(earnings_map, ticker_list):
	tk = IntraDayToolkit(api_key)
	after_market_strat_times = ["9:30-16,16-20", "4-9:30,9:30-16"]
	for ticker in ticker_list:
		for earningsdate in earningdate:
			dateandtime = earningsdate.split(":")
			# We only want to pay attention to stocks with after market close
			if(dateandtime[1] is not "amc"):
				return
			# Setup dates
			start_date = datetime.strptime(earningsdate[0], '%Y%m%d')
			end_date = datetime.strptime(earningsdate[0], '%Y%m%d')
			end_date = start_date + datetime.timedelta(days=1) # last day is not inclusive
			dates = [start_date, end_date]
			# Expected return [1.1,2.1,-1,2] in percentages
			retrieveSelectedTimesDifferences(dates, after_market_strat_times, ticker, "30m")
			# x_axis = ["intraday1", "aftermarket", "premarket", "intraday2"]
			# lg = LineGraph(x_axis, "After market strategy")


cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates")
cp.loadCached(True)
print(cp.earnings_map['AAPL'])
afterMarketCallDifferenceStrategy(cp.earnings_map, ["AAPL"])


# This strategy is to simply compare during day movement, after market movement, and 
# before market movement the next day for earnings calls after market hours.
# Then compare it against intraday ,movement the next day, once at 12pm and once at 4pm
# The output of the data will look like this:
# TSLA 2/5/19
# Change during the day: 5%
# Change after hours: -16%
# Change before hours: -2%
# Change next day: -2%
