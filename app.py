import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="📈", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS PROFESIONALES (MODERNO/DARK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');

    :root {
        --bg-dark: #05070A;
        --card-bg: #0F121A;
        --accent: #00F2FF;
        --text-main: #E2E8F0;
        --border: rgba(255, 255, 255, 0.08);
    }

    .stApp { background-color: var(--bg-dark); color: var(--text-main); }
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    code, .mono { font-family: 'JetBrains Mono', monospace; }

    /* Sidebar futurista */
    [data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border);
    }

    /* Inputs estilizados */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1A1E26 !important;
        border: 1px solid var(--border) !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Botón con Glow */
    .stButton>button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        border: none;
        color: #05070A !important;
        font-weight: 800;
        letter-spacing: 1px;
        border-radius: 8px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
    }

    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background: transparent; border: none;
        color: #64748B; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Contenedores de métricas */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        padding: 24px;
        border-radius: 16px;
        text-align: left;
        transition: 0.3s;
    }
    .metric-card:hover { border-color: var(--accent); background: #161B25; }

    /* Chat UI Rediseñada */
    .chat-bubble {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent);
        background: rgba(255, 255, 255, 0.03);
    }
    
    .ai-bubble { border-left-color: #00F2FF; background: rgba(0, 242, 255, 0.02); }
    .user-bubble { border-left-color: #94A3B8; background: rgba(148, 163, 184, 0.05); }

    /* Badge de recomendación */
    .rec-box {
        background: linear-gradient(145deg, #0F121A 0%, #1A1E26 100%);
        border: 1px solid var(--border);
        padding: 30px;
        border-radius: 20px;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"IDIOMA", "cap":"CAPITAL DISPONIBLE", "risk_lab":"PERFIL DE RIESGO", "ass_lab":"TICKER ACTIVO", 
        "btn":"EJECUTAR ANÁLISIS", "wait":"Procesando datos de mercado...", "price":"PRECIO ACTUAL", "target":"PROYECCIÓN 30D", 
        "shares":"CAPACIDAD ADQUISICIÓN", "analysis":"INFORME ESTRATÉGICO", "hist_t":"HISTÓRICO DE MERCADO", 
        "pred_t":"MODELADO PREDICTIVO PROPHET", "chat_placeholder":"Consultar con analista IA...",
        "news_tab": "NOTICIAS", "news_sub": "FLUJO DE NOTICIAS EN TIEMPO REAL"
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"LANGUAGE", "cap":"AVAILABLE CAPITAL", "risk_lab":"RISK PROFILE", "ass_lab":"ASSET TICKER", 
        "btn":"EXECUTE ANALYSIS", "wait":"Processing market data...", "price":"CURRENT PRICE", "target":"30D TARGET", 
        "shares":"BUYING POWER", "analysis":"STRATEGIC REPORT", "hist_t":"MARKET HISTORY", 
        "pred_t":"PROPHET PREDICTIVE MODELING", "chat_placeholder":"Ask IA analyst...",
        "news_tab": "NEWS", "news_sub": "REAL-TIME NEWS FEED"
    }
}

# --- LÓGICA IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"Act as a Senior Investment Strategist. Give a CUSTOMIZED RECOMMENDATION in {idioma_inst}. Data: {contexto}. Risk Profile: {perfil}. Capital: {capital}€. Question: {pregunta if pregunta else 'General recommendation.'}"
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- ESTADO DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ELEGante ---
with st.sidebar:
    st.markdown(f"<h2 style='color: #00F2FF;'>Elite v2.0</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown(f"**{languages[st.session_state.lang]['lang_lab']}**")
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    
    t = languages[st.session_state.lang]
    
    st.markdown(f"**{t['cap']}**")
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f"**{t['risk_lab']}**")
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown(f"**{t['ass_lab']}**")
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    st.caption("InvestIA Elite Terminal © 2024")

# --- UI PRINCIPAL ---
st.markdown(f"<h1 style='text-align: left; color: white; font-weight: 800; font-size: 2.5rem; letter-spacing: -2px;'>{t['title']}<span style='color: #00F2FF;'>.</span></h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([f"📈 {t['btn']}", f"💬 ANALISTA IA", f"📰 {t['news_tab']}"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                # Limpieza de datos
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
                p_act = data['Close'].iloc[-1]
                
                # Predicción Prophet
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(changepoint_prior_scale=0.05).fit(df_p)
                future = m.make_future_dataframe(periods=30)
                forecast = m.predict(future)
                p_fut = forecast['yhat'].iloc[-1]
                cambio = ((p_fut - p_act) / p_act) * 100
                
                # Layout de métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div class='metric-card'><p style='color: #64748B; font-size: 0.8rem; margin:0;'>{t['price']}</p><h2 style='color: white; margin:0;'>{p_act:,.2f}€</h2></div>", unsafe_allow_html=True)
                with col2:
                    color = "#00FF88" if cambio > 0 else "#FF4B4B"
                    st.markdown(f"<div class='metric-card'><p style='color: #64748B; font-size: 0.8rem; margin:0;'>{t['target']}</p><h2 style='color: {color}; margin:0;'>{p_fut:,.2f}€ ({cambio:+.2f}%)</h2></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='metric-card'><p style='color: #64748B; font-size: 0.8rem; margin:0;'>{t['shares']}</p><h2 style='color: #00F2FF; margin:0;'>{int(capital/p_act)} uds.</h2></div>", unsafe_allow_html=True)

                # Gráfico Plotly
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Real", line=dict(color='#00F2FF', width=2)))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="IA Forecast", line=dict(color='#92FE9D', width=2, dash='dot')))
                fig.update_layout(
                    template="plotly_dark", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

                # Recomendación IA
                st.markdown(f"### 🤖 {t['analysis']}")
                analisis = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"<div class='rec-box'>{analisis}</div>", unsafe_allow_html=True)
                
                # Guardar en sesión para el chat
                st.session_state.p_act = p_act
                st.session_state.p_fut = p_fut
                st.session_state.cambio = cambio
                st.session_state.ticket = ticket
                st.session_state.analizado = True

with tab2:
    if st.session_state.analizado:
        st.markdown(f"#### 💬 Consulting: {st.session_state.ticket}")
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.chat_history:
                role_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
                st.markdown(f"<div class='chat-bubble {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

        if prompt_chat := st.chat_input(t["chat_placeholder"]):
            st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
            res = generar_analisis_ia(st.session_state.lang, st.session_state.ticket, st.session_state.p_act, st.session_state.p_fut, st.session_state.cambio, perfil, capital, pregunta=prompt_chat)
            st.session_state.chat_history.append({"role": "assistant", "content": res})
            st.rerun()
    else:
        st.info("⚠️ Ejecuta un análisis en la primera pestaña para activar el chat.")

with tab3:
    st.markdown(f"### {t['news_sub']}")
    feed = feedparser.parse(f"https://news.google.com{ticket}+stock+finance&hl=en-US&gl=US&ceid=US:en")
    for entry in feed.entries[:5]:
        st.markdown(f"""
        <div style='background: #161B25; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 2px solid #00F2FF;'>
            <a href='{entry.link}' target='_blank' style='color: #00F2FF; text-decoration: none; font-weight: 600;'>{entry.title}</a><br>
            <small style='color: #64748B;'>{entry.published}</small>
        </div>
        """, unsafe_allow_html=True)


