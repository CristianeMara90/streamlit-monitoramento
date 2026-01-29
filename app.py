import streamlit as st
import requests

WEBAPP_URL = "COLE_AQUI_O_LINK_DO_SEU_/exec"

st.title("Envio PSE → Google Sheets")

with st.form("pse"):
    atleta = st.text_input("Atleta")
    pse = st.slider("PSE", 0, 10, 5)
    turno = st.selectbox("Turno", ["Manhã", "Tarde"])
    obs = st.text_area("Observações")
    enviar = st.form_submit_button("Enviar")

if enviar:
    payload = {"tipo": "pse", "atleta": atleta, "pse": pse, "turno": turno, "obs": obs}
    r = requests.post(WEBAPP_URL, json=payload, timeout=20)
    st.write(r.json())
