import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }
.field-title { color: #64ffda; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 20px; margin-bottom: 8px; }
.stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #64ffda, #48cae4); color: #0a192f !important; font-weight: 800; border: none; }
.chat-row { display: flex; margin-bottom: 15px; width: 100%; }
.row-user { justify-content: flex-end; }
.row-ai { justify-content: flex-start; }
.bubble { padding: 12px 18px; border-radius: 18px; max-width: 75%; font-size: 14px; line-height: 1.5; }
.user-bubble { background: #005c4b; color: white; border-bottom-right-radius: 2px; }
.ai-bubble { background: #202c33; color: #e9edef; border-bottom-left-radius: 2px; border: 1px solid #3b4a54; }
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE TRADUCCIÓN ---
languages = {
    "Español": { "title":"InvestIA Elite", "lang_lab":"AJUSTES", "cap":"PRESUPUESTO", "risk_lab":"RIESGO", "ass_lab":"TICKER", "btn":"ANALIZAR MERCADO", "wait":"Procesando...", "price":"Precio Actual", "target":"Predicción 30d", "shares":"Acciones posibles", "analysis":"Veredicto de Inversión", "news_title":"Resumen de Noticias", "chat_p":"Pregunta a tu consultor...", "hist_t":"Evolución Histórica", "pred_t":"Proyección IA" },
    "English": { "title":"InvestIA Elite", "lang_lab":"SETTINGS", "cap":"BUDGET", "risk_lab":"RISK", "ass_lab":"TICKER", "btn":"ANALYZE MARKET", "wait":"Processing...", "price":"Current Price", "target":"30-Day Target", "shares":"Possible Shares", "analysis":"Investment Verdict", "news_title":"News Summary", "chat_p":"Ask your consultant...", "hist_t":"Historical Trend", "pred_t":"AI Projection" },
    "Català": { "title":"InvestIA Elite", "lang_lab":"CONFIGURACIÓ", "cap":"PRESSUPOST", "risk_lab":"RISC", "ass_lab":"TICKER", "btn":"ANALITZAR MERCAT", "wait":"Processant...", "price":"Preu Actual", "target":"Predicció 30d", "shares":"Accions possibles", "analysis":"Veredicte d'Inversió", "news_title":"Resum de Notícies", "chat_p":"Pregunta al teu consultant...", "hist_t":"Evolució Històrica", "pred_t":"Projecció IA" }
}

# --- ESTADO INICIAL ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR (Cambio de idioma instantáneo) ---
with st.sidebar:
    # El cambio aquí es inmediato gracias al on_change implícito de selectbox y el rerun
    lang_choice = st.selectbox("IDIOMA / LANGUAGE", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    
    capital = st.number_input(t["cap"], value=1000.0)
    perfil = st.selectbox(t["risk_lab"], ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(t["ass_lab"], value="NVDA").upper()

# --- LÓGICA DE IA ---
def generar_respuesta_ia(prompt, lang, context_type="analisis", data=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        sys_msg = f"Experto financiero. RESPONDE EN {lang}. "
        if context_type == "noticias": sys_msg += "Resume noticias estratégicamente."
        else: sys_msg += f"Veredicto (SÍ/NO) y 3 alternativas para perfil {data.get('perfil', 'Moderado')}."
        
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return resp.choices[0].message.content
    except Exception as e: return f"Error IA: {e}"

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Smart Advisor"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            # DESCARGA CON FORZADO DE COLUMNAS PLANAS
            data = yf.download(ticket, period="2y", multi_level_index=False)
            
            if not data.empty:
                # Limpieza de seguridad para MultiIndex residual
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                # Preparar para Prophet
                df_p = data.reset_index()[['Date', 'Close']]
                df_p.columns = ['ds', 'y']
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                
                model = Prophet(daily_seasonality=True).fit(df_p)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                
                p_act = float(df_p['y'].iloc[-1])
                p_fut = float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket, "analizado": True})

                # Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€"); c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%"); c3.metric(t["shares"], f"{int(capital/p_act)}")

                # GRÁFICA 1: HISTÓRICO (Velas + Línea)
                st.markdown(f"#### {t['hist_t']}")
                fig1 = go.Figure([go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Velas"),
                                 go.Scatter(x=data.index, y=data['Close'], line=dict(color='#64ffda', width=1.5), name="Línea")])
                fig1.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400); st.plotly_chart(fig1, use_container_width=True)

                # GRÁFICA 2: PREDICCIÓN (Independiente)
                st.markdown(f"#### {t['pred_t']}")
                fig2 = go.Figure([go.Scatter(x=df_p['ds'], y=df_p['y'], name="Real", line=dict(color='#48cae4')), 
                                 go.Scatter(x=forecast['ds'].iloc[-30:], y=forecast['yhat'].iloc[-30:], line=dict(color='#64ffda', dash='dash'), name="IA Forecast")])
                fig2.update_layout(template="plotly_dark", height=300); st.plotly_chart(fig2, use_container_width=True)

                # Veredicto y Noticias
                col_a, col_n = st.columns(2)
                with col_a:
                    st.markdown(f"### 📊 {t['analysis']}")
                    st.write(generar_respuesta_ia(f"¿Invierto en {ticket}?", st.session_state.lang, data={'perfil':perfil}))
                with col_n:
                    st.markdown(f"### 📰 {t['news_title']}")
                    ticker_obj = yf.Ticker(ticket)
                    news_text = "\n".join([f"- {n['title']}" for n in ticker_obj.news[:5]])
                    st.write(generar_respuesta_ia(news_text, st.session_state.lang, context_type="noticias", data={'ticker':ticket}))
            else: st.error("Ticker no válido o sin datos.")

with tab2:
    for chat in st.session_state.chat_history:
        clase, burbuja = ("row-user", "user-bubble") if chat["role"] == "user" else ("row-ai", "ai-bubble")
        st.markdown(f'<div class="chat-row {clase}"><div class="bubble {burbuja}">{chat["content"]}</div></div>', unsafe_allow_html=True)

    if prompt_u := st.chat_input(t["chat_p"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_u})
        res = generar_respuesta_ia(prompt_u, st.session_state.lang, data={'perfil':perfil, 'ticker':st.session_state.get("ticket_act")})
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()
