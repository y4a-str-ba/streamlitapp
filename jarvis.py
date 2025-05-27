
import streamlit as st
import hashlib
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import gspread
import requests
from google.oauth2.service_account import Credentials

# 🛑 This line MUST be the first Streamlit command
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

# ===================== LOGIN PAGE =====================
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
