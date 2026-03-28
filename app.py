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

# --- ESTILOS Y CURSOR PERSONALIZADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* --- CURSOR DE INVERSIÓN (OPUESTO AL FONDO) --- */
html, body, [data-testid="stAppViewContainer"] {
    cursor: none !important;
}

#custom-cursor {
    width: 20px;
    height: 20px;
    background-color: white;
    border-radius: 50%;
    position: fixed;
    pointer-events: none;
    z-index: 999999;
    mix-blend-mode: difference;
    transition: transform 0.15s ease-out;
    transform: translate(-50%, -50%);
}

/* --- GLOBAL --- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
    color: #111827;
}

/* --- SIDEBAR PRO --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A192F 0%, #020617 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

.field-title {
    color: #64FFDA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 18px;
}

/* --- INPUTS --- */
.stTextInput input, .stNumberInput input {
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    padding: 10px !important;
}

.stSelectbox > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    padding: 5px !important;
}

.stSelectbox div[data-baseweb="select"] {
    color: #111827 !important;
}

div[data-baseweb="popover"] {
    background-color: white !important;
    border-radius: 10px !important;
}

/* --- BOTONES PREMIUM --- */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #0A192F, #1E3A8A);
    color: white;
    font-weight: 600;
    height: 50px;
    transition: all 0.25s ease;
    cursor: none !important;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px rgba(0,0,0,0.12);
}

/* --- TABS MODERNAS --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: #F1F5F9;
    border-radius: 10px;
    padding: 10px 18px;
    transition: 0.2s;
    cursor: none !important;
}

.stTabs [aria-selected="true"] {
    background: #0A192F !important;
    color: white !important;
}

/* --- METRICS PRO --- */
.metric-container {
    background: white;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    transition: 0.2s;
}

.metric-container:hover {
    transform: translateY(-4px);
}

/* --- CHARTS --- */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
}

/* --- CHAT --- */
.bubble {
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 14px;
    max-width: 75%;
    margin-bottom: 10px;
}

.user-bubble { background: #F1F5F9; align-self: flex-end; color: #111827; }
.ai-bubble { background: #EEF2FF; border-left: 4px solid #3B82F6; color: #111827; }

/* --- NEWS CARDS --- */
.news-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    transition: 0.2s;
    border: 1px solid #E5E7EB;
}

.news-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
}

/* --- RECOMMENDATION BOX --- */
.recommendation-box {
    border-radius: 16px;
    padding: 25px;
    background: linear-gradient(135deg, #F8FAFC, #FFFFFF);
    border: 1px solid #E5E7EB;
    color: #111827;
}
</style>

<div id="custom-cursor"></div>

<script>
    const cursor = document.getElementById('custom-cursor');
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });
    document.addEventListener('mousedown', () => cursor.style.transform = 'translate(-50%, -50%) scale(0.7)');
    document.addEventListener('mouseup', () => cursor.style.transform = 'translate(-50%, -50%) scale(1)');
</script>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Idioma", "cap": "Presupuesto", "risk_lab": "Riesgo", "ass_lab": "Ticker",
        "btn": "ANALIZAR ACTIVO", "wait": "Consultando mercados...", "price": "Precio Actual",
        "target": "Objetivo 30d", "shares": "Capacidad Compra", "analysis": "Recomendación Estratégica",
        "hist_t": "Movimiento del Mercado", "pred_t": "Proyección Algorítmica",
        "chat_placeholder": "Escribe tu consulta financiera...", "news_tab": "Noticias",
        "news_sub": "Noticias Económicas Globales", "chat_tab": "Chat", "read_more": "Leer más →"
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Language", "cap": "Budget", "risk_lab": "Risk Profile", "ass_lab": "Asset Ticker",
        "btn": "ANALYZE ASSET", "wait": "Consulting markets...", "price": "Current Price",
        "target": "30-Day Target", "shares": "Buying Capacity", "analysis": "Strategic Recommendation",
        "hist_t": "Market Movement", "pred_t": "Algorithmic Projection",
        "chat_placeholder": "Type your financial query...", "news_tab": "News",
        "news_sub": "Global Economic News", "chat_tab": "Chat", "read_more": "Read more →"
    }
}

# --- IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        prompt = f"Act as a Senior Investment Strategist. Recommendation in {'ENGLISH' if lang=='English' else 'ESPAÑOL'}. Data: {contexto}. Risk: {perfil}. Capital: {capital}€. Question: {pregunta if pregunta else 'General'}"
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except Exception as e: return f"Error IA: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "res" not in st.session_state: st.session_state.res = {}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    t = languages[st.session_state.lang]
    capital = st.number_input(t["cap"], value=1000.0)
    perfil = st.selectbox(t["risk_lab"], ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(t["ass_lab"], value="NVDA").upper()

# --- UI ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F; font-weight: 700;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs([f"📊 {t['btn']}", f"💬 {t['chat_tab']}", f"📰 {t['news_tab']}"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                # FIX MULTIINDEX PARA PANDAS/PROPHET
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                
                p_act = float(data['Close'].iloc[-1])
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                
                model = Prophet(daily_seasonality=True).fit(df_p)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)
                p_fut = float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                
                st.session_state.analizado = True
                st.session_state.res = {"p_act": p_act, "p_fut": p_fut, "cambio": cambio, "ticket": ticket}
                
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{capital/p_act:.2f}")
                
                rec = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"<div class='recommendation-box'>{rec}</div>", unsafe_allow_html=True)
                
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    if st.session_state.analizado:
        for m in st.session_state.chat_history:
            st.markdown(f"<div class='bubble {'user-bubble' if m['role']=='user' else 'ai-bubble'}'>{m['content']}</div>", unsafe_allow_html=True)
        
        if pr := st.chat_input(t["chat_placeholder"]):
            st.session_state.chat_history.append({"role": "user", "content": pr})
            r = st.session_state.res
            ans = generar_analisis_ia(st.session_state.lang, r['ticket'], r['p_act'], r['p_fut'], r['cambio'], perfil, capital, pr)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

with tab3:
    feed = feedparser.parse("https://finance.yahoo.com")
    for entry in feed.entries[:5]:
        st.markdown(f"<div class='news-card'><b>{entry.title}</b><br><small>{entry.published}</small><br><a href='{entry.link}'>{t['read_more']}</a></div>", unsafe_allow_html=True)
