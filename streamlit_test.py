import streamlit as st
import requests
import json

st.image("logo.png", width=200)

with open('secret.json') as f:
    secrets = json.load(f)

def authenticate(username, password):
    if username == secrets["username"] and password == secrets["password"]:
        return True
    return False

# Initialize session state for authentication status
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'login_attempted' not in st.session_state:
    st.session_state.login_attempted = False

# Login form
if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        st.session_state.login_attempted = True  # Mark that a login attempt was made
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Authentication failed. Please check your credentials.")

# Check if login was attempted to control app flow
if st.session_state.authenticated:
    # App Title with Icon
    st.title("📢 BI Support Agent")
    st.success(f'Welcome {st.session_state.username}')

    # Columns for layout
    col1, col2 = st.columns(2)

    # Select Group Chat Dropdown
    with col1:
        st.subheader("Select Group Chat")
        option = st.selectbox(
            'Choose a team to notify:',
            ('BI Test Group', 'SFO', 'SSO', 'ATLAS')
        )

    # Define the URLs
    urls = {
        'BI Test Group': 'https://chat.googleapis.com/v1/spaces/AAAAIw-NZNo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=zoRXSSFeY4z_4PJKaQ53kDQ08EnVJwtWT6uAs8QIDfU',
        'SSO': 'https://example.com/sso',
        'SFO': 'https://example.com/sfo',
        'ATLAS': 'https://chat.googleapis.com/v1/spaces/AAAAD_qzkDY/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=XhmSpWmA7S9mkt4Tys6l8NPzddzNONGw4mK57VR_AG0'
    }

    # Message Importance Dropdown
    with col2:
        st.subheader("Select Urgency Level")
        urgency = st.selectbox(
            'Set urgency level for the message:',
            ('🚨 High','⚠️ Medium','ℹ️ Low')
        )

    urgency_text = urgency.split(' ')[1]

    # Sample Messages
    sample_messages = [
        "🔧 Dear Team,\n\nWe have encountered some issues with the dashboard.\nOur technical team is currently investigating the matter and will provide updates shortly.\nThank you for your understanding.",
        "🛠️ Hello Team,\n\nPlease be informed that the dashboard will undergo scheduled maintenance.\nWe expect it to be back online shortly.\nWe appreciate your patience during this time.",
        "🚨 Team,\n\nWe are aware of some performance issues affecting the dashboard.\nOur team is actively working to identify and resolve the root cause.\nWe will keep you updated on our progress.",
        "🔍 Attention Team,\n\nWe are monitoring the system's performance and have noted some irregularities.\nOur team is dedicated to resolving any issues promptly.\nThank you for your cooperation.",
        "⏳ Dear Team,\n\nWe are currently experiencing a temporary service disruption with the dashboard.\nOur team is working diligently to restore full functionality as soon as possible.\nWe appreciate your patience.",
        "📊 Dear SFO MKT Team,\n\nPlease be advised that there is an unusual delay in our data source update, causing a lag in real-time data availability. Our team is actively investigating the issue and working on a resolution.\n\nIn the meantime, for monitoring and performance insights, please refer to the YAMS or Hourly Dashboard.\n\nThank you for your patience and understanding.\n\nBest regards,"

    ]

    message = st.text_area("Customize Your Message", height=150, key="custom_message")

    # Select Group Content Dropdown
    st.subheader("Select Group Content")
    group_content = st.selectbox(
        'Choose the content type:',
        ('Issue Notification', 'Maintenance Notice', 'Performance Issue', 'Performance Alert', 'Service Disruption', 'Data Delay Notice')
    )

 # Define the messages based on Group Content
    messages = {
        'Issue Notification': [
            "🔧 Dear Team,\n\nWe have encountered some issues with the dashboard and our technical team is actively investigating the matter.\nWe are working to resolve this as quickly as possible and will provide updates as soon as they are available.\n\nThank you for your patience and understanding during this time,\nBI Team",
            "🛠️ Dear Team,\n\nPlease be informed that the dashboard will undergo scheduled maintenance.\n\nWe expect it to be back online shortly and will inform you once it’s available.\nThank you for your patience and understanding during this time,\nBI Team"
        ],
        'Maintenance Notice': [
            "🛠️ Dear Team,\n\nPlease be informed that the dashboard will undergo scheduled maintenance.\n\nWe expect it to be back online shortly and will inform you once it’s available.\nThank you for your patience and understanding during this time,\nBI Team"
        ],
        'Performance Issue': [
            "🚨 Dear Team,\n\nWe are aware of some performance issues affecting the dashboard.\nOur team is actively working to identify and resolve the root cause.\nWe will keep you updated on our progress."
        ],
        'Performance Alert': [
            "🔍 Attention Team,\n\nWe are monitoring the system's performance and have noted some irregularities.\nOur team is dedicated to resolving any issues promptly.\nThank you for your cooperation."
        ],
        'Service Disruption': [
            "⏳ Dear Team,\n\nWe are currently experiencing a temporary service disruption with the dashboard.\nOur team is working diligently to restore full functionality as soon as possible.\nWe appreciate your patience."
        ],
        'Data Delay Notice': [
            "📊 Dear SFO MKT Team,\n\nPlease be advised that there is an unusual delay in our data source update, causing a lag in real-time data availability. Our team is actively investigating the issue and working on a resolution.\n\nIn the meantime, for monitoring and performance insights, please refer to the YAMS or Hourly Dashboard.\n\nThank you for your patience and understanding.\n\nBest regards,"
        ]
    }

    # Sample Message Dropdown, Disabled if Custom Message is Entered
    if message:
        sample_message = st.selectbox('Select a sample message (optional)', messages[group_content], disabled=True)
    else:
        sample_message = st.selectbox('Select a sample message (optional)', messages[group_content])

    # Combine Messages for Preview
    urgency_icon = {
        'High': '🚨',
        'Medium': '⚠️',
        'Low': 'ℹ️'
    }

    # Combine Messages for Preview
    final_message = f"{urgency_icon[urgency_text]} Urgency: {urgency_text}\n\n" + (message if message else messages[group_content])

    if option == 'SFO':
        final_message += "\n\n---\nSFO Support Agent"
    elif option == 'SSO':
        final_message += "\n\n---\nSSO Support Agent"
    elif option == 'ATLAS':
        final_message += "\n\n---\nATLAS Support Agent"
    elif option == 'BI Test Group':
        final_message += "\n\n---\nBI Test Group Support Agent"

    # Dynamic Preview Section
    st.subheader("Message Preview")
    if urgency == 'High':
        st.markdown(f"<span style='color:red;'>{final_message}</span>", unsafe_allow_html=True)
    elif urgency == 'Medium':
        st.markdown(f"<span style='color:orange;'>{final_message}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:green;'>{final_message}</span>", unsafe_allow_html=True)

    # Send Notification Button
    if st.button("Send Notification"):
        if final_message:
            url = urls[option]
            headers = {'Content-Type': 'application/json'}
            payload = {'text': final_message.replace('\n', '\n')}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                st.success("Message sent successfully!")
            else:
                st.error(f"Failed to send message. Status code: {response.status_code}")
        else:
            st.warning("Please enter a message or select a sample message before sending.")
