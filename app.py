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
    .chat-container { display: flex; flex-direction: column; gap: 15px; padding: 10px; }
    .bubble { padding: 16px 22px; border-radius: 18px; max-width: 80%; font-size: 15px; line-height: 1.6; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 10px; }
    .user-bubble { background-color: #F8F9FA; color: #374151; border: 1px solid #F3F4F6; border-bottom-left-radius: 4px; align-self: flex-end; }
    .ai-bubble { background-color: #F0F7FF; color: #1E3A8A; border: 1px solid #DBEAFE; border-bottom-left-radius: 4px; align-self: flex-start; }
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

# --- IA RECOMENDACIÓN ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        ctx = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"Act as Senior Strategist. Context: {ctx}. Risk: {perfil}. Capital: {capital}€. Question: {pregunta if pregunta else 'General recommendation.'}. Lang: {idioma_inst}."
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except: return "Error IA."

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    t = languages[st.session_state.lang]
    capital = st.number_input(f"{t['cap']}", value=1000.0, step=100.0)
    perfil = st.selectbox(f"{t['risk_lab']}", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(f"{t['ass_lab']}", value="NVDA").upper()

# --- UI ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F; font-weight: 700;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs([f"📊 {t['btn']}", f"💬 Chat Advisor", "📰 Noticias"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket})
                
                col1, col2, col3 = st.columns(3)
                col1.metric(t["price"], f"{p_act:.2f} €")
                col2.metric(t["target"], f"{p_fut:.2f} €", f"{cambio:.2f}%")
                col3.metric(t["shares"], f"{int(capital/p_act)}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Histórico", line=dict(color='#0A192F')))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Predicción", line=dict(dash='dash', color='#3B82F6')))
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        clase = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="bubble {clase}">{chat["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if user_input := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        res = generar_analisis_ia(st.session_state.lang, st.session_state.get("ticket_act", "N/A"), st.session_state.get("p_act", 0), st.session_state.get("p_pre", 0), st.session_state.get("cambio", 0), perfil, capital, user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()

with tab3:
    feed = feedparser.parse(f"https://finance.yahoo.com{ticket}")
    for entry in feed.entries[:5]:
        st.markdown(f"**[{entry.title}]({entry.link})**")
        st.divider()
