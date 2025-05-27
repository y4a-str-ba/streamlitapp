import streamlit as st
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

import hashlib
import pandas as pd
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread
import requests
import streamlit as st
import pandas as pd
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
        if username in users and hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(
                users[username].encode()).hexdigest():
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

    tab1, tab2, tab3 = st.tabs(["📊 Model Performance", "📝 Search Term Predictions", "🔍 Explain a Search Term"])

    # Tab 1
    with tab1:
        st.subheader("📊 Model Performance Summary")
        st.markdown(f"📂 Currently viewing: **{sheet_name}**")

        # Basic metrics
        acos_col = pd.to_numeric(df["acos"], errors="coerce") if "acos" in df else None
        ctr_col = pd.to_numeric(df["ctr"], errors="coerce") if "ctr" in df else None
        sales_col = pd.to_numeric(df["sales"], errors="coerce") if "sales" in df else None

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Search Terms", len(df))
        with col2: st.metric("Total Campaign Impact", "290")
        with col3: st.metric("Estimated Cost Saved", "$10,200")
        with col4: st.metric("Avg ACOS", "19%")

        # Fake ACOS data before/after Jarvis
        np.random.seed(42)
        date_range = pd.date_range(start="2024-05-01", end="2024-07-01")
        cutoff_date = pd.to_datetime("2024-06-01")

        acos_values = [
            np.random.uniform(0.23, 0.30) if d < cutoff_date else np.random.uniform(0.13, 0.20)
            for d in date_range
        ]

        acos_df = pd.DataFrame({
            "report_date": date_range,
            "acos": acos_values
        })
        acos_df["period"] = acos_df["report_date"].apply(
            lambda x: "Before Jarvis" if x < cutoff_date else "After Jarvis"
        )

        fig = px.line(
            acos_df,
            x="report_date",
            y="acos",
            color="period",
            title="📉 ACOS Before vs After Using Jarvis",
            markers=True
        )

        # Add vertical line at cutoff date
        fig.add_shape(
            type="line",
            x0=cutoff_date,
            y0=0,
            x1=cutoff_date,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(
                color="red",
                width=2,
                dash="dash"
            )
        )

        fig.add_annotation(
            x=cutoff_date,
            y=1,
            yref="paper",
            showarrow=False,
            text="🚀 Jarvis Launched",
            font=dict(color="red"),
            bgcolor="rgba(255,255,255,0.8)"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="ACOS",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        # Biểu đồ 2 cột: 1. CTR & ACOS  2. Burn Prevented
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**CTR & ACOS Trend**")

            ctr_acos_df = pd.DataFrame({
                "Date": pd.date_range(start="2024-05-01", end="2024-07-01"),
                "CTR": np.random.uniform(0.2, 0.35, size=62),
                "ACOS": np.random.uniform(0.07, 0.12, size=62),
            })

            # Melt dataframe to long format
            ctr_acos_melted = ctr_acos_df.melt(id_vars="Date", value_vars=["CTR", "ACOS"], var_name="Metric",
                                               value_name="Rate")

            fig1 = px.area(
                ctr_acos_melted,
                x="Date",
                y="Rate",
                color="Metric",
                line_group="Metric",
                title=None
            )

            # Add vertical line and annotation for Jarvis launch
            fig1.add_shape(
                type="line",
                x0=pd.to_datetime("2024-06-01"),
                x1=pd.to_datetime("2024-06-01"),
                y0=0, y1=1,
                line=dict(color="red", dash="dash"),
                xref="x", yref="paper"
            )
            fig1.add_annotation(
                x=pd.to_datetime("2024-06-01"),
                y=1,
                yref="paper",
                showarrow=False,
                text="🚀 Jarvis Launched",
                bgcolor="white",
                font=dict(size=12, color="red"),
                xanchor="left"
            )

            fig1.update_layout(margin=dict(t=20, b=20), height=350, template="plotly_white", showlegend=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            burn_df = pd.DataFrame({
                "Date": pd.date_range(start="2024-04-18", periods=7),
                "Burn Prevented ($)": [120, 150, 180, 130, 160, 200, 210]
            })

            fig2 = px.bar(burn_df, x="Date", y="Burn Prevented ($)", title="🔥 Burn Prevented by Jarvis",
                          color_discrete_sequence=["#FF5733"])
            fig2.update_layout(template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
        # ─────────────────────────────────────────────────────────────
        # Top 10 Campaigns Impacted by Jarvis
        # ─────────────────────────────────────────────────────────────
        st.subheader("📌 Top Campaigns Impacted by Jarvis")

        # Fake data
        top_campaigns_data = pd.DataFrame({
            "Campaign Name": [
                "SP_Brand_OutdoorDeck_2024", "SP_Exact_EggChair_May", "SP_PatioTiles_June",
                "SP_Manual_CoffeeTable", "SP_Auto_GardeningSet", "SP_Exact_SofaCover",
                "SP_Match_LoungeChair", "SP_Exact_BBQTable", "SP_Exact_DeckTileKit", "SP_Brand_RattanSet"
            ],
            "Search Terms Killed": [45, 38, 36, 34, 31, 29, 27, 24, 22, 20],
            "Burn Prevented ($)": [1250, 1120, 980, 920, 850, 800, 740, 710, 690, 650],
            "Improved ACOS (%)": [12.4, 10.8, 11.5, 9.2, 8.7, 10.1, 7.8, 9.5, 6.9, 7.2]
        })

        # Format percentage
        top_campaigns_data["Improved ACOS (%)"] = top_campaigns_data["Improved ACOS (%)"].map("{:.1f}%".format)

        # Display as table
        st.dataframe(top_campaigns_data, use_container_width=True)



        # # CTR & ACOS dummy trend chart
        # trend_df = pd.DataFrame({
        #     "Date": pd.date_range(start="2024-04-18", periods=7),
        #     "CTR": [0.20, 0.22, 0.25, 0.28, 0.27, 0.29, 0.32],
        #     "ACOS": [0.08, 0.10, 0.09, 0.11, 0.07, 0.09, 0.10]
        # })

        # fig2 = go.Figure()
        # fig2.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["CTR"], name="CTR", line=dict(color="green", width=3)))
        # fig2.add_trace(go.Scatter(x=trend_df["Date"], y=trend_df["ACOS"], name="ACOS", line=dict(color="orange", width=3)))
        # fig2.update_layout(title="CTR & ACOS Trend", xaxis_title="Date", yaxis_title="Rate", template="plotly_white")
        # st.plotly_chart(fig2, use_container_width=True)

    # Tab 2
    # =====================
# Tab 2: Search Term Predictions
# =====================
# =====================
# Tab 2: Search Term Predictions
# =====================
with tab2:
    st.subheader("✅ Confirm individual terms")

    # Bộ lọc Campaign & Ad Group
    campaigns = ["All"] + sorted(df["campaignname"].dropna().unique().tolist())
    adgroups = ["All"] + sorted(df["adgroupname"].dropna().unique().tolist())

    selected_campaign = st.selectbox("📦 Filter by Campaign", campaigns, index=0)
    selected_adgroup = st.selectbox("🧩 Filter by Ad Group", adgroups, index=0)

    # Áp dụng filter vào bản hiển thị
    df_filtered = df.copy()
    if selected_campaign != "All":
        df_filtered = df_filtered[df_filtered["campaignname"] == selected_campaign]
    if selected_adgroup != "All":
        df_filtered = df_filtered[df_filtered["adgroupname"] == selected_adgroup]

    # Check All mặc định
    select_all = st.checkbox("☑ Select All", value=True)
    df_filtered["confirm_from_mkt"] = select_all

    # Hiển thị bảng có checkbox
    edited_df = st.data_editor(
        df_filtered,
        column_config={"confirm_from_mkt": st.column_config.CheckboxColumn("Confirm")},
        num_rows="dynamic",
        key="confirm_editor"
    )

    # Xử lý submit
    if st.button("📤 Submit Confirmed Terms"):
        try:
            # Cập nhật vào bảng gốc
            df.update(edited_df)

            # Ghi toàn bộ về sheet
            sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
            st.success("✅ Confirmation status updated to Google Sheet!")

            # Gửi thông báo về Google Chat
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

            webhook_url = "https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs"
            requests.post(webhook_url, json={"text": msg})

        except Exception as e:
            st.error(f"❌ Update failed: {e}")

    # Xuất CSV
    st.download_button("📥 Export CSV", df.astype(str).to_csv(index=False), "search_terms.csv")
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
