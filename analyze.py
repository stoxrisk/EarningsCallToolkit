from yahoofinancials import YahooFinancials
from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date, datetime
import matplotlib.pyplot as plts
import requests
import os
import json

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
		self.td_api = TDAmeritradeAPI(api_key)

	def __convertTimesMiliseconds(self, date, time):
		times_list = [] 
		# reset for the 20 hour end day
		date = date.replace(hour=0)
		for pull_time in time.split(","):
			if pull_time == "9:30":
				ret_time = ret_time + timedelta(hours=9, minutes=30)
			else:
				ret_time = ret_time + timedelta(hours=pull_time)
			ret_time = date.timestamp() * 1000
			times_list.append(str(ret_time))
		

	def retrieveSelectedTimesDifferences(self, dates, times, ticker, candlestick):
		# Translate candlestick
		if str(dates[0].year) != "2019":
			return	 
		if candlestick == "30m":
			freq_type = "minute"
			freq_num = "30"
		# Convert to miliseconds for api call
		start_date = dates[0].timestamp() * 1000
		end_date = dates[len(dates)-1].timestamp() * 1000
		data_return = self.td_api.getPrices(ticker, freq_type, freq_num, str(int(end_date)), str(int(start_date))).content
		data_return = json.loads(data_return)
		# print(data_return)
		candles = data_return["candles"]
		# no need for two seperate lists if using miliseconds, it incorporates days
		milisecond_list = []
		print('hello')
		for i in range(0, len(times)):
			#Returns it as a list of lists
			milisecond_list += self.__convertTimesMiliseconds(times[i], dates[i])
		# h keeps track of which item in miliscond list you are trying to find
		h = 0
		close_list = []
		print(candles)
		for candle in candles:
			print("Looking for: %s" % milisecond_list[h])
			if candle["datetime"] == start_date:
				close_list.append(candle["close"])
				h += 1

		# for daydata in days:

	def priceDifferenceBetweenTimes(candle1, candle2):
		pass
	



def afterMarketCallDifferenceStrategy(earnings_map, ticker_list):
	tk = IntraDayToolkit(api_key)
	after_market_strat_times = ["9:30,16,20", "4,9:30,16"]
	for ticker in ticker_list:
		earnings_date_list = cp.earnings_map[ticker]
		for earningsdate in earnings_date_list:
			# try:
			dateandtime = earningsdate.split(":")
			# We only want to pay attention to stocks with after market close
			if(dateandtime[1] != "amc"):
				return
			# Setup dates
			start_date = datetime.strptime(dateandtime[0], '%Y%m%d')
			end_date = datetime.strptime(dateandtime[0], '%Y%m%d')
			end_date = start_date + timedelta(days=1, hours=20) # last day is not inclusive
			dates = [start_date, end_date]
			# Expected return [1.1,2.1,-1,2] in percentages
			changes = tk.retrieveSelectedTimesDifferences(dates, after_market_strat_times, ticker, "30m")
			# x_axis = ["intraday1", "aftermarket", "premarket", "intraday2"]
			# lg = LineGraph(x_axis, "After market strategy")
			# except Exception as e: # Last line sometimes throws an error as it's blank
			# 	print("End of list for %s"%ticker)

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
