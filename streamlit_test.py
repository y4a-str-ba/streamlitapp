import streamlit as st
import requests
import json
import toml

st.image("logo.png", width=200)

secrets = st.secrets["auth"]

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
    st.markdown("<h1 style='color:#00008B;'>📢 BI Support Agent</h1>", unsafe_allow_html=True)
    st.success(f'Welcome {st.session_state.username}')
    
    # Columns for layout
    col1, col2 = st.columns(2)

    # Select Group Chat Dropdown
    with col1:
        st.markdown("<h3 style='color:#00008B;'>Select Group Chat</h3>", unsafe_allow_html=True)
        option = st.selectbox(
            'Choose a team to notify:',
            ('BI Test Group', 'SFO_FBP', 'SSO', 'FBP', 'ATLAS')
        )

    urls = st.secrets["urls"]

    # Message Importance Dropdown
    with col2:
        st.markdown("<h3 style='color:#00008B;'>Select Urgency Level</h3>", unsafe_allow_html=True)
        urgency = st.selectbox(
            'Set urgency level for the message:',
            ('Set Urgency Level', '🚨 High', '⚠️ Medium', 'ℹ️ Low'),
            index=0
        )

    urgency_text = urgency.split(' ')[1] if urgency != 'Select Urgency Level' else None

    message = st.text_area("Customize Your Message", height=150, key="custom_message")

    # Select Group Content Dropdown
    st.markdown("<h3 style='color:#00008B;'>Select Group Content</h3>", unsafe_allow_html=True)

    group_content = st.selectbox(
        'Choose the content type:',
        ('Issue Notification'
         , 'Maintenance Notice'
         , 'Performance Issue'
         , 'Performance Alert'
         , 'Service Disruption'
         , 'Data Delay Notice'
         , 'Issue Resolved Notice'
         , 'Welcome Message'
         , 'Out of Office Notice'
         , 'Dashboard Updated')
    )

    # Define the messages based on Group Content
    messages = {
        'Issue Notification': [
            "🔧 Dear Team,\n\n"
            "We have acknowledged your current issue and our technical team is actively investigating the matter.\n\n"
            "We are working to resolve this quickly and will provide updates as soon as they are available.\n\n"
            "To assist us in addressing the issue more effectively, please provide the following information:\n\n"
            "\t- Dashboard name\n\n"
            "\t- Dashboard link\n\n"
            "\t- Filters currently applied\n\n"
            "\t- Specific details about the issue\n\n"
            "Thank you for your patience and understanding during this time"
        ],
        'Maintenance Notice': [
            "🛠️ Dear Team,\n\nPlease be informed that the dashboard will undergo scheduled maintenance.\n\nWe expect it to be back online shortly and will inform you once it’s available.\n\nThank you for your patience and understanding during this time,"
        ],
        'Performance Issue': [
            "🚨 Dear Team,\n\nWe are currently aware of performance issues impacting the dashboard. Our team is actively investigating the root cause and working toward a resolution.\n\nWe will keep you updated on our progress.\n\nThank you for your patience and understanding during this time,"
        ],
        'Performance Alert': [
            "🔍 Attention Team,\n\nWe are actively monitoring the system's performance and have detected some irregularities. Our team is dedicated to addressing these issues as quickly as possible.\n\nThank you for your patience and understanding during this time,"
        ],
        'Service Disruption': [
            "⏳ Dear Team,\n\nWe are currently experiencing a temporary service disruption with the dashboard.\nOur team is working diligently to restore full functionality as soon as possible.\n\nThank you for your patience and understanding during this time,"
        ],
        'Data Delay Notice': [
            "📊 Dear Team,\n\nPlease be advised that there is an unusual delay in our data source update, causing a lag in real-time data availability. Our team is actively investigating the issue and working on a resolution.\n\nIn the meantime, for monitoring and performance insights, please refer to the YAMS or Hourly Dashboard.\n\nThank you for your patience and understanding during this time,"
        ],
        'Issue Resolved Notice': [
            "👌 Dear Team,\n\nWe are pleased to inform you that the reported issue has been resolved. Our technical team has identified and addressed the underlying cause, and the dashboard/report should now be functioning as expected.\n\nPlease verify the functionality on your end, and let us know if you experience any further issues.\n\nThank you for your cooperation and patience throughout this process.\n\nBest regards,"
        ],
        'Welcome Message': [
                "👋 Dear Team,\n\n"
                "Welcome to the Support Agent service. Our team is here to assist you with any issues or questions you may have regarding the dashboard.\n\n"
                "Please feel free to reach out to us at any time. We are committed to providing you with the best support possible.\n\n"
                "Thank you for choosing our service.\n\n"
                "Best regards,"
            ],
        'Out of Office Notice': [
            "Hello! Our Support Agent is currently unavailable, as we are outside of office hours. Please feel free to leave your questions here, and we’ll be happy to assist you when we’re back tomorrow. Thank you for your patience!"
        ],
        'Dashboard Updated': [
            "📊 Dear Team,\n\n"
            "The dashboard has been updated. Please take a moment to review the latest data. If you notice any issues or have any concerns, feel free to reach out.\n\n"
            "Best regards,"
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
        'Low': 'ℹ️',
        'None': ''
    }
    # Combine Messages for Preview
    if urgency_text:
        urgency_icon = urgency_icon.get(urgency_text, '')
        final_message = f"{urgency_icon} Urgency: {urgency_text}\n\n" + (message if message else sample_message)
    else:
        final_message = message if message else sample_message

    if option == 'SFO_FBP':
        final_message += "\n\n---\nSFO FBP Support Agent"
    elif option == 'SSO':
        final_message += "\n\n---\nSSO Support Agent"
    elif option == 'FBP':
        final_message += "\n\n---\nFBP Support Agent"
    elif option == 'ATLAS':
        final_message += "\n\n---\nATLAS Support Agent"
    elif option == 'BI Test Group':
        final_message += "\n\n---\nBI Test Group Support Agent"

    # Dynamic Preview Section
    st.markdown("<h3 style='color:#00008B;'>Message Preview</h3>", unsafe_allow_html=True)
    if urgency == 'High':
        st.markdown(f"<span style='color:red;'>{final_message}</span>", unsafe_allow_html=True)
    elif urgency == 'Medium':
        st.markdown(f"<span style='color:orange;'>{final_message}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:green;'>{final_message}</span>", unsafe_allow_html=True)

    # Custom CSS for the button
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #00008B;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # Send Notification Button
    if st.button("Send Notification"):
        if final_message:
            url = urls[option.replace(" ", "_")]
            headers = {'Content-Type': 'application/json'}
            payload = {'text': final_message.replace('\n', '\n')}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                st.success("Message sent successfully!")
            else:
                st.error(f"Failed to send message. Status code: {response.status_code}")
        else:
            st.warning("Please enter a message or select a sample message before sending.")
