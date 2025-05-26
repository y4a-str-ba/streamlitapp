import streamlit as st
import hashlib
import pandas as pd
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread
import requests

st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# =====================
# LOGIN PAGE
# =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Jarvis Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    users = {
        "admin": "yes4all123",
        "hanhbth@yes4all.com": "h@nhBI2025",
        "duylk@yes4all.com": "duyTeam123",
        "ngatpth@yes4all.com": "ngat123"
    }

    if login_button:
        if username in users and hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(users[username].encode()).hexdigest():
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# =====================
# MAIN DASHBOARD
# =====================
st.sidebar.image("logo.png", width=180)
st.sidebar.title("Filters")
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user}**")

if "department" not in st.session_state:
    st.session_state["department"] = "SFO"

department = st.sidebar.selectbox("Department", ["SFO", "SSO"], index=0)
country = st.sidebar.selectbox("Country", ["All", "US", "UK", "DE", "CA","MX","SA","JP","ES","AU","GB","AE"])

if "apply_filters" not in st.session_state:
    st.session_state["apply_filters"] = True

if st.sidebar.button("Apply Filters"):
    st.session_state["apply_filters"] = True

df = pd.DataFrame()
if st.session_state["apply_filters"]:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    sheet_name = f"Summary_Kill_{department}"
    sheet = client.open_by_key("1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY").worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if "country_code_2" in df.columns and country != "All":
        df = df[df["country_code_2"] == country]

    if "confirm_from_mkt" not in df.columns:
        df["confirm_from_mkt"] = True
    else:
        df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

    tab1, tab2, tab3 = st.tabs(["📊 Model Performance", "📝 Search Term Predictions", "🔍 Explain a Search Term"])

    # Tab 1
    with tab1:
        st.subheader("📊 Model Performance Summary")
        st.markdown(f"📂 Currently viewing: **{sheet_name}**")

        acos_col = pd.to_numeric(df["acos"], errors="coerce") if "acos" in df else None
        ctr_col = pd.to_numeric(df["ctr"], errors="coerce") if "ctr" in df else None
        sales_col = pd.to_numeric(df["sales"], errors="coerce") if "sales" in df else None

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("Total Search Terms", len(df))
        with col2: st.metric("Estimated Cost Saved", "$10,200")
        with col3: st.metric("Avg ACOS", f"{acos_col.mean():.2%}" if acos_col is not None and not acos_col.dropna().empty else "N/A")
        with col4: st.metric("Avg CTR", f"{ctr_col.mean():.2%}" if ctr_col is not None and not ctr_col.dropna().empty else "N/A")
        with col5: st.metric("Avg Sales", f"{sales_col.mean():.0f}" if sales_col is not None and not sales_col.dropna().empty else "N/A")

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

    # Tab 2
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

            total_confirmed = (edited_df["confirm_from_mkt"] == True).sum()
            total_unconfirmed = (edited_df["confirm_from_mkt"] == False).sum()
            user = st.session_state.user
            current_sheet = sheet.title

            msg = (
                "📢 *Jarvis Confirmation Report*\n"
                f"👤 User: `{user}`\n"
                f"📄 Sheet: `{current_sheet}`\n"
                f"✅ Confirmed: `{total_confirmed}`\n"
                f"❌ Not Confirmed: `{total_unconfirmed}`"
            )

            unconfirmed_df = edited_df[edited_df["confirm_from_mkt"] == False]
            if not unconfirmed_df.empty:
                unconfirmed_terms = unconfirmed_df["searchterm"].tolist()
                msg += "\n\n🔍 *Unconfirmed Terms:*"
                for term in unconfirmed_terms[:10]:
                    msg += f"\n• {term}"
                if len(unconfirmed_terms) > 10:
                    msg += f"\n...and `{len(unconfirmed_terms) - 10}` more."

            webhook_url = "https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs"
            try:
                requests.post(webhook_url, json={"text": msg})
            except Exception as e:
                st.warning(f"⚠️ Failed to send alert to Google Chat: {e}")

        st.download_button("📥 Export CSV", edited_df.to_csv(index=False), "search_terms.csv")

    # Tab 3
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

                ctr_val = pd.to_numeric(term_info.get("ctr", None), errors="coerce")
                acos_val = pd.to_numeric(term_info.get("acos", None), errors="coerce")
                conv_val = pd.to_numeric(term_info.get("conversion_rate", None), errors="coerce")

                st.write(f"CTR: {ctr_val:.2%}" if pd.notnull(ctr_val) else "CTR: N/A")
                st.write(f"ACOS: {acos_val:.2%}" if pd.notnull(acos_val) else "ACOS: N/A")
                st.write(f"Day Age: {term_info.get('day_age', 'N/A')}")
                st.write(f"Cost: {term_info.get('cost', 'N/A')}")
                st.write(f"CPC: {term_info.get('cpc', 'N/A')}")
                st.write(f"Conversion Rate: {conv_val:.2%}" if pd.notnull(conv_val) else "Conversion Rate: N/A")
                st.write(f"Clicks: {term_info.get('clicks', 'N/A')}")
                st.write(f"Spend/Day: {term_info.get('spend_per_day', 'N/A')}")
                st.write(f"Purchases: {term_info.get('purchases', 'N/A')}")
                st.write(f"Units Sold: {term_info.get('unitssold', 'N/A')}")
                st.write(f"Score: {term_info.get('score', 'N/A')}")

            with col2:
                st.markdown("**Why was it KILLed?**")
                st.info(f"📌 Reason: {term_info.get('kill_reason', 'N/A')}")
        else:
            st.warning("No data available for selected search term.")

else:
    st.warning("👈 Please select filters and click 'Apply Filters' to view data.")
