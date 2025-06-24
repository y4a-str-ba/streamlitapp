import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import pandas as pd

def log_all_terms(edited_df, user, sheet_id, sheet_name, service_account_info):

    edited_df = edited_df.copy()
    
    submitted_at = pd.Timestamp.now(tz=pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")
    edited_df["confirmed_by"] = user
    edited_df["submitted_at"] = submitted_at

    # Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    # Write Header
    if not sheet.get_all_values():
        sheet.append_row(edited_df.columns.tolist(), value_input_option="USER_ENTERED")

    # Append Rows
    sheet.append_rows(edited_df.astype(str).values.tolist(), value_input_option="USER_ENTERED")

