import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time

# 1. CONFIGURACIÓN Y ESTILO CSS MEJORADO
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* Botones con animación */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        transition: all 0.3s ease;
        background-color: #007bff;
        color: white !important;
        border: none;
        font-weight: bold;
        padding: 10px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,123,255,0.4);
    }
    
    /* Burbujas de Chat Optimizadas */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-top: 20px;
    }
    .bubble {
        padding: 15px 20px;
        border-radius: 20px;
        max-width: 80%;
        font-size: 16px;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    .user-bubble {
        align-self: flex-end;
        background-color: #007bff;
        color: white !important;
        border-bottom-right-radius: 2px;
    }
    .assistant-bubble {
        align-self: flex-start;
        background-color: #262730; /* Color oscuro neutral de Streamlit */
        color: #ffffff !important;
        border-bottom-left-radius: 2px;
        border: 1px solid #464646;
    }
    
    /* Texto dentro de las burbujas para asegurar visibilidad */
    .bubble p, .bubble span {
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 3. BARRA LATERAL
with st.sidebar:
    st.header("⚙️ Configuración")
    moneda = st.radio("Moneda:", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(f"Capital ({simbolo})", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Tu Perfil:", ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {"Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA", "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"}
    sel = st.selectbox("Activo:", list(opciones.keys()))
    ticket = st.text_input("Ticker manual:").upper() if opciones[sel] == "CUSTOM" else opciones[sel]

# 4. CUERPO PRINCIPAL
st.title("🤖 InvestMind AI")
t1, t2 = st.tabs(["📈 Análisis", "💬 Chat"])

with t1:
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.status("Procesando datos...", expanded=False) as s:
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                precio_act = float(datos['Close'].iloc[-1])
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                st.session_state.cambio = ((float(pred['yhat'].iloc[-1]) - precio_act) / precio_act) * 100
                st.session_state.analizado = True
                s.update(label="Análisis Completo!", state="complete")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Hoy", f"{precio_act:.2f} {simbolo}")
                c2.metric("Meta 30d", f"{float(pred['yhat'].iloc[-1]):.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric("Acciones", f"{(capital/precio_act):.4f}")
                st.line_chart(datos['Close'])
            else: st.error("Error de datos.")

with t2:
    st.subheader("💬 Consultoría en Tiempo Real")
    
    # Contenedor de chat
    for m in st.session_state.messages:
        clase = "user-bubble" if m["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{m["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Escribe tu duda..."):
        st.session_state.messages.append({"role": "user", "content": p})
        st.markdown(f'<div class="bubble user-bubble">{p}</div>', unsafe_allow_html=True)
        
        with st.spinner("Escribiendo..."):
            time.sleep(0.5)
            info = f"un cambio del {st.session_state.cambio:.2f}%" if st.session_state.analizado else "tendencia aún no analizada"
            res = f"Como experto para un perfil **{perfil}**, veo que **{ticket}** muestra una {info}. Para tus **{capital}{simbolo}**, sugiero cautela. ¿Quieres más detalles?"
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.markdown(f'<div class="bubble assistant-bubble">{res}</div>', unsafe_allow_html=True)
            st.rerun() # Refresca para limpiar el input y mostrar todo ordenado
