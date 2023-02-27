import json

from scrapy_spiders.ewerk_spider import EwerkSpider
from g_calendar.google_calendar import GoogleCalendar as calendar

# scrap e-werk events
EwerkSpider.run()

# parse events from events.json with json
with open('events.json', 'r') as f:
    events = json.load(f)

cal = calendar()
for event in events:
    cal.add_event(event)