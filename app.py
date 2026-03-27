import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS DE ALTO NIVEL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0A192F !important; border-right: 1px solid #E5E7EB; }
    .field-title { color: #64FFDA; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px; margin-top: 15px; }
    .stButton>button { border: none; border-radius: 10px; background: linear-gradient(135deg, #0A192F 0%, #1F2937 100%); color: #FFFFFF !important; font-weight: 600; height: 48px; width: 100%; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #E5E7EB; }
    .stTabs [aria-selected="true"] { color: #0A192F !important; border-bottom: 2px solid #0A192F !important; }
    .metric-container { background: #FFFFFF; border: 1px solid #F3F4F6; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; }
    .chat-container { display: flex; flex-direction: column; gap: 15px; padding: 10px; }
    .bubble { padding: 16px 22px; border-radius: 18px; max-width: 80%; font-size: 15px; line-height: 1.6; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 10px;}
    .user-bubble { background-color: #F8F9FA; color: #374151; border: 1px solid #F3F4F6; border-bottom-left-radius: 4px; align-self: flex-end; }
    .ai-bubble { background-color: #F0F7FF; color: #1E3A8A; border: 1px solid #DBEAFE; border-bottom-left-radius: 4px; align-self: flex-start; }
    .news-card { background: #FFFFFF; border: 1px solid #F3F4F6; padding: 15px; border-radius: 12px; margin-bottom: 10px; transition: 0.3s; }
    .news-card:hover { border-color: #3B82F6; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", 
        "btn":"ANALIZAR ACTIVO", "wait":"Consultando mercados...", "price":"Precio Actual", "target":"Objetivo 30d", 
        "shares":"Capacidad Compra", "news_tab":"Noticias de Mercado", "chat_placeholder":"Escribe tu consulta financiera..."
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"ANALYZE ASSET", "wait":"Consulting markets...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Buying Capacity", "news_tab":"Market News", "chat_placeholder":"Type your financial query..."
    }
}

# --- IA ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        ctx = f"Ticker: {ticket}. Price: {p_act}€. Prediction: {p_fut}€." if ticket else "Sin ticker."
        prompt = f"Act as Senior Investor Advisor. Context: {ctx}. Risk: {perfil}. Capital: {capital}€. Question: {pregunta if pregunta else 'Strategic recommendation.'}. Lang: {lang}."
        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return response.choices[0].message.content
    except: return "Error IA."

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "news" not in st.session_state: st.session_state.news = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_temp = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_temp != st.session_state.lang:
        st.session_state.lang = lang_temp
        st.rerun()
    t = languages[st.session_state.lang]
    capital = st.number_input(f"{t['cap']}", value=1000.0, step=100.0)
    perfil = st.selectbox(f"{t['risk_lab']}", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input(f"{t['ass_lab']}", value="NVDA").upper()

# --- UI ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F; font-weight: 700;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs([f"📊 {t['btn']}", f"💬 Chat Advisor", f"📰 {t['news_tab']}"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            ticker_obj = yf.Ticker(ticket)
            data = ticker_obj.history(period="2y")
            if not data.empty:
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                st.session_state.update({"p_act":p_act, "p_pre":p_fut, "ticket_act":ticket, "news": ticker_obj.news[:5]})
                
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f} €")
                c2.metric(t["target"], f"{p_fut:.2f} €", f"{((p_fut-p_act)/p_act)*100:.2f}%")
                c3.metric(t["shares"], f"{int(capital/p_act)}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Precio", line=dict(color='#0A192F')))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Predicción", line=dict(dash='dash', color='#3B82F6')))
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        clase = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="bubble {clase}">{chat["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        res = generar_analisis_ia(st.session_state.lang, st.session_state.get("ticket_act"), st.session_state.get("p_act", 0), st.session_state.get("p_pre", 0), 0, perfil, capital, prompt_user)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()

with tab3:
    if st.session_state.news:
        for item in st.session_state.news:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank" style="text-decoration:none; color:#0A192F; font-weight:600;">{item['title']}</a>
                <p style="font-size:12px; color:#6B7280; margin-top:5px;">Fuente: {item.get('publisher', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Analiza un activo para ver noticias relacionadas.")


