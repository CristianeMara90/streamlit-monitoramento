import streamlit as st
import requests

URL = "https://script.google.com/macros/s/AKfycby9LfoWvstv9j5tVMnnYy0JEC0urTcrLlSYG1I1Z_OKooGDBojKEssjwRSQ8RTXb8E/exec?page=home&format=json"

params = {
    "page": "home",
    "format": "json"
}

st.title("Monitoramento — Visualização")

with st.spinner("Buscando dados..."):
    r = requests.get(URL, params=params, timeout=30)

st.write("Status:", r.status_code)

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
