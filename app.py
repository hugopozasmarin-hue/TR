import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time

# 1. CONFIGURACIÓN Y ESTILO CSS (MENÚ Y BOTONES)
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* Estética del Menú Lateral */
    [data-testid="stSidebar"] {
        background-color: #111217;
        padding: 20px;
        border-right: 1px solid #333;
    }
    .sidebar-title {
        color: #007bff;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Botones Animados */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        transition: all 0.3s ease;
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white !important;
        border: none;
        font-weight: bold;
        padding: 12px;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,123,255,0.4);
    }
    
    /* Burbujas de Chat */
    .bubble {
        padding: 15px 20px;
        border-radius: 18px;
        margin-bottom: 12px;
        max-width: 85%;
        font-size: 15px;
    }
    .user-bubble {
        align-self: flex-end;
        background-color: #007bff;
        color: white !important;
        margin-left: auto;
    }
    .assistant-bubble {
        align-self: flex-start;
        background-color: #262730;
        color: white !important;
        border: 1px solid #444;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 3. BARRA LATERAL ESTÉTICA
with st.sidebar:
    st.markdown('<p class="sidebar-title">📊 Configuración</p>', unsafe_allow_html=True)
    
    st.markdown("### 💱 Divisa")
    moneda = st.radio("Selecciona:", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    
    st.markdown("### 💰 Capital")
    capital = st.number_input(f"Inversión ({simbolo})", min_value=1.0, value=1000.0, label_visibility="collapsed")
    
    st.markdown("### 🛡️ Tu Perfil")
    perfil = st.selectbox("Riesgo:", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown("### 🔍 Activo")
    opciones = {"Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA", "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"}
    sel = st.selectbox("Elegir:", list(opciones.keys()), label_visibility="collapsed")
    
    ticket = ""
    if opciones[sel] == "CUSTOM":
        ticket = st.text_input("Escribe el Ticker (ej: MSFT):").upper()
    else:
        ticket = opciones[sel]

# 4. CUERPO PRINCIPAL
st.title("🤖 InvestMind AI")
t1, t2 = st.tabs(["📈 Panel de Análisis", "💬 Chat Asesor"])

with t1:
    if st.button("🚀 INICIAR ANÁLISIS"):
        # VALIDACIÓN: Comprobar si el ticker está vacío
        if not ticket or ticket.strip() == "":
            st.warning("⚠️ **Atención:** Es necesario que elijas un activo o escribas un Ticker en el menú de la izquierda.")
        else:
            try:
                with st.status("Obteniendo datos de mercado...", expanded=False) as s:
                    datos = yf.download(ticket, period="5y")
                    
                    if datos.empty:
                        st.error(f"❌ No pudimos encontrar datos para '{ticket}'. Prueba con otro código.")
                    else:
                        precio_act = float(datos['Close'].iloc[-1])
                        df_p = datos.reset_index()[['Date', 'Close']]
                        df_p.columns = ['ds', 'y']
                        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                        
                        m = Prophet(daily_seasonality=True).fit(df_p)
                        pred = m.predict(m.make_future_dataframe(periods=30))
                        
                        st.session_state.cambio = ((float(pred['yhat'].iloc[-1]) - precio_act) / precio_act) * 100
                        st.session_state.analizado = True
                        s.update(label="Análisis Finalizado!", state="complete")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Precio Actual", f"{precio_act:.2f} {simbolo}")
                        c2.metric("Meta 30d", f"{float(pred['yhat'].iloc[-1]):.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                        c3.metric("Acciones Comprables", f"{(capital/precio_act):.4f}")
                        
                        st.line_chart(datos['Close'])
            except Exception as e:
                st.error(f"Se produjo un error inesperado: {e}")

with t2:
    st.subheader("💬 Consultoría en Tiempo Real")
    for m in st.session_state.messages:
        clase = "user-bubble" if m["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{m["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Escribe tu duda..."):
        st.session_state.messages.append({"role": "user", "content": p})
        st.markdown(f'<div class="bubble user-bubble">{p}</div>', unsafe_allow_html=True)
        
        with st.spinner("IA Pensando..."):
            time.sleep(0.5)
            info = f"un cambio del {st.session_state.cambio:.2f}%" if st.session_state.analizado else "tendencia aún no analizada"
            res = f"Como experto para un perfil **{perfil}**, veo que **{ticket if ticket else 'este activo'}** muestra una {info}. Para tus **{capital}{simbolo}**, mi recomendación es cautela. ¿Deseas más detalles?"
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.markdown(f'<div class="bubble assistant-bubble">{res}</div>', unsafe_allow_html=True)
            st.rerun()

st.caption("InvestMind AI | Uso exclusivo informativo.")
