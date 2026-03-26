import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0c10 0%, #161821 100%); border-right: 1px solid rgba(255,255,255,0.1); }
label { display: none !important; }
.field-title { color: #818cf8; font-size: 10px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-top: 25px; margin-bottom: 8px; display: block; opacity: 0.9; border-bottom: 1px solid rgba(129, 140, 248, 0.2); padding-bottom: 4px; }
.stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input { background-color: #262730 !important; color: #ffffff !important; border: 1px solid #444 !important; border-radius: 10px !important; height: 48px !important; }
.stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #6366f1, #00d4ff); color: white !important; font-weight: 800; border: none; padding: 15px; transition: all 0.4s ease; margin-top: 20px; }
.bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
.user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
.assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
.highlight { color: #00ffcc; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES E INTERFAZ ---
languages = {
    "Español": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESUPUESTO TOTAL","risk_lab":"PERFIL DE RIESGO","ass_lab":"ACTIVO (TICKER - Ej: AAPL)","btn":"EJECUTAR ANÁLISIS","diag":"Consultoría","just":"Justificación Técnica","wait":"Analizando...","price":"Precio Actual","target":"Predicción (30d)","shares":"Acciones","disclaimer":"Simulación InvestIA 2026. Riesgo de capital."},
    "English": {"title":"InvestIA Elite","lang_lab":"LANGUAGE","cap":"TOTAL BUDGET","risk_lab":"RISK PROFILE","ass_lab":"ASSET (TICKER - e.g. NVDA)","btn":"RUN ANALYSIS","diag":"Consultancy","just":"Technical Justification","wait":"Analyzing...","price":"Current Price","target":"Target (30d)","shares":"Shares","disclaimer":"InvestIA 2026 Simulation. Capital risk."},
    "Català": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESSUPOST TOTAL","risk_lab":"PERFIL DE RISC","ass_lab":"ACTIU (TICKER - Ex: TSLA)","btn":"EXECUTAR ANÀLISI","diag":"Consultoria","just":"Justificació Tècnica","wait":"Analitzant...","price":"Preu Actual","target":"Preu previst (30d)","shares":"Accions","disclaimer":"Simulació InvestIA 2026. Risc de capital."}
}

# --- ESTADO DE SESIÓN ---
for key, val in [('messages', []), ('cambio', 0.0), ('analizado', False), ('ticket_act', "N/A"), ('lang', "Español"), ('p_act', 0.0), ('p_pre', 0.0)]:
    if key not in st.session_state: st.session_state[key] = val

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

# --- FUNCIÓN IA ---
def hablar_con_ia(pregunta, lang, ticket, cambio, perfil):
    try:
        client = Groq(api_key="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")
        prompt = f"Eres InvestIA (2026). Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":prompt},{"role":"user","content":pregunta}])
        return res.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- CUERPO PRINCIPAL ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", f"💬 {t['diag']}"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                st.session_state.p_act = float(datos['Close'].iloc[-1])
                df_p = datos.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                
                st.session_state.p_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((st.session_state.p_pre - st.session_state.p_act) / st.session_state.p_act) * 100
                st.session_state.ticket_act = ticket
                st.session_state.analizado = True

        if st.session_state.analizado:
            c1, c2, c3 = st.columns(3)
            c1.metric(t["price"], f"{st.session_state.p_act:.2f}€")
            c2.metric(t["target"], f"{st.session_state.p_pre:.2f}€", f"{st.session_state.cambio:.2f}%")
            c3.metric(t["shares"], f"{(capital/st.session_state.p_act):.2f}")
            st.line_chart(datos['Close'])
            
            st.markdown(f"### 📊 {t['just']}")
            txt = {
                "Español": f"La proyección de <span class='highlight'>{st.session_state.cambio:.2f}%</span> para {ticket} se basa en soportes técnicos en {st.session_state.p_act:.2f}€. Se recomienda prudencia.",
                "English": f"The <span class='highlight'>{st.session_state.cambio:.2f}%</span> projection for {ticket} is based on support at {st.session_state.p_act:.2f}€. Exercise caution.",
                "Català": f"La projecció de <span class='highlight'>{st.session_state.cambio:.2f}%</span> per a {ticket} es basa en suports en {st.session_state.p_act:.2f}€. Es recomana prudència."
            }
            st.markdown(f'<div class="assistant-bubble">{txt[st.session_state.lang]}</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.analizado:
        for m in st.session_state.messages:
            st.markdown(f'<div class="bubble {"user-bubble" if m["role"]=="user" else "assistant-bubble"}">{m["content"]}</div>', unsafe_allow_html=True)
        
        if p := st.chat_input("Pregunta sobre el análisis..."):
            st.session_state.messages.append({"role":"user","content":p})
            res = hablar_con_ia(p, st.session_state.lang, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role":"assistant","content":res})
            st.rerun()
    else: st.info("Ejecuta el análisis primero.")

st.markdown("---")
st.caption(f"⚠️ {t['disclaimer']}")
