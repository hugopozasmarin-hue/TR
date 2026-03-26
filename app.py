import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

# 2. ESTILO CSS (CORREGIDO PARA QUE NO SE VEA EL CÓDIGO)
st.markdown("""
    <style>
    /* Fuente y Animaciones */
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .main .block-container { animation: fadeIn 0.8s ease-out; }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1c23 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Inputs Estilo Glass */
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        background-color: rgba(59, 61, 74, 0.5) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }

    /* Botón Principal */
    .stButton>button {
        width: 100%; border-radius: 14px;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 15px;
        transition: all 0.4s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,123,255,0.4); }

    /* Chat Bubbles */
    .bubble { padding: 18px 22px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; font-size: 15px; }
    .user-bubble { background: linear-gradient(135deg, #007bff, #0056b3); color: white !important; margin-left: auto; border-bottom-right-radius: 4px; }
    .assistant-bubble { background: rgba(38, 39, 48, 0.8); border: 1px solid rgba(255,255,255,0.1); color: #eee !important; border-bottom-left-radius: 4px; }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. TRADUCCIONES
languages = {
    "Español": {
        "title": "InvestMind AI", "config": "Configuración Elite", "btn": "EJECUTAR ANÁLISIS",
        "diag": "Consultoría Estratégica", "wait": "Analizando...", "risk": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "InvestMind AI", "config": "Elite Settings", "btn": "EXECUTE ANALYSIS",
        "diag": "Strategic Consultancy", "wait": "Analyzing...", "risk": ["Conservative", "Moderate", "Aggressive"]
    },
    "Català": {
        "title": "InvestMind AI", "config": "Configuració Elit", "btn": "EXECUTAR ANÀLISI",
        "diag": "Consultoria Estratègica", "wait": "Analitzant...", "risk": ["Conservador", "Moderat", "Arriscat"]
    }
}

# 4. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False

# 5. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️ System", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    
    t = languages[lang_sel]
    st.markdown(f'<p style="color:#888; font-weight:800; font-size:12px; letter-spacing:2px; margin-bottom:20px;">{t["config"].upper()}</p>', unsafe_allow_html=True)
    
    moneda = st.radio("Currency", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Capital", min_value=1.0, value=1000.0)
    perfil = st.selectbox("Profile", t["risk"])
    
    st.markdown("---")
    modo_ticker = st.checkbox("Manual Ticker Input", value=False)
    ticket = st.text_input("Enter Ticker:").upper() if modo_ticker else st.selectbox("Select Asset", ["AAPL", "TSLA", "BTC-USD", "MSFT", "NVDA"])

# 6. CUERPO PRINCIPAL
st.title(f"💎 {t['title']} Elite")
tab1, tab2 = st.tabs(["📉 Terminal de Análisis", "💬 Chat Asesor Pro"])

with tab1:
    if st.button(t["btn"]):
        if not ticket:
            st.warning("⚠️ Provide a Ticker.")
        else:
            with st.status(t["wait"]) as s:
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
                    s.update(label="Complete", state="complete")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current", f"{p_act:.2f}{simbolo}")
                    c2.metric("Target 30d", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                    c3.metric("Units", f"{(capital/p_act):.4f}")
                    st.line_chart(datos['Close'])

                    st.divider()
                    st.header(f"💼 {t['diag']}")
                    st.markdown(f"""
                    ### 📂 Dossier: {ticket} | Perfil {perfil}
                    La IA proyecta un **{st.session_state.cambio:.2f}%**. Para tus **{capital}{simbolo}**:
                    * **Estrategia:** {'Acumulación' if st.session_state.cambio > 0 else 'Protección'}. No invertir más del 10% aquí.
                    * **Psicología:** Horizonte a 30 días. Ignora el ruido diario.
                    * **Seguridad:** Stop-Loss sugerido en **{p_act * 0.95:.2f}{simbolo}**.
                    """)
                else: st.error("No Data.")

with tab2:
    st.subheader("💬 Cognitive Advisory")
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Ask..."):
        st.session_state.messages.append({"role": "user", "content": p})
        tend = "alcista" if st.session_state.cambio > 0 else "bajista"
        res = f"[{lang_sel}] Para {ticket} ({tend} {st.session_state.cambio:.2f}%) y perfil {perfil}, sugiero prudencia operativa con tus {capital}{simbolo}."
        st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()
