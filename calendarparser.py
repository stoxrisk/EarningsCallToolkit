# The goal of this file is to go through each of the days using the endpoint https://api.earningscalendar.net/
# and search for the earnings call dates of each of the symbols provided in a comma seperated file of symbol.
# The output of this will be text files in a given directory, one text file per symbol, each one containing various dates
import requests
import time
import json
import os
from datetime import timedelta, date


class CalendarParser():
	def __init__(self, filename, output_dir):
		file = open(filename, "r")
		text_list = file.read()
		self.whitelist = text_list.split(",")
		self.dir = os.path.join(output_dir)

	# First time use
	def pullandStoreEarningsDates(self, start_date="20121101", end_date="20190815"):
		self.getDates(start_date, end_date)
		preferred_dir = self.dir + "\\preferred"
		other_dir = self.dir + "\\other"
		api_url = "https://api.earningscalendar.net/?date="
		for date in self.dates: 
			response = requests.request(method="GET", url = api_url + date)
			response_map = json.loads(response.content)
			for symbol_map in response_map:
				current_symbol = symbol_map["ticker"]
				if current_symbol in self.whitelist:
					final_path = "%s\\%s.txt"%(preferred_dir, current_symbol)
				else:
					final_path = "%s\\%s.txt"%(other_dir, current_symbol)
				if os.path.exists(final_path):
					append_write = 'a' # append if already exists
				else:
					append_write = 'w' # make a new file if not
				f = open(final_path, append_write)	
				f.write("%s:%s,"%(date, symbol_map["when"]))
				f.close()
			print("Data collected for: %s" % date)
			time.sleep(1)

	# Second and Sequential Time use
	def loadCached(self, not_preferred=False):
		self.earnings_map = {}
		preferred_dir = self.dir + "\\preferred"
		other_dir = self.dir + "\\other"
		file_list = os.listdir(preferred_dir)
		for ticker_file in file_list:
			with open(preferred_dir + "\\" + ticker_file, 'r') as file:
				earnings_dates = file.read()
			earnings_dates_list = earnings_dates.split(",")
			ticker = ticker_file.split(".")[0]
			self.earnings_map[ticker] = []
			for earnings_date in earnings_dates_list:
				self.earnings_map[ticker].append(earnings_date)

		if(not_preferred):
			file_list = os.listdir(other_dir)
			for ticker_file in file_list:
				with open(other_dir + "\\" + ticker_file, 'r') as file:
					earnings_dates = file.read()
				earnings_dates_list = earnings_dates.split(",")
				ticker = ticker_file.split(".")[0]
				self.earnings_map[ticker] = []
				for earnings_date in earnings_dates_list:
					self.earnings_map[ticker].append(earnings_date)

	def getDates(self, start_date, end_date):
		self.dates = []
		from datetime import timedelta, date

		def daterange(start_date, end_date):
			for n in range(int ((end_date - start_date).days)):
				yield start_date + timedelta(n)

		for single_date in daterange(start_date, end_date):
			datestr = single_date.strftime("%Y%m%d")
			self.dates.append(datestr)

# Commands to create all the data in /dates
# start_date = date(2018, 6, 13)
# end_date = date(2019, 8, 14)
# cp = CalendarParser("white_list.txt","C:\\\\Users\\Andrew\\Google Drive\\Dropbox\\stox\\EarningsCallToolkit\\dates", start_date, end_date)
# cp.createMap()