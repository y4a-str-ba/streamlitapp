import streamlit as st
import requests
import json

# Title of the app
st.title("Notify Group Chat")

# Dropdown list for SFO and SSO
option = st.selectbox(
    'Select Group Chat',
    ('SFO', 'SSO')
)

# Define the URLs
urls = {
    'SFO': 'https://chat.googleapis.com/v1/spaces/AAAAIw-NZNo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=zoRXSSFeY4z_4PJKaQ53kDQ08EnVJwtWT6uAs8QIDfU',
    'SSO': 'https://example.com/sso'
}

# Professional sample messages
sample_messages = [
    "We are currently experiencing issues with the dashboard. Our team is actively working to resolve the problem.",
    "The dashboard is undergoing maintenance. We expect it to be back online shortly.",
    "We have identified performance issues with the dashboard and are investigating the cause. Thank you for your patience."
]

# Dropdown for sample messages
sample_message = st.selectbox(
    'Select a sample message (optional)',
    sample_messages
)

# Input for the message
message = st.text_area("Message")

# Send button
if st.button("Send"):
    if message or sample_message:
        url = urls[option]
        headers = {'Content-Type': 'application/json'}
        payload = {'text': message if message else sample_message}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            st.success(f"Message sent to {option}: {message if message else sample_message}")
        else:
            st.error(f"Failed to send message. Status code: {response.status_code}")
    else:
        st.warning("Please enter a message or select a sample message before sending.")