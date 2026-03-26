import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO ELITE (UI FIX: RECTÁNGULOS Y TÍTULOS)
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    /* PANEL LATERAL */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0c10 0%, #161821 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* OCULTAR ETIQUETAS ORIGINALES PARA EVITAR DESORDEN */
    label { display: none !important; }

    /* TÍTULOS PERSONALIZADOS (Pequeños, elegantes y sin rectángulos raros) */
    .field-title {
        color: #818cf8;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 20px;
        display: block;
    }

    /* RECTÁNGULOS DE ENTRADA (Más grandes y espaciosos) */
    .stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
        height: 48px !important; /* Más alto */
        padding: 0 15px !important; /* Más espacio lateral interno */
        font-size: 15px !important;
    }
    
    /* Arreglo específico para el dropdown de Selectbox */
    .stSelectbox div[role="button"] {
        background-color: #262730 !important;
        border-radius: 10px !important;
        height: 48px !important;
        display: flex;
        align-items: center;
    }

    /* BOTÓN PRINCIPAL */
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #6366f1, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 14px;
        transition: all 0.4s ease; margin-top: 10px;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.4); }

    /* BURBUJAS DE CHAT */
    .bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
    .user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
    
    .highlight { color: #00ffcc; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO MULTILINGÜE
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTES", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓN", "curr": "MONEDA", "cap": "CAPITAL A INVERTIR", 
        "risk_lab": "PERFIL DE RIESGO", "ass_lab": "ACTIVO FINANCIERO", "btn": "EJECUTAR ANÁLISIS", 
        "diag": "Consultoría Estratégica", "just": "Justificación Técnica", 
        "wait": "Analizando Big Data...", "price": "Precio Hoy", "shares": "Acciones", 
        "disclaimer": "Aviso: La inversión conlleva riesgos.", "psy_strat": "Psicología y Estrategia", 
        "entry": "Punto de Entrada", "stop": "Stop-Loss", "perfiles": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ SETTINGS", "lang_lab": "LANGUAGE",
        "conf": "🛠️ CONFIGURATION", "curr": "CURRENCY", "cap": "CAPITAL TO INVEST", 
        "risk_lab": "RISK PROFILE", "ass_lab": "FINANCIAL ASSET", "btn": "EXECUTE ANALYSIS", 
        "diag": "Strategic Consultancy", "just": "Technical Justification", 
        "wait": "Analyzing Big Data...", "price": "Price Today", "shares": "Shares", 
        "disclaimer": "Disclaimer: Investment carries risk.", "psy_strat": "Psychology & Strategy", 
        "entry": "Entry Point", "stop": "Stop-Loss", "perfiles": ["Conservative", "Moderate", "Aggressive"]
    },
    "Català": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTOS", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓ", "curr": "MONEDA", "cap": "CAPITAL A INVERTIR", 
        "risk_lab": "PERFIL DE RISC", "ass_lab": "ACTIU FINANCER", "btn": "EXECUTAR ANÀLISI", 
        "diag": "Consultoria Estratègica", "just": "Justificació Tècnica", 
        "wait": "Analitzant Big Data...", "price": "Preu Avui", "shares": "Accions", 
        "disclaimer": "Avís: La inversió comporta riscos.", "psy_strat": "Psicologia i Estratègia", 
        "entry": "Punt d'Entrada", "stop": "Stop-Loss", "perfiles": ["Conservador", "Moderat", "Arriscat"]
    }
}

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"
if 'lang' not in st.session_state: st.session_state.lang = "Español"

# 4. BARRA LATERAL (FIX UI)
with st.sidebar:
    curr_t = languages[st.session_state.lang]
    
    with st.expander(curr_t["ajust"], expanded=False):
        st.markdown(f'<p class="field-title">{curr_t["lang_lab"]}</p>', unsafe_allow_html=True)
        st.session_state.lang = st.selectbox("", ["Español", "English", "Català"], index=["Español", "English", "Català"].index(st.session_state.lang))
    
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["curr"]}</p>', unsafe_allow_html=True)
    moneda = st.radio("", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", t["perfiles"])
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# 5. MOTOR IA (GROQ)
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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" 
    try:
        client = Groq(api_key=api_key)
        prompt = f"Asesor financiero. Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}])
        return completion.choices.message.content
    except: return "Servicio ocupado."

# 6. CUERPO PRINCIPAL
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", f"💬 {t['diag']}"])

with tab1:
    if st.button(t["btn"]):
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
                c2.metric("Target 30d", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/p_act):.4f}")
                st.line_chart(datos['Close'])

                st.divider()
                st.header(f"💼 {t['diag']}")
                st.subheader(f"📊 {t['just']}")
                st.write(f"Análisis para **{ticket}**: <span class='highlight'>{st.session_state.cambio:.2f}%</span> proyectado.", unsafe_allow_html=True)
                
                st.markdown(f"### 🧠 {t['psy_strat']} ({perfil})")
                st.markdown(f"""
                *   **{t['entry']}:** {p_act:.2f} {simbolo}.
                *   **{t['stop']}:** <span class='highlight'>{p_act * 0.94:.2f} {simbolo}</span>.
                """, unsafe_allow_html=True)
                st.caption(f"🛡️ {t['disclaimer']}")
            else: st.error("Ticker Error.")

with tab2:
    st.subheader(t["diag"])
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("..."):
            res = hablar_con_ia_real(p, st.session_state.lang, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption("InvestMind AI v13.5 | 2026")
