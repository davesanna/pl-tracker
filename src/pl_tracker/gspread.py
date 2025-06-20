from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import pandas as pd
import gspread
import os
from google.auth import default

from pathlib import Path


class GSpreadClient:
    def __init__(self, scopes=None):
        if scopes is None:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        self.scopes = scopes
        self.creds = None
        self.service = None
        self.google_authenticate()
        self.gspread_client = self._get_gspread_client()
        self.spreadsheets = {}

    def google_authenticate(self):
        """Authenticate with Google Sheets API and create a service object."""
        base_dir = Path(__file__).resolve().parents[2]
        token_path = os.path.join(base_dir, "token.json")
        credentials_path = os.path.join(base_dir, "credentials.json")

        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.scopes
                )
                creds = flow.run_local_server(port=0)

        # with open("token.json", "w") as token:
        #     token.write(creds.to_json())

        # flow = Flow.from_client_config(
        #     {
        #         "web": {
        #             "client_id": os.environ["GOOGLE_CLIENT_ID"],
        #             "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        #             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        #             "token_uri": "https://oauth2.googleapis.com/token",
        #             "redirect_uris": ["http://localhost:8501/oauth2callback"],
        #         }
        #     },
        #     scopes=self.scopes,
        #     redirect_uri="http://localhost:8501/oauth2callback",
        # )
        # authorization_url, state = flow.authorization_url(
        #     # Enable offline access so that you can refresh an access token without
        #     # re-prompting the user for permission. Recommended for web server apps.
        #     access_type="offline",
        #     # Enable incremental authorization. Recommended as a best practice.
        #     include_granted_scopes="true",
        # )

        # return authorization_url, state

        # self.creds, _ = default(scopes=self.scopes)

    def _get_gspread_client(self):
        """Get a gspread client using the authenticated credentials."""
        return gspread.authorize(self.creds)

    def open_spreadsheet(self, spreadsheet_id):
        """Open a Google Spreadsheet by its ID."""
        return self.gspread_client.open_by_key(spreadsheet_id)

    def get_spreadsheet(self, spreadsheet_name):
        """Get values from a specific range in a Google Spreadsheet."""
        if spreadsheet_name not in self.spreadsheets:
            self.spreadsheets[spreadsheet_name] = self.gspread_client.open(
                spreadsheet_name
            )
        return self.spreadsheets[spreadsheet_name]

    def get_worksheet(self, spreadsheet_name, worksheet_name):
        """Get a specific worksheet from a Google Spreadsheet."""
        spreadsheet = self.get_spreadsheet(spreadsheet_name)
        return spreadsheet.worksheet(worksheet_name)

    def get_df_from_worksheet(self, spreadsheet_name, worksheet_name):
        """Get a DataFrame from a specific worksheet in a Google Spreadsheet."""
        worksheet = self.get_worksheet(spreadsheet_name, worksheet_name)
        data = worksheet.get_all_values()
        return pd.DataFrame(data) if data else pd.DataFrame()
