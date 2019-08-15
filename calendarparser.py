# The goal of this file is to go through each of the days using the endpoint https://api.earningscalendar.net/
# and search for the earnings call dates of each of the symbols provided in a comma seperated file of symbol.
# The output of this will be text files in a given directory, one text file per symbol, each one containing various dates
import requests
import time

class CalendarParser():
	def __init__(self, filename, output_dir, start_date, end_date):
		file = open("testfile.txt", "r")
 		text_list = file.read()
 		self.symbols = text_list.split(",")
 		self.dir = output_dir
 		getDates(start_date, end_date)

 	def createMap(self):
 		
 		# time.sleep(1)
 		# self.
 	def writeMap(self):

 	def getDates(start_date, end_date):
 		self.dates = []
 		from datetime import timedelta, date

		def daterange(start_date, end_date):
		    for n in range(int ((end_date - start_date).days)):
		        yield start_date + timedelta(n)

		for single_date in daterange(start_date, end_date):
		    datestr = single_date.strftime("%Y%m%d")
		    print(datestr)
		    self.dates.append(datestr)