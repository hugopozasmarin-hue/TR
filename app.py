import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ PON AQUÍ TU API KEY ---
GROQ_API_KEY = "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"  # ← reemplaza esto

# --- ESTILOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] { background-color: #0a192f !important; }

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
    }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital):
    try:
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""
Eres un asesor financiero experto.

Activo: {ticket}
Precio actual: {precio_actual}
Precio futuro: {precio_futuro}
Rentabilidad: {cambio:.2f}%
Perfil: {perfil}
Capital: {capital}€

Haz un análisis claro:
- Si vale la pena invertir
- Riesgos
- Estrategia recomendada
"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error IA: {e}"

# --- SESSION ---
if "lang" not in st.session_state:
    st.session_state.lang = "Español"

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

if st.button(t["btn"]):
    data = yf.download(ticket, period="5y")

    if not data.empty:
        df = data.reset_index()[['Date', 'Close']]
        df.columns = ['ds', 'y']

        model = Prophet().fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        precio_actual = df['y'].iloc[-1]
        precio_futuro = forecast['yhat'].iloc[-1]
        cambio = ((precio_futuro - precio_actual) / precio_actual) * 100

        # MÉTRICAS
        c1, c2, c3 = st.columns(3)
        c1.metric(t["price"], f"{precio_actual:.2f}€")
        c2.metric(t["target"], f"{precio_futuro:.2f}€", f"{cambio:.2f}%")
        c3.metric(t["shares"], f"{(capital/precio_actual):.2f}")

        # GRÁFICA
        st.line_chart(df.set_index('ds')['y'])

        # RESUMEN
        st.markdown("### 📊 " + t["analysis"])
        st.write(f"Rentabilidad esperada: {cambio:.2f}%")

        # IA
        with st.spinner("Generando análisis IA..."):
            analisis = generar_analisis_ia(
                ticket, precio_actual, precio_futuro, cambio, perfil, capital
            )

        st.write(analisis)

    else:
        st.error("Ticker no válido")

