import streamlit as st
from openai import OpenAI
import requests

def main(client):
    st.title("ChatGPT Page")

    user_question = st.text_area("Enter your question to ChatGPT:", height=150, key="user_question")

    response_dict = ''

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

    if response_dict:
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

    st.write("Debug: response_dict before button click:", response_dict)
 
    if st.button("Send to Google Chat"):
        st.write("Debug: response_dict inside button click:", response_dict)
        if response_dict:
            headers = {'Content-Type': 'application/json'}
            payload = {'text': response_dict.replace('\n', '\n')}

            st.write("Payload: ", payload)
            
            response = requests.post(group_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                st.success("Message sent successfully!")
            else:
                st.error(f"Failed to send message. Status code: {response.status_code}")
        else:
            st.warning("Please enter a question before submitting.")

