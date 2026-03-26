import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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"

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }
    .field-title { color: #64ffda; font-size: 11px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 8px; margin-top: 15px; }
    .stButton>button { border: none; border-radius: 8px; background-color: #1a1a1a; color: #ffffff !important; font-weight: 600; height: 45px; }
    .metric-card { background: #ffffff; border: 1px solid #e9ecef; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .metric-label { font-size: 11px; color: #adb5bd; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 22px; font-weight: 700; color: #1a1a1a; margin-top: 5px; }
    .chat-row { display: flex; margin-bottom: 25px; justify-content: flex-start; }
    .bubble { padding: 20px; border-radius: 12px; max-width: 85%; font-size: 15px; line-height: 1.6; background: #ffffff; border: 1px solid #e9ecef; }
    .user-bubble { border-left: 4px solid #adb5bd; }
    .ai-bubble { border-left: 4px solid #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { "title":"INVESTIA ELITE", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", "btn":"EJECUTAR ANÁLISIS", "wait":"Procesando...", "price":"Precio Actual", "target":"Objetivo 30d", "shares":"Capacidad Compra", "analysis":"Estrategia Institucional", "hist_t":"Tendencia Histórica", "pred_t":"Proyección IA (30 días)" },
    "English": { "title":"INVESTIA ELITE", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", "btn":"EXECUTE ANALYSIS", "wait":"Processing...", "price":"Current Price", "target":"30-Day Target", "shares":"Buying Capacity", "analysis":"Institutional Strategy", "hist_t":"Historical Trend", "pred_t":"AI Projection (30 Days)" }
}

# --- FUNCIÓN IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%)."
        prompt = f"Asesor Financiero Senior. RESPONDE EN IDIOMA: {lang}. Perfil: {perfil}. Capital: {capital}€. {contexto} Pregunta: {pregunta if pregunta else 'Informe institucional completo.'}"
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except Exception as e: return f"Error IA: {e}"

# --- GESTIÓN DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "ultimo_informe" not in st.session_state: st.session_state.ultimo_informe = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        # Seguridad: Solo regenerar si ya se analizó un ticker previamente
        if st.session_state.analizado and "ticket_act" in st.session_state:
            st.session_state.ultimo_informe = generar_analisis_ia(st.session_state.lang, st.session_state.ticket_act, st.session_state.p_act, st.session_state.p_pre, st.session_state.cambio, st.session_state.perfil_act, st.session_state.cap_act)
        st.rerun()

    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    cap_in = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perf_in = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    tick_in = st.text_input("", value="AAPL", label_visibility="collapsed").upper()

# --- INTERFAZ ---
st.markdown(f"<h1 style='text-align: center; font-weight: 800; color: #1a1a1a; margin-top: 20px;'>{t['title']}</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([f"📊 {t['btn']}", "💬 AI ADVISOR"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            # SOLUCIÓN: yfinance v0.2.50+ requiere limpieza de MultiIndex
            raw_data = yf.download(tick_in, period="2y", interval="1d")
            if not raw_data.empty:
                if isinstance(raw_data.columns, pd.MultiIndex):
                    raw_data.columns = raw_data.columns.get_level_values(0)
                
                df_p = raw_data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                
                model = Prophet(daily_seasonality=True).fit(df_p)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                
                p_act, p_fut = float(df_p['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                
                st.session_state.update({
                    "p_act": p_act, "p_pre": p_fut, "cambio": cambio, 
                    "ticket_act": tick_in, "perfil_act": perf_in, "cap_act": cap_in,
                    "analizado": True, "data_plot": raw_data, "forecast_plot": forecast, "df_p": df_p
                })
                st.session_state.ultimo_informe = generar_analisis_ia(st.session_state.lang, tick_in, p_act, p_fut, cambio, perf_in, cap_in)
            else: st.error("Asset not found.")

    if st.session_state.analizado:
        # Métricas
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['price']}</div><div class='metric-value'>{st.session_state.p_act:.2f}€</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['target']}</div><div class='metric-value'>{st.session_state.p_pre:.2f}€ ({st.session_state.cambio:+.2f}%)</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><div class='metric-label'>{t['shares']}</div><div class='metric-value'>{st.session_state.cap_act/st.session_state.p_act:.2f}</div></div>", unsafe_allow_html=True)

        # Gráfica 1: Velas
        st.markdown(f"#### {t['hist_t']}")
        fig1 = go.Figure(data=[go.Candlestick(x=st.session_state.data_plot.index, open=st.session_state.data_plot['Open'], high=st.session_state.data_plot['High'], low=st.session_state.data_plot['Low'], close=st.session_state.data_plot['Close'], name=st.session_state.ticket_act)])
        fig1.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfica 2: Líneas (Proyección)
        st.markdown(f"#### {t['pred_t']}")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=st.session_state.df_p['ds'], y=st.session_state.df_p['y'], name="Real", line=dict(color='#000000', width=1.5)))
        fig2.add_trace(go.Scatter(x=st.session_state.forecast_plot['ds'].iloc[-30:], y=st.session_state.forecast_plot['yhat'].iloc[-30:], name="Predicción", line=dict(color='#adb5bd', width=2, dash='dot')))
        fig2.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        # Análisis IA
        st.markdown(f"<div style='background:#f8f9fa; padding:30px; border-radius:12px; border:1px solid #e9ecef;'><h3>📊 {t['analysis']}</h3><div style='line-height:1.6;'>{st.session_state.ultimo_informe}</div></div>", unsafe_allow_html=True)

with tab2:
    for chat in st.session_state.chat_history:
        b_class = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="chat-row"><div class="bubble {b_class}"><span style="font-size:10px; font-weight:800; display:block; margin-bottom:10px;">{"INVERSOR" if chat["role"]=="user" else "IA STRATEGIST"}</span>{chat["content"]}</div></div>', unsafe_allow_html=True)

    if pr_u := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": pr_u})
        # Verificamos si existe el ticket analizado antes de enviar el contexto al chat
        tk = st.session_state.get("ticket_act")
        pa = st.session_state.get("p_act")
        pf = st.session_state.get("p_pre")
        ca = st.session_state.get("cambio")
        res = generar_analisis_ia(st.session_state.lang, tk, pa, pf, ca, perf_in, cap_in, pr_u)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()

