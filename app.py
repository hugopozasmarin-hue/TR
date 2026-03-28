import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS DE ALTO NIVEL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0A192F !important; border-right: 1px solid #E5E7EB; }
    .field-title { color: #64FFDA; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px; margin-top: 15px; }
    .stButton>button { border: none; border-radius: 10px; background: linear-gradient(135deg, #0A192F 0%, #1F2937 100%); color: #FFFFFF !important; font-weight: 600; height: 48px; width: 100%; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #E5E7EB; }
    .stTabs [aria-selected="true"] { color: #0A192F !important; border-bottom: 2px solid #0A192F !important; }
    .metric-container { background: #FFFFFF; border: 1px solid #F3F4F6; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; }
    .bubble { padding: 16px 22px; border-radius: 18px; max-width: 80%; font-size: 15px; line-height: 1.6; margin-bottom: 10px; }
    .user-bubble { background-color: #F8F9FA; color: #374151; border: 1px solid #F3F4F6; align-self: flex-end; }
    .ai-bubble { background-color: #F0F7FF; color: #1E3A8A; border: 1px solid #DBEAFE; align-self: flex-start; }
    .recommendation-box { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-left: 5px solid #0A192F; padding: 25px; border-radius: 12px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", 
        "btn":"ANALIZAR ACTIVO", "wait":"Consultando mercados...", "price":"Precio Actual", "target":"Objetivo 30d", 
        "shares":"Capacidad Compra", "analysis":"Recomendación Estratégica", "chat_placeholder":"Escribe tu consulta financiera..."
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"ANALYZE ASSET", "wait":"Consulting markets...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Buying Capacity", "analysis":"Strategic Recommendation", "chat_placeholder":"Type your financial query..."
    }
}

# --- LÓGICA IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"Act as Senior Strategist in {idioma_inst}. Ticker: {ticket}, Price: {p_act}, Prediction: {p_fut} ({cambio:.2f}%). Profile: {perfil}, Capital: {capital}. Answer: {pregunta if pregunta else 'General analysis'}"
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analizado" not in st.session_state: st.session_state.analizado = False

# --- SIDEBAR ---
with st.sidebar:
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, label_visibility="collapsed")
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()

# --- UI PRINCIPAL ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([f"📊 {t['btn']}", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y")
            if not data.empty:
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df['ds'] = df['ds'].dt.tz_localize(None)
                model = Prophet().fit(df)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)
                
                p_act = float(df['y'].iloc[-1])
                p_fut = float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                
                # Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{int(capital/p_act)}")
                
                # Gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Historial", line=dict(color='#0A192F')))
                fig.add_trace(go.Scatter(x=forecast['ds'].iloc[-30:], y=forecast['yhat'].iloc[-30:], name="Predicción", line=dict(dash='dash', color='#3B82F6')))
                st.plotly_chart(fig, use_container_width=True)
                
                # Recomendación
                rec = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f'<div class="recommendation-box"><h4>{t["analysis"]}</h4>{rec}</div>', unsafe_allow_html=True)
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket": ticket, "analizado": True})

with tab2:
    if st.session_state.analizado:
        for chat in st.session_state.chat_history:
            st.markdown(f'<div class="bubble user-bubble">{chat["u"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble ai-bubble">{chat["a"]}</div>', unsafe_allow_html=True)
        
        pregunta = st.chat_input(t["chat_placeholder"])
        if pregunta:
            res = generar_analisis_ia(st.session_state.lang, st.session_state.ticket, st.session_state.p_act, st.session_state.p_pre, st.session_state.cambio, perfil, capital, pregunta)
            st.session_state.chat_history.append({"u": pregunta, "a": res})
            st.rerun()
    else:
        st.info("Analiza un activo primero.")
