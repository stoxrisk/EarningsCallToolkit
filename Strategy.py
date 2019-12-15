from tdameritradeapi import TDAmeritradeAPI
from calendarparser import CalendarParser
from datetime import timedelta, date, datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests
import os
import json
from time import sleep
from yahoofinancials import YahooFinancials
import multiprocessing
import time

# td_api_key needs to be defined as an environment variable
api_key = os.getenv('td_api_key')

import logging
logging.basicConfig(filename='error_log.txt',level=logging.DEBUG)

# This class is used to seperate out the CSV logic and have this object perform CSV related tasks
class _csvRecorder:
    def __init__(self, filename, difference_strategy):
        self.difference_strategy = difference_strategy
        self.filename = filename


    def generateSmallCSVs(self, earnings_data_map, local_dir, select=[]):
        reserved_words = ["after_market_strat_times", "difference_instructions"]
        symbol_list = earnings_data_map if not select else select
        for symbol in symbol_list:
            if symbol not in reserved_words:
            # try:
                print("Generating Earnings Call info for: " + symbol)
                if earnings_data_map[symbol] == {}:
                    continue
                final_path =  local_dir + "\\%s" % symbol + ".csv"
                csv_str = "Earnings Dates: ,"
                earnings_before_temp = []
                earnings_after_temp = []
                difference_temp = []
                for date in earnings_data_map[symbol]:
                    if date == '' or earnings_data_map[symbol][date] == {}:
                        continue
                    csv_str += date + ","
                    earnings_before = earnings_data_map[symbol][date]["close_list"][0]
                    earnings_before_temp.append(earnings_before)
                    earnings_after = earnings_data_map[symbol][date]["close_list"][1]
                    earnings_after_temp.append(earnings_after)
                    difference_percentage = earnings_data_map[symbol][date]["diff_array"][1]
                    difference_temp.append(difference_percentage)
                if(len(earnings_before_temp) > 0):
                    csv_str += "\nBefore Earnings:,"
                    for before in earnings_before_temp:
                        csv_str += str(before) + ","
                    csv_str += "\nAfter Earnings:,"
                    for after in earnings_after_temp:
                        csv_str += str(after) + ","
                    csv_str += "\nDifference:,"
                    total_dif = 0
                    positive_count = 0
                    positive_average = 0
                    negative_count = 0
                    negative_average = 0
                    for diff in difference_temp:
                        if diff >= 0:
                            positive_count += 1
                            positive_average += diff
                        else:
                            negative_count += 1
                            negative_average -= diff
                        total_dif += abs(diff)
                        csv_str += str(diff) + "%,"

                    csv_str += "\nPositive Change Percentage:,%f%%"%(positive_count/len(difference_temp)*100)
                    csv_str += "\nNegative Change Percentage:,%f%%\n"%(negative_count/len(difference_temp)*100)
                    csv_str += "\nAbsolute Average Difference:,%f%%"%(total_dif/len(difference_temp))
                    try:
                        csv_str += "\nPositive Average Difference:,%f%%"%(positive_average/positive_count)
                    except:
                        print("No positive Earnings Calls")
                    try:
                        csv_str += "\nNegative Average Difference:,-%f%%"%(negative_average/negative_count)
                    except:
                        print("No negative Earnings Calls")
                    csv_file = open(final_path, "w") 
                    csv_file.write(csv_str)
                    csv_file.close()
            # except:
            #     print("No data for %s" % symbol)

    """
    This method generates a csv based on the earnings map data generated from the Strategy Class. The CSV
    contains information about percentage over time periods and buckets the data accordingly
    Accepts: earnings_data_map: a return from Strategy.pull_cache_data()
             titles: titles corresponding to the data inside of the earnings_data_map
    Returns: Nothing, but creates a CSV in your local directory 
    """
    def generateCSV(self, earnings_data_map, titles):
        csv_str = ""
        # Example Data format for csv_map:
        #"1":
        #{
        #    "1": {"continuation_probibility": 56, "avg": 3%, "diffs": []}
        #}
        csv_map = {}
        for i, stat_zone in enumerate(self.difference_strategy):
            ind = str(i)
            csv_map[ind] = {}
            diff_indicies = stat_zone.split("->")
            reserved_words = ["after_market_strat_times", "difference_instructions"]
            for symbol in earnings_data_map:
                if symbol not in reserved_words:
                    for earningsdate in earnings_data_map[symbol]:
                        # This is the index of the percentage being compared against
                        main_compare_diff_index = diff_indicies[0] 
                        # These are the percentage(s) used for comaprison
                        try:
                            symbol_diff_array = earnings_data_map[symbol]["diff_array"]
                        except:
                            logging.info("There is no data for symbol %s" % symbol)

                        # Getting the change precentage used for a base comaprison and having it turned into an index
                        csv_map_change_percent_index = self.__intToIndexString(symbol_diff_array[int(main_compare_diff_index)])

                        if csv_map_change_percent_index not in csv_map[ind]:
                            csv_map[ind][csv_map_change_percent_index] = {}
                            csv_map[ind][csv_map_change_percent_index]["diffs"] = []
                        for comparison_indicies in diff_indicies[1]:
                            csv_map[ind][csv_map_change_percent_index]["diffs"].append(symbol_diff_array[int(comparison_indicies)])
            
            # Time to analyze the results gathered
            for perc_change_bucket in csv_map[ind]:
                diffs = csv_map[ind][perc_change_bucket]["diffs"]
                total = 0
                same_direction_count = 0
                total_count = len(diffs)
                positive = True if float(perc_change_bucket) >= 0 else False
                for diff in diffs:
                    total += diff
                    if positive:
                        same_direction_count += 1 if diff > 0 else 0
                    # negative
                    else:
                        same_direction_count += 1 if diff < 0 else 0
                csv_map[ind][perc_change_bucket]["avg"] = total/total_count
                csv_map[ind][perc_change_bucket]["continuation_probibility"] = same_direction_count/total_count
                csv_map[ind][perc_change_bucket]["diffs"] = []

        # Sort the results
        sorted_csv_info = []
        for i in range(0,len(self.difference_strategy)):
            sorted_dict = sorted(csv_map[str(i)].items(), key=lambda x: int(x[0]))
            sorted_csv_info.append(sorted_dict)

        # Check just to be sure
        if len(titles) != len(self.difference_strategy):
            raise Exception("Invalid Length of Titles Array")

        # Top bar of the page
        legend = "Percentage Bucket,Chance of Rising or Declining Further,Average Rise/Decline\n"
        csv_str += legend
        # Form the main bulk of the document from the tuple
        for i, title in enumerate(titles):
            csv_str += title + "\n"
            ind = str(i)
            for k, percent in enumerate(sorted_csv_info[i]):
                csv_str += "%s%%,%s%%,%s%%\n" % (percent[0], str(float(sorted_csv_info[i][k][1]["continuation_probibility"])*100), sorted_csv_info[i][k][1]["avg"])

        # Write to the CSV
        csv_file = open(self.filename, "w") 
        csv_file.write(csv_str)
        csv_file.close()


    def __intToIndexString(self, num):
        return str(int(num))


# Class for creating a linegraph with many different lines, each line representing change over time periods
class _LineGraph:

    def __init__(self, x_axis, title):
        self.x_axis = x_axis
        self.title = title
        self.color = "C0"
        self.x_len = len(x_axis)

        mpl.style.use('seaborn')


    # Change the color for each new symbol
    def changeColor(self):
        old_color = int(self.color[1])
        self.color = "C" + str(old_color + 1)
        

    def plot(self, symbol, diff_array):
        if len(diff_array) == self.x_len:
            plt.plot(self.x_axis, diff_array, color=self.color, label=symbol)

    def show(self):
        plt.legend()
        plt.show()


# The toolkit itself which features methods to help with analyzing time frames around earnings calls
class IntraDayToolkit:

    def __init__(self, api_key):
        self.td_api = TDAmeritradeAPI(api_key)


    # Converts a list of dateimtes into miliseconds in int form used for api calls to TD Ameritrade
    def __convertTimesMiliseconds(self, time, date_for_time):
        times_list = [] 
        # reset for the 20 hour end day
        date_for_time = date_for_time.replace(hour=0)
        for pull_time in time.split(","):
            if pull_time == "9:30":
                ret_time = date_for_time + timedelta(hours=9, minutes=30)
            else:
                ret_time = date_for_time + timedelta(hours=int(pull_time))
            ret_time = ret_time.timestamp() * 1000
            times_list.append(int(ret_time))

        return times_list
        

    """
    Accepts: 
        dates: list of dates to be gathered for
        times: list of times to be gathered for
        symbol: symbol such as 'AAPL'
        candlestick: What kind of candlestick, such a '30m'
        req_data_length: 
    # Returns: A list of closing prices for a given symbol
    """
    def retrieveSelectedTimes(self, dates, times, symbol, candlestick, req_data_length):
        # Only processesing for the year 2019 right now, because the only data I can seem to get from TDAmeritrade is 2019+
        if str(dates[0].year) != "2019":
            return False
        if dates[0].weekday() == "Friday":
            # Not sure if earnings announcements on Friday would be useful yet, so ignoring for now
            return False
        # Temporary code, because the only bars I'm planning to use for now are the 30m
        if candlestick == "30m":
            freq_type = "minute"
            freq_num = "30"
        # Convert to miliseconds for api call
        start_date = dates[0].timestamp() * 1000
        end_date = dates[len(dates)-1].timestamp() * 1000
        data_return = self.td_api.getPrices(symbol, freq_type, freq_num, str(int(end_date)), str(int(start_date))).content
        data_return = json.loads(data_return)
        try:
            candles = data_return["candles"]
        except:
            logging.warning("No data available for %s this date" % symbol)
            sleep(3) # Wait 3 seconds, refreshing the connection
            return False

        # no need for two seperate lists if using miliseconds, it incorporates days
        # So this method simply returns a list of milisconds
        milisecond_list = []
        for i in range(0, len(times)):
            milisecond_list += self.__convertTimesMiliseconds(times[i], dates[i])
        # h keeps track of which item in miliscond list you are trying to find
        h = 0
        close_list = []
        for candle in candles:
            if int(candle["datetime"]) == milisecond_list[h]:
                close_list.append(candle["close"])
                h += 1
                if h == len(milisecond_list):
                    break

        if req_data_length != len(close_list):
            # Debug Messages
            logging.warning("Was unable to retrieve data for %s"%symbol)
            logging.debug(close_list)
            logging.debug("Last looked for was %s" % milisecond_list[h])
            logging.debug(candles)
            return False

        return close_list


    def retrieve_day_bars_yahoo(self, dates, symbol, req_data_length, arr, return_format=["close","close"]):
        symbol_yahoo_finance_interactor = YahooFinancials(symbol)
        print("Getting data for dates between: %s and %s" %(dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d')))
        earnings_days_data = symbol_yahoo_finance_interactor.get_historical_price_data(dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d'), 'daily')
        # earnings_days_data = json.loads(earnings_days_data)
        try:
            price1 = earnings_days_data[symbol]["prices"][0][return_format[0]]
            price2 = earnings_days_data[symbol]["prices"][1][return_format[1]]
            print("Success!")
            arr[0] = price1
            arr[1] = price2
        except:
            # Right now I can only see this coming up because of holidays
            print("Failure.")
            return False

    # Instructions will be a list used to identify which indicies to compare
    # [157.3247, 155.79, 163.02, 163.0, 160.7784, 165.25] , ["1:2", "2:3", "4:5", "5:4"]
    def priceArrayToDifferenceArray(self, price_array, instructions):
        diff_array = []
        # Start off with 0 change for a more readable line chart
        diff_array.append(0)
        for instruction in instructions:
            i_list = instruction.split(":")
            close1 = price_array[int(i_list[0])]
            close2 = price_array[int(i_list[1])] 
            diff = ((close2 - close1)/close1)*100
            diff_array.append(diff)

        return diff_array


    def diff_earnings_map_to_lg(self, earnings_map, x_axis, data_range=[-8,8]):
        lg = _LineGraph(x_axis, "After market strategy 1")
        reserved_words = ["after_market_strat_times", "difference_instructions"]
        for i, symbol in enumerate(earnings_map):
            if symbol not in reserved_words:
                for earningsdate in earnings_map[symbol]:
                    try:
                        outlier = False
                        curr_diff_array = earnings_map[symbol][earningsdate]["diff_array"]
                        for diff in curr_diff_array:
                            if int(diff) > data_range[1] or int(diff) < data_range[0]:
                                outlier = True
                                break
                        if not outlier:
                            lg.plot(symbol, curr_diff_array)    
                            
                    except:
                        logging.info("No data available for %s, not plotting" % symbol)
            lg.changeColor()
        return lg


    def remove_outlier_data(self):
        pass #TODO


class Strategy():

    def __init__(self, strategy_name, linegraph_x_axis, csv_strategy, market_strat_times, difference_instructions, time):
        self.am = True if time == "am" else False
        self.strategy_name = strategy_name    
        self.strategy_earnings_cache = {}
        self.x_axis = linegraph_x_axis
        self.csv_strat = csv_strategy
        self.after_market_strat_times = market_strat_times
        self.difference_instructions = difference_instructions
        self.tk = IntraDayToolkit(api_key)


    """
    Retrieve the data from TD Ameritrade based on the inputs of this strategy
    Accepts: earnings_map: map containing earnings calls dates
    symbol_list: list of symbols to gather the data for
    Returns: Nothing, but writes a json file to store the data
    """
    def gather_data(self, earnings_map, symbol_list, yahoo_daily=False, write=True, append_cache=False):
        self.strategy_earnings_cache["after_market_strat_times"] = self.after_market_strat_times
        self.strategy_earnings_cache["difference_instructions"] = self.difference_instructions
        eastern = pytz.timezone('US/Eastern')
        # Expected return size, Not handling for more than two days at the moment
        expected_size = 0
        if not yahoo_daily:
            for market_time in self.after_market_strat_times:
                expected_size += len(market_time.split(","))
        else:
            expected_size = 2

        if append_cache and symbol_list is None:
            symbol_list = list(self.strategy_earnings_cache.keys())
        
        for symbol in symbol_list:
            if symbol not in self.strategy_earnings_cache:
                self.strategy_earnings_cache[symbol] = {}
            print("Analyzing data for %s"%symbol)
            try:
                earnings_date_list = earnings_map[symbol]
            except:
                print("Don't have the earnings data for %s"%symbol)
                continue
            for earningsdate in earnings_date_list:
                
                dateandtime = earningsdate.split(":")
                if append_cache and dateandtime[0] in self.strategy_earnings_cache[symbol]:
                    #Don't repeat data when appending
                    continue
                else:
                    self.strategy_earnings_cache[symbol][dateandtime[0]] = {}

                if not yahoo_daily:
                    
                    if dateandtime[0] == '':
                        continue

                    # We only want to pay attention to stocks with after market close
                    # No other conditions exist for this right now
                    try:
                        if(dateandtime[1] != "amc" and self.am):
                            print("%s on %s did not announce after market on %s"%(symbol, dateandtime[0]))
                            break
                        if(dateandtime[1] == "amc" and not self.am):
                            print("%s on %s did not announce premarket market on %s"%(symbol, dateandtime[0]))
                            break

                    except:
                        # We have reached the end of the list most likely
                        continue

                    # Setup dates
                    start_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
                    end_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)

                    if self.am:
                        end_date = start_date + timedelta(days=1, hours=20) # last day is not inclusive
                    else: 
                        start_date = start_date - timedelta(hours=20)

                    dates = [start_date, end_date] 

                    # Expected return [1.1,2.1,-1,2] in percentages
                    close_list = self.tk.retrieveSelectedTimes(dates, self.after_market_strat_times, symbol, "30m", expected_size)

                    # If we were able to retrieve the data add it to the map
                    if(close_list):
                        diff_array = self.tk.priceArrayToDifferenceArray(close_list, self.difference_instructions)
                        # print(close_list)
                        self.strategy_earnings_cache[symbol]["diff_array"] = diff_array
                        self.strategy_earnings_cache[symbol]["close_list"] = close_list
                else:
                    # In case of a needed format change:
                    # yahoo_formatted_date = "%s-%s-%s"%(dateandtime[0][:4], dateandtime[0][4:6], dateandtime[0][6:8])
                    if dateandtime[0] == '': # The end of the file contains this, ignore
                        continue
                    start_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
                    end_date = datetime.strptime(dateandtime[0], '%Y%m%d').astimezone(eastern)
                    if dateandtime[1] == "amc":
                        end_date = end_date + timedelta(days=2)
                        if end_date.strftime('%A') == 'Saturday':
                            end_date = end_date + timedelta(days=3)
                    elif dateandtime[1] == "bmo":
                        start_date = start_date - timedelta(days=1)
                        end_date = end_date + timedelta(days=1)
                        if start_date.strftime('%A') == 'Sunday':
                            start_date = start_date - timedelta(days=2)
                    dates = [start_date, end_date]
                    arr = multiprocessing.Array('d', range(expected_size))
                    action_thread = multiprocessing.Process(target=self.tk.retrieve_day_bars_yahoo, args=(dates, symbol, expected_size,arr))
                    action_thread.start()
                    # close_list = self.tk.retrieve_day_bars_yahoo(dates, symbol, expected_size)
                    action_thread.join(timeout=2)

                    if action_thread.is_alive():
                        action_thread.kill()
                    close_list = arr[:]

                    # if p.is_alive():
                    #     p.terminate()
                        # p.join()

                # If we were able to retrieve the data add it to the map
                if(close_list and close_list[0] > 0):
                    diff_array = self.tk.priceArrayToDifferenceArray(close_list, self.difference_instructions)
                    self.strategy_earnings_cache[symbol][dateandtime[0]]["diff_array"] = diff_array
                    self.strategy_earnings_cache[symbol][dateandtime[0]]["close_list"] = close_list
                elif close_list is False:
                    continue 

        # Store the data for next time
        if write:
            self.write_earnings_cache(self.strategy_name + ".json", self.strategy_earnings_cache)
            print("Written Successfully")


    # Load up previously gathered data into a map, add new data if needed
    def pull_cache_data(self, earnings_map=None, pull_list=None):
        f = open(self.strategy_name + ".json", 'r')    
        contents = f.read()    
        f.close()
        current_strategy_earnings_cache =  json.loads(contents)
        if pull_list:
            if pull_list[0] not in current_strategy_earnings_cache:
                self.gather_data(earnings_map, pull_list, yahoo_daily=True, write=False)
            for symbol in pull_list:
                if symbol not in current_strategy_earnings_cache:
                    current_strategy_earnings_cache[symbol] = self.strategy_earnings_cache[symbol]
            self.write_earnings_cache(self.strategy_name + ".json", current_strategy_earnings_cache)

        self.strategy_earnings_cache = current_strategy_earnings_cache
        return current_strategy_earnings_cache


    # Write the gathered data into a json format file for quick use again
    def write_earnings_cache(self, filename, earnings_cache):
        f = open(filename, 'w')    
        f.write(json.dumps(earnings_cache))
        f.close()


    def write_earnings_cache_by_symbol(self, yahoo_data=True):
        pass


    # Generate a line graph for this strategy
    def generate_line_graph(self, data_range=[8,8]):
        return self.tk.diff_earnings_map_to_lg(self.strategy_earnings_cache, self.x_axis, data_range)


    # Generate a CSV file for this strategy
    def generate_csv_file(self, titles):
        csv = _csvRecorder(self.strategy_name + ".csv", self.csv_strat)
        csv.generateCSV(self.strategy_earnings_cache, titles)


    def generate_daily_csv_library(self, earnings_data_map, folder_name, local_dir, select=[]):
        csv = _csvRecorder(folder_name, None)
        csv.generateSmallCSVs(earnings_data_map, local_dir + "\\%s"%folder_name, select)



    def redefine_diff_arrays(self, symbol_list, new_difference_instructions):
        for symbol in symbol_list:
            try:
                new_diff_array = self.tk.priceArrayToDifferenceArray(self.strategy_earnings_cache[symbol]["close_list"], new_difference_instructions)
                self.strategy_earnings_cache[symbol]["diff_array"] = new_diff_array
            except:
                logging.info("No data for redefining difference array for symbol %s")



"""
After Market Strategy 1:
Goal: Analyze the correlation in price change among the following timeframes surrounding an earnings date:
Intra-Day vs. Post Market (earnings call), Post Market vs. Next day premarket, Post Market vs. Next Day intraday
"""
def AM_strategy1(pull_list=None):
    strategy_name = "after_market_strat1"
    titles = ["Comparing Intra Day to After Market", 
              "Comparing After Market to Pre Market Next Day",
              "Comparing After Market to IntraDay Next Day"]
    x_axis = ["9:30 AM", "9:30 AM - 4 PM", "4 PM - 6:00 PM", "7 AM - 9:30 AM", "9:30 AM - 4:00 PM"]
    csv_strat = ["1->2","2->3","2->4"]
    difference_instructions =  ["0:1", "0:2", "0:4", "0:5"]
    after_market_strat_times = ["9:30,16,18", "7,9:30,16"]
    am_strat_1 = Strategy(strategy_name, x_axis, csv_strat, after_market_strat_times, difference_instructions, "am")

    if pull_list and not os.path.exists(strategy_name+".json"):
        cp = CalendarParser("white_list.txt", os.getcwd() + "\\dates")
        cp.loadCached(False)
        am_strat_1.gather_data(cp.earnings_map, pull_list)

    earnings_return_data_map = am_strat_1.pull_cache_data()

    lg = am_strat_1.generate_line_graph(data_range=[-17,17])
    lg.show()

    # Now to perform this again we need a different set of difference instructions, we can use the toolkit for this
    # Before we essentially had a relative line of change since the beginning of the earnings call day
    # Now we are doing active comparisons between the time frame rise/fall percentages
    new_difference_instructions = ["0:1", "1:2", "3:4", "4:5"]
    if pull_list:
        am_strat_1.redefine_diff_arrays(pull_list, new_difference_instructions)
        csv = am_strat_1.generate_csv_file(titles)


"""
Change Average:
Goal: The purpose of this strategy is to analyze the average difference of price before and after earnings calls
"""
def AM_PM_Change_Average(pull_list=None, additional_pull=False):
    strategy_name = "AM_PM_Change_Average_strat"
    difference_instructions =  ["0:1"]
    AM_PM_Change_Average_strat = Strategy(strategy_name, None, None, None, difference_instructions, "am")
    local_dir = os.getcwd()
    cp = CalendarParser("white_list.txt", local_dir + "\\dates")
    cp.loadCached(True)
    if pull_list and not os.path.exists(strategy_name + ".json"):    
        AM_PM_Change_Average_strat.gather_data(cp.earnings_map, pull_list, yahoo_daily=True)

    if pull_list and additional_pull:
        earnings_return_data_map = AM_PM_Change_Average_strat.pull_cache_data(earnings_map=cp.earnings_map, pull_list=pull_list)
        AM_PM_Change_Average_strat.generate_daily_csv_library(earnings_return_data_map, "earnings_call_difference_data", local_dir, select=pull_list)
    else:
        earnings_return_data_map = AM_PM_Change_Average_strat.pull_cache_data()
        AM_PM_Change_Average_strat.generate_daily_csv_library(earnings_return_data_map, "earnings_call_difference_data", local_dir)
    

