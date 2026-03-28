import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS ELITE (CAPVALUEZ UI) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');

/* --- GLOBAL CORE --- */
.stApp {
    background-color: #0A0D10 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
}

/* --- SIDEBAR CAPVALUEZ --- */
[data-testid="stSidebar"] {
    background-color: #0D1117 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.field-title {
    color: #00C853;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 24px;
    opacity: 0.85;
}

/* --- INPUTS PREMIUM --- */
.stTextInput input, .stNumberInput input, .stSelectbox > div {
    background-color: #15191E !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    padding: 12px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 1px #00C853 !important;
}

/* --- BOTONES ELITE --- */
.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #00C853 0%, #009688 100%) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 16px 24px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 200, 83, 0.3) !important;
}

/* --- TABS & NAVIGATION --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background-color: transparent;
    padding: 10px 0;
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    background-color: #15191E !important;
    border-radius: 8px !important;
    color: #64748B !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    padding: 0 25px !important;
    transition: 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #1C2229 !important;
    color: #00C853 !important;
    border: 1px solid rgba(0, 200, 83, 0.3) !important;
}

/* --- CONTAINERS & CARDS --- */
.metric-container, .news-card, .recommendation-box {
    background: #15191E !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 14px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    backdrop-filter: blur(10px);
}

.metric-label { color: #94A3B8; font-size: 0.9rem; }
.metric-value { color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }

/* --- CHAT BUBBLES --- */
.bubble {
    padding: 18px 22px;
    border-radius: 12px;
    margin-bottom: 15px;
    font-size: 0.95rem;
    line-height: 1.6;
}

.user-bubble {
    background: #1C2229;
    border: 1px solid rgba(255,255,255,0.08);
    color: #F8FAFC;
    margin-left: 20%;
}

.ai-bubble {
    background: rgba(0, 200, 83, 0.03);
    border-left: 3px solid #00C853;
    color: #FFFFFF;
    margin-right: 20%;
}

/* --- OVERRIDES --- */
h1, h2, h3 { color: #FFFFFF !important; font-weight: 700 !important; }
.stMarkdown p { color: #E2E8F0; }
hr { border-color: rgba(255,255,255,0.05); }

</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA ELITE TERMINAL",
        "lang_lab": "Idioma / Select Language",
        "cap": "Presupuesto de Inversión",
        "risk_lab": "Perfil de Riesgo",
        "ass_lab": "Ticker de Activo (Yahoo Fin)",
        "btn": "EJECUTAR ANÁLISIS ESTRATÉGICO",
        "wait": "Sincronizando con mercados financieros...",
        "price": "Precio Actual",
        "target": "Objetivo 30 Días",
        "shares": "Capacidad de Adquisición",
        "analysis": "Recomendación de Inteligencia Superior",
        "hist_t": "Tendencia Histórica de Mercado",
        "pred_t": "Proyección Algorítmica Prophet",
        "chat_placeholder": "Consulte sobre este activo o estrategia...",
        "news_tab": "Mercados Globales",
        "news_sub": "Últimas Noticias Financieras",
        "chat_tab": "Asistente AI Pro",
        "read_more": "Ver artículo completo →",
        "summarize": "🧠 Resumen Ejecutivo IA"
    },
    "English": {
        "title": "INVESTIA ELITE TERMINAL",
        "lang_lab": "Language Selection",
        "cap": "Investment Budget",
        "risk_lab": "Risk Profile",
        "ass_lab": "Asset Ticker (Yahoo Fin)",
        "btn": "EXECUTE STRATEGIC ANALYSIS",
        "wait": "Synchronizing with financial markets...",
        "price": "Current Price",
        "target": "30-Day Target",
        "shares": "Buying Capacity",
        "analysis": "Superior Intelligence Recommendation",
        "hist_t": "Historical Market Trend",
        "pred_t": "Prophet Algorithmic Projection",
        "chat_placeholder": "Ask about this asset or strategy...",
        "news_tab": "Global Markets",
        "news_sub": "Latest Financial News",
        "chat_tab": "Pro AI Assistant",
        "read_more": "Read full article →",
        "summarize": "🧠 AI Executive Summary"
    }
}

# --- IA MEJORADA (RECOMENDACIÓN) ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        contexto = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€ ({cambio:.2f}%)."
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        
        prompt = f"""
        Act as a Senior Investment Strategist. Your goal is to give a CUSTOMIZED RECOMMENDATION in {idioma_inst}.
        Data: {contexto}. Risk Profile: {perfil}. Capital: {capital}€.
        
        Structure:
        1. Action: (Buy, Hold or Sell) based on the profile.
        2. Rational: Why this makes sense.
        3. Future Outlook: What to expect if the user follows this advice.
        
        Question: {pregunta if pregunta else "General recommendation."}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"
        
def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pr):
    return generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=pr)
    
# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_ticket" not in st.session_state: st.session_state.last_ticket = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()

# --- UI PRINCIPAL ---
st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h1 style='font-size: 2.8rem; letter-spacing: -2px; margin-bottom: 0;'>{t['title']}<span style='color: #00C853;'>.</span></h1>
        <p style='color: #64748B; font-size: 1.1rem;'>Professional Grade Financial Analysis Terminal</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    f"📊 {t['btn']}", 
    f"💬 {t['chat_tab']}", 
    f"📰 {t['news_tab']}"
])

# --- ANÁLISIS ---
with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                # Datos actuales
                p_act = data['Close'].iloc[-1]
                
                # Prophet Prediction
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                model = Prophet(changepoint_prior_scale=0.05, daily_seasonality=True)
                model.fit(df_p)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)
                p_fut = forecast['yhat'].iloc[-1]
                cambio = ((p_fut - p_act) / p_act) * 100
                
                st.session_state.analizado = True
                st.session_state.res = {
                    "p_act": p_act, "p_fut": p_fut, "cambio": cambio, "ticket": ticket
                }

                # Layout de Métricas
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""<div class='metric-container'><p class='metric-label'>{t['price']}</p><p class='metric-value'>{p_act:,.2f}€</p></div>""", unsafe_allow_html=True)
                with c2:
                    color_c = "#00C853" if cambio > 0 else "#FF5252"
                    st.markdown(f"""<div class='metric-container'><p class='metric-label'>{t['target']}</p><p class='metric-value' style='color: {color_c}'>{p_fut:,.2f}€ ({cambio:+.2f}%)</p></div>""", unsafe_allow_html=True)
                with c3:
                    shares = capital / p_act
                    st.markdown(f"""<div class='metric-container'><p class='metric-label'>{t['shares']}</p><p class='metric-value'>{shares:,.2f} Uds.</p></div>""", unsafe_allow_html=True)

                # Recomendación IA
                st.markdown(f"### 🛡️ {t['analysis']}")
                with st.container():
                    rec = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                    st.markdown(f"<div class='recommendation-box'>{rec}</div>", unsafe_allow_html=True)

                # Gráficos
                st.markdown(f"### 📈 {t['hist_t']}")
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Market"))
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Ticker no encontrado.")

# --- CHAT ---
with tab2:
    if st.session_state.analizado:
        st.markdown(f"### 💬 Terminal de Consulta: {st.session_state.res['ticket']}")
        for m in st.session_state.chat_history:
            role_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
            st.markdown(f"<div class='bubble {role_class}'>{m['content']}</div>", unsafe_allow_html=True)
        
        pr = st.chat_input(t["chat_placeholder"])
        if pr:
            st.session_state.chat_history.append({"role": "user", "content": pr})
            res_chat = generar_chat_ia(st.session_state.lang, st.session_state.res['ticket'], st.session_state.res['p_act'], st.session_state.res['p_fut'], st.session_state.res['cambio'], perfil, capital, pr)
            st.session_state.chat_history.append({"role": "assistant", "content": res_chat})
            st.rerun()
    else:
        st.info("Por favor, analiza un activo en la primera pestaña para activar el asistente.")

# --- NOTICIAS ---
with tab3:
    st.markdown(f"### 🌍 {t['news_sub']}")
    rss_url = "https://finance.yahoo.com"
    feed = feedparser.parse(rss_url)
    for entry in feed.entries[:8]:
        with st.container():
            st.markdown(f"""
                <div class='news-card'>
                    <h4 style='margin-top:0; color: #00C853;'>{entry.title}</h4>
                    <p style='font-size: 0.85rem; color: #94A3B8;'>{entry.published}</p>
                    <p>{entry.summary[:200]}...</p>
                    <a href='{entry.link}' target='_blank' style='color: #00C853; text-decoration: none; font-weight: 600;'>{t['read_more']}</a>
                </div>
            """, unsafe_allow_html=True)
