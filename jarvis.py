import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# ========== LOGIN ==========
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

# ========== SIDEBAR ==========
st.sidebar.image("logo.png", width=180)
st.sidebar.title("Filters")
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user}**")

department = st.sidebar.selectbox("Department", ["SFO", "SSO"], index=0)
country = st.sidebar.selectbox("Country", ["All", "US", "UK", "DE", "CA", "MX", "SA", "JP", "ES", "AU", "GB", "AE"])

# ========== LOAD DATA ==========
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
if "reason_category" not in df.columns:
    df["reason_category"] = "8. Other  → Other (please specify)"

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["Model Performance", "Search Term Predictions", "Explain a Search Term"])

# ========== TAB 1 ==========
with tab1:
    st.subheader("📊 Model Performance Summary")
    st.markdown(f"📂 Currently viewing: **{sheet_name}**")

    if "acos" in df.columns:
        df["acos"] = pd.to_numeric(df["acos"], errors="coerce")
        st.metric("Avg ACOS", f"{df['acos'].mean():.2%}")
    if "sales" in df.columns:
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
        st.metric("Total Sales", f"${df['sales'].sum():,.0f}")

# ========== TAB 2 ==========
with tab2:
    st.subheader("Confirm individual terms")

    campaigns = ["All"] + sorted(df["campaignname"].dropna().unique().tolist())
    adgroups = ["All"] + sorted(df["adgroupname"].dropna().unique().tolist())

    selected_campaign = st.selectbox("Filter by Campaign", campaigns, index=0)
    selected_adgroup = st.selectbox("Filter by Ad Group", adgroups, index=0)

    df_filtered = df.copy()
    if selected_campaign != "All":
        df_filtered = df_filtered[df_filtered["campaignname"] == selected_campaign]
    if selected_adgroup != "All":
        df_filtered = df_filtered[df_filtered["adgroupname"] == selected_adgroup]

    select_all = st.checkbox("Select All", value=True)
    df_filtered["confirm_from_mkt"] = select_all

    reason_options = [
        "1. High CR → Strong conversion rate",
        "2. Low ACOS → Efficient ACOS performance",
        "3. High CTR → High click-through rate",
        "4. Maintain CPC/Traffic → Maintain traffic and stable CPC",
        "5. Follow up → Pending further analysis",
        "6. Not enough data → Insufficient data for decision",
        "7. Brand Name/Product Mapping  → Contains branded & Product keyword",
        "8. Other  → Other (please specify)"
    ]

    preferred_cols = ["confirm_from_mkt", "reason_category", "reason_reject"]
    df_filtered = df_filtered[preferred_cols + [col for col in df_filtered.columns if col not in preferred_cols]]

    edited_df = st.data_editor(
        df_filtered,
        column_config={
            "confirm_from_mkt": st.column_config.CheckboxColumn("Confirm"),
            "reason_category": st.column_config.SelectboxColumn(
                "Reason Category (if Unconfirmed)",
                options=reason_options
            ),
            "reason_reject": st.column_config.TextColumn("Free Text Reason (if Unconfirmed)")
        },
        num_rows="dynamic",
        key="confirm_editor"
    )

    if st.button("Submit Confirmed Terms"):
        invalid_rows = edited_df[
            (edited_df["confirm_from_mkt"] == False) &
            (edited_df["reason_category"] == reason_options[-1]) &
            (edited_df["reason_reject"].str.strip() == "")
        ]
        if not invalid_rows.empty:
            st.error("You selected 'Other' as reason category but did not provide a free text reason.")
            st.stop()

        df.update(edited_df)
        sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
        st.success("Confirmation status updated to Google Sheet!")

        total_confirmed = (df["confirm_from_mkt"] == True).sum()
        total_unconfirmed = (df["confirm_from_mkt"] == False).sum()
        user = st.session_state.user
        current_sheet = sheet.title

        msg = (
            "📢 *Jarvis Confirmation Report*\n"
            f"👤 User: `{user}`\n"
            f"📄 Sheet: `{current_sheet}`\n"
            f"✅ Confirmed: `{total_confirmed}`\n"
            f"❌ Not Confirmed: `{total_unconfirmed}`"
        )

        unconfirmed_df = df[df["confirm_from_mkt"] == False]
        if not unconfirmed_df.empty:
            unconfirmed_terms = unconfirmed_df["searchterm"].tolist()
            msg += "\n\n🔍 *Unconfirmed Terms:*"
            for term in unconfirmed_terms[:10]:
                msg += f"\n• {term}"
            if len(unconfirmed_terms) > 10:
                msg += f"\n...and `{len(unconfirmed_terms) - 10}` more."

        webhook_url = st.secrets["webhook_url"]
        requests.post(webhook_url, json={"text": msg})

    st.download_button("📥 Export CSV", df.astype(str).to_csv(index=False), "search_terms.csv")

# ========== TAB 3 ==========
with tab3:
    st.subheader("Explain a Search Term")
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
