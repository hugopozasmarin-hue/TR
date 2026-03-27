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

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0A192F !important; border-right: 1px solid #E5E7EB; }
    .field-title { color: #64FFDA; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px; margin-top: 15px; }
    .stButton>button { border: none; border-radius: 10px; background: linear-gradient(135deg, #0A192F 0%, #1F2937 100%); color: #FFFFFF !important; font-weight: 600; height: 48px; width: 100%; transition: all 0.3s ease; }
    .metric-container { background: #FFFFFF; border: 1px solid #F3F4F6; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; }
    .chat-container { display: flex; flex-direction: column; gap: 15px; padding: 10px; }
    .bubble { padding: 16px 22px; border-radius: 18px; max-width: 80%; font-size: 15px; line-height: 1.6; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .user-bubble { background-color: #F8F9FA; color: #374151; border: 1px solid #F3F4F6; border-bottom-left-radius: 4px; align-self: flex-end; }
    .ai-bubble { background-color: #F0F7FF; color: #1E3A8A; border: 1px solid #DBEAFE; border-bottom-left-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", 
        "btn":"ANALIZAR ACTIVO", "wait":"Consultando mercados...", "price":"Precio Actual", "target":"Objetivo 30d", 
        "shares":"Capacidad Compra", "analysis":"Recomendación Estratégica", "chat_placeholder":"Escribe tu consulta financiera..."
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"ANALYZE ASSET", "wait":"Consulting markets...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Buying Capacity", "analysis":"Strategic Recommendation", "chat_placeholder":"Type your financial query..."
    }
}

# --- IA MEJORADA (GENERAL Y ESPECÍFICA) ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        
        # Contexto de mercado opcional si hay análisis previo
        contexto_mercado = f"Activo actual analizado: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€." if ticket else "Sin activo analizado aún."

        prompt = f"""
        Actúa como un Estratega Senior de Inversiones. Responde en {idioma_inst}.
        Tu conocimiento abarca: Macroeconomía, análisis técnico, fundamental, cripto, ETFs y educación financiera.
        
        CONTEXTO DEL USUARIO:
        - Perfil: {perfil}
        - Capital: {capital}€
        - {contexto_mercado}
        
        INSTRUCCIÓN: 
        Responde a la pregunta del usuario de forma profesional y clara. Si la pregunta es sobre el activo analizado, usa los datos proporcionados. 
        Si es sobre CUALQUIER otro tema de inversión o finanzas, responde con tu conocimiento general de experto.
        
        PREGUNTA: {pregunta if pregunta else "Dame una recomendación estratégica general basada en mi perfil."}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"

# --- SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

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

# --- UI ---
st.markdown(f"<h2 style='text-align: center; color: #0A192F; font-weight: 700;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([f"📊 {t['btn']}", f"💬 Chat Advisor"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "ticket_act": ticket, "analizado": True})
                
                col1, col2, col3 = st.columns(3)
                col1.metric(t["price"], f"{p_act:.2f} €")
                col2.metric(t["target"], f"{p_fut:.2f} €", f"{((p_fut-p_act)/p_act)*100:.2f}%")
                col3.metric(t["shares"], f"{int(capital/p_act)}")
                
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
        # Si no hay análisis previo, pasamos None a los valores numéricos
        res_ia = generar_analisis_ia(
            st.session_state.lang, 
            st.session_state.get("ticket_act"), 
            st.session_state.get("p_act"), 
            st.session_state.get("p_pre"), 
            0, perfil, capital, prompt_user
        )
        st.session_state.chat_history.append({"role": "assistant", "content": res_ia})
        st.rerun()

