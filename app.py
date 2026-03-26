import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ESTILOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] { 
    background-color: #0a192f !important; 
    border-right: 1px solid rgba(255,255,255,0.1); 
}

.field-title { 
    color: #64ffda; 
    font-size: 10px; 
    font-weight: 800; 
    letter-spacing: 1.5px; 
    text-transform: uppercase; 
    margin-top: 20px; 
    margin-bottom: 8px; 
    display: block; 
    border-bottom: 1px solid rgba(100, 255, 218, 0.2); 
    padding-bottom: 4px; 
}

.stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input { 
    background-color: #112240 !important; 
    color: #ccd6f6 !important; 
    border: 1px solid #233554 !important; 
    border-radius: 10px !important; 
}

div[data-baseweb="select"] > div { color: #ccd6f6 !important; }
label { display: none !important; }

.stButton>button { 
    width: 100%; 
    border-radius: 12px; 
    background: linear-gradient(90deg, #64ffda, #48cae4); 
    color: #0a192f !important; 
    font-weight: 800; 
    border: none; 
    padding: 15px; 
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
        "ass_lab":"TICKER (Ej: AAPL)",
        "btn":"ANALIZAR",
        "wait":"Procesando...",
        "price":"Precio actual",
        "target":"Predicción en 30 días",
        "shares":"Acciones que puedes comprar",
        "analysis":"Análisis de inversión",
        "disclaimer":"Simulación 2026. Riesgo de capital."
    },
    "English": {
        "title":"InvestIA Elite",
        "lang_lab":"LANGUAGE",
        "cap":"BUDGET",
        "risk_lab":"RISK",
        "ass_lab":"TICKER (e.g. TSLA)",
        "btn":"ANALYZE",
        "wait":"Processing...",
        "price":"Current Price",
        "target":"30-Day Prediction",
        "shares":"Shares you can buy",
        "analysis":"Investment Analysis",
        "disclaimer":"2026 Simulation. Capital risk."
    },
    "Català": {
        "title":"InvestIA Elite",
        "lang_lab":"LLENGUA",
        "cap":"PRESSUPOST",
        "risk_lab":"RISC",
        "ass_lab":"TICKER (Ex: NVDA)",
        "btn":"ANALITZAR",
        "wait":"Analitzant...",
        "price":"Preu actual",
        "target":"Predicció en 30 dies",
        "shares":"Accions que pots comprar",
        "analysis":"Anàlisi d'inversió",
        "disclaimer":"Simulació 2026. Risc de capital."
    }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(ticket, precio_actual, precio_futuro, cambio, perfil, capital):
    try:
        client = Groq()  # usa GROQ_API_KEY desde entorno

        prompt = f"""
Actúa como un asesor financiero profesional.

Activo: {ticket}
Precio actual: {precio_actual}
Precio futuro: {precio_futuro}
Rentabilidad: {cambio:.2f}%
Perfil: {perfil}
Capital: {capital}€

Da un análisis claro, directo y útil:
- Interpretación
- Riesgos
- Oportunidad
- Recomendación concreta
"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error IA: {e}"

# --- SESSION STATE ---
for key, val in [('cambio', 0.0), ('analizado', False), ('ticket_act', ""), ('lang', "Español"), ('p_act', 0.0), ('p_pre', 0.0)]:
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR ---
with st.sidebar:
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)

    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            raw_data = yf.download(ticket, period="5y")

            if not raw_data.empty:
                if isinstance(raw_data.columns, pd.MultiIndex):
                    raw_data.columns = raw_data.columns.get_level_values(0)

                df_p = raw_data.reset_index()
                df_p = df_p[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = pd.to_datetime(df_p['ds']).dt.tz_localize(None)
                df_p = df_p.dropna()

                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))

                st.session_state.p_act = float(df_p['y'].iloc[-1])
                st.session_state.p_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((st.session_state.p_pre - st.session_state.p_act) / st.session_state.p_act) * 100
                st.session_state.ticket_act = ticket
                st.session_state.analizado = True

                # MÉTRICAS
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{st.session_state.p_act:.2f}€")
                c2.metric(t["target"], f"{st.session_state.p_pre:.2f}€", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/st.session_state.p_act):.2f}")

                # GRÁFICA
                st.line_chart(df_p.set_index('ds')['y'])

                # RESUMEN RÁPIDO
                rentabilidad = st.session_state.cambio
                if rentabilidad > 5:
                    resumen = "📈 Tendencia positiva"
                elif rentabilidad > 0:
                    resumen = "⚖️ Crecimiento leve"
                else:
                    resumen = "📉 Tendencia negativa"

                st.markdown("### 📊 " + t["analysis"])
                st.write(resumen)

                # IA
                with st.spinner("🧠 Generando análisis profesional..."):
                    analisis_ia = generar_analisis_ia(
                        ticket,
                        st.session_state.p_act,
                        st.session_state.p_pre,
                        rentabilidad,
                        perfil,
                        capital
                    )

                st.markdown("#### 🤖 Análisis avanzado")
                st.write(analisis_ia)

            else:
                st.error("Error: Ticker no encontrado.")

with tab2:
    if st.session_state.analizado:
        st.info(f"Consultoría activa para {st.session_state.ticket_act}")
    else:
        st.write("Realiza un análisis primero.")

st.markdown("---")
st.caption(f"⚠️ {t['disclaimer']}")
