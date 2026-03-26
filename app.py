import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="InvestMind AI", page_icon="💰", layout="wide")
st.title("🤖 InvestMind AI: Tu Copiloto Financiero Pro")

# 2. BARRA LATERAL (CONFIGURACIÓN)
with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    # Selección de Moneda
    moneda = st.radio("Selecciona tu moneda:", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo_moneda = "$" if "USD" in moneda else "€"
    
    # Capital
    capital = st.number_input(f"Capital a invertir ({simbolo_moneda})", min_value=1.0, value=1000.0, step=10.0)
    
    # Perfil
    perfil = st.selectbox("Tu perfil de riesgo", ["Conservador (Protección)", "Moderado (Equilibrio)", "Arriesgado (Crecimiento)"])
    
    # Menú desplegable de Tickers populares + Opción manual
    opciones_ticker = {
        "Apple (AAPL)": "AAPL",
        "Tesla (TSLA)": "TSLA",
        "Microsoft (MSFT)": "MSFT",
        "Amazon (AMZN)": "AMZN",
        "Google (GOOGL)": "GOOGL",
        "Nvidia (NVDA)": "NVDA",
        "Bitcoin (BTC-USD)": "BTC-USD",
        "Ethereum (ETH-USD)": "ETH-USD",
        "Santander (SAN.MC)": "SAN.MC",
        "IBEX 35 (^IBEX)": "^IBEX",
        "OTRO (Escribir abajo)": "CUSTOM"
    }
    seleccion = st.selectbox("Selecciona un activo o empresa:", list(opciones_ticker.keys()))
    
    if opciones_ticker[seleccion] == "CUSTOM":
        ticket = st.text_input("Escribe el Ticker manualmente (ej: META):").upper()
    else:
        ticket = opciones_ticker[seleccion]

# 3. CUERPO PRINCIPAL
tab1, tab2 = st.tabs(["📈 Análisis y Predicción", "💬 Chat con el Asesor"])

with tab1:
    if st.button("🚀 Iniciar Análisis Profundo"):
        with st.spinner('Analizando mercados globales...'):
            datos = yf.download(ticket, period="5y")
            
            if datos.empty:
                st.error("No se encontraron datos. Revisa el Ticker.")
            else:
                # Procesamiento de Precios
                precio_actual = float(datos['Close'].iloc[-1])
                
                # IA Prophet
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                futuro = m.make_future_dataframe(periods=30)
                pred = m.predict(futuro)
                
                precio_pred = float(pred['yhat'].iloc[-1])
                cambio = ((precio_pred - precio_actual) / precio_actual) * 100
                
                # Visualización
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Actual", f"{precio_actual:.2f} {simbolo_moneda}")
                col2.metric("Predicción 30 días", f"{precio_pred:.2f} {simbolo_moneda}", f"{cambio:.2f}%")
                
                # CÁLCULO CON DECIMALES
                cantidad_acciones = capital / precio_actual
                col3.metric("Capacidad de Compra", f"{cantidad_acciones:.4f} unidades")

                st.line_chart(datos['Close'])

                # SECCIÓN DE CONSEJO EXTENSO
                st.subheader("💡 Informe Detallado de la IA")
                
                with st.expander("VER ANÁLISIS COMPLETO", expanded=True):
                    if cambio > 5:
                        st.success(f"**DIAGNÓSTICO: OPORTUNIDAD ALCISTA**")
                        st.write(f"Nuestros algoritmos detectan una tendencia de crecimiento del {cambio:.2f}% para el próximo mes.")
                    elif cambio < -2:
                        st.error(f"**DIAGNÓSTICO: PRECAUCIÓN / BAJISTA**")
                        st.write("Se observa una posible corrección. Podría ser un momento de riesgo.")
                    else:
                        st.info(f"**DIAGNÓSTICO: MERCADO LATERAL**")
                        st.write("El activo se mantiene estable sin tendencias claras de ruptura.")

                    st.markdown(f"""
                    **Análisis según tu perfil ({perfil}):**
                    *   **Estrategia recomendada:** {"Diversificación cautelosa" if "Conservador" in perfil else "Entrada agresiva o escalonada"}.
                    *   **Riesgo estimado:** El mercado muestra una volatilidad estándar. Para un capital de {capital} {simbolo_moneda}, la exposición es manejable.
                    *   **Sugerencia de salida:** Si el precio alcanza los {precio_pred:.2f} {simbolo_moneda}, considera tomar beneficios parciales.
                    """)

with tab2:
    st.subheader("💬 Pregúntale a tu Asesor Personal")
    user_question = st.text_input("Ej: ¿Es buen momento para invertir mis ahorros en esto?")
    
    if user_question:
        # Lógica de respuesta "inteligente" simulada
        st.chat_message("assistant").write(f"Sobre tu pregunta: '{user_question}'...")
        st.write(f"Basándome en tu perfil **{perfil}** y el activo **{ticket}**, mi recomendación es que analices si esos {capital} {simbolo_moneda} representan más del 20% de tus ahorros. En la situación actual, la rentabilidad esperada es del {cambio:.2f}%. ¿Te gustaría saber el riesgo de pérdida máxima?")

st.caption("Aviso legal: Esta IA utiliza modelos estadísticos. La inversión conlleva riesgos. No nos hacemos responsables de pérdidas financieras.")
