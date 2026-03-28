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

# --- ESTILOS CSS PROFESIONALES (Minimalismo Blanco & Premium) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');

/* GLOBAL */
html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    background-color: #FFFFFF;
}
.stApp { background-color: #FFFFFF; color: #1E293B; }

/* SIDEBAR REFINADO */
[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
    border-right: 1px solid #F1F5F9 !important;
}
.sidebar-logo {
    font-weight: 800;
    font-size: 1.5rem;
    color: #0F172A;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.field-label {
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}
.ticker-info-box {
    background: #F1F5F9;
    padding: 12px;
    border-radius: 12px;
    font-size: 0.8rem;
    color: #475569;
    line-height: 1.4;
    margin-bottom: 15px;
    border-left: 4px solid #CBD5E1;
}

/* TABS ESTILO SEGMENTED CONTROL (Apple Style) */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    justify-content: center;
    gap: 8px;
    background-color: #F1F5F9;
    padding: 6px;
    border-radius: 16px;
    border: none;
    max-width: 400px;
    margin: 0 auto 2rem auto;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    background-color: transparent !important;
    border: none !important;
    color: #64748B !important;
    font-weight: 600;
    border-radius: 10px !important;
    padding: 0 20px !important;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* NOTICIAS & CARDS */
.news-container {
    background: #FFFFFF;
    border: 1px solid #F1F5F9;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: transform 0.2s, box-shadow 0.2s;
}
.news-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.04);
    border-color: #E2E8F0;
}
.news-tag {
    font-size: 0.65rem;
    background: #EFF6FF;
    color: #2563EB;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    text-transform: uppercase;
}

/* CHAT MODERNO */
.chat-bubble {
    padding: 16px 20px;
    border-radius: 20px;
    margin-bottom: 12px;
    max-width: 85%;
    font-size: 0.95rem;
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
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* BOTONES */
.stButton>button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s;
    border: 1px solid #E2E8F0;
}
.main-btn > div > button {
    background: #0F172A !important;
    color: white !important;
    width: 100%;
    height: 50px;
}
.summarize-btn > div > button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 0.8rem !important;
    padding: 4px 12px !important;
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "InvestIA Pro Terminal",
        "lang": "Idioma de Interfaz",
        "budget": "Capital Total",
        "risk": "Nivel de Riesgo",
        "ticker_label": "Ticker del Activo",
        "ticker_info": "💡 **¿Qué es un Ticker?** Es el código único (letras) que identifica a una empresa en bolsa. Ej: **AAPL** (Apple), **TSLA** (Tesla) o **BTC-USD** (Bitcoin).",
        "btn_analyze": "ANALIZAR ACTIVO",
        "tab_chat": "Terminal de IA",
        "tab_news": "Mercado en Vivo",
        "sum_btn": "🧠 Resumir noticia con IA",
        "read_more": "Leer fuente oficial →"
    },
    "English": {
        "title": "InvestIA Pro Terminal",
        "lang": "Interface Language",
        "budget": "Total Budget",
        "risk": "Risk Level",
        "ticker_label": "Asset Ticker",
        "ticker_info": "💡 **What is a Ticker?** It is a unique code (letters) used to identify a company in the stock market. Ex: **AAPL** (Apple), **TSLA** (Tesla) or **BTC-USD** (Bitcoin).",
        "btn_analyze": "ANALYZE ASSET",
        "tab_chat": "AI Terminal",
        "tab_news": "Live Market",
        "sum_btn": "🧠 Summarize with AI",
        "read_more": "Read official source →"
    }
}

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">💎 InvestIA</div>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="field-label">{languages[st.session_state.lang]["lang"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()

    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-label">{t["budget"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")

    st.markdown(f'<p class="field-label">{t["risk"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")

    st.markdown(f'<p class="field-label">{t["ticker_label"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="ticker-info-box">{t["ticker_info"]}</div>', unsafe_allow_html=True)
    ticker = st.text_input("", value="AAPL", label_visibility="collapsed").upper()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="main-btn">', unsafe_allow_html=True)
    analyze_btn = st.button(t["btn_analyze"])
    st.markdown('</div>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
st.markdown(f"<h1 style='text-align: center; font-weight: 800; color: #0F172A;'>{t['title']}</h1>", unsafe_allow_html=True)

# TABS REDISEÑADAS (Segmented Control)
tab1, tab2 = st.tabs([f"💬 {t['tab_chat']}", f"📰 {t['tab_news']}"])

with tab1:
    # Contenedor de Chat Estético
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-bubble ai-bubble">Hola. Soy tu analista InvestIA. ¿En qué activo quieres profundizar hoy?</div>', unsafe_allow_html=True)
        # Aquí iría el bucle del historial
        for msg in st.session_state.chat_history:
            clase = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.text_input("", placeholder="Pregunta algo sobre el mercado...", key="chat_input", label_visibility="collapsed")

with tab2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    # Ejemplo de Noticia con funciones mantenidas
    for i in range(2):
        st.markdown(f"""
        <div class="news-container">
            <span class="news-tag">Mercados Financieros</span>
            <h3 style='margin: 12px 0 8px 0; font-size: 1.2rem;'>El impacto de la inflación en el valor de {ticker}</h3>
            <p style='color: #64748B; font-size: 0.9rem; margin-bottom: 20px;'>
                Analistas de Wall Street debaten el futuro del sector tras los últimos anuncios de la Fed...
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones integrados debajo de la tarjeta
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="summarize-btn">', unsafe_allow_html=True)
            st.button(t["sum_btn"], key=f"sum_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='text-align: right; padding-top: 10px;'><a href='#' style='color: #0F172A; text-decoration: none; font-weight: 600; font-size: 0.85rem;'>{t['read_more']}</a></div>", unsafe_allow_html=True)

# Lógica de procesamiento (manteniendo tu motor original)
if analyze_btn:
    st.toast(f"Consultando datos de {ticker}...", icon="📈")

