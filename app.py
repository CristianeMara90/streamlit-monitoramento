import requests, streamlit as st

st.write("Testando conexão com Google...")
r = requests.get("https://www.google.com", timeout=10)
st.write("Status:", r.status_code)
st.write("OK")
