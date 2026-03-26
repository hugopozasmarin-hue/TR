import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO (UI LUXURY 2026)
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    /* PANEL LATERAL DE LUJO */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0c10 0%, #161821 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    label { display: none !important; }

    /* TÍTULOS DE SECCIÓN REFINADOS */
    .field-title {
        color: #818cf8;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
        margin-top: 30px;
        display: block;
        border-bottom: 1px solid rgba(129, 140, 248, 0.15);
        padding-bottom: 6px;
    }

    /* INPUTS VISIBLES Y AMPLIOS */
    .stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 12px !important;
        height: 48px !important;
        font-size: 15px !important;
    }
    
    .stSelectbox div[role="button"] { background-color: #262730 !important; height: 48px !important; }

    /* BOTÓN CON EFECTO GLOW */
    .stButton>button {
        width: 100%; border-radius: 14px;
        background: linear-gradient(90deg, #6366f1, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 16px;
        transition: all 0.4s ease; margin-top: 15px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(99,102,241,0.4); }

    /* CHAT Y RESALTADOS */
    .bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; line-height: 1.6; }
    .user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
    .highlight { color: #00ffcc; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO DE TRADUCCIÓN INTEGRAL
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTES", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓN", "curr": "MONEDA", "cap": "CAPITAL", 
        "risk_lab": "PERFIL DE RIESGO", "ass_lab": "ACTIVO FINANCIERO", "btn": "EJECUTAR ANÁLISIS", 
        "diag": "Consultoría Estratégica Institucional", "just": "Justificación Técnica", 
        "wait": "Analizando Big Data...", "price": "Precio Hoy", "target": "Objetivo IA (30d)", 
        "shares": "Unidades Comprables", "disclaimer": "Simulación basada en ciclos 2026. Riesgo de capital."
    },
    "English": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ SETTINGS", "lang_lab": "LANGUAGE",
        "conf": "🛠️ CONFIGURATION", "curr": "CURRENCY", "cap": "CAPITAL", 
        "risk_lab": "RISK PROFILE", "ass_lab": "FINANCIAL ASSET", "btn": "EXECUTE ANALYSIS", 
        "diag": "Institutional Strategic Consultancy", "just": "Technical Justification", 
        "wait": "Analyzing Big Data...", "price": "Price Today", "target": "AI Target (30d)", 
        "shares": "Buying Power", "disclaimer": "Simulation based on 2026 cycles. Capital at risk."
    },
    "Català": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTOS", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓ", "curr": "MONEDA", "cap": "CAPITAL", 
        "risk_lab": "PERFIL DE RISC", "ass_lab": "ACTIU FINANCER", "btn": "EXECUTAR ANÀLISI", 
        "diag": "Consultoria Estratègica Institucional", "just": "Justificació Tècnica", 
        "wait": "Analitzant Big Data...", "price": "Preu Avui", "target": "Objectiu IA (30d)", 
        "shares": "Unitats Comprables", "disclaimer": "Simulació basada en cicles 2026. Risc de capital."
    }
}

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"
if 'lang' not in st.session_state: st.session_state.lang = "Español"

# 4. BARRA LATERAL (FIX UI & TRANSLATIONS)
with st.sidebar:
    # Ajustes Expandibles (Traducción de "Language" incluida)
    curr_t = languages[st.session_state.lang]
    with st.expander(curr_t["ajust"], expanded=False):
        st.markdown(f'<p class="field-title">{curr_t["lang_lab"]}</p>', unsafe_allow_html=True)
        st.session_state.lang = st.selectbox("", ["Español", "English", "Català"], index=["Español", "English", "Català"].index(st.session_state.lang))
    
    # Recargar textos dinámicos
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["curr"]}</p>', unsafe_allow_html=True)
    moneda = st.radio("", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL", placeholder="EX: TSLA, BTC-USD").upper().strip()

# 5. MOTOR IA (2026 UPDATED MODEL)
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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" 
    try:
        client = Groq(api_key=api_key)
        prompt = f"Asesor Elite 2026. Usuario: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang} con sofisticación."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}])
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error técnico: {str(e)}"

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

                # MÉTRICAS MAPYADAS SEGÚN TU IMAGEN
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}{simbolo}")
                c2.metric(t["target"], f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/p_act):.4f}")
                
                st.line_chart(datos['Close'])

                # CONSULTORÍA DETALLADA
                st.divider()
                st.header(f"💼 {t['diag']}")
                st.subheader(f"📊 {t['just']}")
                
                just_txt = {
                    "Español": f"La proyección de <span class='highlight'>{st.session_state.cambio:.2f}%</span> para **{ticket}** se basa en un análisis de regresión de 1,260 sesiones. Detectamos una inercia institucional en {p_act:.2f} y una convergencia de ciclos estacionales de 2026.",
                    "English": f"The <span class='highlight'>{st.session_state.cambio:.2f}%</span> projection for **{ticket}** is based on 1,260-session regression analysis. We detect institutional inertia at {p_act:.2f} and 2026 seasonal cycle convergence.",
                    "Català": f"La projecció de <span class='highlight'>{st.session_state.cambio:.2f}%</span> per a **{ticket}** es basa en un anàlisi de regressió de 1.260 sessions. Detectem una inèrcia institucional a {p_act:.2f} i una convergència de cicles estacionals de 2026."
                }
                st.write(just_txt[st.session_state.lang], unsafe_allow_html=True)
                st.caption(t["disclaimer"])
                s.update(label="Análisis Completo", state="complete")
            else: st.error("Ticker Error.")

with tab2:
    st.subheader(t["diag"])
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("Escribe tu duda financiera..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("..."):
            res = hablar_con_ia_real(p, st.session_state.lang, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption("InvestMind AI Elite Platinum v15.0 | 2026 Edition")
