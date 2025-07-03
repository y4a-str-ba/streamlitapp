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
    edited_df["submitted_at"] = pd.Timestamp.now(tz=pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")

    # Select columns
    selected_columns = [
        "confirmed_by", "submitted_at", "confirmation_status", "reason_category", "reason_reject",
        "campaignname", "adgroupname", "profile_id", "campaignid", "adgroupid", "keywordid", "searchterm",
        "keywordtext", "country_code_2", "cumulative_clicks",
        "cumulative_impressions", "cumulative_cost", "cumulative_sales",
        "country_code", "department" 
    ]
    edited_df = edited_df[selected_columns]

    # Connect to Google Sheets
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    # Check if sheet is truly empty (cell A1 is blank)
    first_cell = sheet.acell("A1").value

    if not first_cell and not edited_df.empty:
        # Sheet is empty → write header + data
        all_data = [edited_df.columns.tolist()] + edited_df.astype(str).values.tolist()
        sheet.update("A1", all_data, value_input_option="USER_ENTERED")
    elif not edited_df.empty:
        # Sheet has data → only append data
        sheet.append_rows(edited_df.astype(str).values.tolist(), value_input_option="USER_ENTERED")
