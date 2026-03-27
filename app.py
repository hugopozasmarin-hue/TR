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
GROQ_API_KEY = "TU_API_KEY_AQUI"

# --- ESTILOS CSS DE ALTO NIVEL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    * { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #0A192F !important;
        border-right: 1px solid #E5E7EB;
    }

    .field-title {
        color: #64FFDA;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
        margin-top: 15px;
    }

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
        "title":"INVESTIA TERMINAL",
        "lang_lab":"Idioma",
        "cap":"Presupuesto",
        "risk_lab":"Riesgo",
        "ass_lab":"Ticker",
        "btn":"ANALIZAR ACTIVO",
        "wait":"Consultando mercados...",
        "price":"Precio Actual",
        "target":"Objetivo 30d",
        "shares":"Capacidad Compra",
        "analysis":"Recomendación Estratégica",
        "hist_t":"Movimiento del Mercado",
        "pred_t":"Proyección Algorítmica",
        "chat_placeholder":"Escribe tu consulta financiera..."
    },
    "English": {
        "title":"INVESTIA TERMINAL",
        "lang_lab":"Language",
        "cap":"Budget",
        "risk_lab":"Risk Profile",
        "ass_lab":"Asset Ticker",
        "btn":"ANALYZE ASSET",
        "wait":"Consulting markets...",
        "price":"Current Price",
        "target":"30-Day Target",
        "shares":"Buying Capacity",
        "analysis":"Strategic Recommendation",
        "hist_t":"Market Movement",
        "pred_t":"Algorithmic Projection",
        "chat_placeholder":"Type your financial query..."
    }
}

# --- IA RECOMENDACIÓN ---
def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)
    idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"

    prompt = f"""
    Act as a Senior Investment Strategist in {idioma_inst}.
    Data: {ticket}, Price {p_act}, Forecast {p_fut}, Change {cambio:.2f}%.
    Profile: {perfil}, Capital: {capital}€.
    Question: {pregunta if pregunta else "General analysis"}
    """

    res = client.chat.completions.create(
        messages=[{"role":"user","content":prompt}],
        model="llama-3.3-70b-versatile"
    )
    return res.choices[0].message.content


# --- 🔥 FIX: FUNCIÓN CHAT (ANTES DEL USO) ---
def generar_chat_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    client = Groq(api_key=GROQ_API_KEY)
    idioma_inst = "ENGLISH" if lang == "English" else "ESPAÑOL"

    contexto = f"Ticker: {ticket}. Precio: {p_act}€. Predicción: {p_fut}€. Cambio: {cambio:.2f}%"

    prompt = f"""
    Actúa como Senior Investment Strategist.
    Responde en {idioma_inst}.
    Perfil: {perfil}, Capital: {capital}€.
    Contexto: {contexto}
    Pregunta: {pregunta}
    """

    res = client.chat.completions.create(
        messages=[{"role":"user","content":prompt}],
        model="llama-3.3-70b-versatile"
    )
    return res.choices[0].message.content


# --- SESSION ---
if "lang" not in st.session_state:
    st.session_state.lang = "Español"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analizado" not in st.session_state:
    st.session_state.analizado = False

t = languages[st.session_state.lang]


# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()))

    capital = st.number_input("Capital", value=1000.0)
    perfil = st.selectbox("Perfil", ["Conservador", "Moderado", "Arriesgado"])
    ticket = st.text_input("Ticker", value="NVDA").upper()


# --- UI ---
st.markdown(f"<h2 style='text-align:center;color:#0A192F'>{t['title']}</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Análisis", "💬 Chat Advisor", "📰 Noticias"])


# --- TAB ANÁLISIS ---
with tab1:
    if st.button(t["btn"]):
        data = yf.download(ticket, period="2y")

        if not data.empty:
            df = data.reset_index()[['Date','Close']]
            df.columns = ['ds','y']

            model = Prophet()
            model.fit(df)

            future = model.make_future_dataframe(30)
            forecast = model.predict(future)

            p_act = float(df['y'].iloc[-1])
            p_fut = float(forecast['yhat'].iloc[-1])
            cambio = ((p_fut - p_act)/p_act)*100

            st.session_state.update({
                "p_act":p_act,
                "p_pre":p_fut,
                "cambio":cambio,
                "ticket_act":ticket,
                "analizado":True
            })

            st.session_state.analisis = generar_analisis_ia(
                st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital
            )

    if st.session_state.analizado:
        st.write(st.session_state.p_act)
        st.write(st.session_state.p_pre)
        st.write(st.session_state.get("analisis",""))


# --- CHAT TAB (FIXED) ---
with tab2:

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        is_user = msg["role"] == "user"

        st.markdown(f"""
        <div class="chat-row">
            <div class="bubble {'user-bubble' if is_user else 'ai-bubble'}">
                <div class="chat-label {'label-user' if is_user else 'label-ai'}">
                    {'YOU' if is_user else 'AI'}
                </div>
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if pr := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role":"user","content":pr})

        res = generar_chat_ia(
            st.session_state.lang,
            st.session_state.get("ticket_act",""),
            st.session_state.get("p_act",0),
            st.session_state.get("p_pre",0),
            st.session_state.get("cambio",0),
            perfil,
            capital,
            pr
        )

        st.session_state.chat_history.append({"role":"assistant","content":res})
        st.rerun()


# --- TAB NOTICIAS ---
with tab3:
    st.write("Noticias económicas próximamente...")
