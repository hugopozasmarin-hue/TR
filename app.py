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

st.markdown("""<style>@import url('https://fonts.googleapis.com');
/* --- GLOBAL --- */
html, body, [class*="css"] { font-family: 'Inter', sans-serif;}
.stApp { background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%); color: #111827;}
/* --- SIDEBAR PRO --- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A192F 0%, #020617 100%); border-right: 1px solid rgba(255,255,255,0.05);}
.field-title { color: #64FFDA; font-size: 11px; font-weight: 700; letter-spacing: 1.8px; text-transform: uppercase; margin-top: 18px;}
.ticker-help { color: #94A3B8; font-size: 12px; margin-top: 5px; font-style: italic; line-height: 1.4;}
/* --- INPUTS --- */
.stTextInput input, .stNumberInput input { border-radius: 10px !important; border: 1px solid #E5E7EB !important; padding: 10px !important;}
.stSelectbox > div { background-color: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #E5E7EB !important; padding: 5px !important;}
.stSelectbox div[data-baseweb="select"] { color: #111827 !important;}
/* --- BOTONES PREMIUM --- */
.stButton>button { border-radius: 12px; background: linear-gradient(135deg, #0A192F, #1E3A8A); color: white; font-weight: 600; height: 50px; transition: all 0.25s ease; width: 100%;}
.stButton>button:hover { transform: translateY(-3px); box-shadow: 0 12px 20px rgba(0,0,0,0.12);}
/* --- TABS MODERNAS --- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: none;}
.stTabs [data-baseweb="tab"] { background: #F1F5F9; border-radius: 10px; padding: 10px 18px; transition: 0.2s;}
.stTabs [aria-selected="true"] { background: #0A192F !important; color: white !important;}
/* --- NOTICIAS & CHAT --- */
.news-card { background: white; border-radius: 14px; padding: 20px; margin-bottom: 15px; border: 1px solid #E5E7EB;}
.bubble { padding: 16px 20px; border-radius: 16px; font-size: 14px; margin-bottom: 10px;}
.ai-bubble { background: #EEF2FF; border-left: 4px solid #3B82F6;}
</style>""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = { 
    "Español": { "title": "INVESTIA TERMINAL", "lang_lab": "Idioma", "cap": "Presupuesto", "risk_lab": "Riesgo", "ass_lab": "Ticker", "ticker_desc": "El 'Ticker' es el código único de letras de un activo (Ej: AAPL para Apple, BTC-USD para Bitcoin).", "btn": "ANALIZAR ACTIVO", "news_tab": "Noticias", "chat_tab": "Chat", "summarize": "🧠 Resumir con IA" },
    "English": { "title": "INVESTIA TERMINAL", "lang_lab": "Language", "cap": "Budget", "risk_lab": "Risk Profile", "ass_lab": "Asset Ticker", "ticker_desc": "A 'Ticker' is the unique letter code for an asset (Ex: AAPL for Apple, BTC-USD for Bitcoin).", "btn": "ANALYZE ASSET", "news_tab": "News", "chat_tab": "Chat", "summarize": "🧠 Summarize with AI" }
}

if "lang" not in st.session_state: st.session_state.lang = "Español"

# --- SIDEBAR (CON BOTÓN INCLUIDO) ---
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
    ticker = st.text_input("", value="AAPL", label_visibility="collapsed").upper()
    st.markdown(f'<p class="ticker-help">{t["ticker_desc"]}</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    # BOTÓN MOVIDO AQUÍ
    analyze_btn = st.button(t["btn"])

# --- CONTENIDO PRINCIPAL ---
st.title(t["title"])

tab1, tab2 = st.tabs([t["chat_tab"], t["news_tab"]])

with tab1:
    st.markdown('<div class="bubble ai-bubble">Terminal lista. Configura el activo en el panel lateral y pulsa analizar.</div>', unsafe_allow_html=True)
    st.text_input(label="Chat", placeholder="Escribe tu consulta...", label_visibility="collapsed")

with tab2:
    st.markdown(f'<div class="news-card"><h4>Noticias de {ticker}</h4><p>Configura el ticker para ver novedades...</p></div>', unsafe_allow_html=True)
    if st.button(t["summarize"]):
        st.info("Resumiendo...")

if analyze_btn:
    st.success(f"Analizando {ticker} con un presupuesto de {capital}€...")


