import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# ---------------------------
# 1. UI & Auth Config
# ---------------------------
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

st.sidebar.image("logo.png")
st.sidebar.title("Filters")
department = st.sidebar.selectbox("Department", ["SFO", "SSO"])
date = st.sidebar.date_input("Date")
country = st.sidebar.selectbox("Country", ["US", "UK", "DE", "CA"])
st.sidebar.button("Apply Filters")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# ---------------------------
# 2. Load Data
# ---------------------------
SHEET_ID = "1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY"
WORKSHEET_NAME = "Summary_Kill_SFO"
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = False
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

# ---------------------------
# 3. KPIs
# ---------------------------
st.subheader("Model Performance")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Recall@KILL", "82%")
    st.metric("False KILL Rate", "4%")
with col2:
    st.metric("Estimated Cost Saved", "$10,200")
with col3:
    cost_df = pd.DataFrame({
        "Date": pd.date_range(start="2024-04-18", periods=7),
        "CostSaved": [2000, 3000, 3500, 6000, 7000, 9200, 10200]
    })
    fig = px.line(cost_df, x="Date", y="CostSaved", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 4. Tabs
# ---------------------------
tab1, tab2 = st.tabs(["📊 Search Term Predictions", "🔍 Explain a Search Term"])

with tab1:
    st.metric("Total Search Terms", len(df))
    # Add Select All Checkbox
    select_all = st.checkbox("✅ Select All", value=False)
    if select_all:
        df["confirm_from_mkt"] = True

    paginated_df = df.copy()
    paginated_df = paginated_df.reset_index(drop=True)

    edited_df = st.data_editor(
        paginated_df,
        column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
        use_container_width=True,
        num_rows="dynamic",
        key="editor"
    )

    if st.button("📤 Submit Confirmed Terms"):
        sheet.update([edited_df.columns.tolist()] + edited_df.astype(str).values.tolist())
        st.success("✅ Confirmation status updated to Google Sheet!")

    st.download_button("📥 Export CSV", edited_df.to_csv(index=False), "search_terms.csv")

with tab2:
    st.write("### Explain a Search Term")
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
            reason = f"Based on low CTR ({term_info.get('ctr', '?')}%), day_age={term_info.get('day_age', '?')}, and reason: {term_info.get('reason', 'N/A')}"
            st.warning(reason)
    else:
        st.warning("No data available for selected search term.")
