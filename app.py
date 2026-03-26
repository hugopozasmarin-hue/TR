import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# CONFIG
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* SIDEBAR MÁS ELEGANTE */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    padding: 20px;
}

/* TÍTULOS */
.field-title {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-top: 20px;
}

/* INPUTS */
.stNumberInput input, .stSelectbox div, .stTextInput input {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
}

/* BOTÓN */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #6366f1, #22d3ee);
    font-weight: bold;
    padding: 12px;
}

/* CHAT */
.bubble {
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}

.user-bubble { background: #6366f1; color: white; }
.assistant-bubble { background: #1e293b; color: #e2e8f0; }

.highlight { color: #22d3ee; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# IDIOMAS
languages = {
    "Español": {
        "title": "InvestMind AI Elite",
        "conf": "CONFIGURACIÓN",
        "cap": "PRESUPUESTO (€)",
        "risk": "PERFIL DE RIESGO",
        "asset": "ACTIVO",
        "btn": "EJECUTAR ANÁLISIS",
        "price": "Precio actual (€)",
        "target": "Precio predicho (30 días)",
        "shares": "Acciones que puedes comprar",
        "wait": "Analizando..."
    }
}

if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "AAPL"

t = languages["Español"]

# SIDEBAR
with st.sidebar:
    st.markdown(f"<div class='field-title'>{t['conf']}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='field-title'>{t['cap']}</div>", unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)

    st.markdown(f"<div class='field-title'>{t['risk']}</div>", unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])

    st.markdown(f"<div class='field-title'>{t['asset']}</div>", unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# IA
def hablar_con_ia_real(pregunta):
    api_key = "TU_API_KEY"
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": pregunta}]
    )
    return completion.choices[0].message.content

# MAIN
st.title(f"💎 {t['title']}")

tab1, tab2 = st.tabs(["📈 Análisis", "💬 Chat IA"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            datos = yf.download(ticket, period="5y")

            if not datos.empty:
                precio_actual = float(datos['Close'].iloc[-1])

                df = datos.reset_index()[['Date', 'Close']]
                df.columns = ['ds', 'y']
                df['ds'] = df['ds'].dt.tz_localize(None)

                modelo = Prophet().fit(df)
                futuro = modelo.make_future_dataframe(periods=30)
                pred = modelo.predict(futuro)

                precio_futuro = float(pred['yhat'].iloc[-1])

                cambio = ((precio_futuro - precio_actual) / precio_actual) * 100

                acciones = capital / precio_actual

                # MÉTRICAS CON TÍTULOS CLAROS
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    label="💰 Precio actual (€)",
                    value=f"{precio_actual:.2f}€"
                )

                col2.metric(
                    label="📈 Precio predicho (30 días)",
                    value=f"{precio_futuro:.2f}€",
                    delta=f"{cambio:.2f}%"
                )

                col3.metric(
                    label="🧮 Acciones que puedes comprar",
                    value=f"{acciones:.4f}"
                )

                st.line_chart(datos['Close'])

            else:
                st.error("Ticker no válido")

with tab2:
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f"<div class='bubble {clase}'>{msg['content']}</div>", unsafe_allow_html=True)

    if pregunta := st.chat_input("Pregunta..."):
        st.session_state.messages.append({"role": "user", "content": pregunta})

        respuesta = hablar_con_ia_real(pregunta)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()
