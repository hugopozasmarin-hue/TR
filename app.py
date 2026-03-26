import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="InvestMind AI", page_icon="📈")

st.title("🤖 InvestMind AI: Tu Copiloto Financiero")
st.markdown("Analiza tendencias del mercado y recibe consejos basados en tu perfil.")

# FORMULARIO LATERAL PARA EL PERFIL
with st.sidebar:
    st.header("⚙️ Configuración")
    capital = st.number_input("Capital a invertir ($)", min_value=10, value=1000)
    perfil = st.selectbox("Tu perfil de riesgo", ["Conservador", "Arriesgado"])
    ticket = st.text_input("Ticker de la acción (ej: AAPL, TSLA, BTC-USD)", value="AAPL").upper()
    st.info("Nota: Usa códigos de Yahoo Finance (ej: SAN.MC para Santander).")

# BOTÓN DE ANÁLISIS
if st.button("🔍 Analizar Inversión"):
    with st.spinner('Obteniendo datos y entrenando IA...'):
        # 1. Obtener Datos
        datos = yf.download(ticket, period="5y")
        
        if datos.empty or len(datos) < 20:
            st.error(f"❌ No se han encontrado datos para '{ticket}'. Revisa que el código sea correcto.")
        else:
            try:
                # 2. Preparar IA (Prophet)
                df_prophet = datos.reset_index()[['Date', 'Close']]
                df_prophet.columns = ['ds', 'y']
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
                
                modelo = Prophet(daily_seasonality=True)
                modelo.fit(df_prophet)
                
                # Predicción a 30 días
                futuro = modelo.make_future_dataframe(periods=30)
                prediccion = modelo.predict(futuro)
                
                # 3. Mostrar Métricas
                precio_actual = datos['Close'].iloc[-1]
                precio_predicho = prediccion['yhat'].iloc[-1]
                cambio = ((precio_predicho - precio_actual) / precio_actual) * 100
                
                col1, col2 = st.columns(2)
                col1.metric("Precio Actual", f"${precio_actual:.2f}")
                col2.metric("Predicción (30 días)", f"${precio_predicho:.2f}", f"{cambio:.2f}%")
                
                # 4. Gráfica
                st.subheader("Tendencia Histórica y Proyección")
                st.line_chart(datos['Close'])
                
                # 5. Lógica de Consejo
                st.subheader("💡 Consejo de la IA")
                if perfil == "Conservador":
                    if cambio > 7:
                        st.success(f"✅ Parece una buena oportunidad. Con ${capital} podrías comprar {int(capital/precio_actual)} acciones.")
                    else:
                        st.warning("⚠️ No recomendado: La rentabilidad esperada no compensa el riesgo para tu perfil.")
                else: # Perfil Arriesgado
                    if cambio > 2:
                        st.success(f"🚀 Tendencia alcista detectada. Es un buen momento para tu perfil arriesgado.")
                    else:
                        st.info("📉 Tendencia lateral o bajista. Quizás prefieras buscar otro activo hoy.")
                
                st.caption("Aviso: Esto es una simulación basada en datos históricos. No constituye asesoramiento financiero real.")

            except Exception as e:
                st.error(f"Error técnico: {e}")

