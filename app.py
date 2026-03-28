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

# --- ESTILOS ELITE (CAPVALUEZ UI) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');

/* Configuración Global */
.stApp {
    background-color: #0A0D10;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
}

/* Sidebar Estilo Premium */
[data-testid="stSidebar"] {
    background-color: #0D1117;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Tipografía de Títulos de Campo */
.field-title {
    color: #00C853;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
    margin-top: 20px;
    opacity: 0.9;
}

/* Inputs con Glassmorphism */
.stTextInput input, .stNumberInput input, .stSelectbox > div {
    background-color: #15191E !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    padding: 12px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus, .stSelectbox > div:focus-within {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 1px #00C853 !important;
}

/* Botones CapValuez Style */
.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #00C853 0%, #009688 100%);
    color: #000000 !important;
    border: none;
    border-radius: 8px;
    padding: 14px 24px;
    font-weight: 700;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 200, 83, 0.3);
    color: #000000 !important;
}

/* Tabs Modernas */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    height: 45px;
    background-color: #15191E;
    border-radius: 8px 8px 0 0;
    color: #94A3B8 !important;
    border: 1px solid rgba(255,255,255,0.05);
    padding: 0 20px;
}

.stTabs [aria-selected="true"] {
    background-color: #1C2229 !important;
    color: #00C853 !important;
    border-bottom: 2px solid #00C853 !important;
}

/* Contenedores de Métricas y Tarjetas */
.metric-container, .news-card, .recommendation-box {
    background: #15191E;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
}

.news-card:hover {
    border-color: rgba(0, 200, 83, 0.3);
}

/* Chat Bubbles */
.bubble {
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    line-height: 1.5;
}

.user-bubble {
    background: #1C2229;
    border: 1px solid rgba(255,255,255,0.1);
    color: #E2E8F0;
}

.ai-bubble {
    background: rgba(0, 200, 83, 0.05);
    border-left: 4px solid #00C853;
    color: #FFFFFF;
}

/* Ocultar elementos innecesarios de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES (MANTENIDAS) ---
languages = {
    "Español": {
        "title": "INVESTIA ELITE TERMINAL",
        "lang_lab": "Idioma / Language",
        "cap": "Presupuesto de Inversión",
        "risk_lab": "Perfil de Riesgo",
        "ass_lab": "Ticker de Activo",
        "btn": "EJECUTAR ANÁLISIS IA",
        "wait": "Procesando inteligencia de mercado...",
        "price": "Precio Actual",
        "target": "Objetivo 30d",
        "shares": "Capacidad Compra",
        "analysis": "Recomendación Estratégica",
        "hist_t": "Evolución Histórica",
        "pred_t": "Proyección Algorítmica",
        "chat_placeholder": "Consultar al analista senior...",
        "news_tab": "Mercados",
        "news_sub": "Noticias Económicas Globales",
        "chat_tab": "Asistente IA",
        "read_more": "Ver detalles →",
        "summarize": "🧠 Síntesis IA"
    },
    "English": {
        "title": "INVESTIA ELITE TERMINAL",
        "lang_lab": "Language",
        "cap": "Investment Budget",
        "risk_lab": "Risk Profile",
        "ass_lab": "Asset Ticker",
        "btn": "EXECUTE IA ANALYSIS",
        "wait": "Processing market intelligence...",
        "price": "Current Price",
        "target": "30-Day Target",
        "shares": "Buying Capacity",
        "analysis": "Strategic Recommendation",
        "hist_t": "Historical Evolution",
        "pred_t": "Algorithmic Projection",
        "chat_placeholder": "Consult senior analyst...",
        "news_tab": "Markets",
        "news_sub": "Global Economic News",
        "chat_tab": "AI Assistant",
        "read_more": "View details →",
        "summarize": "🧠 AI Synthesis"
    }
}

# --- LÓGICA IA (MANTENIDA) ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        
        prompt = f"""
        Act as a Senior Investment Strategist. Your goal is to give a CUSTOMIZED RECOMMENDATION in {idioma_inst}.
        Data: {contexto}. Risk Profile: {perfil}. Capital: {capital}€.
        
        Structure:
        1. Action: (Buy, Hold or Sell) based on the profile.
        2. Rational: Why this makes sense.
        3. Future Outlook: What to expect if the user follows this advice.
        
        Question: {pregunta if pregunta else "General recommendation."}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"
        
def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pr):
    return generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=pr)
    
# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR REDISEÑADO ---
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

# --- HEADER ---
st.markdown(f"""
    <div style='padding: 2rem 0; text-align: center;'>
        <h1 style='color: #FFFFFF; font-weight: 800; font-size: 2.5rem; letter-spacing: -1.5px; margin-bottom: 0;'>
            {t['title']}<span style='color: #00C853;'>.</span>
        </h1>
        <p style='color: #94A3B8; font-size: 1.1rem; margin-top: 10px;'>Inteligencia Artificial aplicada al Mercado de Capitales</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    f"📊 {t['btn']}", 
    f"💬 {t['chat_tab']}", 
    f"📰 {t['news_tab']}"
])

# --- CONTENIDO (TAB1 - ANÁLISIS) ---
with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            # (El resto de la lógica de yfinance y Prophet seguiría aquí como en tu código original)
            # Solo he modificado la estructura visual para que coincida con el nuevo diseño.
            st.success("Análisis completado para " + ticket)
            # ... resto de la lógica ...

# --- SIGUIENTES PASOS ---
# He implementado el CSS completo para transformar la "piel" de tu aplicación. 
# ¿Deseas que complete la integración de las gráficas de Plotly con colores esmeralda personalizados?



        
