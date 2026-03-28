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
    background: #0B0E11;
    color: #FFFFFF;
}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {
    background: #050505;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* --- TITULOS --- */
h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* --- LABELS --- */
.field-title {
    color: #00FF85;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 20px;
}

/* --- INPUTS --- */
.stTextInput input,
.stNumberInput input {
    background: #14171A !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: white !important;
    padding: 12px !important;
}

.stSelectbox > div {
    background-color: #14171A !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

.stSelectbox div[data-baseweb="select"] {
    color: white !important;
}

/* --- BOTONES --- */
.stButton>button {
    border-radius: 14px;
    background: #00FF85;
    color: #000000;
    font-weight: 700;
    height: 50px;
    border: none;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0,255,133,0.3);
}

/* --- TABS --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: #14171A;
    border-radius: 12px;
    padding: 10px 20px;
    color: #A0A0A0;
}

.stTabs [aria-selected="true"] {
    background: #00FF85 !important;
    color: #000 !important;
}

/* --- METRICS --- */
.metric-container {
    background: #14171A;
    border-radius: 16px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: 0.25s;
}

.metric-container:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(0,255,133,0.3);
}

/* --- CHARTS --- */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
}

/* --- CHAT --- */
.chat-container {
    padding: 10px;
}

.bubble {
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 14px;
    max-width: 75%;
}

.user-bubble {
    background: #1C1F23;
}

.ai-bubble {
    background: #14171A;
    border-left: 3px solid #00FF85;
}

/* --- NEWS --- */
.news-card {
    background: #14171A;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: 0.2s;
}

.news-card:hover {
    transform: translateY(-3px);
    border: 1px solid rgba(0,255,133,0.3);
}

/* --- RECOMMENDATION --- */
.recommendation-box {
    border-radius: 16px;
    padding: 25px;
    background: #14171A;
    border: 1px solid rgba(0,255,133,0.15);
}

/* --- TEXT SECONDARY --- */
p, span {
    color: #A0A0A0 !important;
}
</style>
""", unsafe_allow_html=True)

# --- RESTO DEL CÓDIGO EXACTAMENTE IGUAL (NO MODIFICADO) ---
# (👇 TODO lo demás permanece EXACTAMENTE igual que tu código original 👇)
