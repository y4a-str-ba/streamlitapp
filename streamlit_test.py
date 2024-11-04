import streamlit as st
import requests
import json

# App Title with Icon
st.title("📢 AI Support Agent")

# Columns for layout
col1, col2 = st.columns(2)

# Select Group Chat Dropdown
with col1:
    st.subheader("Select Group Chat")
    option = st.selectbox(
        'Choose a team to notify:',
        ('SFO', 'SSO')
    )

# Define the URLs
urls = {
    'SFO': 'https://chat.googleapis.com/v1/spaces/AAAAIw-NZNo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=zoRXSSFeY4z_4PJKaQ53kDQ08EnVJwtWT6uAs8QIDfU',
    'SSO': 'https://example.com/sso'
}

# Message Importance Dropdown
with col2:
    st.subheader("Select Urgency Level")
    urgency = st.selectbox(
        'Set urgency level for the message:',
        ('High', 'Medium', 'Low')
    )

# Sample Messages
sample_messages = [
    "⚠️ We are experiencing dashboard issues; the team is working on it.",
    "🛠️ Dashboard is under maintenance; back online shortly.",
    "🔍 We are investigating performance issues. Thanks for your patience."
]

message = st.text_area("Customize Your Message", height=150, key="custom_message")

# Sample Message Dropdown, Disabled if Custom Message is Entered
if message:
    sample_message = st.selectbox('Select a sample message (optional)', sample_messages, disabled=True)
else:
    sample_message = st.selectbox('Select a sample message (optional)', sample_messages)

# Combine Messages for Preview
final_message = message if message else sample_message

# Dynamic Preview Section
st.subheader("Message Preview")
if urgency == 'High':
    st.markdown(f"<span style='color:red;'>{final_message}</span>", unsafe_allow_html=True)
elif urgency == 'Medium':
    st.markdown(f"<span style='color:orange;'>{final_message}</span>", unsafe_allow_html=True)
else:
    st.markdown(f"<span style='color:green;'>{final_message}</span>", unsafe_allow_html=True)

# Urgency Colors and Button Actions
if st.button("Send Notification"):
    if message or sample_message:
        url = urls[option]
        headers = {'Content-Type': 'application/json'}
        final_message = f"**Urgency**: {urgency}\n\n{message if message else sample_message}"
        payload = {'text': final_message}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Display Success or Error Message
        if response.status_code == 200:
            st.success(f"Message sent to {option}: {message if message else sample_message}")
        else:
            st.error(f"Failed to send message. Status code: {response.status_code}")
    else:
        st.warning("Please enter a message or select a sample message before sending.")