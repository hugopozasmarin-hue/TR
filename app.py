import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import plotly.graph_objects as go
import time

# 1. DICCIONARIO DE TRADUCCIÓN
languages = {
    "Español": {
        "title": "🤖 InvestMind AI: Tu Copiloto Financiero",
        "config": "📊 Configuración",
        "lang_label": "🌐 Idioma / Language",
        "currency": "Divisa:",
        "capital": "Inversión",
        "profile": "Riesgo:",
        "asset": "Activo:",
        "ticker_manual": "Ticker manual:",
        "candles": "Ver Gráfica de Velas (Pro)",
        "btn": "🚀 INICIAR ANÁLISIS",
        "tab1": "📈 Análisis Pro",
        "tab2": "💬 Chat Asesor",
        "price_now": "Precio Actual",
        "pred_30d": "Predicción 30d",
        "shares": "Acciones",
        "diag": "💡 Diagnóstico Estratégico",
        "warn_ticker": "⚠️ Selecciona un activo en el menú lateral."
    },
    "English": {
        "title": "🤖 InvestMind AI: Your Financial Copilot",
        "config": "📊 Configuration",
        "lang_label": "🌐 Language / Idioma",
        "currency": "Currency:",
        "capital": "Investment",
        "profile": "Risk:",
        "asset": "Asset:",
        "ticker_manual": "Manual Ticker:",
        "candles": "Show Candle Chart (Pro)",
        "btn": "🚀 START ANALYSIS",
        "tab1": "📈 Pro Analysis",
        "tab2": "💬 AI Advisor Chat",
        "price_now": "Current Price",
        "pred_30d": "30d Prediction",
        "shares": "Shares",
        "diag": "💡 Strategic Diagnosis",
        "warn_ticker": "⚠️ Please select an asset in the sidebar."
    }
}

# 2. CONFIGURACIÓN Y ESTILO CSS
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    /* COLOR PERSONALIZADO PARA CONFIGURACIÓN */
    .sidebar-title { color: #FF4B4B !important; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    
    .stNumberInput div div input, .stSelectbox div div div, .stTextInput div div input {
        background-color: #262730 !important; color: white !important; border: 1px solid #444 !important;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; transition: all 0.3s ease;
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white !important; font-weight: bold; padding: 12px;
    }
    .bubble { padding: 15px 20px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; color: white !important; }
    .user-bubble { align-self: flex-end; background-color: #007bff; margin-left: auto; }
    .assistant-bubble { align-self: flex-start; background-color: #262730; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 4. BARRA LATERAL (AJUSTES)
with st.sidebar:
    # NUEVO: Menú de Ajustes de Idioma
    with st.expander("🛠️ Ajustes de Sistema", expanded=True):
        lang_choice = st.selectbox("Idioma", ["Español", "English"], label_visibility="collapsed")
    
    t = languages[lang_choice] # Cargar textos del idioma elegido
    
    st.markdown(f'<p class="sidebar-title">{t["config"]}</p>', unsafe_allow_html=True)
    
    moneda = st.radio(t["currency"], ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(f"{t['capital']} ({simbolo})", min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["profile"], ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {"Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA", "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"}
    sel = st.selectbox(t["asset"], list(opciones.keys()))
    ticket = st.text_input(t["ticker_manual"]).upper() if opciones[sel] == "CUSTOM" else opciones[sel]
    
    st.divider()
    tipo_grafica = st.toggle(t["candles"], value=False)

# 5. CUERPO PRINCIPAL
st.title(t["title"])
tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

with tab1:
    if st.button(t["btn"]):
        if not ticket:
            st.warning(t["warn_ticker"])
        else:
            try:
                with st.status("Analizando...", expanded=False) as s:
                    # Descargamos datos con auto_adjust=False para asegurar Open/High/Low/Close para las velas
                    datos = yf.download(ticket, period="2y", auto_adjust=False)
                    
                    if datos.empty or len(datos) < 10:
                        st.error("Error: No hay datos suficientes.")
                    else:
                        precio_act = float(datos['Close'].iloc[-1])
                        
                        # IA Predicción
                        df_p = datos.reset_index()[['Date', 'Close']]
                        df_p.columns = ['ds', 'y']
                        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                        m = Prophet(daily_seasonality=True).fit(df_p)
                        pred = m.predict(m.make_future_dataframe(periods=30))
                        
                        precio_pre = float(pred['yhat'].iloc[-1])
                        st.session_state.cambio = ((precio_pre - precio_act) / precio_act) * 100
                        st.session_state.analizado = True
                        s.update(label="OK!", state="complete")
                        
                        # Métricas
                        c1, c2, c3 = st.columns(3)
                        c1.metric(t["price_now"], f"{precio_act:.2f} {simbolo}")
                        c2.metric(t["pred_30d"], f"{precio_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                        c3.metric(t["shares"], f"{(capital/precio_act):.4f}")
                        
                        # GRÁFICA DE VELAS CORREGIDA
                        if tipo_grafica:
                            # Filtramos los últimos 6 meses para que las velas se vean grandes y claras
                            datos_recientes = datos.tail(120) 
                            fig = go.Figure(data=[go.Candlestick(
                                x=datos_recientes.index,
                                open=datos_recientes['Open'],
                                high=datos_recientes['High'],
                                low=datos_recientes['Low'],
                                close=datos_recientes['Close'],
                                name='Market Data'
                            )])
                            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.line_chart(datos['Close'])
                        
                        st.divider()
                        st.subheader(t["diag"])
                        st.write(f"Trend: {'Bullish' if st.session_state.cambio > 0 else 'Bearish'} ({st.session_state.cambio:.2f}%)")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader(t["tab2"])
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

st.caption("InvestMind AI v3.0")
