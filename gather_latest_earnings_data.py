from calendarparser import CalendarParser
from datetime import datetime
import Strategy
import sys
import os

difference_instructions_by_strategy = {
    "AM_PM_Change_Average_strat": ["0:1"]
}

def update_caches_with_latest():
    try:
        strategy_name = sys.argv[1]
    except:
        strategy_name = "AM_PM_Change_Average_strat"
        # print("enter a valid strategy name")
        # exit(0)

    local_dir = os.getcwd()

    cp = CalendarParser("white_list.txt", "dates")
    cp.pullandStoreEarningsDates(append_new_data=True)
    cp.loadCached()

    strategy = Strategy.Strategy(strategy_name, None, None, None, difference_instructions_by_strategy[strategy_name], "am")
    strategy.pull_cache_data()
    strategy.gather_data(cp.earnings_map, None, yahoo_daily=True, write=True, append_cache=True)
    earnings_return_data_map = strategy.pull_cache_data()

    if strategy_name == "AM_PM_Change_Average_strat":
        strategy.generate_daily_csv_library(earnings_return_data_map, "earnings_call_difference_data", local_dir)


    # Open file with name, read into map
    # keys of map to array
    # Go by symbol in map, for each symbol open earnings dates location and see if all the dates are loaded in, if not pull it in and add to map
    # write map





if __name__ == '__main__':
    # freeze_support()
    update_caches_with_latest()
