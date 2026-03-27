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

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    * { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] { background-color: #0A192F !important; border-right: 1px solid #E2E8F0; }
    .sb-title { color: #94A3B8; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin: 20px 0 8px 0; }

    .stButton>button {
        border: none; border-radius: 12px;
        background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
        color: white !important; font-weight: 600; height: 50px; width: 100%;
        transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(10, 25, 47, 0.2);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(10, 25, 47, 0.3); }

    .metric-card { background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; text-align: center; }

    /* --- ESTÉTICA DE CHAT MEJORADA --- */
    .chat-bubble {
        padding: 16px 20px;
        border-radius: 18px;
        margin-bottom: 15px;
        max-width: 80%;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        position: relative;
    }
    .ai-bubble { 
        background: #FFFFFF; 
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0A192F; 
        color: #1E293B; 
        margin-right: auto;
    }
    .user-bubble { 
        background: #0A192F; 
        color: #FFFFFF; 
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }
    .chat-label { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; display: block; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {
        "title": "INVESTIA ELITE TERMINAL",
        "sidebar_lang": "Idioma", "sidebar_cap": "Presupuesto", "sidebar_risk": "Riesgo", "sidebar_ticker": "Ticker",
        "btn_analyze": "ANALIZAR ACTIVO", "tab_analysis": "Análisis", "tab_chat": "Chat IA", "tab_news": "Noticias",
        "m_price": "Precio Actual", "m_target": "Predicción 30d", "m_shares": "Capacidad Compra",
        "chat_placeholder": "Escribe tu consulta financiera...", "read_more": "Leer más",
        "risk_options": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "INVESTIA ELITE TERMINAL",
        "sidebar_lang": "Language", "sidebar_cap": "Budget", "sidebar_risk": "Risk Profile", "sidebar_ticker": "Ticker",
        "btn_analyze": "ANALYZE ASSET", "tab_analysis": "Analysis", "tab_chat": "AI Chat", "tab_news": "News",
        "m_price": "Current Price", "m_target": "30d Prediction", "m_shares": "Buying Capacity",
        "chat_placeholder": "Type your financial query...", "read_more": "Read more",
        "risk_options": ["Conservative", "Moderate", "Aggressive"]
    }
}

def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"Act as Senior Strategist. Ticker: {ticket}. Price: {p_act}. Pred: {p_fut}. Risk: {perfil}. Lang: {lang}. Q: {pregunta if pregunta else 'General analysis.'}"
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except: return "Error IA"

if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_data" not in st.session_state: st.session_state.last_data = None

t = languages[st.session_state.lang]

with st.sidebar:
    st.markdown(f'<p class="sb-title">{t["sidebar_lang"]}</p>', unsafe_allow_html=True)
    lang_sel = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_sel != st.session_state.lang: st.session_state.lang = lang_sel; st.rerun()
    st.markdown(f'<p class="sb-title">{t["sidebar_cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    st.markdown(f'<p class="sb-title">{t["sidebar_risk"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", t["risk_options"], label_visibility="collapsed")
    st.markdown(f'<p class="sb-title">{t["sidebar_ticker"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()
    btn_exec = st.button(t["btn_analyze"])

st.markdown(f"<h1 style='text-align:center; color:#0A192F; font-weight:800;'>{t['title']}</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs([f"📊 {t['tab_analysis']}", f"🤖 {t['tab_chat']}", f"📰 {t['tab_news']}"])

with tab1:
    if btn_exec:
        df = yf.download(ticket, period="2y", interval="1d")
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
            df_p['ds'] = df_p['ds'].dt.tz_localize(None)
            m = Prophet(daily_seasonality=True).fit(df_p)
            future = m.make_future_dataframe(periods=30)
            forecast = m.predict(future)
            p_act, p_fut = df['Close'].iloc[-1], forecast['yhat'].iloc[-1]
            cambio = ((p_fut - p_act) / p_act) * 100
            st.session_state.last_data = {"ticket": ticket, "p_act": p_act, "p_fut": p_fut, "cambio": cambio}

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><small>{t["m_price"]}</small><h2>{p_act:,.2f}€</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><small>{t["m_target"]}</small><h2 style="color:{"#10B981" if cambio > 0 else "#EF4444"}">{p_fut:,.2f}€</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><small>{t["m_shares"]}</small><h2>{int(capital // p_act)}</h2></div>', unsafe_allow_html=True)

            # --- GRÁFICO DE VELAS + PREDICCIÓN ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market Data"))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Prophet Prediction", line=dict(color='#007BFF', width=2)))
            fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"### 🛡️ Recomendación Estratégica")
            st.info(generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital))

with tab2:
    if st.session_state.last_data:
        for msg in st.session_state.chat_history:
            bubble_type = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            label = "USER" if msg["role"] == "user" else "INVESTIA AI"
            st.markdown(f'<div class="chat-bubble {bubble_type}"><span class="chat-label">{label}</span>{msg["content"]}</div>', unsafe_allow_html=True)
        
        pregunta = st.chat_input(t["chat_placeholder"])
        if pregunta:
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            ld = st.session_state.last_data
            res = generar_analisis_ia(st.session_state.lang, ld["ticket"], ld["p_act"], ld["p_fut"], ld["cambio"], perfil, capital, pregunta)
            st.session_state.chat_history.append({"role": "assistant", "content": res})
            st.rerun()
    else: st.info("Realiza un análisis primero.")

with tab3:
    url = "https://www.eleconomista.es" if st.session_state.lang == "Español" else "https://rss.nytimes.com"
    feed = feedparser.parse(url)
    for entry in feed.entries[:8]:
        st.markdown(f'<div style="background:white; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #E2E8F0;"><h4 style="margin:0;">{entry.title}</h4><a href="{entry.link}" target="_blank" style="color:#007BFF; font-size:0.8rem;">{t["read_more"]} →</a></div>', unsafe_allow_html=True)


