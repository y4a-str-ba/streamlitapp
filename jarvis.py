import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# ---------------------------
# 1. Config UI
# ---------------------------
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# Remove dark theme CSS override if present
# Sidebar Filters
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("Filters")
department = st.sidebar.selectbox("Department", ["SFO", "SSO"])
date = st.sidebar.date_input("Date")
country = st.sidebar.selectbox("Country", ["US", "UK", "DE", "CA"])
st.sidebar.button("Apply Filters")

# Google Sheets Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# Read Sheet
SHEET_ID = "1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY"
WORKSHEET_NAME = "Summary_Kill_SFO"
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = False
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

# Model Performance
st.subheader("Model Performance")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Recall@KILL", "82%")
    st.metric("False KILL Rate", "4%")
with col2:
    st.metric("Estimated Cost Saved", "$10,200")
with col3:
    chart_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-04-18", periods=7),
        "CostSaved": [2000, 3000, 3500, 6000, 7000, 9200, 10200]
    })
    fig = px.line(chart_data, x="Date", y="CostSaved", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Search Term Predictions
st.subheader("Search Term Predictions")
st.data_editor(
    df,
    column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
    use_container_width=True,
    num_rows="dynamic",
    key="confirm_editor"
)

# Submit
if st.button("📤 Submit Confirmed Terms"):
    sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
    st.success("✅ Confirmation status updated to Google Sheet!")

# Explain a Term
st.subheader("Explain a Search Term")
selected_term = st.selectbox("Choose a search term", df["searchterm"])
term_row = df[df["searchterm"] == selected_term]
if not term_row.empty:
    term_info = term_row.iloc[0]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Explain this term:**")
        st.write(f"**Search Term**: {selected_term}")
        st.write(f"Sales: {term_info.get('sales', 'N/A')}")
        st.write(f"CTR: {term_info.get('ctr', 'N/A')}%")
        st.write(f"ACOS: {term_info.get('acos', 'N/A')}%")
        st.write(f"Day Age: {term_info.get('day_age', 'N/A')}")
    with col2:
        st.markdown("**Why was it KILLed?**")
        if str(term_info.get('predict', '')).upper() == "KILL":
            reason = f"Based on low CTR ({term_info.get('ctr', '?')}%), day_age={term_info.get('day_age', '?')}, and reason: {term_info.get('reason', 'N/A')}"
        else:
            reason = "Term is performing well."
        st.success(reason)
else:
    st.warning("No data available for selected search term.")

# Final
st.write("### Current Confirmation Status")
st.dataframe(df, use_container_width=True)
