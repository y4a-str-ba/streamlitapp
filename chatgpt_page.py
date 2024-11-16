import streamlit as st
from openai import OpenAI

def main():
    api_key = st.secrets["openai"]
    API_KEY = api_key["api_key"]
    client = OpenAI(api_key=API_KEY)

    st.title("ChatGPT Page")

    user_question = st.text_area("Enter your question to ChatGPT:", height=150, key="user_question")

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

                # Show the response to the user
                st.markdown("<h3 style='color:#00008B;'>ChatGPT Response</h3>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:green;'>{response}</span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question before submitting.")

if __name__ == "__main__":
    main()

