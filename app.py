import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time
import random

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="InvestMind AI Pro", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #333; }
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        background-color: #3b3d4a !important; color: white !important; border: 1px solid #555 !important;
    }
    .sidebar-title { color: #888 !important; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 8px; background: #007bff; color: white !important; font-weight: bold; border: none; padding: 12px; }
    .bubble { padding: 15px 20px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; color: white !important; line-height: 1.6; }
    .user-bubble { align-self: flex-end; background-color: #007bff; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { align-self: flex-start; background-color: #262730; border: 1px solid #444; border-bottom-left-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO DE IDIOMAS
languages = {
    "Español": {"diag": "Informe Estratégico Detallado", "btn": "Analizar Mercado", "wait": "Consultando Datos..."},
    "English": {"diag": "Detailed Strategic Report", "btn": "Analyze Market", "wait": "Consulting Data..."},
    "Català": {"diag": "Informe Estratègic Detallat", "btn": "Analitzar Mercat", "wait": "Consultant Dades..."}
}

# 3. MEMORIA DE SESIÓN
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'precio_act' not in st.session_state: st.session_state.precio_act = 0.0

# 4. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    t = languages[lang_sel]
    st.markdown('<p class="sidebar-title">CONFIG</p>', unsafe_allow_html=True)
    moneda = st.radio("Moneda", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Inversión", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Riesgo", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.selectbox("Ticker", ["AAPL", "TSLA", "NVDA", "BTC-USD", "MSFT", "SAN.MC"])

# 5. LÓGICA DE "CEREBRO GRATUITO" (Simulación de IA Cognitiva)
def generar_respuesta_ia(pregunta, perfil, ticker, cambio, precio):
    p = pregunta.lower()
    tendencia = "alcista 📈" if cambio > 2 else "bajista 📉" if cambio < -2 else "lateral ↔️"
    
    # Base de conocimientos por temas
    respuestas = {
        "saludo": ["¡Hola! Soy tu asesor InvestMind. Analizando tu interés en {t}...", "Saludos. He revisado los datos de {t} para tu perfil {p}."],
        "inversion": ["Con una tendencia {tend}, invertir en {t} requiere {plan}. Tu capital de {cap}{s} está {seguro}."],
        "riesgo": ["Como inversor {p}, el riesgo en {t} es notable. La volatilidad histórica sugiere un stop-loss al 5%."],
        "futuro": ["Nuestra IA predice un movimiento del {c}% para {t} en 30 días. Esto implica que {meta}."],
        "desconocido": ["Interesante punto sobre '{q}'. Basado en {t}, mi sugerencia es vigilar el volumen de trading."]
    }
    
    # Lógica de decisión
    if any(x in p for x in ["hola", "buen", "hey"]): key = "saludo"
    elif any(x in p for x in ["mejor", "invertir", "donde", "comprar"]): key = "inversion"
    elif any(x in p for x in ["riesgo", "perder", "seguro", "miedo"]): key = "riesgo"
    elif any(x in p for x in ["cuanto", "precio", "subira", "prediccion"]): key = "futuro"
    else: key = "desconocido"

    res = random.choice(respuestas[key])
    
    # Personalización dinámica de la frase
    return res.format(
        t=ticker, p=perfil, tend=tendencia, c=f"{cambio:.2f}", cap=capital, s=simbolo, q=pregunta,
        plan="una entrada escalonada" if perfil != "Arriesgado" else "una entrada agresiva",
        seguro="bien posicionado" if cambio > 0 else "en zona de riesgo",
        meta=f"el precio podría alcanzar los {precio*(1+cambio/100):.2f}{simbolo}"
    )

# 6. CUERPO PRINCIPAL
st.title(f"🤖 InvestMind AI Pro")
tab1, tab2 = st.tabs([t["t1"] if "t1" in t else "Análisis", t["t2"] if "t2" in t else "Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]) as s:
            datos = yf.download(ticket, period="5y")
            st.session_state.precio_act = float(datos['Close'].iloc[-1])
            df_p = datos.reset_index()[['Date', 'Close']]
            df_p.columns = ['ds', 'y']
            df_p['ds'] = df_p['ds'].dt.tz_localize(None)
            m = Prophet(daily_seasonality=True).fit(df_p)
            p_pre = float(m.predict(m.make_future_dataframe(periods=30))['yhat'].iloc[-1])
            st.session_state.cambio = ((p_pre - st.session_state.precio_act) / st.session_state.precio_act) * 100
            st.session_state.analizado = True
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio", f"{st.session_state.precio_act:.2f}{simbolo}")
            c2.metric("Meta 30d", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
            c3.metric("Acciones", f"{(capital/st.session_state.precio_act):.4f}")
            st.line_chart(datos['Close'])

            st.divider()
            st.subheader(f"🔍 {t['diag']}")
            
            # INFORME TRADUCIDO Y EXTENSO
            msg_diag = {
                "Español": f"Análisis de {ticket}: Tendencia del {st.session_state.cambio:.2f}%. Nivel de riesgo para perfil {perfil}: {'Moderado' if perfil != 'Arriesgado' else 'Alto'}.",
                "English": f"Analysis of {ticket}: {st.session_state.cambio:.2f}% trend. Risk level for {perfil} profile: {'Moderate' if perfil != 'Arriesgado' else 'High'}.",
                "Català": f"Anàlisi de {ticket}: Tendència del {st.session_state.cambio:.2f}%. Nivell de risc per perfil {perfil}: {'Moderat' if perfil != 'Arriesgado' else 'Alt'}."
            }
            
            st.markdown(f"""
            #### 📊 {msg_diag[lang_sel]}
            Nuestros algoritmos han procesado los ciclos de mercado. Para un capital de **{capital}{simbolo}**, la estrategia óptima es:
            *   **Gestión de Capital:** No comprometas más del 15% en una sola orden.
            *   **Psicología:** El mercado muestra señales de {'fortaleza' if st.session_state.cambio > 0 else 'debilidad'}. Mantén la disciplina.
            *   **Salida:** El objetivo técnico se sitúa en los {st.session_state.precio_act * (1 + st.session_state.cambio/100):.2f}{simbolo}.
            """)

with tab2:
    st.subheader("💬 Asesoría Cognitiva")
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Pregúntame..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("IA Pensando..."):
            time.sleep(0.6)
            respuesta = generar_respuesta_ia(p, perfil, ticket, st.session_state.cambio, st.session_state.precio_act)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.rerun()

st.caption("InvestMind AI v6.0 | No se requiere API Key")
