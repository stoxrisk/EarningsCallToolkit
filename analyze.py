import Strategy
import sys
def start():
    with open("white_list.txt", 'r') as f:
    	sp500 = f.read()
    sp500_list = sp500.split(",")

    # Different strategies initiated with a number
    if sys.argv[1] == '1':
        earnings_map = Strategy.AM_strategy1(pull_list=sp500_list)
    elif sys.argv[1] == '2':
        if len(sys.argv) > 2:
            pull_list = Strategy.AM_PM_Change_Average(pull_list=[sys.argv[2]], additional_pull=True)
        else:
            earnings_map = Strategy.AM_PM_Change_Average(pull_list=sp500_list)
        # earnings_map = Strategy.AM_PM_Change_Average(pull_list=["ADT"])

if __name__ == '__main__':
    # freeze_support()
    start()