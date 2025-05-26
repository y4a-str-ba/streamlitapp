import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread

# Setup page
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# Sidebar filters
st.sidebar.image("logo.png", width=180)
st.sidebar.title("Filters")

department = st.sidebar.selectbox("Department", ["SFO", "SSO"])
date = st.sidebar.date_input("Date")
country = st.sidebar.selectbox("Country", ["US", "UK", "DE", "CA"])

# Setup session state for Apply button
if "apply_filters" not in st.session_state:
    st.session_state["apply_filters"] = False

if st.sidebar.button("Apply Filters"):
    st.session_state["apply_filters"] = True

# Load data only after user clicks Apply
df = pd.DataFrame()

if st.session_state["apply_filters"]:
    # Connect to Google Sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    # Load correct worksheet
    sheet_name = f"Summary_Kill_{department}"
    sheet = client.open_by_key("1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY").worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Normalize confirm column
    if "confirm_from_mkt" not in df.columns:
        df["confirm_from_mkt"] = True
    else:
        df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Model Performance", "📝 Search Term Predictions", "🔍 Explain a Search Term"])

    # =====================
    # Tab 1: Model Performance
    # =====================
    with tab1:
        st.subheader("📊 Model Performance Summary")
        st.markdown(f"📂 Currently viewing: **{sheet_name}**")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Search Terms", len(df))
        with col2:
            st.metric("Estimated Cost Saved", "$10,200")  # Placeholder
        with col3:
            st.metric("Avg ACOS", f"{df['acos'].mean():.2%}" if 'acos' in df else "N/A")
        with col4:
            st.metric("Avg CTR", f"{df['ctr'].mean():.2%}" if 'ctr' in df else "N/A")
        with col5:
            st.metric("Avg Sales", f"{df['sales'].mean():.0f}" if 'sales' in df else "N/A")

        trend_df = pd.DataFrame({
            "Date": pd.date_range(start="2024-04-18", periods=7),
            "CTR": [0.2, 0.22, 0.25, 0.28, 0.27, 0.3, 0.32],
            "ACOS": [0.01, 0.012, 0.011, 0.009, 0.008, 0.009, 0.01]
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["CTR"], name="CTR", line=dict(color="green", width=3)))
        fig.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["ACOS"], name="ACOS", line=dict(color="orange", width=3)))
        fig.update_layout(title="CTR & ACOS Trend", xaxis_title="Date", yaxis_title="Rate", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # =====================
    # Tab 2: Search Term Predictions
    # =====================
    with tab2:
        st.subheader("✅ Confirm individual terms")
        select_all = st.checkbox("☑ Select All", value=True)
        df["confirm_from_mkt"] = select_all

        edited_df = st.data_editor(
            df,
            column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
            num_rows="dynamic",
            key="confirm_editor"
        )

        if st.button("📤 Submit Confirmed Terms"):
            sheet.update([edited_df.columns.tolist()] + edited_df.astype(str).values.tolist())
            st.success("✅ Confirmation status updated to Google Sheet!")

        st.download_button("📥 Export CSV", edited_df.to_csv(index=False), "search_terms.csv")

    # =====================
    # Tab 3: Explain a Search Term
    # =====================
    with tab3:
        st.subheader("🔍 Explain a Search Term")
        selected_term = st.selectbox("Choose a search term", df["searchterm"])
        term_row = df[df["searchterm"] == selected_term]
        if not term_row.empty:
            term_info = term_row.iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Search Term Info**")
                st.write(f"🔎 **Search Term**: {selected_term}")
                st.write(f"Sales: {term_info.get('sales', 'N/A')}")
                st.write(f"CTR: {term_info.get('ctr', 'N/A')}%")
                st.write(f"ACOS: {term_info.get('acos', 'N/A')}%")
                st.write(f"Day Age: {term_info.get('day_age', 'N/A')}")
            with col2:
                st.markdown("**Why was it KILLed?**")
                st.info(f"📌 Reason: {term_info.get('kill_reason', 'N/A')}")
        else:
            st.warning("No data available for selected search term.")

else:
    st.warning("👈 Please select filters and click 'Apply Filters' to view data.")
