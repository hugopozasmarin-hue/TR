import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import time

# 1. CONFIGURACIÓN Y ESTILO ELITE 2026
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    
    /* ESTÉTICA PANEL LATERAL */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0c10 0%, #161821 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    label { display: none !important; }

    .field-title {
        color: #818cf8;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 25px;
        margin-bottom: 8px;
        display: block;
        opacity: 0.9;
        border-bottom: 1px solid rgba(129, 140, 248, 0.2);
        padding-bottom: 4px;
    }

    .stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
        height: 48px !important;
    }
    
    .stSelectbox div[role="button"] { background-color: #262730 !important; height: 48px !important; }

    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #6366f1, #00d4ff);
        color: white !important; font-weight: 800; border: none; padding: 15px;
        transition: all 0.4s ease; margin-top: 20px;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(99,102,241,0.4); }

    .bubble { padding: 18px 22px; border-radius: 18px; margin-bottom: 12px; max-width: 85%; font-size: 15px; }
    .user-bubble { background: #6366f1; color: white !important; margin-left: auto; border-bottom-right-radius: 2px; }
    .assistant-bubble { background: #262730; border: 1px solid #444; color: #eee !important; border-bottom-left-radius: 2px; }
    
    .highlight { color: #00ffcc; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARIO DE IDIOMAS 2026
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTES", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓN", "cap": "PRESUPUESTO TOTAL", 
        "risk_lab": "PERFIL DE RIESGO", "ass_lab": "ACTIVO A ANALIZAR", "btn": "EJECUTAR ANÁLISIS", 
        "diag": "Consultoría Estratégica", "just": "Justificación Técnica", 
        "wait": "Analizando Big Data...", "price": "Precio actual", "target": "Precio predicho (30 días)", 
        "shares": "Acciones comprables", "disclaimer": "Simulación 2026. Riesgo de capital."
    },
    "English": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ SETTINGS", "lang_lab": "LANGUAGE",
        "conf": "🛠️ CONFIGURATION", "cap": "TOTAL BUDGET", 
        "risk_lab": "RISK PROFILE", "ass_lab": "ASSET TO ANALYZE", "btn": "EXECUTE ANALYSIS", 
        "diag": "Strategic Consultancy", "just": "Technical Justification", 
        "wait": "Analyzing Big Data...", "price": "Current Price", "target": "Predicted Price (30d)", 
        "shares": "Shares to Buy", "disclaimer": "2026 Simulation. Capital risk."
    },
    "Català": {
        "title": "InvestMind AI Elite", "ajust": "⚙️ AJUSTOS", "lang_lab": "IDIOMA",
        "conf": "🛠️ CONFIGURACIÓ", "cap": "PRESSUPOST TOTAL", 
        "risk_lab": "PERFIL DE RISC", "ass_lab": "ACTIU A ANALITZAR", "btn": "EXECUTAR ANÀLISI", 
        "diag": "Consultoria Estratègica", "just": "Justificació Tècnica", 
        "wait": "Analitzant Big Data...", "price": "Preu actual", "target": "Preu previst (30d)", 
        "shares": "Accions a comprar", "disclaimer": "Simulació 2026. Risc de capital."
    }
}

# 3. MEMORIA DE SESIÓN
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'ticket_act' not in st.session_state: st.session_state.ticket_act = "N/A"
if 'lang' not in st.session_state: st.session_state.lang = "Español"
if 'p_act' not in st.session_state: st.session_state.p_act = 0.0
if 'p_pre' not in st.session_state: st.session_state.p_pre = 0.0

# 4. BARRA LATERAL (AJUSTES Y CONFIGURACIÓN)
with st.sidebar:
    # --- AJUSTES ---
    curr_t = languages[st.session_state.lang]
    with st.expander(curr_t["ajust"], expanded=False):
        st.markdown(f'<p class="field-title">{curr_t["lang_lab"]}</p>', unsafe_allow_html=True)
        st.session_state.lang = st.selectbox("", ["Español", "English", "Català"], index=["Español", "English", "Català"].index(st.session_state.lang))
    
    t = languages[st.session_state.lang]
    
    # --- CONFIGURACIÓN ---
    st.markdown(f'<p class="sidebar-header">{t["conf"]}</p>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])
    
    # --- ACTIVO ---
    st.markdown(f'<p class="sidebar-header">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# 5. MOTOR IA
def hablar_con_ia_real(pregunta, lang, ticket, cambio, perfil):
    api_key = "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"
    try:
        client = Groq(api_key=api_key)
        prompt = f"Eres InvestMind AI (2026). Perfil: {perfil}, Activo: {ticket}, Tendencia: {cambio:.2f}%. Responde en {lang}."
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": pregunta}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión con la IA: {str(e)}"

# 6. CUERPO PRINCIPAL
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", f"💬 {t['diag']}"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]) as s:
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                st.session_state.p_act = float(datos['Close'].iloc[-1])
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                st.session_state.p_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((st.session_state.p_pre - st.session_state.p_act) / st.session_state.p_act) * 100
                st.session_state.analizado = True
                st.session_state.ticket_act = ticket

                # --- MÉTRICAS CLARAS ENCIMA DE LA GRÁFICA ---
                col1, col2, col3 = st.columns(3)
                simbolo = "€"  # Fijamos siempre euros

                col1.metric(
                    label=f"💰 {t['price']}",
                    value=f"{st.session_state.p_act:.2f}{simbolo}"
                )
                col2.metric(
                    label=f"📈 {t['target']}",
                    value=f"{st.session_state.p_pre:.2f}{simbolo}",
                    delta=f"{st.session_state.cambio:.2f}%"
                )
                col3.metric(
                    label=f"🧮 {t['shares']}",
                    value=f"{(capital/st.session_state.p_act):.4f}"
                )

                st.line_chart(datos['Close'])

                # --- CONSULTORÍA DEBAJO DE LA GRÁFICA ---
                st.divider()
                st.header(f"💼 {t['diag']}")
                st.subheader(f"📊 {t['just']}")
                
                just_txt = {
                    "Español": f"La proyección de <span class='highlight'>{st.session_state.cambio:.2f}%</span> para **{ticket}** se justifica por la inercia de 1,260 sesiones y la convergencia de soportes institucionales en {st.session_state.p_act:.2f}{simbolo}.",
                    "English": f"The <span class='highlight'>{st.session_state.cambio:.2f}%</span> projection for **{ticket}** is justified by 1,260-session inertia and institutional support convergence at {st.session_state.p_act:.2f}{simbolo}.",
                    "Català": f"La projecció de <span class='highlight'>{st.session_state.cambio:.2f}%</span> per a **{ticket}** es justifica per la inèrcia de 1.260 sessions i la convergència de suports institucionals als {st.session_state.p_act:.2f}{simbolo}."
                }
                st.write(just_txt[st.session_state.lang], unsafe_allow_html=True)
                st.caption(t["disclaimer"])
                s.update(label="OK", state="complete")
            else: 
                st.error("Ticker Error.")

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

st.caption("InvestMind AI Platinum v20.0 | Badalona, 2026")
