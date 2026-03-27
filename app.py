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

# --- ESTILOS CSS DE ALTO NIVEL (SIN TOCAR) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    /* Fondo principal blanco */
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    * { font-family: 'Inter', sans-serif; }

    /* Barra lateral Azul Profundo Profesional */
    [data-testid="stSidebar"] {
        background-color: #0A192F !important;
        border-right: 1px solid #E5E7EB;
    }

    /* Títulos en la barra lateral */
    .field-title {
        color: #64FFDA;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
        margin-top: 15px;
    }

    /* Botón Moderno */
    .stButton>button {
        border: none;
        border-radius: 10px;
        background: linear-gradient(135deg, #0A192F 0%, #1F2937 100%);
        color: #FFFFFF !important;
        font-weight: 600;
        height: 48px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Tabs minimalistas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #E5E7EB; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; color: #6B7280;
        font-weight: 500; padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] { color: #0A192F !important; border-bottom: 2px solid #0A192F !important; }

    /* Métrica Cards Estilo Fintech */
    .metric-container {
        background: #FFFFFF;
        border: 1px solid #F3F4F6;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* --- CHAT MODERNO --- */
    .chat-container { display: flex; flex-direction: column; gap: 15px; padding: 10px; }
    .chat-row { display: flex; width: 100%; justify-content: flex-start; margin-bottom: 5px; }
    
    .bubble {
        padding: 16px 22px;
        border-radius: 18px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .user-bubble {
        background-color: #F8F9FA;
        color: #374151;
        border: 1px solid #F3F4F6;
        border-bottom-left-radius: 4px;
    }

    .ai-bubble {
        background-color: #F0F7FF;
        color: #1E3A8A;
        border: 1px solid #DBEAFE;
        border-bottom-left-radius: 4px;
    }

    .chat-label {
        font-size: 9px;
        font-weight: 800;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .label-user { color: #9CA3AF; }
    .label-ai { color: #3B82F6; }

    /* Caja de recomendación */
    .recommendation-box {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 5px solid #0A192F;
        padding: 25px;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Idioma", "cap":"Presupuesto", "risk_lab":"Riesgo", "ass_lab":"Ticker", 
        "btn":"ANALIZAR ACTIVO", "wait":"Consultando mercados...", "price":"Precio Actual", "target":"Objetivo 30d", 
        "shares":"Capacidad Compra", "chat_placeholder":"Escribe tu consulta financiera..."
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"ANALYZE ASSET", "wait":"Consulting markets...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Buying Capacity", "chat_placeholder":"Type your financial query..."
    }
}

# --- IA MEJORADA (DISCUSIÓN GENERAL) ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"
        
        # Contexto dinámico
        contexto_activo = f"Activo analizado: {ticket}. Precio actual: {p_act}€. Predicción 30d: {p_fut}€." if ticket else "No hay activo analizado aún."
        
        prompt = f"""
        Actúa como un Senior Investment Strategist experto en mercados globales. Responde en {idioma_inst}.
        
        CONTEXTO DEL USUARIO:
        - Perfil de Riesgo: {perfil}
        - Capital disponible: {capital}€
        - {contexto_activo}
        
        INSTRUCCIONES:
        1. Puedes discutir sobre CUALQUIER tema de inversión: acciones, cripto, ETFs, ahorro, interés compuesto, macroeconomía o dudas técnicas.
        2. Si la pregunta es sobre el activo analizado, usa los datos proporcionados.
        3. Si la pregunta es general o sobre otro tema, responde con autoridad profesional basándote en el perfil del usuario.
        
        PREGUNTA DEL USUARIO: {pregunta if pregunta else "Deseo una recomendación estratégica inicial."}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error en el servicio de IA: {e}"

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
st.markdown(f"<h2 style='text-align: center; color: #0A192F; font-weight: 700; letter-spacing: -1px; margin-bottom: 30px;'>{t['title']}</h2>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([f"📊 {t['btn']}", f"💬 Chat Advisor"])

with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                # Arreglo para MultiIndex de yfinance (Evita el TypeError)
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                
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
                fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Precio", line=dict(color='#0A192F', width=2)))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Proyección", line=dict(color='#3B82F6', dash='dash')))
                fig.update_layout(template="plotly_white", margin=dict(l=0,r=0,t=20,b=0), height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Renderizado del historial de chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        is_user = chat["role"] == "user"
        clase = "user-bubble" if is_user else "ai-bubble"
        label = "TÚ" if is_user else "INVESTIA AI"
        label_clase = "label-user" if is_user else "label-ai"
        
        st.markdown(f'<div class="chat-label {label_clase}">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bubble {clase}">{chat["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input del chat
    if user_input := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Obtenemos respuesta de la IA (pasa None si no hay análisis previo para evitar errores)
        respuesta = generar_analisis_ia(
            st.session_state.lang,
            st.session_state.get("ticket_act"),
            st.session_state.get("p_act"),
            st.session_state.get("p_pre"),
            perfil,
            capital,
            user_input
        )
        
        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        st.rerun()
