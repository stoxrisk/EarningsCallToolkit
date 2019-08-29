from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date, datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests
import os
import json
from time import sleep

# td_api_key needs to be defined as an environment variable
api_key = os.getenv('td_api_key')

import logging
logging.basicConfig(filename='error_log.txt',level=logging.DEBUG)

# This class is used to seperate out the CSV logic and have this object perform CSV related tasks
class _csvRecorder:
	def __init__(self, filename, difference_strategy):
		self.difference_strategy = difference_strategy
		self.filename = filename

	"""
	This method generates a csv based on the earnings map data generated from the Strategy Class. The CSV
	contains information about percentage over time periods and buckets the data accordingly
	Accepts: earnings_data_map: a return from Strategy.pull_cache_data()
			 titles: titles corresponding to the data inside of the earnings_data_map
	Returns: Nothing, but creates a CSV in your local directory 
	"""
	def generateCSV(self, earnings_data_map, titles):
		csv_str = ""
		# Example Data format for csv_map:
		#"1":
		#{
		#	"1": {"continuation_probibility": 56, "avg": 3%, "diffs": []}
		#}
		csv_map = {}
		for i, stat_zone in enumerate(self.difference_strategy):
			ind = str(i)
			csv_map[ind] = {}
			diff_indicies = stat_zone.split("->")
			reserved_words = ["after_market_strat_times", "difference_instructions"]
			for symbol in earnings_data_map:
				if symbol not in reserved_words:
					# This is the index of the percentage being compared against
					main_compare_diff_index = diff_indicies[0] 
					# These are the percentage(s) used for comaprison
					try:
						symbol_diff_array = earnings_data_map[symbol]["diff_array"]
					except:
						logging.info("There is no data for symbol %s" % symbol)

					# Getting the change precentage used for a base comaprison and having it turned into an index
					csv_map_change_percent_index = self.__intToIndexString(symbol_diff_array[int(main_compare_diff_index)])

					if csv_map_change_percent_index not in csv_map[ind]:
						csv_map[ind][csv_map_change_percent_index] = {}
						csv_map[ind][csv_map_change_percent_index]["diffs"] = []
					for comparison_indicies in diff_indicies[1]:
						csv_map[ind][csv_map_change_percent_index]["diffs"].append(symbol_diff_array[int(comparison_indicies)])
			
			# Time to analyze the results gathered
			for perc_change_bucket in csv_map[ind]:
				diffs = csv_map[ind][perc_change_bucket]["diffs"]
				total = 0
				same_direction_count = 0
				total_count = len(diffs)
				positive = True if float(perc_change_bucket) >= 0 else False
				for diff in diffs:
					total += diff
					if positive:
						same_direction_count += 1 if diff > 0 else 0
					# negative
					else:
						same_direction_count += 1 if diff < 0 else 0
				csv_map[ind][perc_change_bucket]["avg"] = total/total_count
				csv_map[ind][perc_change_bucket]["continuation_probibility"] = same_direction_count/total_count
				csv_map[ind][perc_change_bucket]["diffs"] = []

		# Sort the results
		sorted_csv_info = []
		for i in range(0,len(self.difference_strategy)):
			sorted_dict = sorted(csv_map[str(i)].items(), key=lambda x: int(x[0]))
			sorted_csv_info.append(sorted_dict)

		# Check just to be sure
		if len(titles) != len(self.difference_strategy):
			raise Exception("Invalid Length of Titles Array")

		# Top bar of the page
		legend = "Percentage Bucket,Chance of Rising or Declining Further,Average Rise/Decline\n"
		csv_str += legend
		# Form the main bulk of the document from the tuple
		for i, title in enumerate(titles):
			csv_str += title + "\n"
			ind = str(i)
			for k, percent in enumerate(sorted_csv_info[i]):
				csv_str += "%s%%,%s%%,%s%%\n" % (percent[0], str(float(sorted_csv_info[i][k][1]["continuation_probibility"])*100), sorted_csv_info[i][k][1]["avg"])

		# Write to the CSV
		csv_file = open(self.filename, "w") 
		csv_file.write(csv_str)
		csv_file.close()


	def __intToIndexString(self, num):
		return str(int(num))


# Class for creating a linegraph with many different lines, each line representing change over time periods
class _LineGraph:

	def __init__(self, x_axis, title):
		self.x_axis = x_axis
		self.title = title
		self.color = "C0"
		self.x_len = len(x_axis)

		mpl.style.use('seaborn')


	# Change the color for each new symbol
	def changeColor(self):
		old_color = int(self.color[1])
		self.color = "C" + str(old_color + 1)
		

	def plot(self, symbol, diff_array):
		if len(diff_array) == self.x_len:
			plt.plot(self.x_axis, diff_array, color=self.color, label=symbol)

	def show(self):
		plt.legend()
		plt.show()


# The toolkit itself which features methods to help with analyzing time frames around earnings calls
class IntraDayToolkit:

	def __init__(self, api_key):
		self.td_api = TDAmeritradeAPI(api_key)


	# Converts a list of dateimtes into miliseconds in int form used for api calls to TD Ameritrade
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
		

	"""
	Accepts: 
		dates: list of dates to be gathered for
		times: list of times to be gathered for
		symbol: symbol such as 'AAPL'
		candlestick: What kind of candlestick, such a '30m'
		req_data_length: 
	# Returns: A list of closing prices for a given symbol
	"""
	def retrieveSelectedTimes(self, dates, times, symbol, candlestick, req_data_length):
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
		data_return = self.td_api.getPrices(symbol, freq_type, freq_num, str(int(end_date)), str(int(start_date))).content
		data_return = json.loads(data_return)
		try:
			candles = data_return["candles"]
		except:
			logging.warning("No data available for %s this date" % symbol)
			sleep(3) # Wait 3 seconds, refreshing the connection
			return False

		# no need for two seperate lists if using miliseconds, it incorporates days
		# So this method simply returns a list of milisconds
		milisecond_list = []
		for i in range(0, len(times)):
			milisecond_list += self.__convertTimesMiliseconds(times[i], dates[i])
		# h keeps track of which item in miliscond list you are trying to find
		h = 0
		close_list = []
		for candle in candles:
			if int(candle["datetime"]) == milisecond_list[h]:
				close_list.append(candle["close"])
				h += 1
				if h == len(milisecond_list):
					break

		if req_data_length != len(close_list):
			# Debug Messages
			logging.warning("Was unable to retrieve data for %s"%symbol)
			logging.debug(close_list)
			logging.debug("Last looked for was %s" % milisecond_list[h])
			logging.debug(candles)
			return False

		return close_list


	# Instructions will be a list used to identify which indicies to compare
	# [157.3247, 155.79, 163.02, 163.0, 160.7784, 165.25] , ["1:2", "2:3", "4:5", "5:4"]
	def priceArrayToDifferenceArray(self, price_array, instructions):
		diff_array = []
		# Start off with 0 change for a more readable line chart
		diff_array.append(0)
		for instruction in instructions:
			i_list = instruction.split(":")
			close1 = price_array[int(i_list[0])]
			close2 = price_array[int(i_list[1])] 
			diff = ((close2 - close1)/close1)*100
			diff_array.append(diff)

		return diff_array


	def diff_earnings_map_to_lg(self, earnings_map, x_axis, data_range=[-8,8]):
		lg = _LineGraph(x_axis, "After market strategy 1")
		reserved_words = ["after_market_strat_times", "difference_instructions"]
		for i, symbol in enumerate(earnings_map):
			if symbol not in reserved_words:
				try:
					outlier = False
					curr_diff_array = earnings_map[symbol]["diff_array"]
					for diff in curr_diff_array:
						if int(diff) > data_range[1] or int(diff) < data_range[0]:
							outlier = True
							break
					if not outlier:
						lg.plot(symbol, curr_diff_array)	
						lg.changeColor()
				except:
					logging.info("No data available for %s, not plotting" % symbol)
		return lg


	def remove_outlier_data(self):
		pass #TODO


class Strategy():

	def __init__(self, strategy_name, linegraph_x_axis, csv_strategy, market_strat_times, difference_instructions, time):
		self.am = True if time == "am" else False
		self.strategy_name = strategy_name	
		self.strategy_earnings_cache = {}
		self.x_axis = linegraph_x_axis
		self.csv_strat = csv_strategy
		self.market_strat_times = market_strat_times
		self.difference_instructions = difference_instructions
		self.tk = IntraDayToolkit(api_key)


	"""
	Retrieve the data from TD Ameritrade based on the inputs of this strategy
	Accepts: earnings_map: map containing earnings calls dates
	symbol_list: list of symbols to gather the data for
	Returns: Nothing, but writes a json file to store the data
	"""
	def gather_data(self, earnings_map, symbol_list):
		self.strategy_earnings_cache["after_market_strat_times"] = self.market_strat_times
		self.strategy_earnings_cache["difference_instructions"] = self.difference_instructions

		# Expected return size, Not handling for more than two days at the moment
		expected_size = 0
		for market_time in self.market_strat_times:
			expected_size += len(market_time.split(","))
		
		for symbol in symbol_list:
			self.strategy_earnings_cache[symbol] = {}
			print("Analyzing data for %s"%symbol)
			try:
				earnings_date_list = earnings_map[symbol]
			except:
				print("Don't have the earnings data for %s"%symbol)
			for earningsdate in earnings_date_list:

				dateandtime = earningsdate.split(":")
				# We only want to pay attention to stocks with after market close
				try:
					if(dateandtime[1] != "amc" and self.am):
						print("%s on %s did not announce after market on %s"%(symbol, dateandtime[0]))
						break
					if(dateandtime[1] == "amc" and not self.am):
						print("%s on %s did not announce premarket market on %s"%(symbol, dateandtime[0]))
						break

				except:
					# We have reached the end of the list most likely
					continue

				# Setup dates
				eastern = pytz.timezone('US/Eastern')
				start_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
				end_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)

				if self.am:
					end_date = start_date + timedelta(days=1, hours=20) # last day is not inclusive
				else: 
					start_date = start_date - timedelta(hours=20)

				dates = [start_date, end_date] 

				# Expected return [1.1,2.1,-1,2] in percentages
				close_list = self.tk.retrieveSelectedTimes(dates, self.market_strat_times, symbol, "30m", expected_size)

				# If we were able to retrieve the data add it to the map
				if(close_list):
					diff_array = self.tk.priceArrayToDifferenceArray(close_list, self.difference_instructions)
					# print(close_list)
					self.strategy_earnings_cache[symbol]["diff_array"] = diff_array
					self.strategy_earnings_cache[symbol]["close_list"] = close_list

		# Store the data for next time
		self.write_earnings_cache(self.strategy_name + ".json", self.strategy_earnings_cache)


	# Load up previously gathered data into a map
	def pull_cache_data(self):
		f = open(self.strategy_name + ".json", 'r')	
		contents = f.read()
		f.close()
		self.strategy_earnings_cache =  json.loads(contents)
		return self.strategy_earnings_cache


	# Write the gathered data into a json format file for quick use again
	def write_earnings_cache(self, filename, earnings_cache):
		f = open(filename, 'w')	
		f.write(json.dumps(earnings_cache))
		f.close()


	# Generate a line graph for this strategy
	def generate_line_graph(self, data_range=[8,8]):
		return self.tk.diff_earnings_map_to_lg(self.strategy_earnings_cache, self.x_axis, data_range)


	# Generate a CSV file for this strategy
	def generate_csv_file(self, titles):
		titles = ["Comparing Intra Day to After Market", 
				  "Comparing After Market to Pre Market Next Day",
				  "Comparing After Market to IntraDay Next Day"]
		csv = _csvRecorder(self.strategy_name + ".csv", self.csv_strat)
		csv.generateCSV(self.strategy_earnings_cache, titles)


	def redefine_diff_arrays(self, symbol_list, new_difference_instructions):
		for symbol in symbol_list:
			try:
				new_diff_array = self.tk.priceArrayToDifferenceArray(self.strategy_earnings_cache[symbol]["close_list"], new_difference_instructions)
				self.strategy_earnings_cache[symbol]["diff_array"] = new_diff_array
			except:
				logging.info("No data for redefining difference array for symbol %s")



"""
After Market Strategy 1:
Goal: Analyze the correlation in price change among the following timeframes surrounding an earnings date:
Intra-Day vs. Post Market (earnings call), Post Market vs. Next day premarket, Post Market vs. Next Day intraday
"""
def AM_strategy1(pull_list=None):
	strategy_name = "after_market_strat1"
	titles = ["Comparing Intra Day to After Market", 
			  "Comparing After Market to Pre Market Next Day",
			  "Comparing After Market to IntraDay Next Day"]
	x_axis = ["9:30 AM", "9:30 AM - 4 PM", "4 PM - 6:00 PM", "7 AM - 9:30 AM", "9:30 AM - 4:00 PM"]
	csv_strat = ["1->2","2->3","2->4"]
	difference_instructions =  ["0:1", "0:2", "0:4", "0:5"]
	after_market_strat_times = ["9:30,16,18", "7,9:30,16"]
	am_strat_1 = Strategy(strategy_name, x_axis, csv_strat, after_market_strat_times, difference_instructions, "am")

	if pull_list and not os.path.exists(strategy_name+".json"):
		cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates")
		cp.loadCached(False)
		am_strat_1.gather_data(cp.earnings_map, pull_list)

	earnings_return_data_map = am_strat_1.pull_cache_data()

	lg = am_strat_1.generate_line_graph(data_range=[-17,17])
	lg.show()

	# Now to perform this again we need a different set of difference instructions, we can use the toolkit for this
	# Before we essentially had a relative line of change since the beginning of the earnings call day
	# Now we are doing active comparisons between the time frame rise/fall percentages
	new_difference_instructions = ["0:1", "1:2", "3:4", "4:5"]
	if pull_list:
		am_strat_1.redefine_diff_arrays(pull_list, new_difference_instructions)
		csv = am_strat_1.generate_csv_file(titles)