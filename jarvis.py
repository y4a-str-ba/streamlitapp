import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# UI Config
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")
st.title("📊 Jarvis — Kill Search Terms Dashboard")

# Sidebar Filters
st.sidebar.image("logo.png", width=150)
st.sidebar.header("Filters")
department = st.sidebar.selectbox("Department", ["SFO", "SSO"])
date = st.sidebar.date_input("Date")
country = st.sidebar.selectbox("Country", ["US", "UK", "DE", "CA"])
st.sidebar.button("Apply Filters")

# Google Sheets Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# Read Google Sheet
SHEET_ID = "1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY"
WORKSHEET_NAME = "Summary_Kill_SFO"
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Clean confirm column
if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = False
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

# Tabs
tab1, tab2 = st.tabs(["🔍 Predictions", "🧠 Explain a Search Term"])

# --------------------
# TAB 1: Predictions
# --------------------
with tab1:
    st.subheader("📈 Model Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Recall@KILL", "82%")
        st.metric("False KILL Rate", "4%")
    with col2:
        st.metric("Estimated Cost Saved", "$10,200")
    with col3:
        trend = pd.DataFrame({
            "Date": pd.date_range("2024-04-18", periods=7),
            "CostSaved": [2000, 3000, 3500, 6000, 7000, 9200, 10200]
        })
        fig = px.line(trend, x="Date", y="CostSaved", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📋 Search Term Predictions")

    # Badge color
    df["predict_display"] = df["predict"].apply(lambda x: f"🟥 {x}" if x.upper() == "KILL" else f"🟩 {x}")

    # Select All logic
    if st.button("✅ Select All"):
        df["confirm_from_mkt"] = True

    paginated_df = df.copy()
    st.data_editor(
        paginated_df[["searchterm", "predict_display", "sales", "acos", "ctr", "day_age", "confirm_from_mkt"]],
        column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
        num_rows="dynamic",
        use_container_width=True,
        key="confirm_editor"
    )

    # Export button
    st.download_button("📥 Export CSV", df.to_csv(index=False), "search_terms.csv")

    if st.button("📤 Submit Confirmed Terms"):
        sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
        st.success("✅ Confirmation status updated to Google Sheet!")

# --------------------
# TAB 2: Explain a Search Term
# --------------------
with tab2:
    st.subheader("🔍 Explain a Search Term")
    selected_term = st.selectbox("Choose a search term", df["searchterm"])
    row = df[df["searchterm"] == selected_term]
    if not row.empty:
        term_info = row.iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Overview**")
            st.write(f"**Sales:** {term_info.get('sales', '?')}")
            st.write(f"**CTR:** {term_info.get('ctr', '?')}%")
            st.write(f"**ACOS:** {term_info.get('acos', '?')}%")
            st.write(f"**Day Age:** {term_info.get('day_age', '?')}")
        with col2:
            st.markdown("**Why was it KILLed?**")
            if str(term_info.get('predict', '')).upper() == "KILL":
                reason = f"- Low CTR ({term_info.get('ctr', '?')}%)\n- Day Age: {term_info.get('day_age', '?')}\n- Reason: {term_info.get('reason', 'N/A')}"
                st.error(reason)
            else:
                st.success("Term is performing well.")
