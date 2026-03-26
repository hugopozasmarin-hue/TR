import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO (UI ELITE 2026)
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    /* PANEL LATERAL DE LUJO */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050505 0%, #1a1c23 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
        padding: 2rem 1rem;
    }

    label { display: none !important; }

    /* TÍTULOS DE SECCIÓN REFINADOS */
    .field-title {
        color: #a5b4fc;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 25px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        opacity: 0.8;
    }

    /* INPUTS VISIBLES */
    .stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input {
        background-color: #1e1f26 !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    .stSelectbox div[role="button"] { background-color: #1e1f26 !important; }

    /* BOTÓN CON DEGRADADO */
    .stButton>button {
        width: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
        color: white !important; font-weight: 700; border: none; padding: 12px;
        transition: all 0.3s ease; margin-top: 20px;
        text-transform: uppercase; font-size: 13px;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(79,70,229,0.5); }

    /* CHAT */
    .bubble { padding: 15px 20px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; font-size: 14.5px; }
    .user-bubble { background: #4f46e5; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #1e293b; border: 1px solid #334155; color: #f1f5f9 !important; border-bottom-left-radius: 2px; }
    
    .highlight { color: #22d3ee; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO DE TRADUCCIÓN COMPLETO
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTES", "lang_name": "IDIOMA",
        "conf": "📊 CONFIGURACIÓN", "curr": "💰 MONEDA", "cap": "💵 CAPITAL", 
        "risk_lab": "🛡️ RIESGO", "ass_lab": "🔍 ACTIVO", "btn": "EJECUTAR ANÁLISIS", 
        "diag": "Consultoría Estratégica", "just": "Justificación Técnica", 
        "wait": "Analizando Big Data...", "price": "Precio Hoy", "target": "Objetivo IA (30d)", 
        "shares": "Acciones a Comprar", "disclaimer": "Simulación 2026. Riesgo de capital."
    },
    "English": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ SETTINGS", "lang_name": "LANGUAGE",
        "conf": "📊 CONFIGURATION", "curr": "💰 CURRENCY", "cap": "💵 CAPITAL", 
        "risk_lab": "🛡️ RISK", "ass_lab": "🔍 ASSET", "btn": "EXECUTE ANALYSIS", 
        "diag": "Strategic Consultancy", "just": "Technical Justification", 
        "wait": "Analyzing Big Data...", "price": "Current Price", "target": "AI Target (30d)", 
        "shares": "Shares to Buy", "disclaimer": "2026 Simulation. Capital at risk."
    },
    "Català": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTOS", "lang_name": "IDIOMA",
        "conf": "📊 CONFIGURACIÓ", "curr": "💰 MONEDA", "cap": "💵 CAPITAL", 
        "risk_lab": "🛡️ RISC", "ass_lab": "🔍 ACTIU", "btn": "EXECUTAR ANÀLISI", 
        "diag": "Consultoria Estratègica", "just": "Justificació Tècnica", 
        "wait": "Analitzant Big Data...", "price": "Preu Avui", "target": "Objectiu IA (30d)", 
        "shares": "Accions a Comprar", "disclaimer": "Simulació 2026. Risc de capital."
    }
}

# 3. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"
if 'lang' not in st.session_state: st.session_state.lang = "Español"

# 4. BARRA LATERAL (ESTÉTICA MEJORADA)
with st.sidebar:
    # Ajustes con traducción de la palabra "Idioma"
    curr_t = languages[st.session_state.lang]
    with st.expander(curr_t["ajust"], expanded=False):
        st.markdown(f'<p class="field-title">{curr_t["lang_name"]}</p>', unsafe_allow_html=True)
        st.session_state.lang = st.selectbox("", ["Español", "English", "Català"], index=["Español", "English", "Català"].index(st.session_state.lang))
    
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["curr"]}</p>', unsafe_allow_html=True)
    moneda = st.radio("", ["USD ($)", "EUR (€)"], horizontal=True)
    simbolo = "$" if "USD" in moneda else "€"
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# 5. MOTOR IA (GROQ 2026)
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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" 
    try:
        client = Groq(api_key=api_key)
        prompt = f"Eres InvestMind AI (Marzo 2026). Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang} con sabiduría financiera."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}])
        return completion.choices.message.content
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

                # MÉTRICAS CON TÍTULOS CLAROS
                c1, c2, c3 = st.columns(3)
                c1.metric(label=t["price"], value=f"{p_act:.2f}{simbolo}")
                c2.metric(label=t["target"], value=f"{p_pre:.2f}{simbolo}", delta=f"{st.session_state.cambio:.2f}%")
                c3.metric(label=t["shares"], value=f"{(capital/p_act):.4f}")
                
                st.line_chart(datos['Close'])

                # CONSULTORÍA DETALLADA
                st.divider()
                st.header(f"💼 {t['diag']}")
                st.subheader(f"📊 {t['just']}")
                
                just_txt = {
                    "Español": f"Nuestros modelos proyectan un <span class='highlight'>{st.session_state.cambio:.2f}%</span> para **{ticket}**. La justificación reside en la inercia de 1,260 sesiones y la convergencia de soportes en {p_act:.2f}.",
                    "English": f"Our models project <span class='highlight'>{st.session_state.cambio:.2f}%</span> for **{ticket}**. This is justified by 1,260-session inertia and support convergence at {p_act:.2f}.",
                    "Català": f"Els nostres models projecten un <span class='highlight'>{st.session_state.cambio:.2f}%</span> per a **{ticket}**. La justificació resideix en la inèrcia de 1.260 sessions i la convergència de suports a {p_act:.2f}."
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

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("..."):
            res = hablar_con_ia_real(p, st.session_state.lang, st.session_state.ticket_act, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.caption("InvestMind AI Platinum Edition v15.5 | 2026")
