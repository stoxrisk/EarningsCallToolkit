from gather_latest_earnings_data import update_caches_with_latest 
import estimate_strikes
from datetime import datetime
import requests
import json
import os
import subprocess

def start():
    # todaysdate = "20191211"
    todaysdate = datetime.now()
    # todaysdate = todaysdate.replace(day=4)
    todays_string = todaysdate.strftime("%Y%m%d")
    # First update the data 

    # Only update on the weekday
    if todaysdate.weekday() < 5:
        update_caches_with_latest()

    # Get Earnings data for the day

    calendar_api = "https://api.earningscalendar.net/?date=" + todays_string
    response = requests.request(method="GET", url = calendar_api)
    response_map = json.loads(response.content)
    # Will hold the information that will get displayed
    display_map = {}
    for symbol_earnings in response_map:
        symbol = symbol_earnings["ticker"]
        formatted_statistics = estimate_strikes.start(symbol)
        if formatted_statistics:
            display_map[symbol] = formatted_statistics
            print(formatted_statistics)

    html_string = '<html>\n<link rel="stylesheet" href="styles.css">\n'
    for symbol in display_map:
        html_stats = display_map[symbol].replace("\n", "<br>")
        html_string += '<h1>%s</h1>'%symbol 
        html_string += html_stats
    html_string += "</html>"

    f = open("docs/index.html", "w")
    f.write(html_string)
    f.close()

if __name__ == '__main__':
    # freeze_support()
    start()