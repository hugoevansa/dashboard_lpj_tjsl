import streamlit as st
import os

st.write("Isi folder project:")
st.write(os.listdir())

st.set_page_config(
    page_title="Test",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("MAIN PAGE")
