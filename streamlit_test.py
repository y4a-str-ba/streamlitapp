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

# Input for the message
message = st.text_area("Message")

# Send button
if st.button("Send"):
    if message:
        url = urls[option]
        headers = {'Content-Type': 'application/json'}
        payload = {'text': message}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            st.success(f"Message sent to {option}: {message}")
        else:
            st.error(f"Failed to send message. Status code: {response.status_code}")
    else:
        st.warning("Please enter a message before sending.")