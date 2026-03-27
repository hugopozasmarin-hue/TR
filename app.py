import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

GROQ_API_KEY = "TU_API_KEY_AQUI"

# --- IA ANALYSIS ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"

        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."

        prompt = f"""
        Act as a Senior Investment Strategist. Respond in {idioma_inst}.
        Data: {contexto}. Risk Profile: {perfil}. Capital: {capital}€.

        1. Action (Buy/Hold/Sell)
        2. Reasoning
        3. Outlook

        Question: {pregunta if pregunta else "General recommendation"}
        """

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error IA: {e}"


# --- IA CHAT (FIXED) ---
def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"

        contexto = (
            f"Ticker: {ticket}. Precio: {p_act}€. "
            f"Predicción: {p_fut}€. Cambio: {cambio:.2f}%"
            if ticket else "Sin ticker analizado."
        )

        prompt = f"""
        Actúa como un Senior Investment Strategist.
        Responde en {idioma_inst}.

        Contexto:
        - Perfil: {perfil}
        - Capital: {capital}€
        - {contexto}

        Puedes hablar de cualquier acción o tema financiero.

        Pregunta: {pregunta}
        """

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error IA: {e}"


# --- ESTILOS ---
st.markdown("""
<style>
.stApp { background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)


# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA TERMINAL",
        "btn": "ANALIZAR ACTIVO",
        "chat_placeholder": "Escribe tu consulta..."
    },
    "English": {
        "title": "INVESTIA TERMINAL",
        "btn": "ANALYZE ASSET",
        "chat_placeholder": "Type your question..."
    }
}


# --- SESSION ---
if "lang" not in st.session_state:
    st.session_state.lang = "Español"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analizado" not in st.session_state:
    st.session_state.analizado = False


t = languages[st.session_state.lang]


# --- SIDEBAR ---
with st.sidebar:
    lang = st.selectbox("Idioma", list(languages.keys()))
    st.session_state.lang = lang

    capital = st.number_input("Capital", value=1000.0)
    perfil = st.selectbox("Perfil", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input("Ticker", value="NVDA").upper()


# --- UI ---
st.title(t["title"])

tab1, tab2, tab3 = st.tabs(["📊 Análisis", "💬 Chat", "📰 Noticias"])


# --- ANALYSIS TAB ---
with tab1:
    if st.button(t["btn"]):
        data = yf.download(ticket, period="2y")

        if not data.empty:
            df = data.reset_index()[['Date', 'Close']]
            df.columns = ['ds', 'y']

            model = Prophet()
            model.fit(df)

            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            p_act = float(df['y'].iloc[-1])
            p_fut = float(forecast['yhat'].iloc[-1])
            cambio = ((p_fut - p_act) / p_act) * 100

            st.session_state.update({
                "p_act": p_act,
                "p_pre": p_fut,
                "cambio": cambio,
                "ticket_act": ticket,
                "analizado": True
            })

            st.session_state.analisis = generar_analisis_ia(
                st.session_state.lang,
                ticket,
                p_act,
                p_fut,
                cambio,
                perfil,
                capital
            )

    if st.session_state.analizado:
        st.write("Precio:", st.session_state.p_act)
        st.write("Predicción:", st.session_state.p_pre)
        st.write(st.session_state.get("analisis", ""))


# --- CHAT TAB (FIXED CALL) ---
with tab2:
    for msg in st.session_state.chat_history:
        st.write(f"**{msg['role']}**: {msg['content']}")

    if prompt := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        res = generar_chat_ia(
            st.session_state.lang,
            st.session_state.get("ticket_act", ""),
            st.session_state.get("p_act", 0),
            st.session_state.get("p_pre", 0),
            st.session_state.get("cambio", 0),
            perfil,
            capital,
            prompt
        )

        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()


# --- NEWS TAB ---
with tab3:
    st.write("Noticias próximamente...")
