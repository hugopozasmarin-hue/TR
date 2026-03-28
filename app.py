import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* --- GLOBAL --- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
    color: #111827;
}

/* --- SIDEBAR PRO --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A192F 0%, #020617 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

.field-title {
    color: #64FFDA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 18px;
}

/* --- INPUTS --- */
.stTextInput input,
.stNumberInput input {
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    padding: 10px !important;
}

.stSelectbox > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    padding: 5px !important;
}

.stSelectbox div[data-baseweb="select"] {
    color: #111827 !important;
}

div[data-baseweb="popover"] {
    background-color: white !important;
    border-radius: 10px !important;
}

/* --- BOTONES PREMIUM --- */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #0A192F, #1E3A8A);
    color: white;
    font-weight: 600;
    height: 50px;
    transition: all 0.25s ease;
    width: 100%;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px rgba(0,0,0,0.12);
}

/* --- TABS MODERNAS --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: #F1F5F9;
    border-radius: 10px;
    padding: 10px 18px;
    transition: 0.2s;
}

.stTabs [aria-selected="true"] {
    background: #0A192F !important;
    color: white !important;
}

/* --- CHAT & NEWS --- */
.news-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid #E5E7EB;
}

.bubble {
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA TERMINAL", "lang_lab": "Idioma", "cap": "Presupuesto", "risk_lab": "Riesgo", "ass_lab": "Ticker",
        "ticker_hint": "Un ticker es el código único de un activo (ej: AAPL para Apple). Es lo que identifica a la empresa en el mercado.",
        "btn": "ANALIZAR ACTIVO", "news_tab": "Noticias", "chat_tab": "Chat"
    },
    "English": {
        "title": "INVESTIA TERMINAL", "lang_lab": "Language", "cap": "Budget", "risk_lab": "Risk Profile", "ass_lab": "Asset Ticker",
        "ticker_hint": "A ticker is the unique code for an asset (e.g., AAPL for Apple). It identifies the company in the market.",
        "btn": "ANALYZE ASSET", "news_tab": "News", "chat_tab": "Chat"
    }
}

# --- IA FUNCTIONS (Mantenidas) ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"Act as a Senior Strategist. Ticker: {ticket}. Price: {p_act}. Risk: {perfil}."
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except: return "Error IA"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"

# --- SIDEBAR (CAMBIOS AQUÍ) ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()
    # MENSAJE DEBAJO DEL TICKER
    st.markdown(f'<p style="color: #94A3B8; font-size: 11px; margin-top: -10px;">{t["ticker_hint"]}</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    # BOTÓN MOVIDO AL SIDEBAR
    analyze_btn = st.button(t["btn"])

# --- UI PRINCIPAL ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F;'>{t['title']}</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([t["chat_tab"], t["news_tab"]])

with tab1:
    st.markdown('<div class="chat-container">Terminal activa. Configura los datos en el panel izquierdo.</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="news-card">Noticias financieras en tiempo real.</div>', unsafe_allow_html=True)

if analyze_btn:
    st.toast(f"Analizando {ticket}...")


