import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import gspread
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

df_full = pd.DataFrame(sheet.get_all_records())
df = df_full.copy()

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
    df["reason_category"] = "8. Other  → Other (please specify)"

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
    st.subheader("Confirm individual terms")

    campaigns = ["All"] + sorted(df["campaignname"].dropna().unique().tolist())
    selected_campaign = st.selectbox("Filter by Campaign", campaigns, index=0)
    
    df_filtered = df.copy()
    if selected_campaign != "All":
        df_filtered = df_filtered[df_filtered["campaignname"] == selected_campaign]

    adgroups = ["All"] + sorted(df_filtered["adgroupname"].dropna().unique().tolist())
    selected_adgroup = st.selectbox("Filter by Ad Group", adgroups, index=0)

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
    additional_cols = [
    "campaignname", "adgroupname", "searchterm",
    "keywordtext", "country_code_2", "cumulative_clicks",
    "cumulative_impressions", "cumulative_cost", "cumulative_sales",
    "country_code", "department"
    ]

    df_filtered = df_filtered[preferred_cols + additional_cols]

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
        key="confirm_editor",
       use_container_width=True,
       hide_index=False
    )

    if st.button("Submit Confirmed Terms"):
        invalid_rows = edited_df[
            (edited_df["confirm_from_mkt"] == False) &
            (edited_df["reason_category"] == reason_options[-1]) &
            (edited_df["reason_reject"].str.strip() == "")
        ]
        if not invalid_rows.empty:
            st.error("Please add a text reason for any 'Other' selections before submitting!")
            st.stop()

        # df.update(edited_df)
        # # df.loc[edited_df.index] = edited_df

        # sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())

        changed_rows = edited_df[df_filtered.columns].ne(df_filtered).any(axis=1)
        rows_to_update = edited_df[changed_rows]
        
        if not rows_to_update.empty:
            # for idx in rows_to_update.index:
            #     row_num = idx + 2  # +2 vì Google Sheets bắt đầu từ 1 và dòng 1 là header
            #     sheet.update(f"A{row_num}:{chr(65 + len(df.columns) - 1)}{row_num}",
            #                  [df.loc[idx].astype(str).tolist()])
            # for idx in rows_to_update.index:
            #     df_full.loc[idx] = edited_df.loc[idx] 
            #     row_num = idx + 2
            #     sheet.update(f"A{row_num}:{chr(64 + len(df_full.columns))}{row_num}",
            #                  [df_full.loc[idx].astype(str).tolist()])
            for idx in rows_to_update.index:
                row_num = idx + 2
                row_data = [str(x) if x is not None else "" for x in df_full.loc[idx]]
                start_cell = rowcol_to_a1(row_num, 1)
                end_cell = rowcol_to_a1(row_num, len(df_full.columns))
                cell_range = f"{start_cell}:{end_cell}"
                sheet.update(cell_range, [row_data])
        
        st.success("Confirmation status updated to Google Sheet!")

        # Log Writer (Confirmed + Unconfirmed)
        log_all_terms(
            edited_df=edited_df,
            user=st.session_state.user,
            sheet_id="1xORIj-ha6_yXddi-V_6nMNsxM8-A5imI6HSoPUPv9Aw",        
            sheet_name="Jarvis Confirmation Log",        
            service_account_info=st.secrets["gcp_service_account"]
        )
    
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

        # webhook_url = 'https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs'
        webhook_url = 'https://chat.googleapis.com/v1/spaces/AAQAtlalZHg/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=dAqV50K0MSHsB8PRPIqqLTmThgeGtx78zQ6lOBVME8o'
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
