import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")
st.title("🤖 InvestMind AI: Tu Copiloto Financiero Pro")

# Inicializar variables en la memoria del navegador (Session State) para evitar errores
if 'cambio' not in st.session_state:
    st.session_state.cambio = 0.0
if 'analizado' not in st.session_state:
    st.session_state.analizado = False

# 2. BARRA LATERAL
with st.sidebar:
    st.header("⚙️ Panel de Control")
    moneda = st.radio("Moneda:", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(f"Capital ({simbolo})", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Perfil:", ["Conservador", "Moderado", "Arriesgado"])
    
    opciones = {
        "Apple (AAPL)": "AAPL", "Tesla (TSLA)": "TSLA", "Nvidia (NVDA)": "NVDA",
        "Bitcoin (BTC-USD)": "BTC-USD", "Santander (SAN.MC)": "SAN.MC", "OTRO": "CUSTOM"
    }
    sel = st.selectbox("Activo:", list(opciones.keys()))
    ticket = st.text_input("Ticker manual:").upper() if opciones[sel] == "CUSTOM" else opciones[sel]

# 3. PESTAÑAS
tab1, tab2 = st.tabs(["📈 Análisis", "💬 Chat Asesor"])

with tab1:
    if st.button("🚀 Iniciar Análisis"):
        with st.spinner('Procesando...'):
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                precio_act = float(datos['Close'].iloc[-1])
                # IA
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                
                precio_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((precio_pre - precio_act) / precio_act) * 100
                st.session_state.analizado = True
                
                # Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric("Actual", f"{precio_act:.2f} {simbolo}")
                c2.metric("Predicción", f"{precio_pre:.2f} {simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric("Acciones", f"{(capital/precio_act):.4f}")
                st.line_chart(datos['Close'])
                
                # Informe Extenso
                st.subheader("💡 Informe Detallado")
                with st.expander("LEER ANÁLISIS COMPLETO", expanded=True):
                    estado = "ALCISTA" if st.session_state.cambio > 2 else "BAJISTA/LATERAL"
                    st.write(f"**Diagnóstico:** Mercado {estado}. Se estima un movimiento del {st.session_state.cambio:.2f}% en 30 días.")
                    st.write(f"**Estrategia {perfil}:** " + ("Mantener cautela y diversificar." if perfil == "Conservador" else "Oportunidad de entrada técnica."))
            else:
                st.error("No hay datos.")

with tab2:
    st.subheader("💬 Pregúntale a tu Asesor")
    pregunta = st.text_input("Haz una pregunta sobre tu inversión:")
    
    if pregunta:
        # Aquí usamos session_state para que no de error si no hemos analizado nada aún
        info_cambio = f"{st.session_state.cambio:.2f}%" if st.session_state.analizado else "todavía no analizada"
        
        st.chat_message("assistant").write(f"Analizando tu duda: '{pregunta}'")
        st.info(f"""
        **Respuesta de InvestMind AI:**
        Basándome en que eres un inversor **{perfil}** y el activo **{ticket}** tiene una tendencia de **{info_cambio}**, mi consejo es:
        1. Evalúa si esos {capital} {simbolo} son dinero que no necesitarás en 6 meses.
        2. La predicción actual sugiere un escenario de {'crecimiento' if st.session_state.cambio > 0 else 'corrección'}.
        3. No inviertas todo de golpe; usa la técnica de compras escalonadas.
        """)

st.caption("Aviso: Datos históricos. No es asesoramiento financiero oficial.")
