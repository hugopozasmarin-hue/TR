import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO CSS AVANZADO
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* Animación para botones */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        transition: all 0.3s ease-in-out;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #0056b3;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Estilo del Chat (Adiós al fondo azul) */
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    }
    .user-bubble {
        background-color: #f0f2f6;
        text-align: right;
        border-left: 5px solid #007bff;
    }
    .assistant-bubble {
        background-color: #ffffff;
        border-left: 5px solid #28a745;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Mejoras estéticas generales */
    .main { background-color: #f8f9fa; }
    h1 { color: #1e1e1e; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA (SESSION STATE)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'cambio' not in st.session_state:
    st.session_state.cambio = 0.0
if 'analizado' not in st.session_state:
    st.session_state.analizado = False

# 3. BARRA LATERAL (RETRACTABLE POR DEFECTO)
with st.sidebar:
    st.header("⚙️ Configuración")
    moneda = st.radio("Moneda:", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(f"Capital ({simbolo})", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Tu Perfil:", ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {
        "Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA",
        "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"
    }
    sel = st.selectbox("Activo a analizar:", list(opciones.keys()))
    ticket = st.text_input("Ticker manual:").upper() if opciones[sel] == "CUSTOM" else opciones[sel]
    
    st.divider()
    st.caption("Usa la flecha arriba a la izquierda para retraer este menú.")

# 4. CUERPO PRINCIPAL
st.title("🤖 InvestMind AI")
tab1, tab2 = st.tabs(["📈 Panel de Análisis", "💬 Chat del Asesor"])

with tab1:
    if st.button("🚀 INICIAR ANÁLISIS DE MERCADO"):
        with st.status("Analizando datos históricos...", expanded=True) as status:
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                st.write("Calculando tendencias con IA...")
                precio_act = float(datos['Close'].iloc[-1])
                
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                
                precio_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((precio_pre - precio_act) / precio_act) * 100
                st.session_state.analizado = True
                status.update(label="Análisis completado!", state="complete", expanded=False)
                
                # Métricas con estilo
                c1, c2, c3 = st.columns(3)
                c1.metric("Precio Hoy", f"{precio_act:.2f} {simbolo}")
                c2.metric("Meta 30 días", f"{precio_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric("Acciones Comprables", f"{(capital/precio_act):.4f}")
                
                st.line_chart(datos['Close'])
                
                # Informe Extenso
                st.subheader("💡 Informe Estratégico")
                estado = "POSITIVO" if st.session_state.cambio > 2 else "ESTABLE/BAJISTA"
                st.info(f"""
                **Análisis para {ticket}:** El mercado muestra un tono **{estado}**. 
                Para un perfil **{perfil}**, la recomendación es observar el soporte actual. 
                Si el precio se mantiene, la proyección es alcanzar los {precio_pre:.2f} {simbolo}.
                """)
            else:
                st.error("Error al obtener datos.")

with tab2:
    st.subheader("💬 Consultoría en Tiempo Real")
    
    # Mostrar historial de chat con burbujas personalizadas
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="chat-bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Escribe tu duda aquí (ej: ¿Es arriesgado comprar ahora?)"):
        # Añadir pregunta del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)
        
        # Respuesta de la IA
        with st.spinner("Pensando..."):
            time.sleep(1) # Simulación de pensamiento
            info = f"tendencia de {st.session_state.cambio:.2f}%" if st.session_state.analizado else "sin analizar"
            respuesta = f"Como asesor para un perfil **{perfil}**, te diré que {ticket} presenta una {info}. Considero que invertir {capital} {simbolo} en este activo requiere una visión a {'largo plazo' if perfil == 'Conservador' else 'corto plazo'}. ¿Deseas que profundice en el riesgo técnico?"
            
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.markdown(f'<div class="chat-bubble assistant-bubble">{respuesta}</div>', unsafe_allow_html=True)

st.divider()
st.caption("InvestMind AI v2.0 | La inversión conlleva riesgos.")
