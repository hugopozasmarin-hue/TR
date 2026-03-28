import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API (Asegúrate de usar variables de entorno en producción) ---
GROQ_API_KEY = "tu_api_key_aqui" 

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');

/* GLOBAL */
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0F172A; }
.stApp { background: radial-gradient(circle at top right, #1E293B, #0F172A); color: #F8FAFC; }

/* SIDEBAR REINVENTADO (Glassmorphism) */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
.sidebar-header {
    padding: 20px 0px;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 20px;
}
.field-title {
    color: #94A3B8;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.5rem 0;
}
.ticker-info {
    font-size: 0.7rem;
    color: #64748B;
    font-style: italic;
    margin-bottom: 10px;
}

/* TABS ESTILO NAVEGACIÓN MODERNA */
.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
    background-color: rgba(255,255,255,0.03);
    padding: 10px 20px;
    border-radius: 50px;
    border: 1px solid rgba(255,255,255,0.05);
    width: fit-content;
    margin: 0 auto 30px auto;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    background-color: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
    background: rgba(56, 189, 248, 0.1) !important;
    border-radius: 30px !important;
}

/* TARJETAS DE NOTICIAS */
.news-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}
.news-card:hover {
    border-color: #38BDF8;
    background: rgba(30, 41, 59, 0.8);
    transform: translateY(-2px);
}
.news-tag {
    background: #0EA5E9;
    color: white;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: bold;
}

/* CHAT PRO */
.chat-msg {
    padding: 15px 20px;
    border-radius: 20px;
    margin-bottom: 12px;
    max-width: 85%;
    line-height: 1.6;
}
.user-msg {
    background: #334155;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 2px;
}
.ai-msg {
    background: linear-gradient(135deg, #0284C7, #0369A1);
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 2px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* BOTÓN PREMIUM */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #38BDF8, #2563EB);
    border: none;
    color: white;
    font-weight: 700;
    padding: 12px;
    transition: 0.3s;
}
.stButton>button:hover {
    opacity: 0.9;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA ELITE",
        "lang_lab": "Idioma / Language",
        "cap": "Capital Disponible",
        "risk_lab": "Perfil de Riesgo",
        "ass_lab": "Símbolo (Ticker)",
        "ticker_help": "Ej: AAPL (Apple), BTC-USD (Bitcoin), TSLA (Tesla). Es el código único del activo.",
        "btn": "INICIAR ANÁLISIS PRO",
        "chat_tab": "Terminal IA",
        "news_tab": "Global News",
        "read_more": "Ver detalles",
        "news_sub": "Última hora en mercados financieros"
    },
    "English": {
        "title": "INVESTIA ELITE",
        "lang_lab": "Language / Idioma",
        "cap": "Available Capital",
        "risk_lab": "Risk Profile",
        "ass_lab": "Asset Ticker",
        "ticker_help": "Ex: AAPL (Apple), BTC-USD (Bitcoin). A unique code for market assets.",
        "btn": "START PRO ANALYSIS",
        "chat_tab": "AI Terminal",
        "news_tab": "Global News",
        "read_more": "Details",
        "news_sub": "Real-time global market updates"
    }
}

# --- ESTADO DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR REDISEÑADO ---
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h1>💎 InvestIA</h1></div>', unsafe_allow_html=True)
    
    # Selector de Idioma
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    
    t = languages[st.session_state.lang]
    
    # Inputs
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ticker-info">{t["ticker_help"]}</p>', unsafe_allow_html=True)
    ticker = st.text_input("", value="AAPL", label_visibility="collapsed").upper()
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button(t["btn"])

# --- CONTENIDO PRINCIPAL ---
st.markdown(f"<h2 style='text-align: center; letter-spacing: -1px; font-weight: 800;'>{t['title']}</h2>", unsafe_allow_html=True)

# TABS REDISEÑADOS
tab1, tab2 = st.tabs([f"📊 {t['chat_tab']}", f"🌍 {t['news_tab']}"])

with tab1:
    col_chat, col_info = st.columns([2, 1])
    
    with col_chat:
        st.markdown("<div style='height: 400px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
        # Simulación de historial
        st.markdown('<div class="chat-msg ai-msg">Hola. Analicemos el mercado. ¿Qué te gustaría saber sobre este activo hoy?</div>', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
             role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
             st.markdown(f'<div class="chat-msg {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.text_input("", placeholder="Pregunta a la IA sobre estrategias...", key="chat_input", label_visibility="collapsed")

    with col_info:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.03); border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,0.05)'>
            <h4 style='margin-top:0'>{ticker} Stats</h4>
            <p style='color: #94A3B8; font-size: 0.9rem'>Selecciona un ticker y haz clic en analizar para ver proyecciones avanzadas de Prophet y Groq.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown(f"### {t['news_sub']}")
    # Ejemplo de Card de Noticias Estética
    for i in range(3):
        st.markdown(f"""
        <div class="news-card">
            <span class="news-tag">MERCADOS</span>
            <h4 style='margin: 10px 0;'>Impacto del Tesoro en el rendimiento de {ticker}</h4>
            <p style='color: #94A3B8; font-size: 0.9rem;'>Los analistas sugieren una volatilidad alta para la próxima semana debido a los datos de inflación...</p>
            <a href='#' style='color: #38BDF8; text-decoration: none; font-weight: 600; font-size: 0.8rem;'>{t['read_more']} →</a>
        </div>
        """, unsafe_allow_html=True)

# --- LÓGICA DE ANALISIS (Para integrar con tus funciones de Yahoo Finance) ---
if analyze_btn:
    st.toast(f"Analizando {ticker}...", icon="🚀")
