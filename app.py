import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    * { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #0a192f !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    .field-title {
        color: #64ffda;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 15px;
    }

    .stButton>button {
        border: none;
        border-radius: 8px;
        background-color: #1a1a1a;
        color: #ffffff !important;
        font-weight: 600;
        height: 45px;
    }

    .chat-row {
        display: flex;
        margin-bottom: 25px;
        justify-content: flex-start;
    }

    .bubble {
        padding: 20px;
        border-radius: 12px;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.6;
        background: #ffffff;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA ELITE", 
        "lang_lab":"Idioma", 
        "cap":"Presupuesto", 
        "risk_lab":"Riesgo", 
        "ass_lab":"Ticker", 
        "btn":"EJECUTAR ANÁLISIS", 
        "wait":"Procesando...", 
        "price":"Precio Actual", 
        "target":"Objetivo 30d", 
        "shares":"Capacidad Compra", 
        "analysis":"Estrategia Institucional", 
        "hist_t":"Tendencia Histórica", 
        "pred_t":"Proyección IA (30 días)",
        "chat_placeholder":"Pregunta sobre inversiones..."
    },
    "English": { 
        "title":"INVESTIA ELITE", 
        "lang_lab":"Language", 
        "cap":"Budget", 
        "risk_lab":"Risk Profile", 
        "ass_lab":"Asset Ticker", 
        "btn":"EXECUTE ANALYSIS", 
        "wait":"Processing...", 
        "price":"Current Price", 
        "target":"30-Day Target", 
        "shares":"Buying Capacity", 
        "analysis":"Institutional Strategy", 
        "hist_t":"Historical Trend", 
        "pred_t":"AI Projection (30 Days)",
        "chat_placeholder":"Ask about investments..."
    }
}

# --- IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)."
        prompt = f"Asesor Senior. RESPONDE EN {lang}. Perfil: {perfil}. Capital: {capital}€. {contexto} Pregunta: {pregunta if pregunta else 'Informe institucional.'}"
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state:
    st.session_state.lang = "Español"

if "analizado" not in st.session_state:
    st.session_state.analizado = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR (TU DISEÑO) ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()

    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL", label_visibility="collapsed").upper()

# --- UI ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs(["📊 Análisis", "💬 Chat IA"])

# --- ANÁLISIS ---
with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")

            if not data.empty:
                data.columns = data.columns.get_level_values(0)

                df = data.reset_index()[['Date', 'Close']]
                df.columns = ['ds', 'y']
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))

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

                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{capital/p_act:.2f}")

                st.session_state.analisis = generar_analisis_ia(
                    st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital
                )

            else:
                st.error("Ticker no válido")

    if st.session_state.analizado:
        st.markdown("### 📊 Análisis IA")
        st.write(st.session_state.get("analisis", ""))

# --- CHAT ---
with tab2:
    for msg in st.session_state.chat_history:
        st.markdown(f"**{msg['role'].upper()}**: {msg['content']}")

    if prompt := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        respuesta = generar_analisis_ia(
            st.session_state.lang,
            st.session_state.get("ticket_act", "N/A"),
            st.session_state.get("p_act", 0),
            st.session_state.get("p_pre", 0),
            st.session_state.get("cambio", 0),
            perfil,
            capital,
            prompt
        )

        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        st.rerun()
