import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import gspread
import time
from google.oauth2.service_account import Credentials
from jarvis_logger import log_all_terms

from gspread.utils import rowcol_to_a1 # Quoc add

st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# ========== LOGIN ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("\U0001F510 Login to Jarvis Dashboard")
    username = st.text_input("Username").strip()
    password = st.text_input("Password", type="password").strip()
    login_button = st.button("Login")

    users = {
        "admin": hashlib.sha256("yes4all123".encode()).hexdigest(),
        "hanhbth@yes4all.com": hashlib.sha256("h@nhBI2025".encode()).hexdigest(),
        "anhdtt@yes4all.com": hashlib.sha256("anh1234".encode()).hexdigest(),
        "hanhhk@yes4all.com": hashlib.sha256("hanh123".encode()).hexdigest(),
        "khanhdnt@yes4all.com": hashlib.sha256("khanh123".encode()).hexdigest(),
        "lyntb@yes4all.com": hashlib.sha256("ly123".encode()).hexdigest(),
        "hoangl@yes4all.com": hashlib.sha256("hoang123".encode()).hexdigest(),
        "anhttn1@yes4all.com": hashlib.sha256("anh123".encode()).hexdigest(),
        "tuongnq@yes4all.com": hashlib.sha256("tuong123".encode()).hexdigest(),
        "duylk@yes4all.com": hashlib.sha256("kduyle".encode()).hexdigest(),
        "loint1@yes4all.com": hashlib.sha256("loi123".encode()).hexdigest(),
        "vynty@yes4all.com": hashlib.sha256("vy123".encode()).hexdigest(),
        "duongttt@yes4all.com": hashlib.sha256("duong123".encode()).hexdigest(),
        "thula@yes4all.com": hashlib.sha256("thu123".encode()).hexdigest(),
        "huonghtk@yes4all.com": hashlib.sha256("huong123".encode()).hexdigest(),
        "phatpct@yes4all.com": hashlib.sha256("phat123".encode()).hexdigest()
    }

    if login_button:
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        if username in users and hashed_input_password == users[username]:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("\u274c Invalid username or password")
    st.stop()
# ========== SIDEBAR ==========
st.sidebar.image("logo.png", width=180)
st.sidebar.title("Filters")
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user}**")

# department = st.sidebar.selectbox("Department", ["SFO", "SSO"], index=1)
# country = st.sidebar.selectbox("Country", ["All", "US", "INT"], index=2)

department = "SSO"
#country = "INT"

# ========== LOAD DATA ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

sheet_name = f"Summary_Kill_{department}"
sheet = client.open_by_key("1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY").worksheet(sheet_name)
data = sheet.get_all_records()

# df = pd.DataFrame(data)

# Quoc add
df_full = pd.DataFrame(sheet.get_all_records())

## unconfirmed df
# df = df_full.copy()
df = df_full[df_full["flag"] == 0].copy()

## confirmed df
df_confirmed = df_full[df_full["flag"] == 1].copy()

# Team filter
team = st.sidebar.selectbox("Team", ["All", "INT", "US"], index=0)

# Country filter
if "country_code_2" in df.columns:
    all_countries = sorted(df["country_code_2"].dropna().unique())
    if team == "US":
        filtered_countries = ["US"]
    elif team == "INT":
        filtered_countries = [c for c in all_countries if c != "US"]
    else:  # ALL
        filtered_countries = all_countries

    country_options = ["All"] + filtered_countries
    country = st.sidebar.selectbox("Country", country_options, index=0)
else:
    country = "All"
    
if "country_code_2" in df.columns:
    if team == "US":
        df = df[df["country_code_2"] == "US"]
    elif team == "INT":
        df = df[df["country_code_2"] != "US"]

    if country != "All":
        df = df[df["country_code_2"] == country]

if "confirm_from_mkt" not in df.columns:
    df["confirm_from_mkt"] = True
else:
    df["confirm_from_mkt"] = df["confirm_from_mkt"].astype(str).str.lower() == "true"

if "reason_reject" not in df.columns:
    df["reason_reject"] = ""
if "reason_category" not in df.columns:
    # df["reason_category"] = "8. Other  → Other (please specify)"
    df["reason_category"] = None

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["Search Term Predictions", "Model Performance", "Explain a Search Term"])

# ========== TAB 2 ==========
with tab2:
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

# ========== TAB 1 ==========
with tab1:
    # This callback function is triggered when the main "Select All" checkbox changes.
    def handle_select_all():
        # Get the new state (True/False) of the checkbox from session_state
        is_checked = st.session_state.select_all_checkbox

        # Apply the new state to the entire 'confirm_from_mkt' column in our stateful dataframe
        st.session_state.data_editor_df['confirm_from_mkt'] = is_checked

        # If the action was to uncheck all rows, also auto-fill the reason category
        if not is_checked:
            st.session_state.data_editor_df['reason_category'] = st.session_state.selected_filter_reason

    st.subheader("Confirm individual terms")

    # --- Filters ---
    campaigns = ["All"] + sorted(df["campaignname"].dropna().unique().tolist())
    selected_campaign = st.selectbox("Filter by Campaign", campaigns, index=0)

    df_filtered = df.copy()
    if selected_campaign != "All":
        df_filtered = df_filtered[df_filtered["campaignname"] == selected_campaign]

    adgroups = ["All"] + sorted(df_filtered["adgroupname"].dropna().unique().tolist())
    selected_adgroup = st.selectbox("Filter by Ad Group", adgroups, index=0)

    if selected_adgroup != "All":
        df_filtered = df_filtered[df_filtered["adgroupname"] == selected_adgroup]
    
    # --- Column and Reason Definitions ---
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
    additional_cols = [
        "campaignname", "adgroupname", "profile_id", "campaignid", "adgroupid", "keywordid", "searchterm",
        "keywordtext", "country_code_2", "cumulative_clicks",
        "cumulative_impressions", "cumulative_cost", "cumulative_sales",
        "country_code", "department"
    ]

    # --- Robust Session State Initialization ---
    # This block ensures the dataframe for the editor is always correctly prepared.
    filter_key = f"{selected_campaign}-{selected_adgroup}"
    if "data_editor_df" not in st.session_state or st.session_state.get("filter_key") != filter_key:
        st.session_state.filter_key = filter_key
        temp_df = df_filtered.copy()
        
        # Ensure all required columns exist before assigning to session_state
        for col in preferred_cols + additional_cols:
            if col not in temp_df.columns:
                temp_df[col] = None
        
        # Set the default 'confirm' status to True
        temp_df["confirm_from_mkt"] = True
        
        # Fill NA for reason columns to prevent errors
        temp_df["reason_category"] = temp_df["reason_category"].fillna("")
        temp_df["reason_reject"] = temp_df["reason_reject"].fillna("")

        temp_df = temp_df[preferred_cols + additional_cols]
        
        # Assign the fully prepared dataframe to session_state
        st.session_state.data_editor_df = temp_df.copy()

    # --- UI Elements for Auto-filling ---
    st.markdown("#### Apply Reason to all unconfirmed rows")

    def update_reason_for_unconfirmed():
        # Update only rows where confirm_from_mkt == False
        unconfirmed_mask = st.session_state.data_editor_df['confirm_from_mkt'] == False
        st.session_state.data_editor_df.loc[unconfirmed_mask, 'reason_category'] = st.session_state.selected_filter_reason
    
    st.selectbox(
        "Filter Reason Category",
        reason_options,
        index=0,
        key="selected_filter_reason",
        on_change=update_reason_for_unconfirmed,
        help="This reason will be auto-filled for rows you uncheck."
    )
    
    # The "Select All" checkbox, now with an on_change callback
    st.checkbox(
        "Select All",
        value=st.session_state.data_editor_df['confirm_from_mkt'].all(), # The value reflects the current state
        key="select_all_checkbox",
        on_change=handle_select_all,
        help="Check or uncheck all terms in the current view."
    )

    # --- Data Editor ---
    # This component displays the data from our session_state dataframe
    edited_df = st.data_editor(
        st.session_state.data_editor_df,
        column_config={
            "confirm_from_mkt": st.column_config.CheckboxColumn("Confirm", required=True),
            "reason_category": st.column_config.SelectboxColumn(
                "Reason Category (if Unconfirmed)", options=reason_options
            ),
            "reason_reject": st.column_config.TextColumn("Free Text Reason (if Unconfirmed)")
        },
        column_order=preferred_cols + additional_cols,
        disabled=preferred_cols[2:] + additional_cols,
        key="confirm_editor",
        use_container_width=True,
        hide_index=False
    )

    # --- Logic to handle INDIVIDUAL row edits ---
    df_before_edit = st.session_state.data_editor_df
    # Find rows that were individually unchecked by the user inside the data_editor
    newly_unchecked_mask = (df_before_edit["confirm_from_mkt"] == True) & (edited_df["confirm_from_mkt"] == False)

    if newly_unchecked_mask.any():
        # If a specific uncheck action is detected, apply the reason, update state, and rerun
        df_to_update = edited_df.copy()
        df_to_update.loc[newly_unchecked_mask, "reason_category"] = st.session_state.selected_filter_reason
        st.session_state.data_editor_df = df_to_update
        st.rerun()
    else:
        # For any other changes (e.g., re-checking a box, editing text),
        # just silently update the state without a forced rerun.
        if not df_before_edit.equals(edited_df):
            st.session_state.data_editor_df = edited_df.copy()

    # --- Submission Logic ---
    if st.button("Submit Confirmed Terms"):
        final_df = st.session_state.data_editor_df
        
        # Validation for unconfirmed rows
        invalid_rows = final_df[
            (final_df["confirm_from_mkt"] == False) &
            (
                (final_df["reason_category"].isna()) |
                (final_df["reason_category"].str.strip() == "") |
                (
                    (final_df["reason_category"] == reason_options[-1]) &
                    (final_df["reason_reject"].fillna("").str.strip() == "")
                )
            )
        ]
        if not invalid_rows.empty:
            st.error("Please add a text reason for any 'Other' selections before submitting!")
            st.stop()

        # Update the main dataframe (df_full) with changes from the editor
        for idx in final_df.index:
            if idx in df_full.index:
                df_full.loc[idx, final_df.columns] = final_df.loc[idx]
                df_full.at[idx, "flag"] = 1 if final_df.at[idx, "confirm_from_mkt"] else 0

        # Push updates to Google Sheet
        sheet.update([df_full.columns.tolist()] + df_full.astype(str).values.tolist())
        st.success("Confirmation status updated to Google Sheet!")
        
        # Log the action
        log_all_terms(
            edited_df=final_df,
            user=st.session_state.user,
            sheet_id="1xORIj-ha6_yXddi-V_6nMNsxM8-A5imI6HSoPUPv9Aw",
            sheet_name="Jarvis Confirmation Log",
            service_account_info=st.secrets["gcp_service_account"]
        )
    
        # Prepare and send notification
        total_confirmed = df_full[df_full["flag"] == 1].shape[0]
        total_unconfirmed = df_full[df_full["flag"] == 0].shape[0]
        user = st.session_state.user
        current_sheet = sheet.title
        msg = (
            f"📢 *Jarvis Confirmation Report*\n"
            f"👤 User: `{user}`\n"
            f"📄 Sheet: `{current_sheet}`\n"
            f"✅ Confirmed: `{total_confirmed}`\n"
            f"❌ Not Confirmed: `{total_unconfirmed}`"
        )
        webhook_url = 'https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs'
        requests.post(webhook_url, json={"text": msg})
        
        # Clean up session state and rerun the app to fetch fresh data
        del st.session_state.data_editor_df
        del st.session_state.selected_filter_reason
        time.sleep(1)
        st.rerun()

    # --- Display Confirmed Terms ---
    # st.download_button("📥 Export CSV", df.astype(str).to_csv(index=False), "search_terms.csv")
    # st.markdown("### Today Confirmed Terms")
    # if df_confirmed.empty:
    #     st.info("No confirmed terms yet.")
    # else:
    #     cols_to_show = [
    #         "searchterm", "campaignname", "adgroupname",
    #         "reason_category", "reason_reject", "country_code_2", "department",
    #         "cumulative_clicks", "cumulative_impressions", "cumulative_sales"
    #     ]
    #     cols_to_show = [col for col in cols_to_show if col in df_confirmed.columns]
    #     st.dataframe(df_confirmed[cols_to_show], use_container_width=True)
            

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
