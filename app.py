import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time
import random

# 1. CONFIGURACIÓN DE PÁGINA Y FUENTES PERSONALIZADAS
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

# 2. ESTILO CSS AVANZADO (GLASSMORPHISM & ANIMATIONS)
st.markdown("""
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    <style>
    /* Fuente General */
    * { font-family: 'Inter', sans-serif; }
    
    /* Animación de entrada */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .main .block-container { animation: fadeIn 0.8s ease-out; }

    /* Barra Lateral Estilizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1c23 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Inputs con estilo Glass */
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        background-color: rgba(59, 61, 74, 0.5) !important;
        backdrop-filter: blur(10px);
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    .stNumberInput input:focus { border-color: #007bff !important; box-shadow: 0 0 10px rgba(0,123,255,0.3); }

    /* Botón Principal Animado */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        color: white !important;
        font-weight: 800;
        letter-spacing: 1px;
        border: none;
        padding: 15px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(0,123,255,0.4);
    }

    /* Chat Bubbles Estilo Moderno */
    .bubble { padding: 18px 22px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; font-size: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .user-bubble { background: linear-gradient(135deg, #007bff, #0056b3); color: white !important; margin-left: auto; border-bottom-right-radius: 4px; }
    .assistant-bubble { background: rgba(38, 39, 48, 0.8); backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.1); color: #eee !important; border-bottom-left-radius: 4px; }
    
    /* Métricas estilizadas */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. TRADUCCIONES E INFORMES EXTENSOS
languages = {
    "Español": {
        "title": "InvestMind AI", "config": "Configuración Elite", "btn": "EJECUTAR ANÁLISIS",
        "diag": "Consultoría Estratégica de Inversión", "wait": "Analizando ciclos...",
        "risk": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "InvestMind AI", "config": "Elite Settings", "btn": "EXECUTE ANALYSIS",
        "diag": "Strategic Investment Consultancy", "wait": "Analyzing cycles...",
        "risk": ["Conservative", "Moderate", "Aggressive"]
    },
    "Català": {
        "title": "InvestMind AI", "config": "Configuració Elit", "btn": "EXECUTAR ANÀLISI",
        "diag": "Consultoria Estratègica d'Inversió", "wait": "Analitzant cicles...",
        "risk": ["Conservador", "Moderat", "Arriscat"]
    }
}

# 4. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 5. BARRA LATERAL (AJUSTES DISCRETOS)
with st.sidebar:
    with st.expander("⚙️ System", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    
    t = languages[lang_sel]
    st.markdown(f'<p style="color:#888; font-weight:800; font-size:12px; letter-spacing:2px; margin-bottom:20px;">{t["config"].upper()}</p>', unsafe_allow_html=True)
    
    moneda = st.radio("Currency", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Capital", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Profile", t["risk"])
    
    # OPCIÓN DE TICKER PERSONALIZADO
    st.markdown("---")
    modo_ticker = st.checkbox("Manual Ticker Input", value=False)
    if modo_ticker:
        ticket = st.text_input("Enter Ticker (e.g. NVDA, GOOGL):").upper()
    else:
        ticket = st.selectbox("Select Asset", ["AAPL", "TSLA", "BTC-USD", "MSFT", "SAN.MC"])

# 6. CUERPO PRINCIPAL
st.title(f"💎 {t['title']} Elite")
tab1, tab2 = st.tabs(["📉 Terminal de Análisis", "💬 Chat Asesor Pro"])

with tab1:
    if st.button(t["btn"]):
        if not ticket:
            st.warning("⚠️ Please provide a valid Ticker.")
        else:
            with st.status(t["wait"], expanded=False) as s:
                datos = yf.download(ticket, period="5y")
                if not datos.empty:
                    p_act = float(datos['Close'].iloc[-1])
                    df_p = datos.reset_index()[['Date', 'Close']]
                    df_p.columns = ['ds', 'y']
                    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                    m = Prophet(daily_seasonality=True).fit(df_p)
                    p_pre = float(m.predict(m.make_future_dataframe(periods=30))['yhat'].iloc[-1])
                    st.session_state.cambio = ((p_pre - p_act) / p_act) * 100
                    st.session_state.analizado = True
                    s.update(label="Analysis Complete", state="complete")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Value", f"{p_act:.2f}{simbolo}")
                    c2.metric("AI Target (30d)", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                    c3.metric("Buying Power", f"{(capital/p_act):.4f} Units")
                    st.line_chart(datos['Close'])

                    # --- INFORME ESTRATÉGICO EXTENSO (ESTILO CONSULTORÍA) ---
                    st.divider()
                    st.header(f"💼 {t['diag']}")
                    
                    st.markdown(f"""
                    ### 📂 Dossier Técnico: {ticket}
                    Nuestro motor de IA ha procesado los datos de los últimos **1,825 días**. La señal proyectada es de un **{st.session_state.cambio:.2f}%**.
                    
                    #### 🏛️ Arquitectura de Inversión (Perfil {perfil}):
                    *   **Análisis de Tendencia:** Se detecta una estructura de {'fortaleza relativa' if st.session_state.cambio > 3 else 'consolidación lateral'}. El precio de **{p_act:.2f}{simbolo}** actúa como pivote central. 
                    *   **Gestión Monetaria:** Para una inversión de {capital}{simbolo}, sugerimos una **exposición máxima del 12%**. Divida su capital en 3 entradas mensuales para promediar costes.
                    *   **Psicología de Mercado:** Un inversor {perfil} debe vigilar la volatilidad. No se deje llevar por las velas diarias; mantenga el horizonte de 30 a 90 días para permitir que el modelo de IA se cumpla.
                    *   **Resguardo de Capital (Stop-Loss):** Recomendamos fijar una salida de emergencia en los **{p_act * 0.95:.2f}{simbolo}** (umbral de seguridad del 5%).
                    *   **Objetivo de Salida:** La toma de beneficios óptima se sitúa en la banda de los **{p_pre:.2f}{simbolo}**.
                    
                    *Nota: El rendimiento pasado no garantiza resultados futuros. Su capital está sujeto a fluctuaciones del mercado.*
                    """)
                else:
                    st.error("Invalid Ticker or No Data Found.")

with tab2:
    st.subheader("💬 Cognitive Advisory")
    # Historial de Chat
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Ask about your strategy..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("Processing query..."):
            time.sleep(0.5)
            # Lógica mejorada de respuesta
            tend = "alcista" if st.session_state.cambio > 0 else "bajista"
            res = f"[{lang_sel}] Entiendo tu duda sobre '{p}'. Basado en {ticket} y tu perfil {perfil}, la tendencia es {tend} ({st.session_state.cambio:.2f}%). Mi consejo para tus {capital}{simbolo} es {'aprovechar el soporte' if st.session_state.cambio > 2 else 'esperar a que el mercado se calme'}. ¿Deseas que desglosemos más el riesgo?"
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption(f"InvestMind AI v6.0 Platinum Edition | Badalona, 2026")
