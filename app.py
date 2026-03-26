import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time

# 1. DICCIONARIO DE IDIOMAS (ES/EN/CAT)
languages = {
    "Español": {
        "title": "InvestMind AI", "config": "Configuración", "lang": "Idioma", "curr": "Moneda",
        "cap": "Inversión", "risk": "Riesgo", "asset": "Activo", "btn": "Analizar Mercado",
        "t1": "Panel de Control", "t2": "Chat Asesor", "p_now": "Precio Actual", "p_30": "Meta 30d",
        "shares": "Acciones", "diag": "Informe Estratégico de la IA", "wait": "Analizando...",
        "advice_header": "Análisis Detallado", "strategy": "Estrategia Recomendada", "risk_lvl": "Nivel de Riesgo"
    },
    "English": {
        "title": "InvestMind AI", "config": "Settings", "lang": "Language", "curr": "Currency",
        "cap": "Investment", "risk": "Risk", "asset": "Asset", "btn": "Analyze Market",
        "t1": "Dashboard", "t2": "AI Advisor", "p_now": "Current Price", "p_30": "30d Target",
        "shares": "Shares", "diag": "AI Strategic Report", "wait": "Analyzing...",
        "advice_header": "Detailed Analysis", "strategy": "Recommended Strategy", "risk_lvl": "Risk Level"
    },
    "Català": {
        "title": "InvestMind AI", "config": "Configuració", "lang": "Idioma", "curr": "Moneda",
        "cap": "Inversió", "risk": "Risc", "asset": "Actiu", "btn": "Analitzar Mercat",
        "t1": "Tauler de Control", "t2": "Xat Assessor", "p_now": "Preu Actual", "p_30": "Meta 30d",
        "shares": "Accions", "diag": "Informe Estratègic de la IA", "wait": "Analitzant...",
        "advice_header": "Anàlisi Detallada", "strategy": "Estratègia Recomanada", "risk_lvl": "Nivell de Risc"
    }
}

# 2. CONFIGURACIÓN Y CSS
st.set_page_config(page_title="InvestMind AI", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #333; }
    .sidebar-title { color: #888 !important; font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
    .stButton>button {
        width: 100%; border-radius: 8px; background: #007bff; color: white !important; font-weight: bold; border: none; padding: 10px;
    }
    .stButton>button:hover { background: #0056b3; transform: translateY(-1px); }
    .bubble { padding: 12px 18px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; line-height: 1.5; }
    .user-bubble { align-self: flex-end; background-color: #007bff; color: white !important; margin-left: auto; }
    .assistant-bubble { align-self: flex-start; background-color: #262730; color: white !important; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 4. BARRA LATERAL DISCRETA
with st.sidebar:
    # Ajustes mínimos
    with st.expander("⚙️", expanded=False):
        lang_sel = st.selectbox("Language", ["Español", "English", "Català"], label_visibility="collapsed")
    
    t = languages[lang_sel]
    st.markdown(f'<p class="sidebar-title">{t["config"]}</p>', unsafe_allow_html=True)
    
    moneda = st.radio(t["curr"], ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(t["cap"], min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk"], ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {"Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA", "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"}
    sel = st.selectbox(t["asset"], list(opciones.keys()))
    ticket = st.text_input("Ticker:").upper() if opciones[sel] == "CUSTOM" else opciones[sel]

# 5. CONTENIDO
st.title(f"🤖 {t['title']}")
tab1, tab2 = st.tabs([t["t1"], t["t2"]])

with tab1:
    if st.button(t["btn"]):
        if not ticket: st.warning("Ticker?")
        else:
            try:
                with st.status(t["wait"]) as s:
                    datos = yf.download(ticket, period="5y")
                    precio_act = float(datos['Close'].iloc[-1])
                    df_p = datos.reset_index()[['Date', 'Close']]
                    df_p.columns = ['ds', 'y']
                    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                    m = Prophet(daily_seasonality=True).fit(df_p)
                    pred = m.predict(m.make_future_dataframe(periods=30))
                    precio_pre = float(pred['yhat'].iloc[-1])
                    st.session_state.cambio = ((precio_pre - precio_act) / precio_act) * 100
                    st.session_state.analizado = True
                    s.update(label="OK", state="complete")

                # Métricas y Gráfica
                c1, c2, c3 = st.columns(3)
                c1.metric(t["p_now"], f"{precio_act:.2f} {simbolo}")
                c2.metric(t["p_30"], f"{precio_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/precio_act):.4f}")
                st.line_chart(datos['Close'])

                # --- RECOMENDACIÓN EXTENSA ---
                st.subheader(f"🔍 {t['diag']}")
                
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.markdown(f"### {t['advice_header']}")
                    st.write(f"Tras analizar el histórico de **{ticket}**, observamos una proyección de **{st.session_state.cambio:.2f}%**. Esta estimación se basa en patrones de estacionalidad y tendencias cíclicas detectadas por nuestra red neuronal.")
                    
                with col_right:
                    st.markdown(f"### {t['risk_lvl']}")
                    riesgo_color = "🟢 Bajo" if perfil == "Conservador" else "🟡 Medio" if perfil == "Moderado" else "🔴 Alto"
                    st.write(f"Tu perfil es **{perfil}**, por lo que el nivel de exposición recomendado es **{riesgo_color}**.")

                st.info(f"""
                **{t['strategy']}:**
                1. **Entrada:** El precio actual de {precio_act:.2f} {simbolo} se encuentra en zona de {'acumulación' if st.session_state.cambio > 5 else 'observación'}. 
                2. **Diversificación:** No comprometas más del 5-10% de tu capital total ({capital} {simbolo}) en este activo para evitar volatilidad excesiva.
                3. **Horizonte:** Aunque la predicción es a 30 días, la tendencia sugiere que {'es un buen momento para buscar beneficios rápidos' if st.session_state.cambio > 8 else 'es mejor una visión de medio plazo'}.
                4. **Stop-Loss:** Sugerimos colocar una orden de venta automática un 5% por debajo del precio actual para proteger tus ahorros.
                """)
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    st.subheader(t["t2"])
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)
    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        st.rerun()

st.caption("InvestMind AI v4.0")
