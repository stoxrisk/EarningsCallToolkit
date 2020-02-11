from gather_latest_earnings_data import update_caches_with_latest 
import estimate_strikes
from calendarparser import CalendarParser
from datetime import datetime
import requests
import json
import os
import subprocess
from twilio.rest import Client


def start():
    print("Now starting the Daily Run")
    todaysdate = datetime.now()
    todays_string = todaysdate.strftime("%Y%m%d")
    # They removed the free link, so I no longer have access to the latest earnings data, program is depreciated
    calendar_api = "https://freeapi.earningscalendar.net/?date="
    # Manual Date testing \/
    # todaysdate = todaysdate.replace(day=11)
    
    weekday_num = todaysdate.weekday()
    if weekday_num > 4:
        print("Not running, this is the weekend")
        return
    # Not Friday or Weekend
    elif weekday_num < 4:
        print("Getting earnings for the week")
        cp = CalendarParser("white_list.txt", "dates")
        weekly_map = cp.getWeeklySchedule()
   
    
    # First update the data 

    text_message_content = "Goodmorning! the earnings reported today, %s, day are:\n"%todaysdate.strftime("%m-%d-%Y")

    # Only update on the weekday
    if todaysdate.weekday() < 5:
        print("Now updating with the latest earnings calls dates")
        update_caches_with_latest()

    # Get Earnings data for the day

    print("Pinging the Earnings call API")
    todays_calendar_ping = calendar_api + todays_string
    response = requests.request(method="GET", url = todays_calendar_ping)
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
    for day,symboltimes in weekly_map.items():
        html_string += "<h2>%s</h2>"%day
        html_string += "-----------------------------------------<br>"
        for symboltime in symboltimes:
            html_string += "%s<br>"%symboltime


    for symbol in display_map:
        html_stats = display_map[symbol].replace("\n", "<br>")
        html_string += '<h1>%s</h1>'%symbol 
        html_string += html_stats
        text_message_content += "%s\n"%symbol
    html_string += "</html>"

    f = open("docs/index.html", "w")
    f.write(html_string)
    f.close()

    account_sid = os.getenv('twilio_sid')
    auth_token = os.getenv('twilio_token')
    
    client = Client(account_sid, auth_token)

    text_message_content += "View here: https://stoxrisk.github.io/EarningsCallToolkit/"

    message = client.messages \
                    .create(
                         body=text_message_content,
                         from_='+12015716291',
                         to=os.getenv('phone_number')
                     )

    print(message.sid)

if __name__ == '__main__':
    # freeze_support()
    start()