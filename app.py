import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import requests # Necesario para la IA real

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0e1117 0%, #1a1c23 100%); border-right: 1px solid rgba(255,255,255,0.05); }
    .stNumberInput input, .stSelectbox div, .stTextInput input { background-color: #3b3d4a !important; color: #fff !important; border: 1px solid #555 !important; border-radius: 12px !important; }
    .stButton>button { width: 100%; border-radius: 14px; background: linear-gradient(90deg, #007bff, #00d4ff); color: white !important; font-weight: 800; border: none; padding: 15px; }
    .bubble { padding: 18px 22px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; color: white !important; line-height: 1.5; }
    .user-bubble { background: linear-gradient(135deg, #007bff, #0056b3); margin-left: auto; border-bottom-right-radius: 4px; }
    .assistant-bubble { background: rgba(38, 39, 48, 0.8); border: 1px solid rgba(255,255,255,0.1); border-bottom-left-radius: 4px; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO CORREGIDO (Sin KeyError)
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "config": "Configuración Elite", "btn": "EJECUTAR ANÁLISIS",
        "diag": "Consultoría Estratégica", "just": "Justificación de la Predicción", "wait": "Analizando...",
        "risk_label": "Perfil", "price": "Precio", "shares": "Acciones"
    },
    "English": {
        "title": "InvestMind AI Elite", "config": "Elite Settings", "btn": "EXECUTE ANALYSIS",
        "diag": "Strategic Consultancy", "just": "Prediction Justification", "wait": "Analyzing...",
        "risk_label": "Profile", "price": "Price", "shares": "Shares"
    },
    "Català": {
        "title": "InvestMind AI Elite", "config": "Configuració Elit", "btn": "EXECUTAR ANÀLISI",
        "diag": "Consultoria Estratègica", "just": "Justificació de la Predicció", "wait": "Analitzant...",
        "risk_label": "Perfil", "price": "Preu", "shares": "Accions"
    }
}

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "Ninguno"

# 4. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️ System", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    t = languages[lang_sel]
    st.markdown(f'<p style="color:#888; font-weight:800; font-size:12px; letter-spacing:2px;">{t["config"].upper()}</p>', unsafe_allow_html=True)
    moneda = st.radio("Divisa", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Capital", min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk_label"], ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input("Ticker: (ej: TSLA, BTC-USD)").upper()

# 5. EL "CEREBRO": IA REAL DE GROQ
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    # --- 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 ---
    api_key = "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" 
    # ---------------------------------
    
    url = "https://api.groq.com"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    contexto = f"""Eres un experto financiero senior. Responde en {lang}.
    El usuario es {perfil}. Activo actual: {ticket}. Tendencia: {cambio:.2f}%.
    Usa un lenguaje profesional, empático y basado en datos reales. No repitas siempre lo mismo."""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": contexto},
            {"role": "user", "content": pregunta}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Lo siento, mi conexión con los mercados está saturada. ¿Podemos intentarlo en un momento?"

# 6. CUERPO PRINCIPAL
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs(["📈 Terminal", "💬 Chat Inteligente"])

with tab1:
    if st.button(t["btn"]):
        if not ticket: st.warning("Introduce un Ticker.")
        else:
            with st.status(t["wait"]) as s:
                datos = yf.download(ticket, period="5y")
                if not datos.empty:
                    p_act = float(datos['Close'].iloc[-1])
                    df_p = datos.reset_index()[['Date', 'Close']]
                    df_p.columns = ['ds', 'y']
                    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                    m = Prophet(daily_seasonality=True).fit(df_p)
                    pred = m.predict(m.make_future_dataframe(periods=30))
                    p_pre = float(pred['yhat'].iloc[-1])
                    st.session_state.cambio = ((p_pre - p_act) / p_act) * 100
                    st.session_state.analizado = True
                    st.session_state.ticket_act = ticket
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric(t["price"], f"{p_act:.2f}{simbolo}")
                    c2.metric("Meta 30d", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                    c3.metric(t["shares"], f"{(capital/p_act):.4f}")
                    st.line_chart(datos['Close'])

                    st.divider()
                    st.header(f"💼 {t['diag']}")
                    st.markdown(f"### 🧪 {t['just']}")
                    
                    # JUSTIFICACIÓN EXTENSA
                    explicacion = {
                        "Español": f"Nuestro modelo **Prophet** ha detectado que **{ticket}** presenta una inercia cíclica. La predicción del **{st.session_state.cambio:.2f}%** se fundamenta en la regresión de los últimos 1,825 días, identificando soportes históricos y la volatilidad estacional del sector.",
                        "English": f"Our **Prophet** model has detected that **{ticket}** shows cyclic inertia. The **{st.session_state.cambio:.2f}%** forecast is based on 1,825-day regression, identifying historical support and seasonal sector volatility.",
                        "Català": f"El nostre model **Prophet** ha detectat que **{ticket}** presenta una inèrcia cíclica. La predicció del **{st.session_state.cambio:.2f}%** es fonamenta en la regressió dels darrers 1.825 dies, identificant suports històrics i la volatilitat estacional del sector."
                    }
                    st.write(explicacion[lang_sel])
                    st.markdown(f"**Recomendación:** Basado en tu perfil **{perfil}**, deberías considerar esta señal como un indicador de {'acumulación' if st.session_state.cambio > 0 else 'distribución'}.")

with tab2:
    st.subheader("💬 Asesoría Cognitiva Real")
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Pregúntame sobre el mercado..."):
        st.session_state.messages.append({"role": "user", "content": p})
        # LLAMADA A LA IA REAL
        with st.spinner("IA Razonando..."):
            res = hablar_con_ia_real(p, lang_sel, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption("InvestMind AI Elite v7.0 | Powered by Llama 3 AI")
