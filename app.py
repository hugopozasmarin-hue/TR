if st.button("Analizar Inversión"):
    # 1. Intentar obtener datos
    datos = yf.download(ticket, period="5y")
    
    # SEGURIDAD: Comprobar si el ticker es válido y tiene datos
    if datos.empty or len(datos) < 10:
        st.error(f"❌ No se encontraron datos para '{ticket}'. Asegúrate de usar el código correcto (ej: TSLA para Tesla, MSFT para Microsoft).")
    else:
        # 2. Si hay datos, procedemos con la predicción
        try:
            df_prophet = datos.reset_index()[['Date', 'Close']]
            df_prophet.columns = ['ds', 'y']
            df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
            
            with st.spinner('La IA está analizando tendencias...'):
                modelo = Prophet(daily_seasonality=True)
                modelo.fit(df_prophet)
                futuro = modelo.make_future_dataframe(periods=30)
                prediccion = modelo.predict(futuro)
            
            # 3. Mostrar Resultados (Igual que antes)
            precio_actual = datos['Close'].iloc[-1]
            precio_predicho = prediccion['yhat'].iloc[-1]
            cambio = ((precio_predicho - precio_actual) / precio_actual) * 100
            
            col1, col2 = st.columns(2)
            col1.metric("Precio Actual", f"${precio_actual:.2f}")
            col2.metric("Predicción (30 días)", f"${precio_predicho:.2f}", f"{cambio:.2f}%")
            
            st.line_chart(datos['Close'])
            
            # 4. Consejo basado en tu perfil
            if perfil == "Conservador" and cambio < 5:
                st.warning("⚠️ No se recomienda: La ganancia esperada es muy baja para el riesgo.")
            elif perfil == "Arriesgado" and cambio > 2:
                st.success(f"✅ ¡Oportunidad detectada! Podrías comprar {int(capital/precio_actual)} acciones.")
            else:
                st.info("Estrategia neutral: Espera a una mejor señal del mercado.")
                
        except Exception as e:
            st.error(f"Ocurrió un error en el cálculo: {e}")


