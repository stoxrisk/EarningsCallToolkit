import sys
import os 
from datetime import timedelta, date, datetime
from yahoofinancials import YahooFinancials

def start(arg = None):
    if arg:
        symbol = arg
    else:
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
        print(day_before_latest_str)
        print(latest_day_str)
        symbol_yahoo_finance_interactor = YahooFinancials(symbol)
        earnings_days_data = symbol_yahoo_finance_interactor.get_historical_price_data(day_before_latest_str, latest_day_str, 'daily')
        print(earnings_days_data)
        try:
            current_price = earnings_days_data[symbol]['prices'][0]['close']
        except:
            print('Was not able to pull price from Yahoo Finance for symbol %s' % symbol)

    try:
        symbol_file = os.getcwd() + "/earnings_call_difference_data/%s.csv"%symbol
        csv_file = open(symbol_file, "r")
    except:
        import Strategy
        pull_list = Strategy.AM_PM_Change_Average(pull_list=[symbol], additional_pull=True)
        symbol_file = os.getcwd() + "/earnings_call_difference_data/%s.csv"%symbol
        try:
            csv_file = open(symbol_file, "r")
        except:
            print("No data for earnings calls could be called for %s"%symbol)
            return None

    lines = csv_file.readlines()

    print(symbol)
    absolute_diff = float(lines[7].rstrip().split(',')[1][:-1])
    positive_diff = float(lines[8].rstrip().split(',')[1][:-1])
    negative_diff = float(lines[9].rstrip().split(',')[1][:-1])

    earnings_date_list = lines[0].rstrip().split(',')
    diff_list = lines[3].rstrip().split(',')

    fin_string = ""

    fin_string += "-----------------------------------------\n"
    for i in range(1, len(lines[0])):
        if diff_list[i] == "":
            break
        fin_string += "Earnings Date %s: %f%%\n"%(earnings_date_list[i], float(diff_list[i][:-1]))

    fin_string += "-----------------------------------------\n"
    fin_string += "Chance of Rising: %s\n"%lines[4].split(',')[1].rstrip()
    fin_string += "Chance of Falling: %s\n"%lines[5].split(',')[1].rstrip()

    fin_string += "-----------------------------------------\n"
    fin_string += "Absolute Difference Average: %f%%\n"% absolute_diff
    fin_string += "Positive Difference Average: %f%%\n"% positive_diff
    fin_string += "Negative Difference Average: %f%%\n"% negative_diff
    fin_string += "-----------------------------------------\n"

    fin_string += "Current Price: %f\n"%current_price
    lower_strike = (round((current_price - ((abs(negative_diff)/100)*current_price))*2))/2
    higher_strike = (round((current_price + ((positive_diff/100)*current_price))*2))/2
    fin_string += "Recommended Lower Strike: %f\n"%lower_strike
    fin_string += "Recommended Higher Strike: %f\n"%higher_strike
    fin_string += "-----------------------------------------\n"
    csv_file.close()

    print(fin_string)
    return fin_string


if __name__ == '__main__':
    # freeze_support()
    start()