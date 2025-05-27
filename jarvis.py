import streamlit as st
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

import hashlib
import pandas as pd
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread
import requests
import numpy as np
import plotly.express as px

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
country = st.sidebar.selectbox("Country", ["All", "US", "UK", "DE", "CA", "MX", "SA", "JP", "ES", "AU", "GB", "AE"])

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

    if "reason_reject" not in df.columns:
        df["reason_reject"] = ""

    tab1, tab2, tab3 = st.tabs(["\ud83d\udcca Model Performance", "\ud83d\udcdd Search Term Predictions", "\ud83d\udd0d Explain a Search Term"])

    with tab1:
        st.subheader("\ud83d\udcca Model Performance Summary")
        st.markdown(f"\ud83d\udcc2 Currently viewing: **{sheet_name}**")
        # You can keep your chart logic here as before

    with tab2:
        st.subheader("\u2705 Confirm individual terms")

        campaigns = ["All"] + sorted(df["campaignname"].dropna().unique().tolist())
        adgroups = ["All"] + sorted(df["adgroupname"].dropna().unique().tolist())

        selected_campaign = st.selectbox("\ud83d\udce6 Filter by Campaign", campaigns, index=0)
        selected_adgroup = st.selectbox("\ud83e\udde9 Filter by Ad Group", adgroups, index=0)

        df_filtered = df.copy()
        if selected_campaign != "All":
            df_filtered = df_filtered[df_filtered["campaignname"] == selected_campaign]
        if selected_adgroup != "All":
            df_filtered = df_filtered[df_filtered["adgroupname"] == selected_adgroup]

        select_all = st.checkbox("\u2611 Select All", value=True)
        df_filtered["confirm_from_mkt"] = select_all

        edited_df = st.data_editor(
            df_filtered,
            column_config={
                "confirm_from_mkt": st.column_config.CheckboxColumn("\u2705 Confirm"),
                "reason_reject": st.column_config.TextColumn("\u270f\ufe0f Reason (if Unconfirmed)")
            },
            num_rows="dynamic",
            key="confirm_editor"
        )

        if st.button("\ud83d\udce4 Submit Confirmed Terms"):
            invalid_rows = edited_df[(edited_df["confirm_from_mkt"] == False) & (edited_df["reason_reject"].str.strip() == "")]
            if not invalid_rows.empty:
                st.error("\u274c Please provide a reason for ALL unconfirmed terms before submitting.")
                st.stop()

            df.update(edited_df)
            sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
            st.success("\u2705 Confirmation status updated to Google Sheet!")

            total_confirmed = (df["confirm_from_mkt"] == True).sum()
            total_unconfirmed = (df["confirm_from_mkt"] == False).sum()
            user = st.session_state.user
            current_sheet = sheet.title

            msg = (
                "\ud83d\udce2 *Jarvis Confirmation Report*\n"
                f"\ud83d\udc64 User: `{user}`\n"
                f"\ud83d\udcc4 Sheet: `{current_sheet}`\n"
                f"\u2705 Confirmed: `{total_confirmed}`\n"
                f"\u274c Not Confirmed: `{total_unconfirmed}`"
            )

            unconfirmed_df = df[df["confirm_from_mkt"] == False]
            if not unconfirmed_df.empty:
                unconfirmed_terms = unconfirmed_df["searchterm"].tolist()
                msg += "\n\n\ud83d\udd0d *Unconfirmed Terms:*"
                for term in unconfirmed_terms[:10]:
                    msg += f"\n• {term}"
                if len(unconfirmed_terms) > 10:
                    msg += f"\n...and `{len(unconfirmed_terms) - 10}` more."

            webhook_url = "https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs"
            requests.post(webhook_url, json={"text": msg})

        st.download_button("\ud83d\udcc5 Export CSV", df.astype(str).to_csv(index=False), "search_terms.csv")

    with tab3:
        st.subheader("\ud83d\udd0d Explain a Search Term")
        selected_term = st.selectbox("Choose a search term", df["searchterm"])
        term_row = df[df["searchterm"] == selected_term]

        if not term_row.empty:
            term_info = term_row.iloc[0]
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Search Term Info**")
                st.write(f"\ud83d\udd0e **Search Term**: {selected_term}")
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
                st.info(f"\ud83d\udccc Reason: {term_info.get('kill_reason', 'N/A')}")
        else:
            st.warning("No data available for selected search term.")
