import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- API ---
GROQ_API_KEY = "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"

# --- UI PREMIUM STYLE ---
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #0b1220;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a192f 0%, #0b1220 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* TITLES */
h1, h2, h3 {
    color: #e6f1ff;
    letter-spacing: -0.5px;
}

/* FIELD LABELS */
.field-title { 
    color: #64ffda;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 18px;
    margin-bottom: 8px;
    opacity: 0.9;
}

/* BUTTON */
.stButton>button { 
    width: 100%;
    border-radius: 14px;
    background: linear-gradient(135deg, #64ffda, #48cae4);
    color: #0a192f !important;
    font-weight: 800;
    border: none;
    padding: 0.6rem;
    box-shadow: 0 6px 20px rgba(100,255,218,0.15);
    transition: all 0.2s ease;
}

/* METRICS */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 14px;
    border-radius: 14px;
}

/* CHAT BUBBLES */
.chat-row {
    display: flex;
    margin-bottom: 12px;
    width: 100%;
}

.bubble {
    padding: 12px 14px;
    border-radius: 16px;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.user-bubble {
    background: linear-gradient(135deg, #004d40, #00695c);
    color: #e0f2f1;
    border-left: 4px solid #64ffda;
}

.ai-bubble {
    background: linear-gradient(135deg, #1b2430, #111827);
    color: #cbd5e1;
    border-left: 4px solid #48cae4;
}

.chat-label {
    font-size: 10px;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: 1px;
    opacity: 0.8;
}

/* CHART AREA */
.js-plotly-plot {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

</style>
""", unsafe_allow_html=True)

# --- LÓGICA IA ---
def generar_analisis_ia(lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)

    contexto = ""
    if ticket:
        contexto = f"Activo: {ticket} | Precio: {p_act}€ | Predicción: {p_fut}€ ({cambio:.2f}%)"

    prompt = f"""
RESPONDE EN: {lang}

Eres un analista senior de inversión tipo hedge fund.

Perfil: {perfil}
Capital: {capital}€

{contexto}

Usuario pregunta: {pregunta if pregunta else "Haz un análisis estratégico completo"}

Sé claro, profesional y directo.
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content

# --- SESIÓN ---
if "lang" not in st.session_state:
    st.session_state.lang = "Español"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")

    t_temp = {"Español":"IDIOMA", "English":"LANGUAGE"}
    st.markdown(f'<p class="field-title">{t_temp[st.session_state.lang]}</p>', unsafe_allow_html=True)

    lang = st.selectbox("", ["Español", "English"], index=["Español","English"].index(st.session_state.lang), label_visibility="collapsed")
    st.session_state.lang = lang

    capital = st.number_input("CAPITAL", value=1000.0)
    perfil = st.selectbox("RISK", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input("TICKER", value="AAPL").upper()

# --- MAIN ---
st.title("💎 InvestIA Elite")

tab1, tab2 = st.tabs(["📊 Market", "💬 Chat"])

with tab1:
    if st.button("ANALYZE"):
        data = yf.download(ticket, period="2y")

        data.columns = data.columns.get_level_values(0)
        df = data.reset_index()[['Date','Close']]
        df.columns = ['ds','y']

        model = Prophet(daily_seasonality=True).fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        p_act = float(df['y'].iloc[-1])
        p_fut = float(forecast['yhat'].iloc[-1])
        cambio = ((p_fut - p_act) / p_act) * 100

        c1,c2,c3 = st.columns(3)
        c1.metric("Price", f"{p_act:.2f}")
        c2.metric("Target", f"{p_fut:.2f}", f"{cambio:.2f}%")
        c3.metric("Shares", f"{capital/p_act:.2f}")

        informe = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
        st.write(informe)

with tab2:
    for chat in st.session_state.chat_history:
        cls = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        label = "YOU" if chat["role"] == "user" else "AI"

        st.markdown(f"""
        <div class="chat-row">
            <div class="bubble {cls}">
                <div class="chat-label">{label}</div>
                {chat["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if msg := st.chat_input("Ask anything..."):
        st.session_state.chat_history.append({"role":"user","content":msg})

        r = generar_analisis_ia(
            st.session_state.lang,
            ticket,
            p_act if "p_act" in locals() else None,
            p_fut if "p_fut" in locals() else None,
            cambio if "cambio" in locals() else None,
            perfil,
            capital,
            msg
        )

        st.session_state.chat_history.append({"role":"assistant","content":r})
        st.rerun()
