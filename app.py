import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ PON AQUÍ TU API KEY ---
GROQ_API_KEY = "PON_AQUI_TU_API_KEY" 

# --- ESTILOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }
.field-title { 
    color: #64ffda; font-size: 10px; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 20px; margin-bottom: 8px;
}
.stButton>button { 
    width: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #64ffda, #48cae4);
    color: #0a192f !important; font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title":"InvestIA Elite", "lang_lab":"IDIOMA", "cap":"PRESUPUESTO", "risk_lab":"RIESGO",
        "ass_lab":"TICKER", "btn":"ANALIZAR", "wait":"Procesando...", "price":"Precio actual",
        "target":"Predicción 30d", "shares":"Acciones posibles", "analysis":"Análisis IA",
        "chat_placeholder":"Pregunta a la IA..."
    },
    "English": {
        "title":"InvestIA Elite", "lang_lab":"LANGUAGE", "cap":"BUDGET", "risk_lab":"RISK",
        "ass_lab":"TICKER", "btn":"ANALYZE", "wait":"Processing...", "price":"Current Price",
        "target":"30-Day Target", "shares":"Possible Shares", "analysis":"AI Analysis",
        "chat_placeholder":"Ask the AI..."
    }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""Actúa como analista senior. Activo: {ticket}. Perfil: {perfil}. Capital: {capital}€.
        Precio: {precio_actual}€ -> Predicción 30d: {precio_futuro}€ ({cambio:.2f}%).
        Analiza riesgos, estrategia y responde: {pregunta if pregunta else "Análisis general"}."""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"

# --- INICIALIZACIÓN DE ESTADO ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()))
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0)
    perfil = st.selectbox(t["risk_lab"], ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(t["ass_lab"], value="AAPL").upper()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="5y")

            if not data.empty:
                # --- CORRECCIÓN AQUÍ: Aplanar columnas y quitar zona horaria ---
                data.columns = data.columns.get_level_values(0) 
                df = data.reset_index()[['Date', 'Close']]
                df.columns = ['ds', 'y']
                df['ds'] = df['ds'].dt.tz_localize(None) 

                model = Prophet(daily_seasonality=True).fit(df)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)

                precio_actual = float(df['y'].iloc[-1])
                precio_futuro = float(forecast['yhat'].iloc[-1])
                cambio = ((precio_futuro - precio_actual)/precio_actual)*100

                st.session_state.update({"p_act": precio_actual, "p_pre": precio_futuro, 
                                       "cambio": cambio, "ticket_act": ticket, "analizado": True})

                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{precio_actual:.2f}€")
                c2.metric(t["target"], f"{precio_futuro:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/precio_actual):.2f}")

                st.line_chart(df.set_index('ds')['y'])
                
                with st.spinner("🧠 Generando análisis..."):
                    analisis = generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital)
                st.markdown(f"### {t['analysis']}")
                st.write(analisis)
            else:
                st.error("Ticker no encontrado.")

with tab2:
    if st.session_state.analizado:
        for msg in st.session_state.chat_messages: st.write(msg)
        user_msg = st.text_input(t["chat_placeholder"], key="chat_input")
        if user_msg:
            resp = generar_analisis_ia(st.session_state.ticket_act, st.session_state.p_act, 
                                     st.session_state.p_pre, st.session_state.cambio, perfil, capital, user_msg)
            st.session_state.chat_messages.append(f"**Tú:** {user_msg}")
            st.session_state.chat_messages.append(f"**IA:** {resp}")
            st.rerun() # Versión actualizada
    else:
        st.info("Primero realiza un análisis en la pestaña principal.")

