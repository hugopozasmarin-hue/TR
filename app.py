import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ESTILOS CSS ACTUALIZADOS (MENU BLANCO) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

/* BARRA LATERAL EN BLANCO */
[data-testid="stSidebar"] { 
    background-color: #ffffff !important; 
    border-right: 1px solid #e0e0e0; 
}

/* Títulos de campos en la barra lateral (ajustado para fondo blanco) */
.field-title { 
    color: #4f46e5; 
    font-size: 10px; 
    font-weight: 800; 
    letter-spacing: 2px; 
    text-transform: uppercase; 
    margin-top: 25px; 
    margin-bottom: 8px; 
    display: block; 
    opacity: 0.9; 
    border-bottom: 1px solid #f0f0f0; 
    padding-bottom: 4px; 
}

/* Inputs y Selectores (ajustados para ser visibles en blanco) */
.stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input { 
    background-color: #f9fafb !important; 
    color: #1f2937 !important; 
    border: 1px solid #d1d5db !important; 
    border-radius: 10px !important; 
}

label { display: none !important; }

.stButton>button { 
    width: 100%; 
    border-radius: 12px; 
    background: linear-gradient(90deg, #6366f1, #00d4ff); 
    color: white !important; 
    font-weight: 800; 
    border: none; 
    padding: 15px; 
    transition: all 0.4s ease; 
    margin-top: 20px; 
}

.bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
.user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
.assistant-bubble { background: #f3f4f6; border: 1px solid #e5e7eb; color: #1f2937 !important; border-bottom-left-radius: 2px; }
.highlight { color: #4f46e5; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- RESTO DEL CÓDIGO (Lógica de InvestIA) ---
languages = {
    "Español": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESUPUESTO TOTAL","risk_lab":"PERFIL DE RIESGO","ass_lab":"ACTIVO (TICKER - Ej: AAPL)","btn":"EJECUTAR ANÁLISIS","diag":"Consultoría","just":"Justificación Técnica","wait":"Analizando...","price":"Precio Actual","target":"Predicción (30d)","shares":"Acciones","disclaimer":"Simulación InvestIA 2026. Riesgo de capital."},
    "English": {"title":"InvestIA Elite","lang_lab":"LANGUAGE","cap":"TOTAL BUDGET","risk_lab":"RISK PROFILE","ass_lab":"ASSET (TICKER - e.g. NVDA)","btn":"RUN ANALYSIS","diag":"Consultancy","just":"Technical Justification","wait":"Analyzing...","price":"Current Price","target":"Target (30d)","shares":"Shares","disclaimer":"InvestIA 2026 Simulation. Capital risk."},
    "Català": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESSUPOST TOTAL","risk_lab":"PERFIL DE RISC","ass_lab":"ACTIU (TICKER - Ex: TSLA)","btn":"EXECUTAR ANÀLISI","diag":"Consultoria","just":"Justificació Tècnica","wait":"Analitzant...","price":"Preu Actual","target":"Preu previst (30d)","shares":"Accions","disclaimer":"Simulació InvestIA 2026. Risc de capital."}
}

if 'lang' not in st.session_state: st.session_state.lang = "Español"
if 'analizado' not in st.session_state: st.session_state.analizado = False

with st.sidebar:
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# El resto del código de análisis y pestañas se mantiene igual...
st.title(f"💎 {t['title']}")
# ... (continuación del script anterior)

