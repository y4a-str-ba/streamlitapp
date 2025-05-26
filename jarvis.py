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

# Set default department to "SFO"
if "department" not in st.session_state:
    st.session_state["department"] = "SFO"

department = st.sidebar.selectbox("Department", ["SFO", "SSO"], index=0)
country = st.sidebar.selectbox("Country", ["US", "UK", "DE", "CA"])

    # Filter by country_code_2 column if exists
    if "country_code_2" in df.columns:
        df = df[df["country_code_2"] == country]

# Setup session state for Apply button
if "apply_filters" not in st.session_state:
    st.session_state["apply_filters"] = True  # auto-load SFO by default

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
    tab1, tab2, tab3 = st.tabs(["\U0001F4CA Model Performance", "\U0001F4DD Search Term Predictions", "\U0001F50D Explain a Search Term"])

    # =====================
    # Tab 1: Model Performance
    # =====================
    with tab1:
        st.subheader("\U0001F4CA Model Performance Summary")
        st.markdown(f"\U0001F4C2 Currently viewing: **{sheet_name}**")

        # Convert to numeric safely
        acos_col = pd.to_numeric(df["acos"], errors="coerce") if "acos" in df else None
        ctr_col = pd.to_numeric(df["ctr"], errors="coerce") if "ctr" in df else None
        sales_col = pd.to_numeric(df["sales"], errors="coerce") if "sales" in df else None

        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Search Terms", len(df))
        with col2:
            st.metric("Estimated Cost Saved", "$10,200")
        with col3:
            st.metric("Avg ACOS", f"{acos_col.mean():.2%}" if acos_col is not None and not acos_col.dropna().empty else "N/A")
        with col4:
            st.metric("Avg CTR", f"{ctr_col.mean():.2%}" if ctr_col is not None and not ctr_col.dropna().empty else "N/A")
        with col5:
            st.metric("Avg Sales", f"{sales_col.mean():.0f}" if sales_col is not None and not sales_col.dropna().empty else "N/A")

        # Dummy chart for trend
        trend_df = pd.DataFrame({
            "Date": pd.date_range(start="2024-04-18", periods=7),
            "CTR": [0.20, 0.22, 0.25, 0.28, 0.27, 0.29, 0.32],
            "ACOS": [0.08, 0.10, 0.09, 0.11, 0.07, 0.09, 0.10]
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
        st.subheader("\u2705 Confirm individual terms")
        select_all = st.checkbox("\u2611 Select All", value=True)
        df["confirm_from_mkt"] = select_all

        edited_df = st.data_editor(
            df,
            column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
            num_rows="dynamic",
            key="confirm_editor"
        )

        if st.button("\U0001F4E4 Submit Confirmed Terms"):
            sheet.update([edited_df.columns.tolist()] + edited_df.astype(str).values.tolist())
            st.success("\u2705 Confirmation status updated to Google Sheet!")

        st.download_button("\U0001F4E5 Export CSV", edited_df.to_csv(index=False), "search_terms.csv")

    # =====================
    # Tab 3: Explain a Search Term
    # =====================
    with tab3:
        st.subheader("\U0001F50D Explain a Search Term")
        selected_term = st.selectbox("Choose a search term", df["searchterm"])
        term_row = df[df["searchterm"] == selected_term]
        if not term_row.empty:
            term_info = term_row.iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Search Term Info**")
                st.write(f"\U0001F50E **Search Term**: {selected_term}")
                st.write(f"Sales: {term_info.get('sales', 'N/A')}")
                st.write(f"CTR: {term_info.get('ctr', 'N/A')}%")
                st.write(f"ACOS: {term_info.get('acos', 'N/A')}%")
                st.write(f"Day Age: {term_info.get('day_age', 'N/A')}")
            with col2:
                st.markdown("**Why was it KILLed?**")
                st.info(f"\U0001F4CC Reason: {term_info.get('kill_reason', 'N/A')}")
        else:
            st.warning("No data available for selected search term.")

else:
    st.warning("\U0001F448 Please select filters and click 'Apply Filters' to view data.")
