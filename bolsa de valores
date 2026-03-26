import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd

st.title("🤖 Asesor de Inversiones con IA")

# Formulario lateral para el perfil
with st.sidebar:
    st.header("Tu Perfil")
    capital = st.number_input("Capital a invertir ($)", min_value=10, value=1000)
    perfil = st.selectbox("Perfil de riesgo", ["Conservador", "Arriesgado"])
    ticket = st.text_input("Ticker de la acción (ej: AAPL)", value="AAPL").upper()

if st.button("Analizar Inversión"):
    # 1. Obtener Datos
    datos = yf.download(ticket, period="5y")
    
    # 2. Predicción
    df_prophet = datos.reset_index()[['Date', 'Close']]
    df_prophet.columns = ['ds', 'y']
    df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
    
    modelo = Prophet(daily_seasonality=True)
    modelo.fit(df_prophet)
    futuro = modelo.make_future_dataframe(periods=30)
    prediccion = modelo.predict(futuro)
    
    # 3. Mostrar Resultados
    precio_actual = datos['Close'].iloc[-1]
    precio_predicho = prediccion['yhat'].iloc[-1]
    cambio = ((precio_predicho - precio_actual) / precio_actual) * 100
    
    st.metric("Precio Actual", f"${precio_actual:.2f}")
    st.metric("Predicción (30 días)", f"${precio_predicho:.2f}", f"{cambio:.2f}%")
    st.line_chart(datos['Close'])
    
    # 4. Consejo
    if perfil == "Conservador" and cambio < 5:
        st.warning("⚠️ No se recomienda: Poco beneficio para tu perfil.")
    elif perfil == "Arriesgado" and cambio > 2:
        st.success(f"✅ ¡Adelante! Podrías comprar {int(capital/precio_actual)} acciones.")
    else:
        st.info("Estrategia neutral: El mercado está lateral.")

