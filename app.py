import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="InvestMind AI", page_icon="📈")
st.title("🤖 InvestMind AI: Tu Copiloto Financiero")

with st.sidebar:
    st.header("⚙️ Configuración")
    capital = st.number_input("Capital a invertir ($)", min_value=1, value=1000)
    perfil = st.selectbox("Tu perfil de riesgo", ["Conservador", "Arriesgado"])
    ticket = st.text_input("Ticker (ej: AAPL, TSLA, BTC-USD)", value="TSLA").upper()

if st.button("🔍 Analizar Inversión"):
    with st.spinner('Analizando datos...'):
        # 1. Descarga de datos
        datos = yf.download(ticket, period="5y")
        
        if datos.empty or len(datos) < 20:
            st.error("❌ No hay datos suficientes para este Ticker.")
        else:
            try:
                # --- EL PARCHE DE SEGURIDAD ESTÁ AQUÍ ---
                # Forzamos a que sean números simples (floats) y no listas
                precio_actual = float(datos['Close'].iloc[-1]) 
                
                # 2. IA de Predicción
                df_prophet = datos.reset_index()[['Date', 'Close']]
                df_prophet.columns = ['ds', 'y']
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
                
                modelo = Prophet(daily_seasonality=True)
                modelo.fit(df_prophet)
                futuro = modelo.make_future_dataframe(periods=30)
                prediccion = modelo.predict(futuro)
                
                # Extraemos el valor predicho como número simple
                precio_predicho = float(prediccion['yhat'].iloc[-1])
                cambio = float(((precio_predicho - precio_actual) / precio_actual) * 100)
                # ----------------------------------------

                # 3. Mostrar métricas sin errores
                col1, col2 = st.columns(2)
                col1.metric("Precio Actual", f"${precio_actual:.2f}")
                col2.metric("Predicción (30 días)", f"${precio_predicho:.2f}", f"{cambio:.2f}%")
                
                st.subheader("Gráfica de Tendencia")
                st.line_chart(datos['Close'])
                
                st.subheader("💡 Consejo de la IA")
                if perfil == "Conservador":
                    if cambio > 7:
                        st.success(f"✅ Oportunidad sólida. Comprarías aprox. {int(capital/precio_actual)} acciones.")
                    else:
                        st.warning("⚠️ Poco beneficio esperado para un perfil conservador.")
                else:
                    if cambio > 2:
                        st.success(f"🚀 Tendencia positiva detectada para perfil arriesgado.")
                    else:
                        st.info("📉 No es el mejor momento para este activo.")
                
            except Exception as e:
                st.error(f"Error al procesar datos: {e}")

st.caption("Nota: Los datos pueden tardar unos segundos en cargar.")
