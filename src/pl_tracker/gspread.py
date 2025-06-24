import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import pandas as pd
import gspread
import os
from google.auth import default

from pathlib import Path
from googleapiclient.discovery import build

load_dotenv()


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
        # base_dir = Path(__file__).resolve().parents[2]
        # token_path = os.path.join(base_dir, "token.json")
        # credentials_path = os.path.join(base_dir, "credentials.json")

        # if os.path.exists(token_path):
        #     self.creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        # # If there are no (valid) credentials available, let the user log in.
        # if not self.creds or not self.creds.valid:
        #     if self.creds and self.creds.expired and self.creds.refresh_token:
        #         self.creds.refresh(Request())
        #     else:
        #         flow = InstalledAppFlow.from_client_secrets_file(
        #             credentials_path, self.scopes
        #         )
        #         creds = flow.run_local_server(port=0)

        # with open("token.json", "w") as token:
        #     token.write(creds.to_json())

        json_data = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_data:
            raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON in environment")

        info = json.loads(json_data)
        self.creds = Credentials.from_service_account_info(info, scopes=self.scopes)

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
