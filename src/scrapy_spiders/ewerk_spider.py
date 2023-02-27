import os
import scrapy
import datetime
import locale
from .event_items import EventItem

locale.setlocale(locale.LC_ALL, 'de_DE')
class EwerkSpider(scrapy.Spider):
    name = "ewerk"
    allowed_domains = ["e-werk.de"]
    start_urls = ["https://www.e-werk.de/programm/alle-termine/"]

    current_date = datetime.date.today()
    page_count = 0

    def __init__(self, name=None, **kwargs):
        # delete events.json if it exists
        if os.path.exists("events.json"):
            os.remove("events.json")
        super().__init__(name, **kwargs)

    def parse(self, response, days_to_scrape=7):
        # Extract all events on the page
        events = response.xpath('//div[contains(@class, "eventsWrap")]/div[contains(@class, "singleEventWrap")]')

        # Loop through all events
        for e in events:
            # Parse the event
            parsed_event = self.parse_event(e) 

            days_in_future = (parsed_event.datetime.date() - self.current_date).days
            if days_in_future > days_to_scrape:
                return
            
            yield parsed_event

        self.page_count += 1
        yield scrapy.Request(response.url + f"?loadmore=1&offset={12*self.page_count}", self.parse)
        
    def parse_event(self, event) -> EventItem:
        # Extract the event data
        event_locations = [loc.strip() for loc in event.xpath('.//span[contains(@class, "eventLocation")]/text()').getall()]
        event_title = event.xpath('.//div[contains(@class, "singleEventContent")]/a/@title').get()
        event_time = event.xpath('.//span[contains(@class, "eventTime")]/text()').get().strip().replace(' Uhr', '')
        event_url = "https://e-werk.de" + event.xpath('.//div[contains(@class, "singleEventContent")]/a/@href').get()

        # Convert the date string to a datetime.datetime object
        date_str = event.xpath('.//span[contains(@class, "eventDate")]/time/@datetime').get()
        event_datetime = datetime.datetime.strptime(f"{date_str}|{event_time}", '%a %d.%m.%y|%H:%M')
        
        parsed_event = EventItem(title=event_title, datetime=event_datetime, locations=event_locations, url=event_url)
    
        return parsed_event

    def run():
        from scrapy.crawler import CrawlerProcess

        process = CrawlerProcess({
            'FEED_FORMAT': 'json',
            'FEED_URI': 'events.json',
            'FEED_EXPORT_ENCODING': 'utf-8',
        })
        spider = EwerkSpider
        process.crawl(spider)
        process.start()


if __name__ == '__main__':
    EwerkSpider.run()
