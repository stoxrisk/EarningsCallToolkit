from yahoofinancials import YahooFinancials

# Return info as map
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

for ticker in tickers:
	data = EarningsData('5m', ticker, 4)
	print('')
