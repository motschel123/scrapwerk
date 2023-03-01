from __future__ import print_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendar:
    _service = None

    def __init__(self):
        self._get_service()

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

    def get_calendar_list(self) -> list:
        try:
            if self.service is None:
                self.service = self.get_service()

            # list available calendars
            calendars = self.service.calendarList().list(minAccessRole='writer').execute()

            return calendars['items']
        except HttpError as error:
            print('An error occurred: %s' % error)

    def create_event(self, calendarId, body):
        try:
            self.service.events().insert(
                calendarId=calendarId,
                body=body,
            ).execute()
        except HttpError as error:
            print('An error occurred: %s' % error)