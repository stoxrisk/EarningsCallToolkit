import sys
import os 
from datetime import timedelta, date, datetime
from yahoofinancials import YahooFinancials

def start():
    symbol = sys.argv[1]
    try:
        current_price = float(sys.argv[2])
    except:
        # Code for gathering the latest day
        latest_day = date.today() - timedelta(days=1)
        if latest_day.strftime('%A') == 'Saturday':
            latest_day = latest_day - timedelta(days=3)
        elif latest_day.strftime('%A') == 'Sunday':
            latest_day = latest_day - timedelta(days=3)
        latest_day_str = latest_day.strftime('%Y-%m-%d') 
        day_before_latest = latest_day - timedelta(days=1)
        if day_before_latest.strftime('%A') == "Sunday":
            day_before_latest = day_before_latest - timedelta(days=2)
        day_before_latest_str = day_before_latest.strftime('%Y-%m-%d')
        symbol_yahoo_finance_interactor = YahooFinancials(symbol)
        earnings_days_data = symbol_yahoo_finance_interactor.get_historical_price_data(day_before_latest_str, latest_day_str, 'daily')
        current_price = earnings_days_data[symbol]['prices'][0]['close']

    try:
        symbol_file = os.getcwd() + "\\earnings_call_difference_data\\%s.csv"%symbol
        csv_file = open(symbol_file, "r")
    except:
        import Strategy
        pull_list = Strategy.AM_PM_Change_Average(pull_list=[sys.argv[1]], additional_pull=True)
        symbol_file = os.getcwd() + "\\earnings_call_difference_data\\%s.csv"%symbol
        csv_file = open(symbol_file, "r")

    lines = csv_file.readlines()


    absolute_diff = float(lines[7].rstrip().split(',')[1][:-1])
    positive_diff = float(lines[8].rstrip().split(',')[1][:-1])
    negative_diff = float(lines[9].rstrip().split(',')[1][:-1])

    earnings_date_list = lines[0].rstrip().split(',')
    diff_list = lines[3].rstrip().split(',')

    print("-----------------------------------------")
    for i in range(1, len(lines[0])):
        if diff_list[i] == "":
            break
        print("Earnings Date %s: %f%%"%(earnings_date_list[i], float(diff_list[i][:-1])))

    print("-----------------------------------------")
    print("Chance of Rising: %s"%lines[4].split(',')[1].rstrip())
    print("Chance of Falling: %s"%lines[5].split(',')[1].rstrip())

    print("-----------------------------------------")
    print("Absolute Difference Average: %f%%"% absolute_diff)
    print("Positive Difference Average: %f%%"% positive_diff)
    print("Negative Difference Average: %f%%"% negative_diff)
    print("-----------------------------------------")

    print("Current Price: %f"%current_price)
    lower_strike = (round((current_price - ((abs(negative_diff)/100)*current_price))*2))/2
    higher_strike = (round((current_price + ((positive_diff/100)*current_price))*2))/2
    print("Recommended Lower Strike: %f"%lower_strike)
    print("Recommended Higher Strike: %f"%higher_strike)
    print("-----------------------------------------")
    csv_file.close()


if __name__ == '__main__':
    # freeze_support()
    start()