from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import pytz

def log_all_terms(edited_df, user, sheet_id, sheet_name, service_account_info):
    # Filter rejected value
    edited_df = edited_df[edited_df["confirm_from_mkt"] == False].copy()
    edited_df.loc[:, "confirm_from_mkt"] = "Rejected"
    edited_df.rename(columns={"confirm_from_mkt": "confirmation_status"}, inplace=True)

    # Add user and submitted_at
    edited_df["confirmed_by"] = user
    edited_df["submitted_at"] = pd.timestamp.now(tz=pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")

    # Select columns
    selected_columns = [
        "confirmation_status", "reason_category", "reason_reject",
        "campaignname", "adgroupid", "adgroupname", "searchterm",
        "keywordtext", "country_code_2", "cumulative_clicks",
        "cumulative_impressions", "cumulative_cost", "cumulative_sales",
        "country", "department", "confirmed_by", "submitted_at"
    ]
    edited_df = edited_df[selected_columns]

    # Connect to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    # Add header
    existing_values = sheet.get_all_values()
    header = edited_df.columns.tolist()
    if not existing_values:
        sheet.append_row(header, value_input_option="USER_ENTERED")

    # Append rows
    sheet.append_rows(edited_df.astype(str).values.tolist(), value_input_option="USER_ENTERED")
