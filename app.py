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

# --- DISEÑO DE VANGUARDIA (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    /* Variables y Reset */
    :root {
        --bg-deep: #050a14;
        --accent: #64ffda;
        --secondary: #48cae4;
        --glass: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at top right, #0a192f, #050a14);
    }

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: #050a14 !important;
        border-right: 1px solid var(--glass-border);
    }
    
    .field-title { 
        color: var(--accent); font-size: 11px; font-weight: 800;
        letter-spacing: 1.8px; text-transform: uppercase;
        margin-bottom: 10px; opacity: 0.8;
    }

    /* Tabs Modernos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; border-radius: 10px; border: none;
        background-color: var(--glass); color: white;
        transition: all 0.3s ease; padding: 0 25px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #64ffda33, #48cae433) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Botón Premium */
    .stButton>button { 
        border: none; border-radius: 12px;
        background: linear-gradient(135deg, var(--accent), var(--secondary));
        color: #050a14 !important; font-weight: 700;
        height: 48px; letter-spacing: 0.5px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(100, 255, 218, 0.3);
    }

    /* Tarjetas de Métricas Custom */
    .metric-card {
        background: var(--glass); border: 1px solid var(--glass-border);
        border-radius: 16px; padding: 20px; text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: 800; color: white; }

    /* Chat Estilo Consultoría de Lujo */
    .chat-row { display: flex; margin-bottom: 20px; justify-content: flex-start; }
    .bubble { 
        padding: 16px 20px; border-radius: 20px; 
        max-width: 85%; font-size: 15px; line-height: 1.6;
        backdrop-filter: blur(10px);
    }
    .user-bubble { 
        background: rgba(100, 255, 218, 0.1); color: #e2e8f0; 
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-left: 5px solid var(--accent);
    }
    .ai-bubble { 
        background: rgba(72, 202, 228, 0.05); color: #cbd5e1; 
        border: 1px solid rgba(72, 202, 228, 0.1);
        border-left: 5px solid var(--secondary);
    }
    .chat-label { 
        font-size: 10px; font-weight: 800; margin-bottom: 6px; 
        letter-spacing: 1.2px; color: var(--accent); opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": {
        "title":"INVESTIA ELITE", "lang_lab":"Ajustes de Idioma", "cap":"Capital de Inversión", "risk_lab":"Perfil de Riesgo",
        "ass_lab":"Símbolo del Activo", "btn":"EJECUTAR ANÁLISIS", "wait":"IA Procesando datos...", 
        "price":"Precio Actual", "target":"Objetivo 30d", "shares":"Capacidad Compra", 
        "analysis":"Estrategia Institucional", "chat_placeholder":"Consultar a la IA..."
    },
    "English": {
        "title":"INVESTIA ELITE", "lang_lab":"Language Settings", "cap":"Investment Capital", "risk_lab":"Risk Profile",
        "ass_lab":"Asset Ticker", "btn":"EXECUTE ANALYSIS", "wait":"AI Processing...", 
        "price":"Current Price", "target":"30-Day Target", "shares":"Buying Capacity", 
        "analysis":"Institutional Strategy", "chat_placeholder":"Ask the IA Advisor..."
    }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)." if ticket else ""
        prompt = f"""Actúa como analista senior de un Hedge Fund. RESPONDE SIEMPRE EN {lang}. Perfil {perfil}, Capital {capital}€. {contexto}
        Pregunta: {pregunta if pregunta else "Realiza un informe de inversión institucional."}"""
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- GESTIÓN DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR PREMIUM ---
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

# --- CUERPO PRINCIPAL ---
st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px; font-weight: 800; color: white;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64ffda; opacity: 0.6; font-size: 13px; margin-bottom: 40px;'>ADVANCED QUANTITATIVE AI ANALYSIS</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([f"📊 {t['btn']}", "💬 AI ADVISOR"])

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

                # Métricas Estilizadas
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['price']}</div><div class='metric-value'>{p_act:.2f}€</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['target']}</div><div class='metric-value' style='color:#64ffda'>{p_fut:.2f}€ ({cambio:+.2f}%)</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['shares']}</div><div class='metric-value'>{capital/p_act:.2f}</div></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Gráficas
                fig_candles = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name=ticket)])
                fig_candles.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_candles, use_container_width=True)

                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name="Histórico", line=dict(color='#48cae4', width=2)))
                fig_pred.add_trace(go.Scatter(x=forecast['ds'].iloc[-30:], y=forecast['yhat'].iloc[-30:], name="Predicción", line=dict(color='#64ffda', width=3, dash='dot')))
                fig_pred.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pred, use_container_width=True)

                st.markdown(f"<div style='background:var(--glass); padding:30px; border-radius:20px; border:1px solid var(--glass-border);'><h3>📊 {t['analysis']}</h3>{generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)}</div>", unsafe_allow_html=True)
            else: st.error("Asset not found.")

with tab2:
    for chat in st.session_state.chat_history:
        b_class = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        label = "INVERSOR" if chat["role"] == "user" else "IA STRATEGIST"
        st.markdown(f'<div class="chat-row"><div class="bubble {b_class}"><span class="chat-label">{label}</span>{chat["content"]}</div></div>', unsafe_allow_html=True)

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        res = generar_analisis_ia(st.session_state.lang, st.session_state.get("ticket_act"), st.session_state.get("p_act"), st.session_state.get("p_pre"), st.session_state.get("cambio"), perfil, capital, prompt_user)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()
