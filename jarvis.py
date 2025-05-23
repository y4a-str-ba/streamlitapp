import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Jarvis Dashboard", layout="wide")
st.title("🔍 Jarvis — Kill Search Terms")
st.write("These terms are identified as low-performing and should be reviewed before being negativized.")

# ───────────────────────────────────────────────────────
# 1. Kết nối Google Sheet từ st.secrets
# ───────────────────────────────────────────────────────
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
service_account_info = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Mở Sheet
SHEET_NAME = "JARVIS_PREDICT_OUTPUT"  
sheet = client.open(SHEET_NAME).Summary_Kill_SFO
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ───────────────────────────────────────────────────────
# 2. Hiển thị Confirm từng dòng
# ───────────────────────────────────────────────────────
st.write("### Confirm individual terms")
confirm_status = []

for i in range(len(df)):
    term = df.loc[i, 'Search Term']
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(f"🔎 **{term}** — Sale Prob: {df.loc[i, 'Sale Probability']}, "
                 f"Impr: {df.loc[i, 'Impressions']}, Age: {df.loc[i, 'Day Age']}")
    with col2:
        confirm = st.checkbox("Confirm", key=f"confirm_{i}", value=df.loc[i, "Confirm"] == "TRUE")
        confirm_status.append(confirm)

df["Confirm"] = confirm_status

# ───────────────────────────────────────────────────────
# 3. Submit để ghi ngược vào Google Sheet
# ───────────────────────────────────────────────────────
if st.button("📤 Submit Confirmed Terms"):
    sheet.update([df.columns.values.tolist()] + df.astype(str).values.tolist())
    st.success("✅ Confirmation status successfully updated to Google Sheet!")

# ───────────────────────────────────────────────────────
# 4. Hiển thị bảng kết quả
# ───────────────────────────────────────────────────────
st.write("### Current Confirmation Status")
st.dataframe(df)
