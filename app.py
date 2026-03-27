import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="InvestIA Elite | Pro Terminal",
    page_icon="💎",
    layout="wide"
)

# =========================
# API KEY
# =========================
GROQ_API_KEY = "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"

# =========================
# ESTILOS CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.stApp {
    background-color: #FFFFFF;
    color: #1F2937;
    font-family: 'Inter', sans-serif;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #0A192F !important;
}

/* TITULOS SIDEBAR */
.field-title {
    color: #64FFDA;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 5px;
    margin-top: 15px;
}

/* BOTONES */
.stButton>button {
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, #0A192F 0%, #1F2937 100%);
    color: white !important;
    font-weight: 600;
    height: 48px;
    width: 100%;
}

/* METRICAS */
.metric-container {
    background: white;
    border: 1px solid #F3F4F6;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* CHAT */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
}

.user-bubble {
    background: #0A192F;
    color: white;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}

.ai-bubble {
    background: #F3F4F6;
    color: #111827;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# IA FUNCTIONS
# =========================
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)
    idioma = "ENGLISH" if lang == "English" else "ESPAÑOL"

    prompt = f"""
Act as a Senior Investment Strategist.
Language: {idioma}

Asset: {ticket}
Current Price: {p_act}
Forecast: {p_fut}
Change: {cambio:.2f}%
Profile: {perfil}
Capital: {capital} EUR

Question: {pregunta if pregunta else "General analysis"}
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content


def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)
    idioma = "ENGLISH" if lang == "English" else "ESPAÑOL"

    contexto = f"""
Ticker: {ticket}
Precio: {p_act}
Forecast: {p_fut}
Cambio: {cambio:.2f}%
"""

    prompt = f"""
Actúa como Senior Investment Strategist.
Idioma: {idioma}
Perfil: {perfil}
Capital: {capital} EUR

Contexto:
{contexto}

Pregunta:
{pregunta}
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content


# =========================
# TRADUCCIONES
# =========================
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
        "pred_t": "Proyección IA",
        "chat_placeholder": "Escribe tu consulta..."
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "lang_lab": "Language",
        "cap": "Budget",
        "risk_lab": "Risk Profile",
        "ass_lab": "Asset",
        "btn": "ANALYZE ASSET",
        "wait": "Consulting markets...",
        "price": "Current Price",
        "target": "30-Day Target",
        "shares": "Buying Power",
        "analysis": "Strategic Recommendation",
        "hist_t": "Market Movement",
        "pred_t": "AI Projection",
        "chat_placeholder": "Type your query..."
    }
}

# =========================
# SESSION STATE
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "Español"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analizado" not in st.session_state:
    st.session_state.analizado = False

t = languages[st.session_state.lang]

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown(f"<p class='field-title'>{t['lang_lab']}</p>", unsafe_allow_html=True)
    lang = st.selectbox("", list(languages.keys()))

    st.session_state.lang = lang
    t = languages[lang]

    st.markdown(f"<p class='field-title'>{t['cap']}</p>", unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0)

    st.markdown(f"<p class='field-title'>{t['risk_lab']}</p>", unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])

    st.markdown(f"<p class='field-title'>{t['ass_lab']}</p>", unsafe_allow_html=True)
    ticket = st.text_input("", "NVDA").upper()

# =========================
# HEADER
# =========================
st.markdown(f"<h2 style='text-align:center;color:#0A192F'>{t['title']}</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Análisis", "💬 Chat", "📰 Noticias"])

# =========================
# TAB 1 - ANÁLISIS
# =========================
with tab1:
    if st.button(t["btn"]):
        data = yf.download(ticket, period="2y")

        if not data.empty:
            df = data.reset_index()[["Date", "Close"]]
            df.columns = ["ds", "y"]

            model = Prophet()
            model.fit(df)

            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            p_act = float(df["y"].iloc[-1])
            p_fut = float(forecast["yhat"].iloc[-1])
            cambio = ((p_fut - p_act) / p_act) * 100

            st.session_state.update({
                "p_act": p_act,
                "p_fut": p_fut,
                "cambio": cambio,
                "analizado": True,
                "df": df,
                "forecast": forecast
            })

            st.session_state.analisis = generar_analisis_ia(
                lang, ticket, p_act, p_fut, cambio, perfil, capital
            )

    if st.session_state.analizado:
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='metric-container'><h4>{t['price']}</h4><h3>{st.session_state.p_act:.2f}</h3></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-container'><h4>{t['target']}</h4><h3>{st.session_state.p_fut:.2f} ({st.session_state.cambio:.2f}%)</h3></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-container'><h4>{t['shares']}</h4><h3>{capital/st.session_state.p_act:.2f}</h3></div>", unsafe_allow_html=True)

# =========================
# TAB 2 - CHAT
# =========================
with tab2:
    for msg in st.session_state.chat_history:
        st.markdown(f"<div class='ai-bubble'>{msg}</div>", unsafe_allow_html=True)

    user = st.chat_input(t["chat_placeholder"])

    if user:
        st.session_state.chat_history.append(user)

        resp = generar_chat_ia(
            lang, ticket,
            st.session_state.get("p_act", 0),
            st.session_state.get("p_fut", 0),
            st.session_state.get("cambio", 0),
            perfil, capital,
            user
        )

        st.session_state.chat_history.append(resp)
        st.rerun()

# =========================
# TAB 3 - NOTICIAS
# =========================
def obtener_noticias():
    feed = feedparser.parse("https://feeds.bbci.co.uk/news/business/rss.xml")
    noticias = []

    for e in feed.entries[:5]:
        noticias.append({
            "titulo": e.title,
            "link": e.link,
            "resumen": e.get("summary", "")[:150]
        })

    return noticias


with tab3:
    st.subheader("Noticias económicas")

    for n in obtener_noticias():
        st.markdown(f"""
        <div style="border:1px solid #E5E7EB;padding:15px;border-radius:10px;margin-bottom:10px;">
            <h4>{n['titulo']}</h4>
            <p>{n['resumen']}</p>
            <a href="{n['link']}" target="_blank">Leer más →</a>
        </div>
        """, unsafe_allow_html=True)
