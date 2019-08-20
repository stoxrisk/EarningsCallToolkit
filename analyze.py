from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date, datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests
import os
import json

api_key = os.getenv('td_api_key')

# Class for creating a linegraph with many different lines, each line representing change over time periods
class LineGraph:
	def __init__(self, x_axis, title):
		self.x_axis = x_axis
		self.title = title
		self.color = "C0"
		self.x_len = len(x_axis)

		mpl.style.use('seaborn')

	def changeColor(self):
		old_color = int(self.color[1])
		self.color = "C" + str(old_color + 1)
		

	def plot(self, symbol, diff_array, x_axis, color):
		if len(diff_array) == self.x_len:
			plt.plot(x_axis, diff_array, color=self.color, label=symbol)

	def show(self):
		plt.legend()
		plt.show()


# The toolkit itself which features methods to help with analyzing time frames around earnings calls
class IntraDayToolkit:
	def __init__(self, api_key):
		self.td_api = TDAmeritradeAPI(api_key)

	def __convertTimesMiliseconds(self, time, date_for_time):
		times_list = [] 
		# reset for the 20 hour end day
		date_for_time = date_for_time.replace(hour=0)
		for pull_time in time.split(","):
			if pull_time == "9:30":
				ret_time = date_for_time + timedelta(hours=9, minutes=30)
			else:
				ret_time = date_for_time + timedelta(hours=int(pull_time))
			ret_time = ret_time.timestamp() * 1000
			times_list.append(int(ret_time))

		return times_list
		
	# Takes in datetimes, times as strings, ticker, candlestick type
	# Returns: Candles for the beginning and ends of the times
	def retrieveSelectedTimes(self, dates, times, ticker, candlestick, req_data_length):
		# Only processesing for the year 2019 right now, because the only data I can seem to get from TDAmeritrade is 2019+
		if str(dates[0].year) != "2019":
			return False
		if dates[0].weekday() == "Friday":
			# Not sure if earnings announcements on Friday would be useful yet, so ignoring for now
			return False
		# Temporary code, because the only bars I'm planning to use for now are the 30m
		if candlestick == "30m":
			freq_type = "minute"
			freq_num = "30"
		# Convert to miliseconds for api call
		start_date = dates[0].timestamp() * 1000
		end_date = dates[len(dates)-1].timestamp() * 1000
		data_return = self.td_api.getPrices(ticker, freq_type, freq_num, str(int(end_date)), str(int(start_date))).content
		data_return = json.loads(data_return)
		candles = data_return["candles"]

		# no need for two seperate lists if using miliseconds, it incorporates days
		# So this method simply returns a list of milisconds
		milisecond_list = []
		for i in range(0, len(times)):
			milisecond_list += self.__convertTimesMiliseconds(times[i], dates[i])
		# h keeps track of which item in miliscond list you are trying to find
		# print(milisecond_list)
		h = 0
		close_list = []
		# print(candles)
		for candle in candles:
			# print("Looking for: %s" % milisecond_list[h])
			# print("Comparing %s and %s"%(candle["datetime"], milisecond_list[h]))
			if int(candle["datetime"]) == milisecond_list[h]:
				# print("found!")
				close_list.append(candle["close"])
				h += 1
				if h == len(milisecond_list):
					break

		if req_data_length != len(close_list):
			# Debug Messages
			print(close_list)
			print("Last looked for was %s" % milisecond_list[h])
			print(candles)
			raise Exception("Invalid Data length retrieved")

		return close_list

	# Instructions will be a list used to identify which indicies to compare
	# [157.3247, 155.79, 163.02, 163.0, 160.7784, 165.25] , ["1:2", "2:3", "4:5", "5:4"]
	def priceArrayToDifferenceArray(self, price_array, instructions):
		diff_array = []
		# print(price_array)
		# Start off with 0 change for a more readable line chart
		diff_array.append(0)
		for instruction in instructions:
			i_list = instruction.split(":")
			close1 = price_array[int(i_list[0])]
			close2 = price_array[int(i_list[1])] 
			diff = ((close2 - close1)/close1)*100
			diff_array.append(diff)

		return diff_array

# Strategy 1: Analyzing After market earnings calls.
# We look at intra market data that day, then the after hours, then the next day we look at premarket and intraday
# and we find a correlation among the data
def afterMarketCallDifferenceStrategy(earnings_map, ticker_list):
	tk = IntraDayToolkit(api_key)
	# 7 to adjust for TD Ameritrade api, earliest data available
	after_market_strat_times = ["9:30,16,18", "5,9:30,16"]
	# We can use a graph like this to look for a pattern of upward or downward slopes to buy in at the right times
	difference_instructions =  ["0:1", "1:2", "3:4", "4:5"]
	# We can use this graph for the simplest viewing experience, comparing vs. a given day
	# difference_instructions_s =  ["1:2", "1:3", "4:5", "5:4"]
	x_axis = ["9:30 AM", "9:30 AM - 4 PM", "4 PM - 7:00 PM", "4 AM - 9:30 AM", "9:30 AM - 4:00 PM"]
	lg = LineGraph(x_axis, "After market strategy")
	for ticker in ticker_list:
		print("Analyzing data for %s"%ticker)
		earnings_date_list = cp.earnings_map[ticker]
		lg.changeColor()
		for earningsdate in earnings_date_list:
			# print(earningsdate)
			dateandtime = earningsdate.split(":")

			# We only want to pay attention to stocks with after market close
			try:
				if(dateandtime[1] != "amc"):
					print("%s on %s did not announce after market on %s"%(ticker, dateandtime[0]))
					break
			except:
				# We have reached the end of the list most likely
				continue

			# Setup dates
			eastern = pytz.timezone('US/Eastern')
			start_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
			end_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
			end_date = start_date + timedelta(days=1, hours=20) # last day is not inclusive
			dates = [start_date, end_date]
			# Expected return [1.1,2.1,-1,2] in percentages
			close_list = tk.retrieveSelectedTimes(dates, after_market_strat_times, ticker, "30m", 6)
			if(close_list):
				diff_array = tk.priceArrayToDifferenceArray(close_list, difference_instructions)
				# print(close_list)
				lg.plot(ticker, diff_array, x_axis,'g')
		
	lg.show()



cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates")
cp.loadCached(False)
afterMarketCallDifferenceStrategy(cp.earnings_map, ["AMZN", "MSFT", "AAPL", "HP"])
