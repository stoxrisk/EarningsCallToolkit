import Strategy

with open("white_list.txt", 'r') as f:
	sp500 = f.read()
sp500_list = sp500.split(",")

earnings_map = Strategy.AM_strategy1(pull_list=sp500_list)