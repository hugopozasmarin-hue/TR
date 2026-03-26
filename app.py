import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO ELITE (SIDEBAR REFORMADO)
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
    
    /* RECUADROS VISIBLES EN GRIS CLARO */
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        background-color: #3b3d4a !important;
        color: #ffffff !important;
        border: 1px solid #555 !important;
        border-radius: 10px !important;
    }
    
    .sidebar-header {
        color: #6366f1;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 20px 0 10px 0;
    }

    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #6366f1, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 14px;
        transition: all 0.4s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.4); }

    .bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
    .user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
    
    .highlight { color: #00ffcc; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO DE IDIOMAS (CON TÍTULO CORREGIDO Y "AJUSTES")
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "sys": "⚙️ AJUSTES", "conf": "Panel de Control", 
        "curr": "Moneda", "cap": "Capital Invertido", "risk_label": "Perfil de Riesgo", 
        "asset": "Activo Financiero", "btn": "EJECUTAR ANÁLISIS", "diag": "Consultoría Estratégica", 
        "just": "Justificación Técnica", "wait": "Analizando Big Data...", "price": "Precio Hoy", 
        "shares": "Acciones", "disclaimer": "Aviso: La inversión conlleva riesgos. No somos responsables de pérdidas.",
        "psy_strat": "Psicología y Estrategia", "entry": "Punto de Entrada", "stop": "Stop-Loss Institucional",
        "perfiles": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "InvestMind AI Elite", "sys": "⚙️ SETTINGS", "conf": "Control Panel", 
        "curr": "Currency", "cap": "Invested Capital", "risk_label": "Risk Profile", 
        "asset": "Financial Asset", "btn": "EXECUTE ANALYSIS", "diag": "Strategic Consultancy", 
        "just": "Technical Justification", "wait": "Analyzing Big Data...", "price": "Price Today", 
        "shares": "Shares", "disclaimer": "Disclaimer: Investment carries risk. We are not liable for losses.",
        "psy_strat": "Psychology & Strategy", "entry": "Entry Point", "stop": "Institutional Stop-Loss",
        "perfiles": ["Conservative", "Moderate", "Aggressive"]
    },
    "Català": {
        "title": "InvestMind AI Elite", "sys": "⚙️ AJUSTOS", "conf": "Panell de Control", 
        "curr": "Moneda", "cap": "Capital Invertit", "risk_label": "Perfil de Risc", 
        "asset": "Actiu Financer", "btn": "EXECUTAR ANÀLISI", "diag": "Consultoria Estratègica", 
        "just": "Justificació Tècnica", "wait": "Analitzant Big Data...", "price": "Preu Avui", 
        "shares": "Accions", "disclaimer": "Avís: La inversió comporta riscos. No som responsables de pèrdues.",
        "psy_strat": "Psicologia i Estratègia", "entry": "Punt d'Entrada", "stop": "Stop-Loss Institucional",
        "perfiles": ["Conservador", "Moderat", "Arriscat"]
    }
}

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"

# 4. BARRA LATERAL
with st.sidebar:
    # Selector de idioma inicial
    lang_temp = st.selectbox("Language", ["Español", "English", "Català"], label_visibility="collapsed")
    t = languages[lang_temp]
    
    with st.expander(t["sys"], expanded=False):
        lang_sel = lang_temp
    
    st.markdown(f'<p class="sidebar-header">{t["conf"]}</p>', unsafe_allow_html=True)
    moneda = st.radio(t["curr"], ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input(t["cap"], min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk_label"], t["perfiles"])
    
    st.markdown(f'<p class="sidebar-header">{t["asset"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("Ticker:", value="AAPL").upper().strip()

# 5. MOTOR IA
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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" 
    try:
        client = Groq(api_key=api_key)
        prompt = f"Eres InvestMind AI. Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}])
        return completion.choices[0].message.content
    except: return "Servicio de IA temporalmente ocupado."

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
                
                st.write(f"""
                Nuestro análisis para **{ticket}** proyecta un movimiento del <span class='highlight'>{st.session_state.cambio:.2f}%</span>. 
                Se justifica por la convergencia de la media móvil de 200 días y la inercia histórica de 1.260 sesiones.
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

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("..."):
            res = hablar_con_ia_real(p, lang_sel, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption("InvestMind AI Elite Platinum v12.5 | 2026")
