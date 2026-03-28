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
GROQ_API_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# --- 🎨 UI PREMIUM DARK ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* GLOBAL */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0B0E11;
    color: #FFFFFF;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #050505;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TITLES */
h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* LABELS */
.field-title {
    color: #00FF85;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* INPUTS */
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

/* BUTTON */
.stButton>button {
    border-radius: 14px;
    background: #00FF85;
    color: #000;
    font-weight: 700;
    height: 48px;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 18px rgba(0,255,133,0.3);
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    background: #14171A;
    border-radius: 10px;
    color: #A0A0A0;
}

.stTabs [aria-selected="true"] {
    background: #00FF85 !important;
    color: black !important;
}

/* METRICS */
.metric-container {
    background: #14171A;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* CHAT */
.user-bubble {
    background: #1F2227;
}

.ai-bubble {
    background: #14171A;
    border-left: 3px solid #00FF85;
}

/* NEWS */
.news-card {
    background: #14171A;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* RECOMMENDATION */
.recommendation-box {
    background: #14171A;
    border: 1px solid rgba(0,255,133,0.2);
    border-radius: 16px;
    padding: 25px;
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
        "ass_lab": "Ticker",
        "btn": "ANALIZAR ACTIVO",
        "wait": "Consultando mercados...",
        "price": "Precio Actual",
        "target": "Objetivo 30d",
        "shares": "Capacidad Compra",
        "analysis": "Recomendación Estratégica",
        "hist_t": "Movimiento del Mercado",
        "pred_t": "Proyección Algorítmica",
        "chat_placeholder": "Escribe tu consulta financiera...",
        "news_tab": "Noticias",
        "news_sub": "Noticias Económicas Globales",
        "chat_tab": "Chat",
        "read_more": "Leer más →",
        "summarize": "🧠 Resumir con IA"
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Language",
        "cap": "Budget",
        "risk_lab": "Risk Profile",
        "ass_lab": "Asset Ticker",
        "btn": "ANALYZE ASSET",
        "wait": "Consulting markets...",
        "price": "Current Price",
        "target": "30-Day Target",
        "shares": "Buying Capacity",
        "analysis": "Strategic Recommendation",
        "hist_t": "Market Movement",
        "pred_t": "Algorithmic Projection",
        "chat_placeholder": "Type your financial query...",
        "news_tab": "News",
        "news_sub": "Global Economic News",
        "chat_tab": "Chat",
        "read_more": "Read more →",
        "summarize": "🧠 Summarize with AI"
    }
}

# --- IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"

        prompt = f"""
        Act as a Senior Investment Strategist. Your goal is to give a CUSTOMIZED RECOMMENDATION in {idioma_inst}.
        Data: {contexto}. Risk Profile: {perfil}. Capital: {capital}€.

        Structure:
        1. Action
        2. Rational
        3. Future Outlook

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

# --- SESSION ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()))

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0)

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA").upper()

# --- HEADER ---
st.markdown(f"<h2 style='text-align:center'>{t['title']}</h2>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊", "💬", "📰"])

# --- ANALYSIS ---
with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y")

            if not data.empty:
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds','Close':'y'})
                model = Prophet().fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))

                p_act = float(df['y'].iloc[-1])
                p_fut = float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act)/p_act)*100

                st.session_state.update({
                    "analizado": True,
                    "p_act": p_act,
                    "p_pre": p_fut,
                    "cambio": cambio
                })

    if st.session_state.analizado:
        st.markdown(f"<div class='metric-container'><h3>{t['price']}: {st.session_state.p_act:.2f}€</h3></div>", unsafe_allow_html=True)

# --- CHAT ---
with tab2:
    if pr := st.chat_input(t["chat_placeholder"]):
        res = generar_chat_ia(st.session_state.lang, "", 0, 0, 0, perfil, capital, pr)
        st.write(res)

# --- NEWS ---
with tab3:
    st.subheader(t["news_sub"])
