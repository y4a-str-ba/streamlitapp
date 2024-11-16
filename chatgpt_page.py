import streamlit as st
from openai import OpenAI

def main():
    api_key = st.secrets["openai"]["api_key"]
    client = OpenAI(api_key=api_key)

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
    response = ''
    if st.button("Ask ChatGPT"):
        if user_question.strip():
            try:                
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": user_question}
                    ]
                )
                response = completion['choices'][0].message.content
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question before submitting.")
    
    if response:
        #preview the response
        st.markdown("<h3 style='color:#00008B;'>ChatGPT Response Preview</h3>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:green;'>{response}</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

