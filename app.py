import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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"

# --- ESTILOS CSS CUSTOM ---
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
    color: #0a192f !important; font-weight: 800; border: none;
}
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": {
        "title":"InvestIA Elite", "lang_lab":"IDIOMA", "cap":"PRESUPUESTO", "risk_lab":"RIESGO",
        "ass_lab":"TICKER (Ej: NVDA)", "btn":"ANALIZAR MERCADO", "wait":"Procesando datos...", 
        "price":"Precio Actual", "target":"Predicción 30d", "shares":"Acciones posibles", 
        "analysis":"Análisis Estratégico IA", "chat_placeholder":"Pregunta sobre cualquier tema de inversión..."
    },
    "English": {
        "title":"InvestIA Elite", "lang_lab":"LANGUAGE", "cap":"BUDGET", "risk_lab":"RISK",
        "ass_lab":"TICKER (e.g. NVDA)", "btn":"ANALYZE MARKET", "wait":"Processing...", 
        "price":"Current Price", "target":"30-Day Target", "shares":"Shares you can buy", 
        "analysis":"AI Strategic Analysis", "chat_placeholder":"Ask about any investment topic..."
    }
}

# --- FUNCION IA ---
def generar_analisis_ia(lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Contexto dinámico: si hay datos de ticker los incluye, si no, es consulta general
        contexto_activo = ""
        if ticket:
            contexto_activo = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)."

        prompt = f"""
Actúa como analista senior de Wall Street. RESPONDE SIEMPRE EN {lang}.
Contexto del usuario: Perfil {perfil}, Capital {capital}€.
{contexto_activo}

Instrucción: Si el usuario hace una pregunta general sobre inversiones, responde como experto global. 
Si pregunta sobre el activo actual, integra los datos técnicos proporcionados.
Pregunta del usuario: {pregunta if pregunta else "Realiza un análisis estratégico del activo actual."}
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error en el motor de IA: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL", label_visibility="collapsed").upper()

# --- CUERPO ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat de Inversión"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                df_prophet = data.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df_prophet)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)

                p_act = float(df_prophet['y'].iloc[-1])
                p_fut = float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100

                st.session_state.update({
                    "p_act": p_act, "p_pre": p_fut, "cambio": cambio,
                    "ticket_act": ticket, "analizado": True
                })

                # Métricas
                c1,c2,c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{capital/p_act:.2f}")

                # Gráfica Velas
                fig_candles = go.Figure(data=[go.Candlestick(
                    x=data.index, open=data['Open'], high=data['High'],
                    low=data['Low'], close=data['Close'], name=ticket
                )])
                fig_candles.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig_candles, use_container_width=True)

                # Proyección
                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name="Real", line=dict(color='#48cae4')))
                fig_pred.add_trace(go.Scatter(x=forecast['ds'].iloc[-30:], y=forecast['yhat'].iloc[-30:], name="Predicción", line=dict(color='#64ffda', dash='dash')))
                fig_pred.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(fig_pred, use_container_width=True)

                # Análisis IA (AHORA EN EL IDIOMA SELECCIONADO)
                informe = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"--- \n ### 📊 {t['analysis']}")
                st.write(informe)
            else:
                st.error("No se encontraron datos.")

with tab2:
    st.markdown("### 💬 Consultoría Global")
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        with st.chat_message("user"): st.write(prompt_user)
        
        with st.chat_message("assistant"):
            # Si no se ha analizado nada, enviamos parámetros vacíos pero permitimos que el chat funcione
            r = generar_analisis_ia(
                st.session_state.lang,
                st.session_state.get("ticket_act"),
                st.session_state.get("p_act"),
                st.session_state.get("p_pre"),
                st.session_state.get("cambio"),
                perfil,
                capital,
                prompt_user
            )
            st.write(r)
        st.session_state.chat_history.append({"role": "assistant", "content": r})
        st.rerun()
