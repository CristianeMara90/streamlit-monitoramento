import time
import requests
import streamlit as st
import streamlit.components.v1 as components
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://script.google.com/macros/s/AKfycby9LfoWvstv9j5tVMnnYy0JEC0urTcrLlSYG1I1Z_OKooGDBojKEssjwRSQ8RTXb8E/exec"

st.set_page_config(page_title="Monitoramento — Visualização", page_icon="📊", layout="wide")

# =========================
# CSS (premium + mobile nav)
# =========================
st.markdown("""
<style>
:root{
  --bg1:#0b3c6f; --bg2:#041e3c;
  --glass: rgba(255,255,255,.08);
  --line: rgba(255,255,255,.14);
  --txt: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.70);

  --gradA:#7C3AED; --gradB:#2563EB; --gradC:#06B6D4;
  --ok:#16A34A; --warn:#F59E0B; --bad:#DC2626;
}

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1200px 700px at 20% 0%, rgba(255,255,255,.10), transparent 60%),
    radial-gradient(900px 600px at 90% 10%, rgba(255,255,255,.08), transparent 55%),
    linear-gradient(180deg, var(--bg1), var(--bg2)) !important;
}

.block-container{ padding-top: 1rem; padding-bottom: 6.8rem; }

.bigTitle{ font-size: 44px; font-weight: 1000; letter-spacing:.2px; margin:0; text-shadow: 0 18px 40px rgba(0,0,0,.25);}
.subTitle{ margin-top:.35rem; font-weight:850; opacity:.82; font-size:13px; color:var(--txt);}

.shell{
  max-width: 1250px; margin: 0 auto;
  border-radius: 28px; background: var(--glass);
  border: 1px solid var(--line);
  box-shadow: 0 28px 90px rgba(0,0,0,.35);
  overflow: hidden;
}
.shellInner{ padding: 16px; background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.06)); }

.footer{ max-width:1250px; margin:12px auto 0; color:rgba(255,255,255,.85); font-size:11px; font-weight:800; text-align:center; opacity:.9;}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(2,6,23,.34), rgba(2,6,23,.10)) !important;
  border-right: 1px solid rgba(255,255,255,.10) !important;
}
.sidebarBrand{
  display:flex; align-items:center; gap:10px;
  padding:12px; border-radius:18px;
  background: rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.14);
  box-shadow:0 16px 34px rgba(0,0,0,.25);
  margin-bottom:12px;
}
.sidebarBrand img{ width:46px; height:46px; border-radius:14px; object-fit:contain; background: rgba(255,255,255,.10); }
.sidebarBrandTxt b{ display:block; font-size:13px; letter-spacing:.2px; color:#fff; }
.sidebarBrandTxt span{ display:block; margin-top:4px; font-size:11px; opacity:.86; color:#fff; font-weight:800; }
.sidebarNote{
  margin-top:14px; padding:12px; border-radius:18px;
  background: rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.14);
  color: rgba(255,255,255,.88);
  font-size:11px; line-height:1.35; font-weight:850;
}

/* Mobile bottom nav */
.bottomNav{ display:none; }
@media (max-width: 900px){
  section[data-testid="stSidebar"]{ display:none; }
  .bottomNav{
    display:flex; position:fixed; left:0; right:0; bottom:0; z-index:9999;
    padding:10px; gap:8px;
    background: linear-gradient(180deg, rgba(2,6,23,.08), rgba(2,6,23,.45));
    border-top:1px solid rgba(255,255,255,.10);
    backdrop-filter: blur(10px);
  }
  .bottomNav a{
    flex:1 1 0; text-decoration:none; color:#0b1220;
    background: rgba(255,255,255,.92);
    border-radius: 16px; padding:10px; font-weight:1000;
    display:flex; align-items:center; justify-content:center; gap:8px;
    box-shadow: 0 12px 26px rgba(0,0,0,.20);
  }
  .bottomNav a.active{ color:#fff; background: linear-gradient(90deg,var(--gradA),var(--gradB),var(--gradC)); }
}
</style>
""", unsafe_allow_html=True)

# =========================
# HTTP
# =========================
def _session():
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

@st.cache_data(ttl=25)
def fetch(page: str):
    s = _session()
    params = {"page": page, "format": "json", "t": int(time.time())}
    r = s.get(URL, params=params, timeout=90)
    r.raise_for_status()
    return r.json()

# =========================
# HELPERS
# =========================
def safe_int(x, default=0):
    try:
        return int(x)
    except:
        return default

def pct(part, total):
    if total <= 0:
        return 0
    return int(round((part / total) * 100))

def alert_level(p):
    # Regras: >=85 verde; 70-84 amarelo; <70 vermelho
    if p >= 85:
        return ("Verde", "✅", "rgba(22,163,74,.22)")
    if p >= 70:
        return ("Amarelo", "⚠️", "rgba(245,158,11,.22)")
    return ("Vermelho", "🛑", "rgba(220,38,38,.22)")

def render_card_html(title, icon, subtitle_line, pills_html, total, responded, missing, p):
    lvl, lvl_icon, bg = alert_level(p)

    html = f"""
<div style="
  border-radius:22px; overflow:hidden;
  border:1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.10);
  box-shadow:0 24px 70px rgba(0,0,0,.30);
">
  <div style="
    padding:16px; color:#fff; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;
    background: linear-gradient(90deg, rgba(6,182,212,.20), rgba(37,99,235,.20), rgba(124,58,237,.20));
  ">
    <div>
      <div style="display:flex; align-items:center; gap:10px; font-weight:1000; font-size:18px;">
        <span style="
          background: rgba(255,255,255,.16);
          border:1px solid rgba(255,255,255,.18);
          padding:8px 10px; border-radius:16px; font-weight:1000;
          display:inline-flex; align-items:center; justify-content:center;
        ">{icon}</span>
        {title}
      </div>
      <div style="font-weight:850; font-size:12px; opacity:.92; margin-top:6px;">
        {subtitle_line}
      </div>
    </div>

    <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center; justify-content:flex-end;">
      <div style="
        padding:6px 10px; border-radius:999px; font-weight:1000; font-size:12px;
        border:1px solid rgba(255,255,255,.25);
        background:{bg};
      ">{lvl_icon} Alerta: {lvl}</div>

      {pills_html}
    </div>
  </div>

  <div style="padding:16px; background: rgba(255,255,255,.92); color:#0b1220;">
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <div style="padding:10px 12px; border-radius:16px; border:1px solid rgba(15,23,42,.10); background:#f1f5f9; font-weight:1000;">
        Total: {total}
      </div>
      <div style="padding:10px 12px; border-radius:16px; border:1px solid rgba(15,23,42,.10); background:#ecfeff; font-weight:1000;">
        Respondidos: {responded}
      </div>
      <div style="padding:10px 12px; border-radius:16px; border:1px solid rgba(15,23,42,.10); background:#fff1f2; font-weight:1000;">
        Faltantes: {missing}
      </div>
    </div>

    <div style="margin-top:12px; height:10px; border-radius:999px; overflow:hidden;
      background: rgba(15,23,42,.08); border:1px solid rgba(15,23,42,.10);">
      <div style="height:100%; width:{p}%; border-radius:999px;
        background: linear-gradient(90deg, #06B6D4, #2563EB, #7C3AED);">
      </div>
    </div>

    <div style="margin-top:8px; color:#5b6472; font-weight:850; font-size:12px;">
      Leitura rápida: quanto mais próximo de 100%, maior adesão ao formulário.
    </div>
  </div>
</div>
"""
    # Render 100% como HTML (não vaza como texto)
    components.html(html, height=290)

def render_top10(title, rows):
    with st.expander(title, expanded=False):
        if not rows:
            st.info("Sem dados ainda.")
            return
        for i, r in enumerate(rows, start=1):
            faltas = r.get("faltas", r.get("count", 0))
            atleta = r.get("atleta", "")
            st.write(f"**{i}. {atleta}** — {faltas} dia(s) faltando")

# =========================
# CARDS
# =========================
def render_card_rec(rec: dict):
    total = safe_int(rec.get("rosterCount", 0))
    missing_list = rec.get("missingToday", []) or []
    missing = safe_int(rec.get("missing", len(missing_list)))
    responded = safe_int(rec.get("responded", max(total - missing, 0)))
    p = pct(responded, total)

    pills = ""  # REC não precisa de pílula extra além do alerta geral
    render_card_html(
        title="Recuperação (Hoje)",
        icon="🧠",
        subtitle_line=f"% respondido: <b>{p}%</b>",
        pills_html=pills,
        total=total,
        responded=responded,
        missing=missing,
        p=p
    )

    with st.expander("👀 Ver faltantes (Recuperação)", expanded=False):
        q = st.text_input("Buscar atleta", "", key="q_rec")
        filt = [a for a in missing_list if q.strip().lower() in a.lower()] if q else missing_list
        if not filt:
            st.info("Nenhum atleta encontrado nesse filtro.")
        else:
            st.write(f"**{len(filt)}** faltante(s):")
            st.markdown("\n".join([f"- **{a}**" for a in filt]))

    render_top10("🏆 Top 10 faltantes mais recorrentes (últimos 7 dias) — Recuperação", rec.get("topMissing7d", []) or [])

def render_card_pse(pse: dict):
    k = pse.get("kpis", {}) or {}
    manha_ok = safe_int(k.get("pseManhaOk", 0))
    manha_f  = safe_int(k.get("pseManhaFalt", 0))
    tarde_ok = safe_int(k.get("pseTardeOk", 0))
    tarde_f  = safe_int(k.get("pseTardeFalt", 0))

    total_m = manha_ok + manha_f
    total_t = tarde_ok + tarde_f
    p_m = pct(manha_ok, total_m)
    p_t = pct(tarde_ok, total_t)

    # pílulas (manhã/tarde) no topo
    lvl_m, icon_m, bg_m = alert_level(p_m)
    lvl_t, icon_t, bg_t = alert_level(p_t)
    pills = f"""
      <div style="padding:6px 10px; border-radius:999px; font-weight:1000; font-size:12px; border:1px solid rgba(255,255,255,.25); background:{bg_m};">
        {icon_m} Manhã: {lvl_m} ({p_m}%)
      </div>
      <div style="padding:6px 10px; border-radius:999px; font-weight:1000; font-size:12px; border:1px solid rgba(255,255,255,.25); background:{bg_t};">
        {icon_t} Tarde: {lvl_t} ({p_t}%)
      </div>
    """

    # Para PSE, o "total/respondidos/faltantes" do card principal fica baseado no total do roster (manhã)
    # mas a leitura principal está nas pílulas manhã/tarde.
    total = max(total_m, total_t, manha_ok + manha_f)  # robusto
    # aqui não faz sentido "respondidos" agregado, então usamos o total do dia "qualquer resposta"
    missing_list = pse.get("missingToday", []) or []
    missing = len(missing_list)
    responded = max(total - missing, 0)
    p = pct(responded, total)  # só para barra geral (não é a leitura principal)

    render_card_html(
        title="PSE (Hoje)",
        icon="🔥",
        subtitle_line=f"% Manhã: <b>{p_m}%</b> • % Tarde: <b>{p_t}%</b>",
        pills_html=pills,
        total=total,
        responded=responded,
        missing=missing,
        p=p
    )

    # KPIs detalhados logo abaixo (sem HTML)
    st.markdown(
        f"""
<div style="margin-top:10px; padding:12px; border-radius:18px; background: rgba(255,255,255,.92); border:1px solid rgba(15,23,42,.10);">
  <div style="font-weight:1000; margin-bottom:8px;">Detalhe de contagem</div>
  <div style="display:flex; gap:10px; flex-wrap:wrap;">
    <div style="padding:8px 10px; border-radius:14px; background:#ecfeff; font-weight:1000;">Manhã OK: {manha_ok}</div>
    <div style="padding:8px 10px; border-radius:14px; background:#fff1f2; font-weight:1000;">Manhã faltou: {manha_f}</div>
    <div style="padding:8px 10px; border-radius:14px; background:#ecfeff; font-weight:1000;">Tarde OK: {tarde_ok}</div>
    <div style="padding:8px 10px; border-radius:14px; background:#fff1f2; font-weight:1000;">Tarde faltou: {tarde_f}</div>
  </div>
</div>
""",
        unsafe_allow_html=True
    )

    with st.expander("👀 Ver faltantes (PSE)", expanded=False):
        q = st.text_input("Buscar atleta", "", key="q_pse")
        filt = [a for a in missing_list if q.strip().lower() in a.lower()] if q else missing_list
        if not filt:
            st.info("Nenhum atleta encontrado nesse filtro.")
        else:
            st.write(f"**{len(filt)}** faltante(s):")
            st.markdown("\n".join([f"- **{a}**" for a in filt]))

    render_top10("🏆 Top 10 faltantes mais recorrentes (últimos 7 dias) — PSE", pse.get("topMissing7d", []) or [])

# =========================
# NAV (sidebar + bottom nav)
# =========================
qp = st.query_params
page = (qp.get("page", "home") or "home").lower()

st.sidebar.markdown("""
<div class="sidebarBrand">
  <img src="https://i.imgur.com/0HqQZ2a.png" />
  <div class="sidebarBrandTxt">
    <b>Relatório Diário</b>
    <span>Visualização</span>
  </div>
</div>
""", unsafe_allow_html=True)

sel = st.sidebar.radio("Menu", ["Home", "Recuperação", "PSE"], index={"home":0, "rec":1, "pse":2}.get(page, 0))
page = {"Home":"home", "Recuperação":"rec", "PSE":"pse"}[sel]

st.sidebar.markdown("""
<div class="sidebarNote">
<b>Dica:</b> no celular, o menu vira uma barra inferior.<br>
Use “Ver faltantes” + busca para achar atletas rápido.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="bottomNav">
  <a class="{ 'active' if page=='home' else '' }" href="?page=home">🏠 Home</a>
  <a class="{ 'active' if page=='rec' else '' }"  href="?page=rec">🧠 Recuperação</a>
  <a class="{ 'active' if page=='pse' else '' }"  href="?page=pse">🔥 PSE</a>
</div>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
colA, colB = st.columns([4,1])
with colA:
    st.markdown('<p class="bigTitle">Painel do Dia</p>', unsafe_allow_html=True)
    st.markdown('<div class="subTitle">Visão rápida de presença (Rec) e intensidade (PSE) com foco em decisão.</div>', unsafe_allow_html=True)
with colB:
    if st.button("↻ Atualizar"):
        st.cache_data.clear()

# =========================
# DATA
# =========================
data = fetch(page)

# Mostra erros do backend, se houver
if data.get("errorMsg"):
    st.error(data.get("errorMsg"))

st.markdown(f'<div class="footer">Atualizado em {data.get("lastUpdated","")}</div>', unsafe_allow_html=True)
st.markdown('<div class="shell"><div class="shellInner">', unsafe_allow_html=True)

# =========================
# CONTENT
# =========================
if page == "home":
    c1, c2 = st.columns(2)
    with c1:
        render_card_rec(data.get("rec", {}) or {})
    with c2:
        render_card_pse(data.get("pse", {}) or {})

elif page == "rec":
    st.markdown("### 🧠 Recuperação — Hoje")
    render_card_rec(data.get("rec", {}) or {})

elif page == "pse":
    st.markdown("### 🔥 PSE — Hoje")
    render_card_pse(data.get("pse", {}) or {})

st.markdown('</div></div>', unsafe_allow_html=True)
