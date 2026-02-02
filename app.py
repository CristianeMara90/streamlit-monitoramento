import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://script.google.com/macros/s/AKfycby9LfoWvstv9j5tVMnnYy0JEC0urTcrLlSYG1I1Z_OKooGDBojKEssjwRSQ8RTXb8E/exec"

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1.2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

params = {"page":"home", "format":"json"}

r = session.get(URL, params=params, timeout=90)  # ✅ 90s
r.raise_for_status()
data = r.json()

st.write("Atualizado em:", data["lastUpdated"])

# REC
st.subheader("Recuperação")
st.metric("Total atletas", data["rec"]["rosterCount"])
st.metric("Faltantes hoje", len(data["rec"]["missingToday"]))

# PSE
st.subheader("PSE")
st.metric("Manhã OK", data["pse"]["kpis"]["pseManhaOk"])
st.metric("Manhã faltou", data["pse"]["kpis"]["pseManhaFalt"])
st.metric("Tarde OK", data["pse"]["kpis"]["pseTardeOk"])
st.metric("Tarde faltou", data["pse"]["kpis"]["pseTardeFalt"])
