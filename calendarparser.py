# The goal of this file is to go through each of the days using the endpoint https://api.earningscalendar.net/
# and search for the earnings call dates of each of the symbols provided in a comma seperated file of symbol.
# The output of this will be text files in a given directory, one text file per symbol, each one containing various dates
import requests
import time
import json
import os
from datetime import timedelta, date
import datetime


class CalendarParser():
	def __init__(self, filename, output_dir):
		file = open(filename, "r")
		text_list = file.read()
		self.whitelist = text_list.split(",")
		self.dir = os.path.join(output_dir)


	# First time use
	def pullandStoreEarningsDates(self, append_new_data=True):
		if append_new_data:
			# set it to one day after
			start_date =  self.getStartingDate()
			print("Date last gathered for was: " + start_date.strftime("%Y%m%d"))
			end_date = datetime.datetime.now()
		self.getDates(start_date, end_date)
		preferred_dir = self.dir + "\\preferred"
		other_dir = self.dir + "\\other"
		api_url = "https://api.earningscalendar.net/?date="
		if len(self.dates) < 1:
			print("You have the latest earnings information!")
		else:
			print("Need to get the following dates:\n" + str(self.dates))
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


	# Returns 
	def getDates(self, start_date, end_date):
		self.dates = []
		from datetime import timedelta, date

		def daterange(start_date, end_date):
			for n in range(int ((end_date - start_date).days)):
				yield start_date + timedelta(n)

		for single_date in daterange(start_date, end_date):
			datestr = single_date.strftime("%Y%m%d")
			self.dates.append(datestr)


	# The purpose of this method is to find out what the last date that data was gathered for
	# and return the day after so that the program can start from there
	def getStartingDate(self):
		last_latest_date = 0
		preferred_dir = self.dir + "\\preferred"
		other_dir = self.dir + "\\other"
		preferred_path = "%s\\"%(preferred_dir)
		other_path = "%s\\"%(other_dir)
		preferred_files = os.listdir(preferred_path)
		other_files = os.listdir(other_path)
		# Search through both directories for the last date gathered for it
		for name in preferred_files:
			final_path = preferred_path + name
			f = open(final_path, 'r')
			data = f.read()
			datetimes = data.split(",")
			for dt in datetimes:
				datetime_split = dt.split(":")
				date = datetime_split[0]

				if len(date)>0 and int(date) > last_latest_date:
					last_latest_date = int(date)
		for name in other_files:
			final_path = other_path + name
			f = open(final_path, 'r')
			data = f.read()
			datetimes = data.split(",")
			for dt in datetimes:
				datetime_split = dt.split(":")
				date = datetime_split[0]

				if len(date)>0 and int(date) > last_latest_date:
					last_latest_date = int(date)
		
		return (datetime.datetime.strptime(str(last_latest_date), "%Y%m%d") + datetime.timedelta(days=1))
		# TODO parse through all the files and determine the latest date
