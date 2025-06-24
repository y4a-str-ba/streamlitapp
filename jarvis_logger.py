import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def log_all_terms(edited_df, user, sheet_id, sheet_name, service_account_info):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    edited_df = edited_df.copy()
    edited_df["confirmed_by"] = user
    edited_df["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_to_append = edited_df.astype(str).values.tolist()
    sheet.append_rows(data_to_append, value_input_option="USER_ENTERED")
