from calendarparser import CalendarParser
import Strategy
import sys

def update_caches_with_latest():
    try:
        strategy_name = sys.argv[1]
    except:
        strategy_name = "AM_PM_Change_Average_strat"
        # print("enter a valid strategy name")
        # exit(0)

    cp = CalendarParser("white_list.txt", "dates")
    cp.pullandStoreEarningsDates(append_new_data=True)
    cp.loadCached()

    # strategy = Strategy(strategy_name, None, None, None, difference_instructions, "am")
    # strategy.pull_cache_data()
    # strategy.gather_data(self, cp.earnings_map, symbol_list, yahoo_daily=False, write=True, append_cache=True)


    # Open file with name, read into map
    # keys of map to array
    # Go by symbol in map, for each symbol open earnings dates location and see if all the dates are loaded in, if not pull it in and add to map
    # write map





if __name__ == '__main__':
    # freeze_support()
    update_caches_with_latest()