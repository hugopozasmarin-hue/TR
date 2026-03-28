import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="InvestIA Elite | Pro Terminal",
    page_icon="💎",
    layout="wide"
)

GROQ_API_KEY = "gsk_NAIdRYkP6cOuKIMSFpTiGYOURKEY"

# =========================
# CSS (PRO TERMINAL STYLE)
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A192F, #020617);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* BUTTONS */
.stButton>button {
    background: linear-gradient(135deg, #0A192F, #1E3A8A);
    color: white;
    border-radius: 10px;
    height: 45px;
}

/* CARDS */
.card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 16px;
}

/* CHAT */
.chat-bubble-user {
    background: #F1F5F9;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.chat-bubble-ai {
    background: #0F172A;
    color: #E2E8F0;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LANG
# =========================
languages = {
    "Español": {
        "title": "INVESTIA TERMINAL",
        "analyze": "ANALIZAR ACTIVO",
        "news": "Noticias",
        "chat": "Chat",
        "workspace": "Workspace",
        "price": "Precio",
        "target": "Objetivo",
        "capital": "Capital",
        "risk": "Riesgo",
        "ticker": "Ticker",
        "read": "Leer más →",
        "summarize": "🧠 Resumir"
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "analyze": "ANALYZE ASSET",
        "news": "News",
        "chat": "Chat",
        "workspace": "Workspace",
        "price": "Price",
        "target": "Target",
        "capital": "Capital",
        "risk": "Risk",
        "ticker": "Ticker",
        "read": "Read more →",
        "summarize": "🧠 Summarize"
    }
}

# =========================
# IA
# =========================
def generar_analisis(ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
    Act as a senior investment strategist.
    Ticker: {ticket}
    Price: {p_act}
    Target: {p_fut}
    Change: {cambio:.2f}%
    Risk: {perfil}
    Capital: {capital}

    Question: {pregunta if pregunta else "General analysis"}
    """

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# SESSION STATE
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "Español"

if "chat" not in st.session_state:
    st.session_state.chat = []

if "analizado" not in st.session_state:
    st.session_state.analizado = False


# =========================
# SIDEBAR = BLOOMBERG CONTROL CENTER
# =========================
with st.sidebar:

    t = languages[st.session_state.lang]

    st.markdown("## 📡 INVESTIA")

    lang = st.selectbox("Language", list(languages.keys()))
    st.session_state.lang = lang
    t = languages[lang]

    st.markdown("---")

    capital = st.number_input("Capital", value=1000.0)
    perfil = st.selectbox("Risk", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input("Ticker", value="NVDA").upper()

    st.markdown("---")

    st.markdown("### ℹ Ticker info")
    with st.expander("What is a ticker?"):
        st.write("NVDA = Nvidia, AAPL = Apple, TSLA = Tesla")


# =========================
# HEADER
# =========================
st.markdown(f"""
<h2 style='text-align:center; color:#0A192F;'>
{languages[st.session_state.lang]['title']}
</h2>
""", unsafe_allow_html=True)


# =========================
# WORKSPACE SWITCHER
# =========================
mode = st.radio(
    "Workspace",
    ["📊 Trading Desk", "💬 AI Terminal", "📰 Market Feed"],
    horizontal=True
)


# =========================
# ANALYSIS ENGINE
# =========================
def run_analysis(ticket):

    data = yf.download(ticket, period="2y", interval="1d")

    if data.empty:
        st.error("Invalid ticker")
        return

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    df = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    p_act = float(df['y'].iloc[-1])
    p_fut = float(forecast['yhat'].iloc[-1])
    cambio = ((p_fut - p_act) / p_act) * 100

    return data, df, forecast, p_act, p_fut, cambio


# =========================
# TRADING DESK
# =========================
if mode == "📊 Trading Desk":

    if st.button(languages[st.session_state.lang]["analyze"]):

        with st.spinner("Analyzing markets..."):

            result = run_analysis(ticket)

            if result:
                data, df, forecast, p_act, p_fut, cambio = result

                st.session_state.update({
                    "data": data,
                    "df": df,
                    "forecast": forecast,
                    "p_act": p_act,
                    "p_fut": p_fut,
                    "cambio": cambio,
                    "analizado": True
                })

                st.session_state.analisis = generar_analisis(
                    ticket, p_act, p_fut, cambio, perfil, capital
                )

    if st.session_state.analizado:

        col1, col2, col3 = st.columns(3)

        col1.metric("Price", f"{st.session_state.p_act:.2f}")
        col2.metric("Target", f"{st.session_state.p_fut:.2f}")
        col3.metric("Change", f"{st.session_state.cambio:.2f}%")

        st.plotly_chart(
            go.Figure(data=[
                go.Scatter(x=st.session_state.df['ds'], y=st.session_state.df['y'], name="Price")
            ]),
            use_container_width=True
        )

        st.markdown("### AI Analysis")
        st.write(st.session_state.analisis)


# =========================
# AI TERMINAL
# =========================
elif mode == "💬 AI Terminal":

    st.markdown("### AI Strategist")

    for msg in st.session_state.chat:

        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'>USER: {msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'>AI: {msg['text']}</div>", unsafe_allow_html=True)

    q = st.text_input("Ask the market...")

    if q:
        st.session_state.chat.append({"role": "user", "text": q})

        answer = generar_analisis(
            ticket, 0, 0, 0, perfil, capital, q
        )

        st.session_state.chat.append({"role": "assistant", "text": answer})

        st.rerun()


# =========================
# MARKET FEED
# =========================
elif mode == "📰 Market Feed":

    st.markdown("### Live News Feed")

    feeds = {
        "Global": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "Europe": "https://www.lemonde.fr/en/europe/rss_full.xml",
        "Crypto": "https://www.coindesk.com/arc/outboundfeeds/rss/"
    }

    feed = feedparser.parse(feeds["Global"])

    for entry in feed.entries[:8]:

        st.markdown(f"""
        <div class="card">
            <h4>{entry.title}</h4>
            <p style="font-size:12px; color:gray;">{entry.get('published','')}</p>
            <p>{entry.get('summary','')[:150]}...</p>
            <a href="{entry.link}" target="_blank">Open →</a>
        </div>
        """, unsafe_allow_html=True)
