import streamlit as st
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://script.google.com/macros/s/AKfycby9LfoWvstv9j5tVMnnYy0JEC0urTcrLlSYG1I1Z_OKooGDBojKEssjwRSQ8RTXb8E/exec"

st.set_page_config(page_title="Monitoramento", layout="wide")
st.title("📊 Monitoramento — Visualização")

# --- Sidebar
page = st.sidebar.radio("Página", ["Home", "PSE", "Recuperação"], index=0)
page_key = {"Home": "home", "PSE": "pse", "Recuperação": "rec"}[page]

auto_refresh = st.sidebar.checkbox("Atualizar ao abrir", value=True)
if st.sidebar.button("🔄 Atualizar agora"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=60)  # cache por 60s
def fetch_payload(page_key: str):
    url = f"{BASE_URL}?page={page_key}&format=json"
    r = requests.get(url, timeout=25)
    r.raise_for_status()
    return r.json()

if auto_refresh:
    try:
        data = fetch_payload(page_key)
    except Exception as e:
        st.error("Não consegui carregar os dados do Apps Script.")
        st.caption("Verifique se o Web App está acessível como 'Qualquer pessoa com o link' e se a URL com format=json abre no navegador.")
        st.code(str(e))
        st.stop()
else:
    st.info("Marque 'Atualizar ao abrir' ou clique em 'Atualizar agora' no menu lateral.")
    st.stop()

# --- Header info
last = data.get("lastUpdated")
st.caption(f"Fonte: Apps Script | Página: {page_key} | lastUpdated: {last}")

if data.get("errorMsg"):
    st.warning(data["errorMsg"])

# ------------------------
# HOME: PSE + REC
# ------------------------
def render_pse_block(pse):
    st.subheader("PSE — Hoje")

    k = pse.get("kpis", {}) or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Manhã OK", k.get("pseManhaOk", 0))
    c2.metric("Manhã faltando", k.get("pseManhaFalt", 0))
    c3.metric("Tarde OK", k.get("pseTardeOk", 0))
    c4.metric("Tarde faltando", k.get("pseTardeFalt", 0))

    df = pd.DataFrame(pse.get("pseRows", []) or [])
    if df.empty:
        st.info("Sem dados de PSE para hoje.")
        return

    busca = st.text_input("Buscar atleta (PSE)", "")
    if busca.strip():
        df = df[df["atleta"].str.contains(busca, case=False, na=False)]

    st.dataframe(df, use_container_width=True, hide_index=True)

    falt = pse.get("pseMissingToday", []) or []
    with st.expander(f"Faltantes (PSE) — {len(falt)}"):
        st.write(falt)

def render_rec_block(rec):
    st.subheader("Recuperação — Hoje")

    df = pd.DataFrame(rec.get("rowsToday", []) or [])
    if df.empty:
        st.info("Sem dados de recuperação para hoje.")
    else:
        busca = st.text_input("Buscar atleta (Recuperação)", "")
        if busca.strip():
            df = df[df["atleta"].str.contains(busca, case=False, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    falt = rec.get("missingToday", []) or []
    with st.expander(f"Faltantes (Recuperação) — {len(falt)}"):
        st.write(falt)

# Render por página
if page_key == "home":
    colA, colB = st.columns([1, 1], gap="large")
    with colA:
        render_pse_block(data.get("pse", {}) or {})
    with colB:
        render_rec_block(data.get("rec", {}) or {})

elif page_key == "pse":
    render_pse_block(data.get("pse", {}) or {})

elif page_key == "rec":
    render_rec_block(data.get("rec", {}) or {})
