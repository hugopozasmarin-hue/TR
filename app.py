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

# --- SISTEMA DE DISEÑO PROFESIONAL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    :root {
        --primary: #64FFDA;
        --bg-dark: #0A192F;
        --text-main: #1F2937;
        --glass: rgba(255, 255, 255, 0.05);
    }

    .stApp { background: #F8FAFC; color: var(--text-main); }
    * { font-family: 'Inter', sans-serif; }

    /* Animaciones de entrada */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTabs, .stButton, .metric-container { animation: fadeIn 0.6s ease-out; }

    /* Barra lateral Ultra-Pro */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A192F 0%, #112240 100%) !important;
        border-right: 1px solid rgba(100, 255, 218, 0.1);
        box-shadow: 10px 0 30px rgba(0,0,0,0.2);
    }

    /* Labels de la Sidebar */
    .field-title {
        color: var(--primary);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin: 20px 0 8px 0;
        opacity: 0.8;
    }

    /* Botón con efecto de brillo */
    .stButton>button {
        background: linear-gradient(90deg, #64FFDA 0%, #48D1B2 100%);
        color: #0A192F !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        height: 52px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(100, 255, 218, 0.3);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(100, 255, 218, 0.5);
    }

    /* Tabs Estilo Apple */
    .stTabs [data-baseweb="tab-list"] { 
        background: white;
        padding: 8px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 25px;
        color: #64748B;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        background: #0A192F !important; 
        color: white !important; 
    }

    /* Contenedores de Chat / Noticias */
    .chat-bubble-container {
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .ai-bubble {
        background: white;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    /* Recomendación Card */
    .recommendation-box {
        background: #0A192F;
        color: white;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid var(--primary);
        box-shadow: 0 20px 40px rgba(10, 25, 47, 0.2);
    }

    /* Inputs Modernizados */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA • PRO TERMINAL", "lang_lab":"Idioma / Language", "cap":"Capital Operativo", "risk_lab":"Perfil de Riesgo", "ass_lab":"Ticker del Activo", 
        "btn":"EJECUTAR ANÁLISIS", "wait":"Procesando Big Data...", "price":"Cotización Actual", "target":"Objetivo 30d", 
        "shares":"Títulos sugeridos", "analysis":"Informe Estratégico", "hist_t":"Evolución Histórica", 
        "pred_t":"Proyección Cuántica", "chat_placeholder":"Consulta a la IA de inversión...",
        "news_tab": "Noticias", "news_sub": "Inteligencia de Mercado Global", "filter_lab": "Filtrar por mercado"
    },
    "English": { 
        "title":"INVESTIA • PRO TERMINAL", "lang_lab":"Language / Idioma", "cap":"Operating Capital", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"RUN ANALYTICS", "wait":"Processing Big Data...", "price":"Current Quote", "target":"30-Day Target", 
        "shares":"Suggested Units", "analysis":"Strategic Report", "hist_t":"Historical Evolution", 
        "pred_t":"Quantum Projection", "chat_placeholder":"Ask the Investment IA...",
        "news_tab": "News", "news_sub": "Global Market Intelligence", "filter_lab": "Filter by market"
    }
}

# --- IA Y LOGICA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"Act as a Senior Investment Strategist. Recommendation in {idioma_inst}. Data: {contexto}. Risk: {perfil}. Capital: {capital}€. Question: {pregunta if pregunta else 'General analysis.'}"
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pr):
    return generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=pr)

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com", width=60) # Logo estético
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
st.markdown(f"<h1 style='text-align: center; color: #0A192F; font-weight: 800; font-size: 42px; margin-bottom: 5px;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 40px;'>Inteligencia Artificial aplicada al análisis de mercados financieros de alta precisión.</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([f"📈 {t['btn']}", "💬 Smart Advisor", f"📰 {t['news_tab']}"])

# ... (El resto del código funcional se mantiene igual siguiendo esta línea de diseño)
