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

/* Estilos de Chat Unificado a la Izquierda */
.chat-row { display: flex; margin-bottom: 12px; width: 100%; justify-content: flex-start; }
.bubble { 
    padding: 12px 16px; border-radius: 18px; 
    max-width: 85%; font-size: 14px; line-height: 1.5;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.user-bubble { background: #004d40; color: #e0f2f1; border-bottom-left-radius: 2px; border-left: 4px solid #64ffda; }
.ai-bubble { background: #1c2533; color: #cbd5e0; border-bottom-left-radius: 2px; border-left: 4px solid #48cae4; }
.chat-label { font-size: 10px; font-weight: bold; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; display: block; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": {
        "title":"InvestIA Elite", "lang_lab":"IDIOMA", "cap":"PRESUPUESTO", "risk_lab":"RIESGO",
        "ass_lab":"TICKER (Ej: NVDA)", "btn":"ANALIZAR MERCADO", "wait":"Procesando datos...", 
        "price":"Precio Actual", "target":"Predicción 30d", "shares":"Acciones posibles", 
        "analysis":"Análisis Estratégico IA", "chat_placeholder":"Pregunta sobre inversiones..."
    },
    "English": {
        "title":"InvestIA Elite", "lang_lab":"LANGUAGE", "cap":"BUDGET", "risk_lab":"RISK",
        "ass_lab":"TICKER (e.g. NVDA)", "btn":"ANALYZE MARKET", "wait":"Processing...", 
        "price":"Current Price", "target":"30-Day Target", "shares":"Shares you can buy", 
        "analysis":"AI Strategic Analysis", "chat_placeholder":"Ask about investments..."
    }
}

# --- FUNCION IA ---
def generar_analisis_ia(lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto_activo = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)." if ticket else ""
        prompt = f"""Actúa como analista senior. RESPONDE SIEMPRE EN {lang}. Perfil {perfil}, Capital {capital}€. {contexto_activo}
        Pregunta: {pregunta if pregunta else "Realiza un análisis estratégico."}"""
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    # Título de idioma arriba de la caja
    t_temp = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t_temp["lang_lab"]}</p>', unsafe_allow_html=True)
    
    lang_temp = st.selectbox("Select Language", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
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

# --- CUERPO ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat Advisor"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                df_prophet = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df_prophet)
                forecast = model.predict(model.make_future_dataframe(periods=30))

                p_act, p_fut = float(df_prophet['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100

                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket, "analizado": True})

                c1,c2,c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{capital/p_act:.2f}")

                fig_candles = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name=ticket)])
                fig_candles.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig_candles, use_container_width=True)

                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name="Real", line=dict(color='#48cae4')))
                fig_pred.add_trace(go.Scatter(x=forecast['ds'].iloc[-30:], y=forecast['yhat'].iloc[-30:], name="Predicción", line=dict(color='#64ffda', dash='dash')))
                fig_pred.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(fig_pred, use_container_width=True)

                informe = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"--- \n ### 📊 {t['analysis']}")
                st.write(informe)
            else: st.error("No data found.")

with tab2:
    for chat in st.session_state.chat_history:
        bubble_class = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        label = "YOU" if chat["role"] == "user" else "IA ADVISOR"
        st.markdown(f'''
            <div class="chat-row">
                <div class="bubble {bubble_class}">
                    <span class="chat-label">{label}</span>
                    {chat["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        r = generar_analisis_ia(st.session_state.lang, st.session_state.get("ticket_act"), st.session_state.get("p_act"), st.session_state.get("p_pre"), st.session_state.get("cambio"), perfil, capital, prompt_user)
        st.session_state.chat_history.append({"role": "assistant", "content": r})
        st.rerun()

