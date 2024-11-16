import streamlit as st
from openai import OpenAI
import requests

def main(client):
    st.title("ChatGPT Page")

    user_question = st.text_area("Enter your question to ChatGPT:", height=150, key="user_question")

    st.markdown("""
    <style>
    .stButton>button {
        background-color: #00008B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("Ask ChatGPT"):
        if user_question.strip():
            try:                
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": user_question}
                    ]
                )
                response_dict = completion.model_dump()
                response_dict = response_dict['choices'][0]['message']['content']
                st.write(response_dict['choices'][0]['message']['content'])
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question before submitting.")
    
    st.markdown("<h3 style='color:#00008B;'>Send to Google Chat Groups</h3>", unsafe_allow_html=True)

    option = st.selectbox(
        'Choose a team to notify:',
        ('BI Test Group', 'SFO_FBP', 'SSO', 'FBP', 'ATLAS')
    )

    urls = st.secrets["urls"]
    group_url = urls[option.replace(" ", "_")]

    if option == 'SFO_FBP':
        response_dict += "\n\n---\nSFO FBP Support Agent"
    elif option == 'SSO':
        response_dict += "\n\n---\nSSO Support Agent"
    elif option == 'FBP':
        response_dict += "\n\n---\nFBP Support Agent"
    elif option == 'ATLAS':
        response_dict += "\n\n---\nATLAS Support Agent"
    elif option == 'BI Test Group':
        response_dict += "\n\n---\nBI Test Group Support Agent"

    #preview the response
    st.markdown("<h3 style='color:#00008B;'>ChatGPT Response Preview</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:green;'>{response_dict}</span>", unsafe_allow_html=True)
        
    if st.button("Send to Google Chat"):
        if group_url:
            try:
                send_to_google_chat(group_url, response_dict)
                st.success("Message sent to Google Chat group successfully!")
            except Exception as e:
                st.error(f"An error occurred while sending the message: {e}")
        else:
            st.warning("Please select a valid Google Chat Group.")

def send_to_google_chat(group_url, message):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }
    data = {
        'text': message
    }
    response = requests.post(group_url, headers=headers, json=data)
    response.raise_for_status()
