import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import time
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="InvestMind AI Elite", page_icon="💎", layout="wide")

# 2. ESTILO CSS (DISEÑO ELITE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    * { font-family: 'Inter', sans-serif; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .main .block-container { animation: fadeIn 0.8s ease-out; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0e1117 0%, #1a1c23 100%); border-right: 1px solid rgba(255,255,255,0.05); }
    .stNumberInput input, .stSelectbox div, .stTextInput input { background-color: rgba(59, 61, 74, 0.5) !important; color: #fff !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; }
    .stButton>button { width: 100%; border-radius: 14px; background: linear-gradient(90deg, #007bff, #00d4ff); color: white !important; font-weight: 800; border: none; padding: 15px; transition: all 0.4s ease; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,123,255,0.4); }
    .bubble { padding: 18px 22px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; font-size: 15px; color: white !important; }
    .user-bubble { background: linear-gradient(135deg, #007bff, #0056b3); margin-left: auto; border-bottom-right-radius: 4px; }
    .assistant-bubble { background: rgba(38, 39, 48, 0.8); border: 1px solid rgba(255,255,255,0.1); border-bottom-left-radius: 4px; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. DICCIONARIO MULTILINGÜE INTEGRAL
languages = {
    "Español": {
        "title": "InvestMind AI Elite", "config": "Configuración Elite", "btn": "EJECUTAR ANÁLISIS",
        "diag": "Consultoría Estratégica", "wait": "Analizando ciclos...", "risk_label": "Perfil",
        "dossier": "📂 Dossier Técnico", "strat": "Estrategia", "psy": "Psicología", "safety": "Seguridad",
        "msg_alc": "Acumulación", "msg_baj": "Protección", "msg_neu": "Neutral",
        "inf_1": "Nuestra IA proyecta un movimiento del", "inf_2": "en 30 días.",
        "stop_msg": "Stop-Loss sugerido en", "shares": "Acciones", "price": "Precio"
    },
    "English": {
        "title": "InvestMind AI Elite", "config": "Elite Settings", "btn": "EXECUTE ANALYSIS",
        "diag": "Strategic Consultancy", "wait": "Analyzing cycles...", "risk_label": "Profile",
        "dossier": "📂 Technical Dossier", "strat": "Strategy", "psy": "Psychology", "safety": "Safety",
        "msg_alc": "Accumulation", "msg_baj": "Protection", "msg_neu": "Neutral",
        "inf_1": "Our AI projects a movement of", "inf_2": "in 30 days.",
        "stop_msg": "Suggested Stop-Loss at", "shares": "Shares", "price": "Price"
    },
    "Català": {
        "title": "InvestMind AI Elite", "config": "Configuració Elit", "btn": "EXECUTAR ANÀLISI",
        "diag": "Consultoria Estratègica", "wait": "Analitzant cicles...", "risk_label": "Perfil",
        "dossier": "📂 Dossier Tècnic", "strat": "Estratègia", "psy": "Psicologia", "safety": "Seguretat",
        "msg_alc": "Acumulació", "msg_baj": "Protecció", "msg_neu": "Neutral",
        "inf_1": "La nostra IA projecta un moviment del", "inf_2": "en 30 dies.",
        "stop_msg": "Stop-Loss suggerit en", "shares": "Accions", "price": "Preu"
    }
}

# 4. MEMORIA
if 'messages' not in st.session_state: st.session_state.messages = []
if 'cambio' not in st.session_state: st.session_state.cambio = 0.0
if 'analizado' not in st.session_state: st.session_state.analizado = False
if 'precio_act' not in st.session_state: st.session_state.precio_act = 0.0

# 5. BARRA LATERAL
with st.sidebar:
    with st.expander("⚙️ System", expanded=False):
        lang_sel = st.selectbox("L", ["Español", "English", "Català"], label_visibility="collapsed")
    
    t = languages[lang_sel]
    st.markdown(f'<p style="color:#888; font-weight:800; font-size:12px; letter-spacing:2px; margin-bottom:20px;">{t["config"].upper()}</p>', unsafe_allow_html=True)
    
    moneda = st.radio("Currency", ["USD ($)", "EUR (€)"], horizontal=True, label_visibility="collapsed")
    simbolo = "$" if "USD" in moneda else "€"
    capital = st.number_input("Capital", min_value=1.0, value=1000.0)
    perfil = st.selectbox(t["risk_label"], ["Conservador", "Moderado", "Arriesgado"])
    
    st.markdown("---")
    modo_ticker = st.checkbox("Manual Ticker", value=False)
    ticket = st.text_input("Enter Ticker:").upper() if modo_ticker else st.selectbox("Select Asset", ["AAPL", "TSLA", "BTC-USD", "NVDA", "MSFT"])

# 6. MOTOR DE CHAT INTELIGENTE (NATIVO)
def generar_respuesta_inteligente(pregunta, lang, ticket, cambio, perfil):
    p = pregunta.lower()
    t_tend = "alcista 📈" if cambio > 2 else "bajista 📉" if cambio < -2 else "lateral ↔️"
    
    # Base de conocimiento multilingüe
    if lang == "Español":
        if any(x in p for x in ["hola", "buen", "hey"]): res = f"¡Hola! Soy tu asesor InvestMind. Analizando tu interés en {ticket} para tu perfil {perfil}. ¿Qué deseas saber?"
        elif any(x in p for x in ["invertir", "mejor", "donde", "comprar"]): res = f"Para invertir {capital}{simbolo} en {ticket}, mi análisis sugiere una tendencia {t_tend}. Como eres {perfil}, te recomiendo {'entrar con cautela' if cambio < 5 else 'aprovechar el impulso'}."
        elif any(x in p for x in ["riesgo", "perder", "seguro"]): res = f"El riesgo en {ticket} ahora mismo es {'moderado' if cambio > 0 else 'elevado'}. Para un perfil {perfil}, sugiero no exceder el 10% de tu capital total."
        else: res = f"Entiendo tu duda. Con una proyección del {cambio:.2f}% en {ticket}, el escenario para un inversor {perfil} es de {'crecimiento' if cambio > 0 else 'ajuste'}. ¿Quieres ver el Stop-Loss?"
    elif lang == "English":
        if any(x in p for x in ["hello", "hi", "hey"]): res = f"Hello! I am your InvestMind advisor. Checking {ticket} for your {perfil} profile. How can I help?"
        elif any(x in p for x in ["invest", "best", "where", "buy"]): res = f"To invest {capital}{simbolo} in {ticket}, the current trend is {t_tend}. Since you are {perfil}, I recommend {'caution' if cambio < 5 else 'buying the momentum'}."
        else: res = f"I understand. With a {cambio:.2f}% projection for {ticket}, the scenario for a {perfil} investor is {'bullish' if cambio > 0 else 'bearish'}. Need safety tips?"
    else: # Català
        if any(x in p for x in ["hola", "bon", "ei"]): res = f"Hola! Sóc el teu assessor InvestMind. Analitzant {ticket} pel teu perfil {perfil}. Què vols saber?"
        elif any(x in p for x in ["invertir", "millor", "on", "comprar"]): res = f"Per invertir {capital}{simbolo} a {ticket}, la tendència és {t_tend}. Com que ets {perfil}, et recomano {'prudència' if cambio < 5 else 'aprofitar l\'impuls'}."
        else: res = f"Entenc el dubte. Amb una projecció del {cambio:.2f}% a {ticket}, l'escenari per a un inversor {perfil} és de {'creixement' if cambio > 0 else 'correcció'}. Vols veure el Stop-Loss?"
    return res

# 7. CUERPO PRINCIPAL
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs(["📉 Terminal", "💬 Chat Pro"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]) as s:
            datos = yf.download(ticket, period="5y")
            if not datos.empty:
                st.session_state.precio_act = float(datos['Close'].iloc[-1])
                df_p = datos.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                p_pre = float(m.predict(m.make_future_dataframe(periods=30))['yhat'].iloc[-1])
                st.session_state.cambio = ((p_pre - st.session_state.precio_act) / st.session_state.precio_act) * 100
                st.session_state.analizado = True
                s.update(label="OK", state="complete")

                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{st.session_state.precio_act:.2f}{simbolo}")
                c2.metric("Target 30d", f"{p_pre:.2f}{simbolo}", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/st.session_state.precio_act):.4f}")
                st.line_chart(datos['Close'])

                # CONSULTORÍA ESTRATÉGICA DINÁMICA
                st.divider()
                st.header(f"💼 {t['diag']}")
                msg_tend = t["msg_alc"] if st.session_state.cambio > 2 else t["msg_baj"] if st.session_state.cambio < -2 else t["msg_neu"]
                
                st.markdown(f"""
                ### {t['dossier']}: {ticket} | {t['risk_label']} {perfil}
                {t['inf_1']} **{st.session_state.cambio:.2f}%** {t['inf_2']}
                
                *   **{t['strat']}:** {msg_tend}. Sugerimos una entrada técnica en **{st.session_state.precio_act:.2f}{simbolo}**.
                *   **{t['psy']}:** Mantén disciplina. Un inversor {perfil} no debe actuar por pánico.
                *   **{t['safety']}:** {t['stop_msg']} **{st.session_state.precio_act * 0.95:.2f}{simbolo}**.
                """)
            else: st.error("No Data.")

with tab2:
    st.subheader("💬 Cognitive Advisory")
    for msg in st.session_state.messages:
        clase = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f'<div class="bubble {clase}">{msg["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("..."):
            time.sleep(0.4)
            respuesta = generar_respuesta_inteligente(p, lang_sel, ticket, st.session_state.cambio, perfil)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.rerun()

st.caption("InvestMind AI Elite v6.5 | 2026 Edition")
