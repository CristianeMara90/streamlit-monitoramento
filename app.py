import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://script.google.com/macros/s/AKfycby9LfoWvstv9j5tVMnnYy0JEC0urTcrLlSYG1I1Z_OKooGDBojKEssjwRSQ8RTXb8E/exec"

@st.cache_data(ttl=30)
def fetch(page="home"):
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    params = {"page": page, "format": "json", "t": int(__import__("time").time())}
    r = session.get(URL, params=params, timeout=90)
    r.raise_for_status()
    return r.json()

st.title("Monitoramento — Visualização")

data = fetch("home")

st.caption(f'Atualizado em: {data.get("lastUpdated","")}')

# REC
st.subheader("Recuperação")
st.metric("Total atletas", data["rec"]["rosterCount"])
st.metric("Respondidos hoje", data["rec"]["responded"])
st.metric("Faltantes hoje", data["rec"]["missing"])

# PSE
st.subheader("PSE")
k = data["pse"]["kpis"]
st.metric("Manhã OK", k["pseManhaOk"])
st.metric("Manhã faltou", k["pseManhaFalt"])
st.metric("Tarde OK", k["pseTardeOk"])
st.metric("Tarde faltou", k["pseTardeFalt"])
