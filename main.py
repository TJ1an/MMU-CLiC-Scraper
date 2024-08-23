import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scraper import scrape

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
    
    """Shows basic usage of the Google Calendar API and integrates with the scraper."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        
        # Scrape the schedule data
        schedule_data = scrape()
        
        repeat_weeks = int(input("Enter the number of weeks the event should repeat: "))
        print(" ")
        
        for event_data in schedule_data:
            event = {
                "summary": event_data["subject"],
                "location": event_data["room"],
                "description": f"Class for {event_data['subject']}",
                "start": {
                    "dateTime": event_data["start"],
                    "timeZone": "Asia/Kuala_Lumpur"
                },
                "recurrence": [
                     f"RRULE:FREQ=WEEKLY;COUNT={repeat_weeks}",
                ],
                "end": {
                    "dateTime": event_data["end"],
                    "timeZone": "Asia/Kuala_Lumpur"
                },
                "attendees": [],  # Add any specific attendees if necessary
            }
            
            created_event = service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
