import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------
# 1. Config UI
# ---------------------------
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")
st.title("🔍 Jarvis — Kill Search Terms")
st.write("These terms are identified as low-performing and should be reviewed before being negativized.")

# ---------------------------
# 2. Google Sheets Auth
# ---------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# ---------------------------
# 3. Read Sheet
# ---------------------------
SHEET_ID = "1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY"
WORKSHEET_NAME = "Summary_Kill_SFO"
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ---------------------------
# 4. Chuẩn hóa cột Confirm
# ---------------------------
if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = False
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

# ---------------------------
# 5. Hiển thị bảng checkbox
# ---------------------------
st.write("### ✅ Confirm individual terms")
edited_df = st.data_editor(
    df,
    column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
    use_container_width=True,
    num_rows="dynamic",
    key="confirm_editor"
)

# ---------------------------
# 6. Gửi lại vào Google Sheet
# ---------------------------
if st.button("📤 Submit Confirmed Terms"):
    sheet.update([edited_df.columns.tolist()] + edited_df.astype(str).values.tolist())
    st.success("✅ Confirmation status updated to Google Sheet!")

# ---------------------------
# 7. Hiển thị bảng sau confirm
# ---------------------------
st.write("### Current Confirmation Status")
st.dataframe(edited_df)
