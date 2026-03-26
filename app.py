import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import plotly.graph_objects as go
import time

# 1. CONFIGURACIÓN Y ESTILO CSS
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")

# Aseguramos que plotly esté en el requirements.txt (añádelo si no está)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .stNumberInput div div input, .stSelectbox div div div, .stTextInput div div input {
        background-color: #262730 !important; color: white !important; border: 1px solid #444 !important;
    }
    .sidebar-title { color: #007bff; font-size: 22px; font-weight: bold; }
    .stButton>button {
        width: 100%; border-radius: 12px; transition: all 0.3s ease;
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white !important; font-weight: bold; padding: 12px;
    }
    .bubble { padding: 15px 20px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; }
    .user-bubble { align-self: flex-end; background-color: #007bff; color: white !important; margin-left: auto; }
    .assistant-bubble { align-self: flex-start; background-color: #262730; color: white !important; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# 2. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown('<p class="sidebar-title">📊 Configuración</p>', unsafe_allow_html=True)
    moneda = st.radio("Divisa:", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(f"Inversión ({simbolo})", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Riesgo:", ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {"Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA", "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"}
    sel = st.selectbox("Activo:", list(opciones.keys()))
    ticket = st.text_input("Ticker manual:").upper() if opciones[sel] == "CUSTOM" else opciones[sel]
    
    st.divider()
    tipo_grafica = st.toggle("Ver Gráfica de Velas (Pro)", value=False)

# 4. CUERPO PRINCIPAL
st.title("🤖 InvestMind AI")
t1, t2 = st.tabs(["📈 Análisis Pro", "💬 Chat Asesor"])

with t1:
    if st.button("🚀 INICIAR ANÁLISIS"):
        if not ticket:
            st.warning("⚠️ Selecciona un activo en el menú lateral.")
        else:
            try:
                with st.status("Analizando mercado...", expanded=False) as s:
                    datos = yf.download(ticket, period="1y") # Usamos 1 año para que las velas se vean claras
                    
                    if datos.empty:
                        st.error("No hay datos.")
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
                        s.update(label="¡Análisis listo!", state="complete")
                        
                        # Métricas
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Precio Actual", f"{precio_act:.2f} {simbolo}")
                        c2.metric("Predicción 30d", f"{precio_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                        c3.metric("Acciones", f"{(capital/precio_act):.4f}")
                        
                        # LÓGICA DE GRÁFICA (Velas vs Línea)
                        if tipo_grafica:
                            fig = go.Figure(data=[go.Candlestick(x=datos.index,
                                            open=datos['Open'], high=datos['High'],
                                            low=datos['Low'], close=datos['Close'],
                                            name='Velas')])
                            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.line_chart(datos['Close'])
                        
                        # Informe directo
                        st.divider()
                        st.subheader("💡 Diagnóstico Estratégico")
                        st.write(f"Para tu perfil **{perfil}**, la IA proyecta un {'ascenso' if st.session_state.cambio > 0 else 'descenso'} hacia los {precio_pre:.2f} {simbolo}.")
                        st.info(f"**Consejo:** {'Es un buen momento de entrada técnica.' if st.session_state.cambio > 4 else 'Mantén liquidez y espera mejores confirmaciones.'}")
            except Exception as e:
                st.error(f"Error: {e}")

with t2:
    st.subheader("💬 Consultoría")
    for m in st.session_state.messages:
        clase = "user-bubble" if m["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{m["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Escribe tu duda..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("IA Pensando..."):
            time.sleep(0.5)
            res = f"Basado en {ticket} y tu perfil {perfil}, mi análisis indica una tendencia de {st.session_state.cambio:.2f}%. ¿Te gustaría saber más sobre el volumen de trading?"
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()
