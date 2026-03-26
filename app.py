import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# --- CONFIGURACIÓN Y TÍTULO ACTUALIZADO ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
/* ... (mantenemos tu CSS original) ... */
.field-title { color: #818cf8; font-size: 10px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-top: 25px; margin-bottom: 8px; display: block; opacity: 0.9; border-bottom: 1px solid rgba(129, 140, 248, 0.2); padding-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO ACTUALIZADO CON InvestIA Y TICKER ---
languages = {
    "Español": {"title":"InvestIA Elite","ajust":"⚙️ AJUSTES","lang_lab":"IDIOMA",
                "cap":"PRESUPUESTO TOTAL","risk_lab":"PERFIL DE RIESGO",
                "ass_lab":"ACTIVO (INTRODUCIR TICKER - Ej: AAPL, BTC-USD)",
                "btn":"EJECUTAR ANÁLISIS","diag":"Consultoría Estratégica","just":"Justificación Técnica",
                "wait":"Analizando Big Data...","price":"Precio actual","target":"Precio predicho (30 días)",
                "shares":"Acciones comprables","disclaimer":"Simulación InvestIA 2026. Riesgo de capital."},
    "English": {"title":"InvestIA Elite","ajust":"⚙️ SETTINGS","lang_lab":"LANGUAGE",
                "cap":"TOTAL BUDGET","risk_lab":"RISK PROFILE",
                "ass_lab":"ASSET (ENTER TICKER - e.g., AAPL, BTC-USD)",
                "btn":"EXECUTE ANALYSIS","diag":"Strategic Consultancy","just":"Technical Justification",
                "wait":"Analyzing Big Data...","price":"Current Price","target":"Predicted Price (30d)",
                "shares":"Shares to Buy","disclaimer":"InvestIA 2026 Simulation. Capital risk."},
    "Català": {"title":"InvestIA Elite","ajust":"⚙️ AJUSTOS","lang_lab":"IDIOMA",
               "cap":"PRESSUPOST TOTAL","risk_lab":"PERFIL DE RISC",
               "ass_lab":"ACTIU (INTRODUIR TICKER - Ex: AAPL, BTC-USD)",
               "btn":"EXECUTAR ANÀLISI","diag":"Consultoria Estratègica","just":"Justificació Tècnica",
               "wait":"Analitzant Big Data...","price":"Preu actual","target":"Preu previst (30d)",
               "shares":"Accions a comprar","disclaimer":"Simulació InvestIA 2026. Risc de capital."}
}

# ... (inicialización de session_state igual) ...

# BARRA LATERAL
with st.sidebar:
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", ["Español","English","Català"], index=0)
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador","Moderado","Arriesgado"])

    # --- CAMBIO CLAVE: INSTRUCCIÓN DE TICKER ---
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL", placeholder="Ej: NVDA, TSLA, BTC-USD").upper().strip()

def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    # Nota: He actualizado el nombre del bot en el prompt del sistema
    api_key = "TU_API_KEY_AQUI" 
    client = Groq(api_key=api_key)
    prompt = f"Eres InvestIA (2026). Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
    # ... resto de la lógica de la función ...
