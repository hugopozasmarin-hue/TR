import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API (Manteniendo tu clave original) ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    * { font-family: 'Inter', sans-serif; }

    /* Sidebar Dark Pro */
    [data-testid="stSidebar"] {
        background-color: #0A192F !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Títulos Sidebar */
    .sb-title {
        color: #94A3B8;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 20px 0 8px 0;
    }

    /* Botón Principal */
    .stButton>button {
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
        color: white !important;
        font-weight: 600;
        height: 50px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(10, 25, 47, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(10, 25, 47, 0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; color: #64748B;
        font-weight: 600; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { 
        color: #0A192F !important; 
        border-bottom: 3px solid #007BFF !important; 
    }

    /* Cards de Métricas */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        text-align: center;
    }

    /* Chat Estético */
    .chat-bubble {
        padding: 15px 20px;
        border-radius: 15px;
        margin-bottom: 12px;
        max-width: 85%;
        line-height: 1.5;
    }
    .ai-bubble { background: #F1F5F9; border-left: 4px solid #0A192F; color: #1E293B; }
    .user-bubble { background: #E0F2FE; border-right: 4px solid #007BFF; color: #0369A1; margin-left: auto; text-align: right; }

    /* Animación de carga */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .fade-in { animation: fadeIn 0.8s ease-in; }
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE TRADUCCIÓN COMPLETO ---
languages = {
    "Español": {
        "title": "INVESTIA ELITE TERMINAL",
        "sidebar_lang": "Seleccionar Idioma",
        "sidebar_cap": "Capital de Inversión (€)",
        "sidebar_risk": "Perfil de Riesgo",
        "sidebar_ticker": "Símbolo del Activo",
        "btn_analyze": "ANALIZAR MERCADO",
        "tab_analysis": "Análisis",
        "tab_chat": "Consultoría IA",
        "tab_news": "Noticias en Tiempo Real",
        "loading": "Conectando con servidores financieros...",
        "m_price": "Precio Actual",
        "m_target": "Objetivo (30 días)",
        "m_shares": "Títulos Sugeridos",
        "graph_hist": "Precio Histórico",
        "graph_pred": "Predicción Algorítmica",
        "ia_header": "Dictamen del Analista IA",
        "chat_placeholder": "Haz una pregunta sobre el activo...",
        "news_empty": "No hay noticias disponibles en este momento.",
        "read_more": "Leer noticia completa",
        "risk_options": ["Conservador", "Moderado", "Arriesgado"]
    },
    "English": {
        "title": "INVESTIA ELITE TERMINAL",
        "sidebar_lang": "Select Language",
        "sidebar_cap": "Investment Capital (€)",
        "sidebar_risk": "Risk Profile",
        "sidebar_ticker": "Asset Ticker",
        "btn_analyze": "ANALYZE MARKET",
        "tab_analysis": "Analysis",
        "tab_chat": "AI Consultant",
        "tab_news": "Live News Feed",
        "loading": "Connecting to financial servers...",
        "m_price": "Current Price",
        "m_target": "Target (30 Days)",
        "m_shares": "Suggested Shares",
        "graph_hist": "Historical Price",
        "graph_pred": "Algorithmic Prediction",
        "ia_header": "AI Analyst Opinion",
        "chat_placeholder": "Ask a question about the asset...",
        "news_empty": "No news available at the moment.",
        "read_more": "Read full story",
        "risk_options": ["Conservative", "Moderate", "Aggressive"]
    }
}

# --- LÓGICA DE IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"""
        Act as a Senior Investment Analyst. 
        Asset: {ticket}. Price: {p_act}€. Forecast: {p_fut}€ ({cambio:.2f}%).
        Profile: {perfil}. Capital: {capital}€.
        Language: {idioma_inst}.
        
        Provide:
        1. Action (Buy/Sell/Hold).
        2. Strategic justification.
        3. Specific risk management for a {perfil} profile.
        Specific Question: {pregunta if pregunta else "General analysis."}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- INICIALIZACIÓN DE ESTADO ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_data" not in st.session_state: st.session_state.last_data = None

t = languages[st.session_state.lang]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="sb-title">{t["sidebar_lang"]}</p>', unsafe_allow_html=True)
    lang_sel = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_sel != st.session_state.lang:
        st.session_state.lang = lang_sel
        st.rerun()

    st.markdown(f'<p class="sb-title">{t["sidebar_cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="sb-title">{t["sidebar_risk"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", t["risk_options"], label_visibility="collapsed")
    
    st.markdown(f'<p class="sb-title">{t["sidebar_ticker"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()
    
    btn_exec = st.button(t["btn_analyze"])

# --- HEADER ---
st.markdown(f"<h1 style='text-align:center; color:#0A192F; font-weight:800; letter-spacing:-1.5px;'>{t['title']}</h1>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([f"📊 {t['tab_analysis']}", f"🤖 {t['tab_chat']}", f"📰 {t['tab_news']}"])

# --- LÓGICA DE ANÁLISIS ---
with tab1:
    if btn_exec:
        with st.spinner(t["loading"]):
            # Descarga de datos
            df = yf.download(ticket, period="2y", interval="1d")
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                # Predicción Prophet
                df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                future = m.make_future_dataframe(periods=30)
                forecast = m.predict(future)
                
                p_act = df['Close'].iloc[-1]
                p_fut = forecast['yhat'].iloc[-1]
                cambio = ((p_fut - p_act) / p_act) * 100
                
                st.session_state.last_data = {"ticket": ticket, "p_act": p_act, "p_fut": p_fut, "cambio": cambio}

                # Métricas UI
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-card"><small>{t["m_price"]}</small><h2>{p_act:,.2f}€</h2></div>', unsafe_allow_html=True)
                with c2:
                    color = "#10B981" if cambio > 0 else "#EF4444"
                    st.markdown(f'<div class="metric-card"><small>{t["m_target"]}</small><h2 style="color:{color}">{p_fut:,.2f}€ ({cambio:+.2f}%)</h2></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-card"><small>{t["m_shares"]}</small><h2>{int(capital // p_act)}</h2></div>', unsafe_allow_html=True)

                # Gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_p['ds'], y=df_p['y'], name=t["graph_hist"], line=dict(color='#0A192F', width=2.5)))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name=t["graph_pred"], line=dict(color='#007BFF', width=2, dash='dot')))
                fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=400, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                # Texto IA
                st.markdown(f"### 🛡️ {t['ia_header']}")
                analisis = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f'<div style="background:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">{analisis}</div>', unsafe_allow_html=True)
            else:
                st.error("Error: Ticker no encontrado.")

# --- CHAT ---
with tab2:
    if st.session_state.last_data:
        for msg in st.session_state.chat_history:
            div_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {div_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        pregunta = st.chat_input(t["chat_placeholder"])
        if pregunta:
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            ld = st.session_state.last_data
            respuesta = generar_analisis_ia(st.session_state.lang, ld["ticket"], ld["p_act"], ld["p_fut"], ld["cambio"], perfil, capital, pregunta)
            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
            st.rerun()
    else:
        st.info("Realiza un análisis primero para activar el consultor IA." if st.session_state.lang == "Español" else "Perform an analysis first to activate the AI consultant.")

# --- NOTICIAS DINÁMICAS ---
with tab3:
    st.markdown(f"### {t['tab_news']}")
    # Cambia la fuente RSS según el idioma
    if st.session_state.lang == "Español":
        url = "https://www.eleconomista.es"
    else:
        url = "https://rss.nytimes.com"
    
    feed = feedparser.parse(url)
    
    if not feed.entries:
        st.warning(t["news_empty"])
    else:
        for entry in feed.entries[:10]:
            with st.container():
                st.markdown(f"""
                <div style="background:white; padding:20px; border-radius:10px; margin-bottom:15px; border:1px solid #F1F5F9;">
                    <h4 style="margin:0; color:#0A192F;">{entry.title}</h4>
                    <p style="font-size:0.9rem; color:#64748B;">{entry.published if 'published' in entry else ''}</p>
                    <a href="{entry.link}" target="_blank" style="color:#007BFF; text-decoration:none; font-weight:600;">{t['read_more']} →</a>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("<br><p style='text-align:center; color:#94A3B8; font-size:0.8rem;'>InvestIA Elite Pro | Terminal Institucional v2.0</p>", unsafe_allow_html=True)

