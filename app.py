import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import random

# 1. DICCIONARIO DE IDIOMAS Y TEXTOS
languages = {
    "Español": {
        "title": "InvestMind AI", "config": "Configuración", "curr": "Moneda",
        "cap": "Inversión", "risk": "Riesgo", "asset": "Activo", "btn": "Analizar Mercado",
        "t1": "Panel de Control", "t2": "Chat Asesor", "p_now": "Precio Actual", "p_30": "Meta 30d",
        "shares": "Acciones", "diag": "Informe Estratégico", "wait": "Analizando...",
        "advice_h": "Análisis Detallado", "strategy": "Estrategia Recomendada", "risk_lvl": "Nivel de Riesgo",
        "inf_1": "Tras analizar", "inf_2": "observamos una proyección de",
        "str_1": "Entrada", "str_2": "Diversificación", "str_3": "Horizonte", "str_4": "Stop-Loss",
    },
    "English": {
        "title": "InvestMind AI", "config": "Settings", "curr": "Currency",
        "cap": "Investment", "risk": "Risk", "asset": "Asset", "btn": "Analyze Market",
        "t1": "Dashboard", "t2": "AI Advisor", "p_now": "Current Price", "p_30": "30d Target",
        "shares": "Shares", "diag": "Strategic Report", "wait": "Analyzing...",
        "advice_h": "Detailed Analysis", "strategy": "Recommended Strategy", "risk_lvl": "Risk Level",
        "inf_1": "After analyzing", "inf_2": "we observe a projection of",
        "str_1": "Entry", "str_2": "Diversification", "str_3": "Horizon", "str_4": "Stop-Loss",
    },
    "Català": {
        "title": "InvestMind AI", "config": "Configuració", "curr": "Moneda",
        "cap": "Inversió", "risk": "Risc", "asset": "Actiu", "btn": "Analitzar Mercat",
        "t1": "Tauler de Control", "t2": "Xat Assessor", "p_now": "Preu Actual", "p_30": "Meta 30d",
        "shares": "Accions", "diag": "Informe Estratègic", "wait": "Analitzant...",
        "advice_h": "Anàlisi Detallada", "strategy": "Estratègia Recomanada", "risk_lvl": "Nivell de Risc",
        "inf_1": "Després d'analitzar", "inf_2": "observem una projecció de",
        "str_1": "Entrada", "str_2": "Diversificació", "str_3": "Horitzó", "str_4": "Stop-Loss",
    }
}

# 2. CONFIGURACIÓN Y CSS (RECUADROS VISIBLES)
st.set_page_config(page_title="InvestMind AI", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #333; }
    .stNumberInput div div input, .stSelectbox div div div, .stTextInput div div input {
        background-color: #3b3d4a !important; color: white !important; border: 1px solid #555 !important;
    }
    .sidebar-title { color: #888 !important; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 8px; background: #007bff; color: white !important; font-weight: bold; border: none; padding: 10px; }
    .bubble { padding: 12px 18px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; color: white !important; font-size: 15px; }
    .user-bubble { align-self: flex-end; background-color: #007bff; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { align-self: flex-start; background-color: #262730; border: 1px solid #444; border-bottom-left-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 4. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️", expanded=False):
        lang_sel = st.selectbox("Lang", ["Español", "English", "Català"], label_visibility="collapsed")
    
    t = languages[lang_sel]
    st.markdown(f'<p class="sidebar-title">{t["config"]}</p>', unsafe_allow_html=True)
    moneda = st.radio(t["curr"], ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(t["cap"], min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk"], ["Conservador", "Moderado", "Arriesgado"])
    
    # TICKERS SIN NOMBRES LARGOS
    opciones = ["AAPL", "TSLA", "NVDA", "BTC-USD", "MSFT", "SAN.MC", "CUSTOM"]
    sel = st.selectbox(t["asset"], opciones)
    ticket = st.text_input("Ticker:").upper() if sel == "CUSTOM" else sel

# 5. CUERPO PRINCIPAL
st.title(f"🤖 {t['title']}")
tab1, tab2 = st.tabs([t["t1"], t["t2"]])

with tab1:
    if st.button(t["btn"]):
        if ticket:
            with st.status(t["wait"]) as s:
                datos = yf.download(ticket, period="5y")
                if not datos.empty:
                    p_act = float(datos['Close'].iloc[-1])
                    df_p = datos.reset_index()[['Date', 'Close']]
                    df_p.columns = ['ds', 'y']
                    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                    m = Prophet(daily_seasonality=True).fit(df_p)
                    pred = m.predict(m.make_future_dataframe(periods=30))
                    p_pre = float(pred['yhat'].iloc[-1])
                    st.session_state.cambio = ((p_pre - p_act) / p_act) * 100
                    st.session_state.analizado = True
                    s.update(label="OK", state="complete")

                    c1, c2, c3 = st.columns(3)
                    c1.metric(t["p_now"], f"{p_act:.2f} {simbolo}")
                    c2.metric(t["p_30"], f"{p_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                    c3.metric(t["shares"], f"{(capital/p_act):.4f}")
                    st.line_chart(datos['Close'])

                    st.subheader(f"🔍 {t['diag']}")
                    st.info(f"**{t['advice_h']}:** {t['inf_1']} **{ticket}**, {t['inf_2']} **{st.session_state.cambio:.2f}%**.")

with tab2:
    st.subheader(t["t2"])
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        p_lower = p.lower()
        
        # --- LÓGICA DE RESPUESTA DINÁMICA ---
        if any(x in p_lower for x in ["hola", "buenas", "hi"]):
            res = f"¡Hola! Soy tu asistente InvestMind en {lang_sel}. He visto que te interesa {ticket}. ¿Quieres que analicemos su riesgo?"
        elif any(x in p_lower for x in ["mejor", "invertir", "donde"]):
            res = f"La mejor inversión depende de tu perfil {perfil}. Actualmente {ticket} tiene una proyección de {st.session_state.cambio:.2f}%. ¿Es suficiente para ti?"
        elif any(x in p_lower for x in ["riesgo", "perder", "peligro"]):
            res = f"Al ser un perfil {perfil}, el riesgo con {ticket} es {'moderado' if st.session_state.cambio > 0 else 'alto'}. No inviertas dinero que necesites pronto."
        elif any(x in p_lower for x in ["gracias", "adios", "chau"]):
            res = "¡De nada! Aquí estaré si necesitas más análisis financieros. ¡Buena suerte!"
        else:
            res = f"Entiendo tu duda sobre '{p}'. Con los datos actuales de {ticket} ({st.session_state.cambio:.2f}%), mi consejo es mantener la estrategia {perfil}."
            
        st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

st.caption("InvestMind AI v5.1 | Financial Thought Partner")

