import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "TU_API_KEY_AQUI" 

# --- ESTILOS CSS (Incluye diseño de burbujas de chat) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }
.field-title { color: #64ffda; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 20px; margin-bottom: 8px; }
.stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #64ffda, #48cae4); color: #0a192f !important; font-weight: 800; border: none; }

/* Burbujas de Chat */
.chat-row { display: flex; margin-bottom: 15px; width: 100%; }
.row-user { justify-content: flex-end; }
.row-ai { justify-content: flex-start; }
.bubble { padding: 12px 18px; border-radius: 20px; max-width: 75%; font-size: 14px; line-height: 1.5; }
.user-bubble { background: #005c4b; color: white; border-bottom-right-radius: 2px; }
.ai-bubble { background: #202c33; color: #e9edef; border-bottom-left-radius: 2px; border: 1px solid #3b4a54; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS ---
languages = {
    "Español": { "title":"InvestIA Elite", "lang_lab":"AJUSTES", "cap":"PRESUPUESTO", "risk_lab":"RIESGO", "ass_lab":"TICKER", "btn":"ANALIZAR MERCADO", "wait":"Procesando...", "price":"Precio Actual", "target":"Predicción 30d", "shares":"Acciones posibles", "analysis":"Veredicto de Inversión", "chat_placeholder":"Pregunta a tu consultor..." },
    "English": { "title":"InvestIA Elite", "lang_lab":"SETTINGS", "cap":"BUDGET", "risk_lab":"RISK", "ass_lab":"TICKER", "btn":"ANALYZE MARKET", "wait":"Processing...", "price":"Current Price", "target":"30-Day Target", "shares":"Possible Shares", "analysis":"Investment Verdict", "chat_placeholder":"Ask your consultant..." },
    "Català": { "title":"InvestIA Elite", "lang_lab":"CONFIGURACIÓ", "cap":"PRESSUPOST", "risk_lab":"RISC", "ass_lab":"TICKER", "btn":"ANALITZAR MERCAT", "wait":"Processant...", "price":"Preu Actual", "target":"Predicció 30d", "shares":"Accions possibles", "analysis":"Veredicte d'Inversió", "chat_placeholder":"Pregunta al teu consultor..." }
}

# --- LÓGICA DE IA (Enfoque en Recomendación y Alternativas) ---
def generar_analisis_ia(pregunta, lang, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = ""
        if ticket:
            contexto = f"Activo: {ticket} | Precio: {p_act}€ | Predicción: {p_fut}€ ({cambio:.2f}%) | Perfil: {perfil} | Capital: {capital}€"

        system_prompt = f"""Eres un estratega de inversiones de élite. RESPONDE SIEMPRE EN {lang}.
        Tu misión es ser binario: ¿Es buena idea invertir en {ticket if ticket else 'activos'} para un perfil {perfil}?
        1. Da un veredicto claro (SÍ/NO/ESPERAR).
        2. Analiza el activo mencionado basándote en: {contexto}.
        3. OBLIGATORIO: Sugiere 3 alternativas de inversión (otros tickers, ETFs o sectores) que encajen específicamente con la personalidad {perfil} del usuario.
        Se crítico, profesional y añade disclaimer legal."""

        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": pregunta}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- ESTADO ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analizado" not in st.session_state: st.session_state.analizado = False

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
    t = languages[st.session_state.lang]
    capital = st.number_input(t["cap"], value=1000.0)
    perfil = st.selectbox(t["risk_lab"], ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(t["ass_lab"], value="NVDA").upper()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Smart Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="2y")
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df_p)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df_p['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket, "analizado": True})

                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{int(capital/p_act)}")

                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Velas"))
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Línea", line=dict(color='#64ffda', width=1)))
                fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450)
                st.plotly_chart(fig, use_container_width=True)

                with st.spinner("🧠 Generando veredicto..."):
                    inf = generar_analisis_ia(f"¿Invierto en {ticket}?", st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"### 📊 {t['analysis']}")
                st.write(inf)
            else: st.error("Ticker no válido.")

with tab2:
    for chat in st.session_state.chat_history:
        clase_fila = "row-user" if chat["role"] == "user" else "row-ai"
        clase_burbuja = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="chat-row {clase_fila}"><div class="bubble {clase_burbuja}">{chat["content"]}</div></div>', unsafe_allow_html=True)

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        res = generar_analisis_ia(prompt_user, st.session_state.lang, st.session_state.get("ticket_act"), st.session_state.get("p_act"), st.session_state.get("p_pre"), st.session_state.get("cambio"), perfil, capital)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()
