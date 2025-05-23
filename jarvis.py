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
sheet = client.open_by_key(SHEET_ID).worksheet("Summary_Kill_SFO")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ---------------------------
# 4. Hiển thị Confirm
# ---------------------------
st.write("### Confirm individual terms")
confirm_status = []

for i in range(len(df)):
    term = df.loc[i, 'searchterm']
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(f"🔎 **{term}** — Sale Prob: {df.loc[i, 'Sale Probability']}, "
                 f"Impr: {df.loc[i, 'Impressions']}, Age: {df.loc[i, 'Day Age']}")
    with col2:
        confirm = st.checkbox("Confirm", key=f"confirm_{i}", value=str(df.loc[i, "Confirm"]).lower() == "true")
        confirm_status.append(confirm)

df["Confirm"] = confirm_status

# ---------------------------
# 5. Gửi kết quả xác nhận
# ---------------------------
if st.button("📤 Submit Confirmed Terms"):
    sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
    st.success("✅ Confirmation status updated to Google Sheet!")

# ---------------------------
# 6. Hiển thị bảng
# ---------------------------
st.write("### Current Confirmation Status")
st.dataframe(df)
