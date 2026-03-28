# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite | Pro Terminal", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS DE ALTO NIVEL ---
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
        padding: 166px 22px;
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
        "shares":"Capacidad Compra", "analysis":"Recomendación Estratégica", "hist_t":"Movimiento del Mercado", 
        "pred_t":"Proyección Algorítmica", "chat_placeholder":"Escribe tu consulta financiera...",
        "news_tab": "Noticias",
        "news_sub": "Noticias Económicas Globales"
    },
    "English": { 
        "title":"INVESTIA TERMINAL", "lang_lab":"Language", "cap":"Budget", "risk_lab":"Risk Profile", "ass_lab":"Asset Ticker", 
        "btn":"ANALYZE ASSET", "wait":"Consulting markets...", "price":"Current Price", "target":"30-Day Target", 
        "shares":"Buying Capacity", "analysis":"Strategic Recommendation", "hist_t":"Market Movement", 
        "pred_t":"Algorithmic Projection", "chat_placeholder":"Type your financial query...",
        "news_tab": "News",
        "news_sub": "Global Economic News"
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
tab1, tab2, tab3 = st.tabs([f"📊 {t['btn']}", f"💬 Chat", f"📰 {t['news_tab']}"])

# --- ANÁLISIS ---
with tab1:
    if st.button(t["btn"]):
        with st.spinner(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                df = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
                model = Prophet(daily_seasonality=True).fit(df)
                forecast = model.predict(model.make_future_dataframe(periods=30))
                p_act, p_fut = float(df['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "analizado": True})
