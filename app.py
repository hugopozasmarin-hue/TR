import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import feedparser
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS AVANZADOS (UI/UX) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    :root {
        --primary: #0A192F;
        --accent: #007BFF;
        --bg-light: #F8FAFC;
        --text-main: #1E293B;
        --white: #FFFFFF;
    }

    .stApp { background-color: var(--bg-light); color: var(--text-main); }
    * { font-family: 'Inter', sans-serif; }

    /* Barra lateral Ultra-Moderna */
    [data-testid="stSidebar"] {
        background-color: var(--primary) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] .stMarkdown p { color: #E2E8F0; }

    /* Títulos de secciones */
    .field-title {
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 20px;
    }

    /* Botón Profesional con Animación */
    .stButton>button {
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
        color: white !important;
        font-weight: 600;
        padding: 12px 24px;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
    }

    /* Tabs Estilo Dashboard */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent !important;
        border: none !important;
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 3px solid var(--accent) !important;
    }

    /* Métricas / Cards */
    .metric-card {
        background: var(--white);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        text-align: center;
    }
    .metric-card:hover { transform: translateY(-5px); }

    /* Chat Bubbles */
    .chat-bubble {
        padding: 18px 24px;
        border-radius: 20px;
        margin-bottom: 15px;
        line-height: 1.6;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .ai-msg { background: #F1F5F9; border-left: 5px solid var(--primary); color: #1E293B; }
    .user-msg { background: #E0F2FE; border-right: 5px solid var(--accent); text-align: right; color: #0369A1; }

    /* Header */
    .main-header {
        background: linear-gradient(90deg, #0A192F 0%, #1E3A8A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA PRO TERMINAL", "lang_lab":"Idioma", "cap":"Capital Disponible", "risk_lab":"Perfil de Riesgo", "ass_lab":"Símbolo (Ticker)", 
        "btn":"EJECUTAR ANÁLISIS", "wait":"Procesando datos de mercado...", "price":"Precio Actual", "target":"Objetivo 30d", 
        "shares":"Acciones Sugeridas", "analysis":"Estrategia de Inversión", "hist_t":"Tendencia Histórica", 
        "pred_t":"Predicción Algorítmica", "chat_placeholder":"Consulta a la IA sobre este activo...",
        "news_tab": "Noticias", "news_sub": "Última Hora Económica"
    },
    "English": { 
        "title":"INVESTIA PRO TERMINAL", "lang_lab":"Language", "cap":"Available Capital", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"RUN ANALYSIS", "wait":"Processing market data...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Suggested Shares", "analysis":"Investment Strategy", "hist_t":"Historical Trend", 
        "pred_t":"Algorithmic Projection", "chat_placeholder":"Ask IA about this asset...",
        "news_tab": "News", "news_sub": "Global Economic News"
    }
}

# --- LÓGICA DE IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"""
        Actúa como un Analista Senior de Fondos de Inversión. 
        Activo: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€ ({cambio:.2f}%).
        Perfil: {perfil}. Capital: {capital}€.
        
        Responde en {idioma_inst} de forma profesional:
        1. Acción Recomendada (Compra/Venta/Mantener).
        2. Análisis técnico resumido.
        3. Gestión de riesgo para este perfil.
        Pregunta específica: {pregunta if pregunta else "Análisis general."}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error en conexión IA: {e}"

# --- GESTIÓN DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_analysis" not in st.session_state: st.session_state.last_analysis = None

# --- SIDEBAR (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com", width=60) # Icono decorativo
    st.markdown('<p class="field-title">Preferencias</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["cap"]} (€)</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL", label_visibility="collapsed").upper()
    
    analyze_clicked = st.button(t["btn"])

# --- CUERPO PRINCIPAL ---
st.markdown(f'<h1 class="main-header">{t["title"]}</h1>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([f"📈 {t['btn']}", f"🤖 Smart Chat", f"🌍 {t['news_tab']}"])

with tab1:
    if analyze_clicked:
        with st.spinner(t["wait"]):
            # Obtención de datos
            df = yf.download(ticket, period="2y")
            if not df.empty:
                # Limpieza de datos (manejo de MultiIndex si ocurre)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Predicción con Prophet
                df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                future = m.make_future_dataframe(periods=30)
                forecast = m.predict(future)
                
                p_act = df['Close'].iloc[-1]
                p_fut = forecast['yhat'].iloc[-1]
                cambio = ((p_fut - p_act) / p_act) * 100
                
                # Guardar en sesión para el chat
                st.session_state.last_analysis = {"ticket": ticket, "p_act": p_act, "p_fut": p_fut, "cambio": cambio}

                # Layout de Métricas
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""<div class="metric-card"><p style='color:#64748B; margin:0;'>{t['price']}</p>
                                <h2 style='color:#0A192F; margin:0;'>{p_act:,.2f}€</h2></div>""", unsafe_allow_html=True)
                with c2:
                    color = "#10B981" if cambio > 0 else "#EF4444"
                    st.markdown(f"""<div class="metric-card"><p style='color:#64748B; margin:0;'>{t['target']}</p>
                                <h2 style='color:{color}; margin:0;'>{p_fut:,.2f}€ ({cambio:+.2f}%)</h2></div>""", unsafe_allow_html=True)
                with c3:
                    num_acc = capital // p_act
                    st.markdown(f"""<div class="metric-card"><p style='color:#64748B; margin:0;'>{t['shares']}</p>
                                <h2 style='color:#007BFF; margin:0;'>{int(num_acc)} Units</h2></div>""", unsafe_allow_html=True)

                # Gráfico Profesional
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_p['ds'], y=df_p['y'], name="Histórico", line=dict(color='#0A192F', width=2)))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Predicción", line=dict(color='#007BFF', width=2, dash='dot')))
                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), height=400, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                # Recomendación IA
                st.markdown(f"### 🛡️ {t['analysis']}")
                analisis = generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital)
                st.info(analisis)
            else:
                st.error("Ticker no encontrado o sin datos.")

with tab2:
    st.markdown("### 💬 Asistente Financiero Pro")
    if st.session_state.last_analysis:
        for chat in st.session_state.chat_history:
            role_class = "user-msg" if chat["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-bubble {role_class}">{chat["content"]}</div>', unsafe_allow_html=True)

        pregunta = st.chat_input(t["chat_placeholder"])
        if pregunta:
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            with st.spinner("IA Pensando..."):
                la = st.session_state.last_analysis
                res = generar_analisis_ia(st.session_state.lang, la["ticket"], la["p_act"], la["p_fut"], la["cambio"], perfil, capital, pregunta)
                st.session_state.chat_history.append({"role": "assistant", "content": res})
            st.rerun()
    else:
        st.warning("Primero realiza un análisis en la pestaña principal.")

with tab3:
    st.markdown(f"### {t['news_sub']}")
    rss_url = "https://www.eleconomista.es" if st.session_state.lang == "Español" else "https://rss.nytimes.com"
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries[:8]:
        with st.expander(f"📰 {entry.title}"):
            st.write(entry.summary if 'summary' in entry else "Sin descripción disponible.")
            st.markdown(f"[Leer noticia completa]({entry.link})")

# --- FOOTER ---
st.markdown("""<hr><p style='text-align: center; color: #94A3B8; font-size: 0.8rem;'>
    InvestIA Elite Pro Terminal © 2024 | Financial Intelligence System</p>""", unsafe_allow_html=True)

