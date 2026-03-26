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

# --- ESTILOS: FONDO BLANCO + MENÚ LATERAL OSCURO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    * { font-family: 'Inter', sans-serif; }
    
    /* Regreso al Menú Lateral Oscuro */
    [data-testid="stSidebar"] {
        background-color: #0a192f !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    .field-title { 
        color: #64ffda; font-size: 11px; font-weight: 700;
        letter-spacing: 1.2px; text-transform: uppercase;
        margin-bottom: 8px; margin-top: 15px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #dee2e6; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #6c757d; font-weight: 500; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { color: #000000 !important; border-bottom: 2px solid #000000 !important; }

    .stButton>button { 
        border: none; border-radius: 8px; background-color: #1a1a1a;
        color: #ffffff !important; font-weight: 600; height: 45px; transition: all 0.2s ease;
    }
    
    .metric-card {
        background: #ffffff; border: 1px solid #e9ecef;
        border-radius: 12px; padding: 20px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-label { font-size: 11px; color: #adb5bd; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 22px; font-weight: 700; color: #1a1a1a; margin-top: 5px; }

    .chat-row { display: flex; margin-bottom: 25px; justify-content: flex-start; }
    .bubble { 
        padding: 20px; border-radius: 12px; max-width: 85%; font-size: 15px;
        line-height: 1.6; background: #ffffff; border: 1px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .user-bubble { border-left: 4px solid #adb5bd; }
    .ai-bubble { border-left: 4px solid #1a1a1a; }
    .chat-label { font-size: 10px; font-weight: 800; display: block; margin-bottom: 12px; letter-spacing: 1px; color: #212529; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": { "title":"INVESTIA ELITE", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", "btn":"EJECUTAR ANÁLISIS", "wait":"Procesando...", "price":"Precio Actual", "target":"Objetivo 30d", "shares":"Capacidad Compra", "analysis":"Estrategia Institucional", "chat_placeholder":"Escribe tu consulta..." },
    "English": { "title":"INVESTIA ELITE", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", "btn":"EXECUTE ANALYSIS", "wait":"Processing...", "price":"Current Price", "target":"30-Day Target", "shares":"Buying Capacity", "analysis":"Institutional Strategy", "chat_placeholder":"Type your query..." }
}

# --- FUNCIÓN IA (CORREGIDA) ---
def generar_analisis_ia(lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)." if ticket else ""
        prompt = f"Asesor Senior. Idioma: {lang}. Perfil: {perfil}. Capital: {capital}€. {contexto} Pregunta: {pregunta if pregunta else 'Informe detallado.'}"
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], 
            model="llama-3.3-70b-versatile"
        )
        # CORRECCIÓN AQUÍ: Se añade [0] para acceder a la primera opción
        return response.choices[0].message.content
    except Exception as e: 
        return f"Error: {e}"

# --- GESTIÓN DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
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

# --- CUERPO ---
st.markdown(f"<h1 style='text-align: center; font-weight: 800; color: #1a1a1a; margin-top: 20px;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #adb5bd; font-weight: 500; font-size: 12px; letter-spacing: 2px; margin-bottom: 50px;'>QUANTITATIVE INTELLIGENCE TERMINAL</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([f"📊 {t['btn']}", "💬 AI ADVISOR"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df_p)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df_p['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket, "analizado": True})

                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['price']}</div><div class='metric-value'>{p_act:.2f}€</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['target']}</div><div class='metric-value'>{p_fut:.2f}€ ({cambio:+.2f}%)</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['shares']}</div><div class='metric-value'>{capital/p_act:.2f}</div></div>", unsafe_allow_html=True)

                fig1 = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name=ticket)])
                fig1.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig1, use_container_width=True)

                st.markdown(f"<div style='background:#f8f9fa; padding:30px; border-radius:12px; border:1px solid #e9ecef;'><h3>📊 {t['analysis']}</h3><div style='line-height:1.6;'>{generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)}</div></div>", unsafe_allow_html=True)
            else: st.error("Asset not found.")

with tab2:
    for chat in st.session_state.chat_history:
        b_class = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="chat-row"><div class="bubble {b_class}"><span class="chat-label">{"INVERSOR" if chat["role"]=="user" else "IA STRATEGIST"}</span><div style="white-space: pre-wrap;">{chat["content"]}</div></div></div>', unsafe_allow_html=True)

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        res = generar_analisis_ia(st.session_state.lang, st.session_state.get("ticket_act"), st.session_state.get("p_act"), st.session_state.get("p_pre"), st.session_state.get("cambio"), perfil, capital, prompt_user)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()
