import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import gspread
import datetime
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
        "phatpct@yes4all.com": hashlib.sha256("phat123".encode()).hexdigest(),
        "vynth1@yes4all.com": hashlib.sha256("vy123".encode()).hexdigest()
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

@st.cache_resource(show_spinner="Connecting to Google Sheet...")
def get_sheet(sheet_name):
    return client.open_by_key("1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY").worksheet(sheet_name)

sheet_name = f"Summary_Kill_{department}"
sheet = get_sheet(sheet_name)

data = sheet.get_all_records()

# Quoc add
df_full = pd.DataFrame(data)

## unconfirmed df
df = df_full[df_full["flag"] == 0].copy()

## confirmed df
df_confirmed = df_full[df_full["flag"] == 1].copy()

# Team filter
team = st.sidebar.selectbox("Team", ["INT", "US"], index=0)

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

if "reason_category_previous" not in df.columns:
    df["reason_category_previous"] = ""

if "reason_reject_previous" not in df.columns:
    df["reason_reject_previous"] = ""

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
    
    def handle_select_all():
        is_checked = st.session_state.select_all_checkbox
        st.session_state.data_editor_df['confirm_from_mkt'] = is_checked
        if not is_checked:
            st.session_state.data_editor_df['reason_category'] = st.session_state.selected_filter_reason

    def update_reason_for_unconfirmed():
        unconfirmed_mask = st.session_state.data_editor_df['confirm_from_mkt'] == False
        st.session_state.data_editor_df.loc[unconfirmed_mask, 'reason_category'] = st.session_state.selected_filter_reason
    
        st.subheader("Confirm individual terms")

    # --- Use filters from Sidebar ---
    selected_team = team
    selected_country = country

    df_filtered = df.copy()

    # Team & Country Filter
    if selected_team != "All" and "team" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["team"] == selected_team]

    if selected_country != "All" and "country" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["country"] == selected_country]

    # Campaign Filter
    st.markdown("### Campaign Filter")
    col1, col2 = st.columns([1, 5])
    with col1:
        campaign_operator = st.selectbox(
            "Operator",
            ["Contains", "Not Contains", "Equals", "Starts With", "Ends With"],
            key="campaign_operator"
        )
    with col2:
        campaign_value = st.text_input("Value", key="campaign_value")

    if campaign_value.strip() != "":
        if campaign_operator == "Contains":
            df_filtered = df_filtered[df_filtered["campaignname"].str.contains(campaign_value, case=False, na=False)]
        elif campaign_operator == "Not Contains":
            df_filtered = df_filtered[~df_filtered["campaignname"].str.contains(campaign_value, case=False, na=False)]
        elif campaign_operator == "Equals":
            df_filtered = df_filtered[df_filtered["campaignname"].str.lower() == campaign_value.strip().lower()]
        elif campaign_operator == "Starts With":
            df_filtered = df_filtered[df_filtered["campaignname"].str.startswith(campaign_value, na=False)]
        elif campaign_operator == "Ends With":
            df_filtered = df_filtered[df_filtered["campaignname"].str.endswith(campaign_value, na=False)]
    selected_campaign = campaign_value 

    # Adgroup Filter
    st.markdown("### Adgroup Filter")
    col1, col2 = st.columns([1, 5])
    with col1:
        adgroup_operator = st.selectbox(
            "Operator",
            ["Contains", "Not Contains", "Equals", "Starts With", "Ends With"],
            key="adgroup_operator"
        )
    with col2:
        adgroup_value = st.text_input("Value", key="adgroup_value")

    if adgroup_value.strip() != "":
        if adgroup_operator == "Contains":
            df_filtered = df_filtered[df_filtered["adgroupname"].str.contains(adgroup_value, case=False, na=False)]
        elif adgroup_operator == "Not Contains":
            df_filtered = df_filtered[~df_filtered["adgroupname"].str.contains(adgroup_value, case=False, na=False)]
        elif adgroup_operator == "Equals":
            df_filtered = df_filtered[df_filtered["adgroupname"].str.lower() == adgroup_value.strip().lower()]
        elif adgroup_operator == "Starts With":
            df_filtered = df_filtered[df_filtered["adgroupname"].str.startswith(adgroup_value, na=False)]
        elif adgroup_operator == "Ends With":
            df_filtered = df_filtered[df_filtered["adgroupname"].str.endswith(adgroup_value, na=False)]
    selected_adgroup = adgroup_value

    # Search Term Filter
    st.markdown("### Search Term Filter")
    col1, col2 = st.columns([1, 5])
    with col1:
        search_operator = st.selectbox(
            "Operator",
            ["Contains", "Not Contains", "Equals", "Starts With", "Ends With"],
            key="search_operator"
        )
    with col2:
        search_value = st.text_input("Value", key="search_value")

    if search_value.strip() != "":
        if search_operator == "Contains":
            df_filtered = df_filtered[df_filtered["searchterm"].str.contains(search_value, case=False, na=False)]
        elif search_operator == "Not Contains":
            df_filtered = df_filtered[~df_filtered["searchterm"].str.contains(search_value, case=False, na=False)]
        elif search_operator == "Equals":
            df_filtered = df_filtered[df_filtered["searchterm"].str.lower() == search_value.strip().lower()]
        elif search_operator == "Starts With":
            df_filtered = df_filtered[df_filtered["searchterm"].str.startswith(search_value, na=False)]
        elif search_operator == "Ends With":
            df_filtered = df_filtered[df_filtered["searchterm"].str.endswith(search_value, na=False)]
    selected_search_term = search_value

    # Date Range Filter
    st.markdown("### Date Range Filter") 
    if "report_date" in df_full.columns:
        # Convert report_date to datetime
        df_full["report_date"] = pd.to_datetime(df_full["report_date"], errors="coerce")
    
        # Get min & max dates from full dataset
        if not df_full["report_date"].dropna().empty:
            min_date = df_full["report_date"].dropna().min().date()
            max_date = df_full["report_date"].dropna().max().date()
        else:
            today = datetime.date.today()
            min_date = max_date = today
    
        # Show Date Range Picker
        selected_date_range = st.date_input(
            "Filter by Report Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter rows by report_date"
        )
    
        # Apply date filter safely
        if (
            isinstance(selected_date_range, (tuple, list)) and
            len(selected_date_range) == 2 and
            all(isinstance(d, datetime.date) for d in selected_date_range)
        ):
            start_date, end_date = selected_date_range
    
            # Ensure df_filtered report_date is datetime
            df_filtered["report_date"] = pd.to_datetime(df_filtered["report_date"], errors="coerce")
    
            df_filtered = df_filtered[
                (df_filtered["report_date"].dt.date >= start_date) &
                (df_filtered["report_date"].dt.date <= end_date)
            ]
        else:
            st.warning("Select both start and end date to apply date range filter.")

        # Performance Metrics Filter
        st.markdown("### Performance Metrics Filter")
        
        metric_map = {
            "Clicks": "cumulative_clicks",
            "Impressions": "cumulative_impressions",
            "Cost": "cumulative_cost",
            "Sales": "cumulative_sales",
            "Converted Amount": "get_amount_transformed"
        }
        
        comparison_ops = {
            "=": lambda x, y: x == y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
        }
        
        if "metric_filters" not in st.session_state:
            st.session_state.metric_filters = []
        
        col1, col2, col3, col4 = st.columns([1.5, 1, 2, 1])
        with col1:
            selected_metric_label = st.selectbox("Metric", list(metric_map.keys()), key="metric_filter_column")
        with col2:
            selected_operator = st.selectbox("Operator", list(comparison_ops.keys()), index=1, key="metric_filter_operator")
        with col3:
            input_value = st.number_input("Value", key="metric_filter_value", value=1.0, step=0.1, format="%.6f")
        with col4:
            if st.button("➕ Add Filter"):
                st.session_state.metric_filters.append({
                    "label": selected_metric_label,
                    "col": metric_map[selected_metric_label],
                    "op": selected_operator,
                    "value": round(float(input_value), 6),  # avoid floating point issue
                })
        
        # Apply All Filters to df
        df_filtered = df.copy()
        for f in st.session_state.metric_filters:
            try:
                df_filtered[f["col"]] = pd.to_numeric(df_filtered[f["col"]], errors="coerce")
                op_func = comparison_ops[f["op"]]
                df_filtered = df_filtered[op_func(df_filtered[f["col"]], f["value"])]
            except Exception as e:
                st.warning(f"❌ Error applying filter on {f['label']}: {e}")
        
        # -Show Applied Filters
        if st.session_state.metric_filters:
            st.markdown("#### ✅ Applied Filters")
            for f in st.session_state.metric_filters:
                st.markdown(f"- {f['label']} {f['op']} {f['value']}")

        
    # --- Column and Reason Definitions ---
    reason_options = [
        "1. High CR → Strong conversion rate",
        "2. Low ACOS → Efficient ACOS performance",
        "3. High CTR → High click-through rate",
        "4. Maintain CPC/Traffic → Maintain traffic and stable CPC",
        "5. Follow up → Pending further analysis",
        "6. Not enough data → Insufficient data for decision",
        "7. Brand Name/Product Mapping → Contains branded & Product keyword",
        "8. Other → Other (please specify)"
    ]
    preferred_cols = [
    "confirm_from_mkt", 
    "searchterm", 
    "reason_category", 
    "reason_reject", 
    "reason_category_previous", 
    "reason_reject_previous"
    ]
    additional_cols = [
        "report_date", "campaignname", "adgroupname",
        "keywordtext", "cumulative_clicks", "cumulative_impressions",
        "cumulative_cost", "cumulative_sales", "get_amount_transformed", 
        "profile_id", "campaignid", "adgroupid", "keywordid",
        "country_code_2", "country_code", "department"
    ]

    # --- Session State Initialization ---
    if (
        isinstance(selected_date_range, (tuple, list)) and
        len(selected_date_range) == 2 and
        all(isinstance(d, datetime.date) for d in selected_date_range)
    ):
        start_date, end_date = selected_date_range
    else:
        start_date = end_date = "all"
    
    metric_key = f"{selected_metric_label}-{selected_operator}-{input_value}"
    filter_key = f"{selected_team}-{selected_country}-{selected_campaign}-{selected_adgroup}-{selected_search_term}-{start_date}-{end_date}-{metric_key}"
    
    if "data_editor_df" not in st.session_state or st.session_state.get("filter_key") != filter_key:
        st.session_state.filter_key = filter_key
        temp_df = df_filtered.copy()

        # Ensure all required columns exist
        for col in preferred_cols + additional_cols:
            if col not in temp_df.columns:
                temp_df[col] = None

        temp_df["confirm_from_mkt"] = True
        temp_df["reason_category"] = temp_df["reason_category"].fillna("")
        temp_df["reason_reject"] = temp_df["reason_reject"].fillna("")
        temp_df = temp_df[preferred_cols + additional_cols]

        st.session_state.data_editor_df = temp_df.copy()

    # --- UI Elements ---
    st.markdown("#### Apply Reason To All Unconfirmed Rows")
    st.selectbox(
        "Filter Reason Category",
        reason_options,
        index=0,
        key="selected_filter_reason",
        on_change=update_reason_for_unconfirmed,
        help="This reason will be auto-filled for rows you uncheck."
    )

    st.checkbox(
        "Select All",
        value=st.session_state.data_editor_df['confirm_from_mkt'].all(),
        key="select_all_checkbox",
        on_change=handle_select_all,
        help="Check or uncheck all terms in the current view."
    )

    # --- Data Editor ---
    edited_df = st.data_editor(
        st.session_state.data_editor_df,
        column_config={
            "confirm_from_mkt": st.column_config.CheckboxColumn("Confirm", required=True),
            "reason_category": st.column_config.SelectboxColumn(
                "Reason Category (if Unconfirmed)", options=reason_options
            ),
            "reason_reject": st.column_config.TextColumn("Free Text Reason (if Unconfirmed)"),
            "reason_category_previous": st.column_config.TextColumn("Previous Reason Category", disabled=True),
            "reason_reject_previous": st.column_config.TextColumn("Previous Free Text Reason", disabled=True),
            "get_amount_transformed": st.column_config.NumberColumn("converted_amount")
        },
        column_order=preferred_cols + additional_cols,
        disabled=additional_cols,
        key="confirm_editor",
        use_container_width=True,
        hide_index=False
    )
    # Compare df before and after editing
    if not st.session_state.data_editor_df.equals(edited_df):
        df_to_update = edited_df.copy()
        newly_unchecked_mask = (st.session_state.data_editor_df["confirm_from_mkt"] == True) & (df_to_update["confirm_from_mkt"] == False)
        if newly_unchecked_mask.any():
            df_to_update.loc[newly_unchecked_mask, "reason_category"] = st.session_state.selected_filter_reason
        st.session_state.data_editor_df = df_to_update
        st.rerun()

    # --- Submission Logic ---
    if st.button("Submit Confirmed Terms"):
        final_df = st.session_state.data_editor_df
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

        for idx in final_df.index:
            if idx in df_full.index:
                df_full.loc[idx, final_df.columns] = final_df.loc[idx]
                df_full.at[idx, "flag"] = 1 if final_df.at[idx, "confirm_from_mkt"] else 0

        sheet = client.open_by_key("1w3bLxTdo00o0ZY7O3Kbrv3LJs6Enzzfbbjj24yWSMlY").worksheet(sheet_name)
        sheet.update([df_full.columns.tolist()] + df_full.astype(str).values.tolist())

        st.success("Confirmation status updated to Google Sheet!")

        log_all_terms(
            edited_df=final_df,
            user=st.session_state.user,
            sheet_id="1xORIj-ha6_yXddi-V_6nMNsxM8-A5imI6HSoPUPv9Aw",
            sheet_name="Jarvis Confirmation Log",
            service_account_info=st.secrets["gcp_service_account"]
        )

        total_confirmed = final_df[final_df["confirm_from_mkt"] == True].shape[0]
        total_unconfirmed = final_df[final_df["confirm_from_mkt"] == False].shape[0]
        user = st.session_state.user
        current_sheet = sheet.title

        filter_campaign = selected_campaign if selected_campaign != "All" else "All Campaigns"
        filter_adgroup = selected_adgroup if selected_adgroup != "All" else "All Adgroups"
        
        if isinstance(selected_date_range, (tuple, list)) and len(selected_date_range) == 2:
            date_range_str = f"{selected_date_range[0]} → {selected_date_range[1]}"
        else:
            date_range_str = "All Dates"
    
        msg = (
            f"📢 *Jarvis Confirmation Report*\n"
            f"👤 User: `{user}`\n"
            f"📄 Sheet: `{current_sheet}`\n"
            f"🏷️ Team: `{selected_team}`\n"
            f"🌎 Country: `{selected_country}`\n"
            f"📌 Campaign: `{filter_campaign}`\n"
            f"📌 Adgroup: `{filter_adgroup}`\n"
            f"📅 Date Range: `{date_range_str}`\n"
            f"✅ Confirmed: `{total_confirmed}`\n"
            f"❌ Not Confirmed: `{total_unconfirmed}`"
        )
        webhook_url = 'https://chat.googleapis.com/v1/spaces/AAQA4vfwkIw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=TyhGKT_IfWTpa8e5A2N2KlVvK-ZSpu4PMclPG2YmtXs'
        requests.post(webhook_url, json={"text": msg})

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
