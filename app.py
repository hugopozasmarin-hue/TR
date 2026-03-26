import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO ELITE (DISEÑO FINAL DE SIDEBAR)
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    /* ESTÉTICA PANEL LATERAL */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0c10 0%, #161821 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* RECUADROS DE ENTRADA VISIBLES */
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        background-color: #3b3d4a !important;
        color: #ffffff !important;
        border: 1px solid #555 !important;
        border-radius: 12px !important;
    }
    
    /* TÍTULOS DE SECCIÓN PREMIUM */
    .sidebar-header {
        color: #818cf8;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin: 25px 0 12px 0;
        border-bottom: 1px solid rgba(129, 140, 248, 0.2);
        padding-bottom: 5px;
    }

    /* BOTÓN PRINCIPAL */
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #6366f1, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 14px;
        transition: all 0.4s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.4); }

    /* BURBUJAS DE CHAT */
    .bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
    .user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
    
    .highlight { color: #00ffcc; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO MULTILINGÜE (CON "AJUSTES" E "IDIOMA")
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTES", "lang_lab": "Idioma",
        "conf": "🛠️ CONFIGURACIÓN", "curr": "MONEDA DE CUENTA", "cap": "CAPITAL A INVERTIR", 
        "risk_lab": "PERFIL DE RIESGO", "ass_lab": "ACTIVO FINANCIERO", "btn": "EJECUTAR ANÁLISIS", 
        "diag": "Consultoría Estratégica", "just": "Justificación Técnica", 
        "wait": "Analizando Big Data...", "price": "Precio Hoy", "shares": "Acciones", 
        "disclaimer": "Aviso: La inversión conlleva riesgos. No somos responsables de pérdidas.",
        "psy_strat": "Psicología y Estrategia", "entry": "Punto de Entrada", "stop": "Stop-Loss Institucional",
        "perfiles": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ SETTINGS", "lang_lab": "Language",
        "conf": "🛠️ CONFIGURATION", "curr": "ACCOUNT CURRENCY", "cap": "CAPITAL TO INVEST", 
        "risk_lab": "RISK PROFILE", "ass_lab": "FINANCIAL ASSET", "btn": "EXECUTE ANALYSIS", 
        "diag": "Strategic Consultancy", "just": "Technical Justification", 
        "wait": "Analyzing Big Data...", "price": "Price Today", "shares": "Shares", 
        "disclaimer": "Disclaimer: Investment carries risk. We are not liable for losses.",
        "psy_strat": "Psychology & Strategy", "entry": "Entry Point", "stop": "Institutional Stop-Loss",
        "perfiles": ["Conservative", "Moderate", "Aggressive"]
    },
    "Català": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTOS", "lang_lab": "Idioma",
        "conf": "🛠️ CONFIGURACIÓ", "curr": "MONEDA DEL COMPTE", "cap": "CAPITAL A INVERTIR", 
        "risk_lab": "PERFIL DE RISC", "ass_lab": "ACTIU FINANCER", "btn": "EXECUTAR ANÀLISI", 
        "diag": "Consultoria Estratègica", "just": "Justificació Tècnica", 
        "wait": "Analitzant Big Data...", "price": "Preu Avui", "shares": "Accions", 
        "disclaimer": "Avís: La inversió comporta riscos. No som responsables de pèrdues.",
        "psy_strat": "Psicologia i Estratègia", "entry": "Punt d'Entrada", "stop": "Stop-Loss Institucional",
        "perfiles": ["Conservador", "Moderat", "Arriscat"]
    }
}

# 3. MEMORIA DE SESIÓN
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"
if 'lang' not in st.session_state: st.session_state.lang = "Español"

# 4. BARRA LATERAL (ESTÉTICA Y LÓGICA DE IDIOMA)
with st.sidebar:
    # Ajustes Expandibles
    # Primero cargamos el idioma actual para el título del expander
    current_t = languages[st.session_state.lang]
    
    with st.expander(current_t["ajust"], expanded=False):
        st.session_state.lang = st.selectbox(current_t["lang_lab"], ["Español", "English", "Català"], index=["Español", "English", "Català"].index(st.session_state.lang))
    
    # Recargar textos tras posible cambio
    t = languages[st.session_state.lang]
    
    # SECCIÓN: CONFIGURACIÓN
    st.markdown(f'<p class="sidebar-header">{t["conf"]}</p>', unsafe_allow_html=True)
    moneda = st.radio(t["curr"], ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(t["cap"], min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk_lab"], t["perfiles"])
    
    # SECCIÓN: ACTIVO
    st.markdown(f'<p class="sidebar-header">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("TICKER:", value="AAPL").upper().strip()

# 5. MOTOR IA (GROQ)
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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" 
    try:
        client = Groq(api_key=api_key)
        prompt = f"Asesor financiero. Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}])
        return completion.choices.message.content
    except: return "Servicio de IA ocupado."

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

                # CONSULTORÍA CON RESALTADO CIÁN
                st.divider()
                st.header(f"💼 {t['diag']}")
                st.subheader(f"📊 {t['just']}")
                st.write(f"""
                Nuestro análisis proyecta un movimiento del <span class='highlight'>{st.session_state.cambio:.2f}%</span> para **{ticket}**. 
                Se justifica por la inercia histórica de 5 años y la convergencia de ciclos institucionales.
                """, unsafe_allow_html=True)
                
                st.markdown(f"### 🧠 {t['psy_strat']} ({perfil})")
                st.markdown(f"""
                *   **{t['entry']}:** {p_act:.2f} {simbolo}.
                *   **Estrategia:** {"Protección" if st.session_state.cambio < 0 else "Acumulación"}.
                *   **{t['stop']}:** <span class='highlight'>{p_act * 0.94:.2f} {simbolo}</span>.
                """, unsafe_allow_html=True)
                
                st.caption(f"🛡️ {t['disclaimer']}")
            else: st.error("Error: Ticker no encontrado.")

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

st.caption("InvestMind AI Elite Platinum v13.0 | Badalona, 2026")
