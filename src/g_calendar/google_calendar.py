from __future__ import print_function

import datetime
import os.path
import inquirer

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendar:
    _service = None
    _calendar_id = None

    def __init__(self):
        self._get_service()
        self._select_calendar()

    def _get_service(self):
        try: 
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
        except HttpError as error:
            print('An error occurred: %s' % error)

    def _select_calendar(self) -> str:
        try:
            if self.service is None:
                self.service = self.get_service()

            # list available calendars
            calendars = self.service.calendarList().list(minAccessRole='writer').execute()

            # prompt the user to select a calendar
            selected_calendar_name = inquirer.prompt([
                inquirer.List('calendar',
                    message="In which calendar do you want to add events from E-Werk?",
                    choices=[calendar['summary'] for calendar in calendars['items'] if calendar['accessRole'] == 'owner'])
            ])['calendar']
            # get calendar item with name supplied by user
            self.calendar_id = [calendar for calendar in calendars['items'] if calendar['summary'] == selected_calendar_name][0]['id']
        except HttpError as error:
            print('An error occurred: %s' % error)

    def add_event(self, event):
        try:
            if self.calendar_id is None:
                self.calendar_id = self.select_calendar()
            self.service.events().insert(
                calendarId=self.calendar_id,
                body={
                "summary": "[E-Werk] " + f"{event['title']}",
                    "location": "E-Werk Kulturzentrum Erlangen: " + "/".join(event['locations']),
                    "start": {
                        "dateTime": event['datetime'],
                        "timeZone": "Europe/Berlin",
                    },
                    "end": {
                        "dateTime": (datetime.datetime.fromisoformat(event['datetime']) + datetime.timedelta(hours=2)).isoformat(),
                        "timeZone": "Europe/Berlin",
                    },
                    "source": {
                        "title": "E-Werk Kulturzentrum Erlangen",
                        "url": event['url'],
                    },
                    "transparency": "transparent",
                    #"status": "cancelled",
                }
            ).execute()
        except HttpError as error:
            print('An error occurred: %s' % error)