import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(page_title="Jarvis Dashboard", layout="wide", initial_sidebar_state="expanded")

# Sidebar
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
df = pd.DataFrame(sheet.get_all_records())

if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = True
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() != "false"

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📈 Model Performance", "✅ Search Term Predictions", "🔍 Explain a Search Term"])

with tab1:
    st.subheader("Model Performance")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Search Terms", len(df))
    col2.metric("Estimated Cost Saved", "$10,200")
    col3.metric("Avg ACOS", "0.01%")
    col4.metric("Avg CTR", f"{df['ctr'].mean():.2%}")
    col5.metric("Avg Sales", f"{df['sales'].mean():.2f}")

    chart_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-04-18", periods=7),
        "CostSaved": [2000, 3000, 3500, 6000, 7000, 9200, 10200]
    })
    fig = px.line(chart_data, x="Date", y="CostSaved", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Confirm individual terms")
    select_all = st.checkbox("Select All", value=True)
    if select_all:
        df["confirm_from_mkt"] = True

    edited_df = st.data_editor(
        df,
        column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
        num_rows="dynamic",
        key="confirm_editor"
    )

    if st.button("📤 Submit Confirmed Terms"):
        sheet.update([df.columns.tolist()] + edited_df.astype(str).values.tolist())
        st.success("✅ Confirmation status updated to Google Sheet!")

    st.download_button("📥 Export CSV", edited_df.to_csv(index=False), "search_terms.csv")

with tab3:
    st.subheader("Explain a Search Term")
    selected_term = st.selectbox("Choose a search term", df["searchterm"].unique())
    term_row = df[df["searchterm"] == selected_term]
    if not term_row.empty:
        term_info = term_row.iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Search Term**: {selected_term}")
            st.write(f"Sales: {term_info.get('sales', 'N/A')}")
            st.write(f"CTR: {term_info.get('ctr', 'N/A')}%")
            st.write(f"ACOS: {term_info.get('acos', 'N/A')}%")
            st.write(f"Day Age: {term_info.get('day_age', 'N/A')}")
        with col2:
            st.markdown("**Why was it KILLed?**")
            reason = f"Based on low CTR ({term_info.get('ctr', '?')}%), day_age={term_info.get('day_age', '?')}, and reason: {term_info.get('reason', 'N/A')}"
            st.success(reason)
