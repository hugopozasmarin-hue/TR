import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ESTILOS CSS (MENÚ BLANCO Y INTERFAZ LIMPIA) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

/* BARRA LATERAL BLANCA */
[data-testid="stSidebar"] { 
    background-color: #ffffff !important; 
    border-right: 1px solid #eef2f6; 
}

/* Títulos de campos en sidebar */
.field-title { 
    color: #6366f1; 
    font-size: 10px; 
    font-weight: 800; 
    letter-spacing: 1.5px; 
    text-transform: uppercase; 
    margin-top: 20px; 
    margin-bottom: 8px; 
    display: block; 
    border-bottom: 1px solid #f1f5f9; 
    padding-bottom: 4px; 
}

/* Inputs ajustados para fondo blanco */
.stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input { 
    background-color: #f8fafc !important; 
    color: #1e293b !important; 
    border: 1px solid #e2e8f0 !important; 
    border-radius: 10px !important; 
}

label { display: none !important; }

/* Botón Principal */
.stButton>button { 
    width: 100%; 
    border-radius: 12px; 
    background: linear-gradient(90deg, #6366f1, #06b6d4); 
    color: white !important; 
    font-weight: 800; 
    border: none; 
    padding: 15px; 
    transition: all 0.3s ease; 
}

/* Burbujas de Chat */
.bubble { padding: 16px 20px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; font-size: 14px; line-height: 1.5; }
.user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
.assistant-bubble { background: #f1f5f9; border: 1px solid #e2e8f0; color: #334155 !important; border-bottom-left-radius: 2px; }
.highlight { color: #6366f1; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESUPUESTO","risk_lab":"RIESGO","ass_lab":"ACTIVO (TICKER - Ej: AAPL, BTC-USD)","btn":"ANALIZAR MERCADO","diag":"Consultoría","just":"Análisis Técnico","wait":"Procesando Big Data...","price":"Precio","target":"Objetivo (30d)","shares":"Títulos","disclaimer":"Simulación InvestIA 2026. Riesgo de capital."},
    "English": {"title":"InvestIA Elite","lang_lab":"LANGUAGE","cap":"BUDGET","risk_lab":"RISK","ass_lab":"ASSET (TICKER - e.g. NVDA, BTC-USD)","btn":"ANALYZE MARKET","diag":"Consultancy","just":"Technical Analysis","wait":"Processing Big Data...","price":"Price","target":"Target (30d)","shares":"Shares","disclaimer":"InvestIA 2026 Simulation. Capital risk."},
    "Català": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESSUPOST","risk_lab":"RISC","ass_lab":"ACTIU (TICKER - Ex: TSLA, BTC-USD)","btn":"ANALITZAR MERCAT","diag":"Consultoria","just":"Anàlisi Tècnica","wait":"Analitzant Big Data...","price":"Preu","target":"Objectiu (30d)","shares":"Accions","disclaimer":"Simulació InvestIA 2026. Risc de capital."}
}

# --- INICIALIZACIÓN ---
for key, val in [('messages', []), ('cambio', 0.0), ('analizado', False), ('ticket_act', ""), ('lang', "Español"), ('p_act', 0.0), ('p_pre', 0.0)]:
    if key not in st.session_state: st.session_state[key] = val

# --- SIDEBAR (BLANCO) ---
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

# --- LÓGICA IA ---
def hablar_con_ia(pregunta, lang, ticket, cambio, perfil):
    try:
        client = Groq(api_key="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")
        prompt = f"Eres InvestIA (2026). Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":prompt},{"role":"user","content":pregunta}])
        return res.choices[0].message.content
    except: return "Servicio de IA temporalmente no disponible."

# --- INTERFAZ PRINCIPAL ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", f"💬 {t['diag']}"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                # CORRECCIÓN DE ERROR PROPHET (ZONAS HORARIAS)
                df_p = datos.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = pd.to_datetime(df_p['ds']).dt.tz_localize(None)
                
                m = Prophet(daily_seasonality=True).fit(df_p)
                futuro = m.make_future_dataframe(periods=30)
                pred = m.predict(futuro)
                
                st.session_state.p_act = float(datos['Close'].iloc[-1])
                st.session_state.p_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((st.session_state.p_pre - st.session_state.p_act) / st.session_state.p_act) * 100
                st.session_state.ticket_act = ticket
                st.session_state.analizado = True
            else:
                st.error("Ticker no válido o sin datos.")

    if st.session_state.analizado:
        c1, c2, c3 = st.columns(3)
        c1.metric(t["price"], f"{st.session_state.p_act:.2f}€")
        c2.metric(t["target"], f"{st.session_state.p_pre:.2f}€", f"{st.session_state.cambio:.2f}%")
        c3.metric(t["shares"], f"{(capital/st.session_state.p_act):.2f}")
        st.line_chart(datos['Close'])
        
        st.markdown(f"### 📊 {t['just']}")
        txt = f"Basado en datos históricos de **{st.session_state.ticket_act}**, la IA proyecta un movimiento del <span class='highlight'>{st.session_state.cambio:.2f}%</span>."
        st.markdown(f'<div class="assistant-bubble">{txt}</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.analizado:
        for m in st.session_state.messages:
            clase = "user-bubble" if m["role"]=="user" else "assistant-bubble"
            st.markdown(f'<div class="bubble {clase}">{m["content"]}</div>', unsafe_allow_html=True)
        
        if p := st.chat_input("Pregunta a la IA..."):
            st.session_state.messages.append({"role":"user","content":p})
            res = hablar_con_ia(p, st.session_state.lang, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role":"assistant","content":res})
            st.rerun()
    else:
        st.info("Inicia el análisis técnico para habilitar la consultoría.")

st.markdown("---")
st.caption(f"⚠️ {t['disclaimer']}")
