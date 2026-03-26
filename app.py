import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ PON AQUÍ TU API KEY ---
GROQ_API_KEY = "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"  # ← reemplaza esto

# --- ESTILOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }

.field-title { 
    color: #64ffda; font-size: 10px; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 20px; margin-bottom: 8px;
}

.stButton>button { 
    width: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #64ffda, #48cae4);
    color: #0a192f !important; font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title":"InvestIA Elite",
        "lang_lab":"IDIOMA",
        "cap":"PRESUPUESTO",
        "risk_lab":"RIESGO",
        "ass_lab":"TICKER",
        "btn":"ANALIZAR",
        "wait":"Procesando...",
        "price":"Precio actual",
        "target":"Predicción en 30 días",
        "shares":"Acciones que puedes comprar",
        "analysis":"Análisis de inversión",
        "chat_placeholder":"Escribe tu pregunta..."
    },
    "English": {
        "title":"InvestIA Elite",
        "lang_lab":"LANGUAGE",
        "cap":"BUDGET",
        "risk_lab":"RISK",
        "ass_lab":"TICKER",
        "btn":"ANALYZE",
        "wait":"Processing...",
        "price":"Current Price",
        "target":"30-Day Prediction",
        "shares":"Shares you can buy",
        "analysis":"Investment Analysis",
        "chat_placeholder":"Type your question..."
    },
    "Català": {
        "title":"InvestIA Elite",
        "lang_lab":"LLENGUA",
        "cap":"PRESSUPOST",
        "risk_lab":"RISC",
        "ass_lab":"TICKER",
        "btn":"ANALITZAR",
        "wait":"Analitzant...",
        "price":"Preu actual",
        "target":"Predicció en 30 dies",
        "shares":"Accions que pots comprar",
        "analysis":"Anàlisi d'inversió",
        "chat_placeholder":"Escriu la teva pregunta..."
    }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prompt ultra pro para inversión
        prompt = f"""
Actúa como un analista financiero de alto nivel (tipo hedge fund). 
Analiza el activo {ticket} para un inversor con perfil {perfil} y capital {capital}€.

Datos:
- Precio actual: {precio_actual}€
- Predicción a 30 días: {precio_futuro}€
- Rentabilidad esperada: {cambio:.2f}%

Analiza:
1. Fiabilidad de la predicción
2. Riesgos reales (volatilidad, tendencia)
3. Oportunidad para este perfil
4. Estrategia concreta (comprar, esperar, dividir inversión, evitar)
5. Consideraciones macroeconómicas y sectoriales

Si se proporciona una pregunta del usuario, inclúyela al final y respóndela de manera profesional: {pregunta if pregunta else "N/A"}
Sé crítico, profesional y directo. Evita respuestas genéricas.
"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error IA: {e}"

# --- SESSION ---
for key in ["lang", "analizado", "ticket_act", "p_act", "p_pre", "cambio", "chat_messages"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key=="chat_messages" else (False if key=="analizado" else 0.0 if "p_" in key or key=="cambio" else "" if key=="ticket_act" else "Español")

# --- SIDEBAR ---
with st.sidebar:
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()))
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0)

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")

tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="5y")

            if not data.empty:
                df = data.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))

                precio_actual = df['y'].iloc[-1]
                precio_futuro = forecast['yhat'].iloc[-1]
                cambio = ((precio_futuro - precio_actual)/precio_actual)*100

                st.session_state.p_act = precio_actual
                st.session_state.p_pre = precio_futuro
                st.session_state.cambio = cambio
                st.session_state.ticket_act = ticket
                st.session_state.analizado = True

                # MÉTRICAS
                c1,c2,c3 = st.columns(3)
                c1.metric(t["price"], f"{precio_actual:.2f}€")
                c2.metric(t["target"], f"{precio_futuro:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/precio_actual):.2f}")

                # GRÁFICA
                st.line_chart(df.set_index('ds')['y'])

                # ANÁLISIS BÁSICO
                resumen = "📈 Tendencia positiva" if cambio>5 else "⚖️ Crecimiento leve" if cambio>0 else "📉 Tendencia negativa"
                st.markdown("### 📊 " + t["analysis"])
                st.write(resumen)

                # ANALISIS ULTRA PRO
                with st.spinner("🧠 Generando análisis profesional..."):
                    analisis = generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital)
                st.write(analisis)

            else:
                st.error("Ticker no válido")

with tab2:
    st.markdown("### 💬 Chat con IA")
    if st.session_state.analizado:
        # Mostrar chat previo
        for msg in st.session_state.chat_messages:
            st.write(msg)

        # Input de usuario
        user_msg = st.text_input(t["chat_placeholder"])
        if user_msg:
            respuesta = generar_analisis_ia(
                st.session_state.ticket_act,
                st.session_state.p_act,
                st.session_state.p_pre,
                st.session_state.cambio,
                perfil,
                capital,
                pregunta=user_msg
            )
            st.session_state.chat_messages.append(f"**Tú:** {user_msg}")
            st.session_state.chat_messages.append(f"**IA:** {respuesta}")
            st.experimental_rerun()
    else:
        st.write("Realiza primero un análisis en la pestaña de 📈")
