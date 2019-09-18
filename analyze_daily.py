import Strategy

with open("white_list.txt", 'r') as f:
    sp500 = f.read()
sp500_list = sp500.split(",")

earnings_map = Strategy.AM_PM_Change_Average(pull_list=sp500_list)