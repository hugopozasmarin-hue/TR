import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "tu_api_key_aqui" 

# --- DISEÑO CSS PROFESIONAL (MINIMALISTA BLANCO) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');

/* GLOBAL */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    background-color: #FFFFFF; 
    color: #1E293B;
}
.stApp { background-color: #FFFFFF; }

/* SIDEBAR MINIMALISTA */
[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
    padding-top: 2rem;
}
.field-title {
    color: #475569;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 1.2rem 0 0.4rem 0;
}
.ticker-hint {
    font-size: 0.75rem;
    color: #94A3B8;
    line-height: 1.4;
    margin-bottom: 8px;
}

/* TABS TIPO SEGMENTED CONTROL */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    background-color: #F1F5F9;
    padding: 4px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    margin-bottom: 2rem;
}
.stTabs [data-baseweb="tab"] {
    height: 38px;
    background-color: transparent !important;
    border: none !important;
    color: #64748B !important;
    font-weight: 500;
    border-radius: 8px !important;
    padding: 0 24px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* NOTICIAS & CARDS */
.news-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}
.news-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04);
}
.news-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 8px;
    text-decoration: none;
}

/* CHAT BUBBLES */
.chat-container { margin-top: 20px; }
.bubble {
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 0.95rem;
    max-width: 80%;
    margin-bottom: 10px;
    line-height: 1.5;
}
.user-bubble {
    background: #F1F5F9;
    color: #1E293B;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.ai-bubble {
    background: #0F172A;
    color: #FFFFFF;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

/* BOTONES */
.stButton>button {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    transition: 0.2s;
}
/* Botón principal Analizar */
[data-testid="stSidebar"] .stButton>button {
    background: #0F172A;
    color: white;
    width: 100%;
}
/* Botón Resumir (secundario) */
.news-card .stButton>button {
    background: #F8FAFC;
    color: #475569;
    border: 1px solid #E2E8F0;
    font-size: 0.8rem;
    height: 32px;
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Idioma",
        "cap": "Presupuesto",
        "risk_lab": "Riesgo",
        "ass_lab": "Símbolo Activo (Ticker)",
        "ticker_help": "Un **Ticker** es el código único de una empresa o activo. Ej: 'AAPL' para Apple o 'BTC-USD' para Bitcoin.",
        "btn": "ANALIZAR MERCADO",
        "news_tab": "Noticias",
        "chat_tab": "Terminal IA",
        "read_more": "Leer noticia original",
        "summarize": "🧠 Resumir con IA"
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Language",
        "cap": "Budget",
        "risk_lab": "Risk",
        "ass_lab": "Asset Ticker",
        "ticker_help": "A **Ticker** is a unique code for a company or asset. Ex: 'AAPL' for Apple or 'BTC-USD' for Bitcoin.",
        "btn": "ANALYZE MARKET",
        "news_tab": "News",
        "chat_tab": "AI Terminal",
        "read_more": "Read original news",
        "summarize": "🧠 AI Summary"
    }
}

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR (MODERNO & EDUCATIVO) ---
with st.sidebar:
    st.markdown(f"### 💎 InvestIA")
    
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
    st.markdown(f'<p class="ticker-hint">{t["ticker_help"]}</p>', unsafe_allow_html=True)
    ticker = st.text_input("", value="AAPL", label_visibility="collapsed").upper()

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button(t["btn"])

# --- CUERPO PRINCIPAL ---
st.markdown(f"<h1 style='font-weight:800; color:#0F172A; margin-bottom:0.5rem;'>{t['title']}</h1>", unsafe_allow_html=True)

# TABS REDISEÑADOS (TIPO NAVEGACIÓN SaaS)
tab1, tab2 = st.tabs([f"💬 {t['chat_tab']}", f"📰 {t['news_tab']}"])

with tab1:
    # Contenedor de Chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="bubble ai-bubble">Bienvenido a la terminal. Indica un activo para comenzar el análisis financiero.</div>', unsafe_allow_html=True)
    
    # Historial (Simulación estética)
    for msg in st.session_state.chat_history:
        clase = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input de chat fijo abajo (simulado)
    st.text_input("", placeholder="Pregunta sobre tendencias de mercado...", key="chat_in", label_visibility="collapsed")

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    # Ejemplo de Noticia con todas las funciones mantenidas
    for i in range(2):
        st.markdown(f"""
        <div class="news-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <a class="news-title" href="#">Las acciones de {ticker} muestran señales de rebote técnico</a>
                    <p style="color: #64748B; font-size: 0.9rem; margin-top: 8px;">
                        Análisis detallado sobre el comportamiento de los mercados globales y el impacto en los sectores tecnológicos...
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones de función (Mantenidos)
        c1, c2 = st.columns([1, 4])
        with c1:
            st.button(t["summarize"], key=f"sum_{i}")
        with c2:
            st.markdown(f"<small style='line-height:35px'><a href='#'>{t['read_more']}</a></small>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA DE FONDO (Sin cambios en tus funciones originales) ---
if analyze_btn:
    st.success(f"Analizando {ticker}...")

