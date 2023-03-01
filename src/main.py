import datetime
import json
import inquirer

from scrapy_spiders.ewerk_spider import EwerkSpider
from scrapy_spiders.event_items import EventItem
from g_calendar.google_calendar import GoogleCalendar


# scrap e-werk events
#EwerkSpider.run()

# parse events from events.json with json
with open('events.json', 'r') as f:
    json_data = json.load(f)
    events = [EventItem(**event) for event in json_data]

# prompt the user to confirm adding events to the calendar
if inquirer.confirm(f"Found {len(events)} events from E-Werk do you want to add them to your Google Calendar?", default=True) == False:
    print("Exiting...")
    exit()


cal = GoogleCalendar()
# get all calendars
calendar_list = cal.get_calendar_list()
choices = [calendar['summary'] for calendar in calendar_list]
choices.append(None)

# prompt the user to select a calendar
selected_calendar_name = inquirer.prompt([
    inquirer.List('calendar',
        message="In which calendar do you want to add events from E-Werk?",
        choices=choices,
)])['calendar']

if selected_calendar_name == None:
    print("No calendar selected. Exiting...")
    exit()

# get calendar id with name supplied by user
selected_calendar_id = [calendar for calendar in calendar_list if calendar['summary'] == selected_calendar_name][0]['id']

# create event bodys and add them to the calendar
for event in events:
    body = {
        'summary': f"[E-Werk] {event.title}",
        'location': f"E-Werk Kulturzentrum Erlangen: {'/'.join(event.locations)}",
        'description': f"{event.url}",
        "start": {
            "dateTime": event.datetime,
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": (datetime.datetime.fromisoformat(event.datetime) + datetime.timedelta(hours=2)).isoformat(),
            "timeZone": "Europe/Berlin",
        },
        "source": {
            "title": "E-Werk Kulturzentrum Erlangen",
            "url": event.url,
        },
        "transparency": "transparent",
    }

    cal.create_event(selected_calendar_id, body)
