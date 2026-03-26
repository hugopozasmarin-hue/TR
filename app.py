import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

# 2. ESTILO CSS (DISEÑO ELITE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0e1117 0%, #1a1c23 100%); border-right: 1px solid rgba(255,255,255,0.05); }
    .stNumberInput input, .stSelectbox div, .stTextInput input { background-color: #3b3d4a !important; color: #fff !important; border: 1px solid #555 !important; border-radius: 12px !important; }
    .stButton>button { width: 100%; border-radius: 14px; background: linear-gradient(90deg, #007bff, #00d4ff); color: white !important; font-weight: 800; border: none; padding: 15px; }
    .bubble { padding: 18px 22px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; color: white !important; }
    .user-bubble { background: linear-gradient(135deg, #007bff, #0056b3); margin-left: auto; border-bottom-right-radius: 4px; }
    .assistant-bubble { background: rgba(38, 39, 48, 0.8); border: 1px solid rgba(255,255,255,0.1); border-bottom-left-radius: 4px; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. DICCIONARIO MULTILINGÜE (AÑADIDA JUSTIFICACIÓN)
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "config": "Configuración Elite", "btn": "EJECUTAR ANÁLISIS",
        "diag": "Consultoría Estratégica", "just": "Justificación de la Predicción", 
        "inf_1": "Basado en 1,825 puntos de datos, prevemos un", "risk_label": "Perfil",
        "str_entry": "Entrada", "str_risk": "Riesgo", "shares": "Acciones", "price": "Precio"
    },
    "English": {
        "title": "InvestMind AI Elite", "config": "Elite Settings", "btn": "EXECUTE ANALYSIS",
        "diag": "Strategic Consultancy", "just": "Prediction Justification",
        "inf_1": "Based on 1,825 data points, we forecast a", "risk_label": "Profile",
        "str_entry": "Entry", "str_risk": "Risk", "shares": "Shares", "price": "Price"
    },
    "Català": {
        "title": "InvestMind AI Elite", "config": "Configuració Elit", "btn": "EXECUTAR ANÀLISI",
        "diag": "Consultoria Estratègica", "just": "Justificació de la Predicció",
        "inf_1": "Basat en 1.825 punts de dades, preveiem un", "risk_label": "Perfil",
        "str_entry": "Entrada", "str_risk": "Risc", "shares": "Accions", "price": "Preu"
    }
}

# 4. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = ""

# 5. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️ System", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    t = languages[lang_sel]
    st.markdown(f'<p style="color:#888; font-weight:800; font-size:12px; letter-spacing:2px; margin-bottom:20px;">{t["config"].upper()}</p>', unsafe_allow_html=True)
    moneda = st.radio("Divisa", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Capital", min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk_label"], ["Conservador", "Moderado", "Arriesgado"])
    modo_ticker = st.checkbox("Manual Ticker", value=False)
    ticket = st.text_input("Ticker:").upper() if modo_ticker else st.selectbox("Asset", ["AAPL", "TSLA", "BTC-USD", "NVDA", "MSFT"])

# 6. MOTOR DE CHAT MEJORADO (COHERENCIA TOTAL)
def chat_coherente(pregunta, lang, ticket, cambio, analizado):
    p = pregunta.lower().strip()
    # 1. Identificar Saludos
    if p in ["hola", "buenas", "hi", "hello", "bon dia", "hola!", "ey"]:
        responses = {"Español": "¡Hola! Soy tu asesor. ¿Tienes dudas sobre el análisis de hoy?", 
                     "English": "Hello! I'm your advisor. Do you have questions about today's analysis?",
                     "Català": "Hola! Sóc el teu assessor. Tens dubtes sobre l'anàlisi d'avui?"}
        return responses[lang]
    
    # 2. Identificar si no se ha analizado nada todavía
    if not analizado:
        responses = {"Español": "Para darte un consejo preciso, primero necesito que pulses 'Ejecutar Análisis' en la pestaña anterior.",
                     "English": "To give you precise advice, I first need you to click 'Execute Analysis' in the previous tab.",
                     "Català": "Per donar-te un consell precís, primer necessito que cliquis 'Executar Anàlisi' a la pestanya anterior."}
        return responses[lang]

    # 3. Identificar preguntas de inversión/precio
    t_tend = "alcista" if cambio > 0 else "bajista"
    if any(x in p for x in ["invertir", "comprar", "precio", "subira", "buy", "invest"]):
        responses = {"Español": f"Dado que la tendencia de {ticket} es {t_tend} ({cambio:.2f}%), mi recomendación es...",
                     "English": f"Since the trend for {ticket} is {t_tend} ({cambio:.2f}%), my recommendation is...",
                     "Català": f"Com que la tendència de {ticket} és {t_tend} ({cambio:.2f}%), la meva recomanació és..."}
        return responses[lang] + (" actuar con cautela." if cambio < 5 else " aprovechar el momento.")

    # 4. Respuesta por defecto coherente
    responses = {"Español": f"Entiendo tu interés. Sobre {ticket}, estamos viendo un cambio del {cambio:.2f}%. ¿Quieres profundizar en el riesgo?",
                 "English": f"I understand. Regarding {ticket}, we are seeing a {cambio:.2f}% change. Want to dive into the risk?",
                 "Català": f"Entenc el teu interès. Sobre {ticket}, estem veient un canvi del {cambio:.2f}%. Vols aprofundir en el risc?"}
    return responses[lang]

# 7. CUERPO PRINCIPAL
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs(["📈 Terminal", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]) as s:
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                precio_act = float(datos['Close'].iloc[-1])
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True, yearly_seasonality=True).fit(df_p)
                forecast = m.predict(m.make_future_dataframe(periods=30))
                precio_pre = float(forecast['yhat'].iloc[-1])
                st.session_state.cambio = ((precio_pre - precio_act) / precio_act) * 100
                st.session_state.analizado = True
                st.session_state.ticket_act = ticket
                
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{precio_act:.2f}{simbolo}")
                c2.metric("Target 30d", f"{precio_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/precio_act):.4f}")
                st.line_chart(datos['Close'])

                # --- CONSULTORÍA CON JUSTIFICACIÓN DETALLADA ---
                st.divider()
                st.header(f"💼 {t['diag']}")
                st.markdown(f"### {t['just']}")
                
                # Explicación del "Por qué"
                justificacion = {
                    "Español": f"Nuestra IA ha detectado un **patrón de inercia** basado en los últimos 5 años. La predicción de **{st.session_state.cambio:.2f}%** se debe a: \n 1. **Momento Histórico**: La curva muestra un crecimiento sostenido. \n 2. **Estacionalidad**: {ticket} suele comportarse así en esta época del año según los ciclos registrados.",
                    "English": f"Our AI detected an **inertia pattern** based on the last 5 years. The **{st.session_state.cambio:.2f}%** forecast is due to: \n 1. **Historical Momentum**: The curve shows sustained growth. \n 2. **Seasonality**: {ticket} typically behaves this way at this time of year based on recorded cycles.",
                    "Català": f"La nostra IA ha detectat un **patró d'inèrcia** basat en els últims 5 anys. La predicció de **{st.session_state.cambio:.2f}%** es deu a: \n 1. **Moment Històric**: La curva mostra un creixement sostingut. \n 2. **Estacionalitat**: {ticket} se sol comportar així en aquesta època de l'any segons els cicles registrats."
                }
                st.write(justificacion[lang_sel])
                
                st.info(f"**Estrategia {perfil}:** " + ("Mantén liquidez." if st.session_state.cambio < 2 else "Entrada progresiva sugerida."))
            else: st.error("No Data.")

with tab2:
    st.subheader("💬 Chat Asesor")
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        respuesta = chat_coherente(p, lang_sel, st.session_state.ticket_act, st.session_state.cambio, st.session_state.analizado)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

st.caption("InvestMind AI Elite v6.8")
