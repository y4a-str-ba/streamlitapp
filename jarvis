import streamlit as st
import pandas as pd

st.set_page_config(page_title="Jarvis Dashboard", layout="wide")

df = pd.read_csv("data/dummy_kill_list.csv")

st.title("Jarvis — Kill Search Terms")
st.write("These terms are identified as low-performing and should be reviewed before being negativized.")

if st.button("Confirm All"):
    df["Confirm"] = True
    st.success("All terms confirmed!")

st.dataframe(df)
