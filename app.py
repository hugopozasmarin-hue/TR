import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ESTILOS CSS (MENÚ AZUL MARINO OSCURO) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }

/* BARRA LATERAL AZUL MARINO OSCURO */
[data-testid="stSidebar"] { 
    background-color: #0a192f !important; 
    border-right: 1px solid rgba(255,255,255,0.1); 
}

/* Títulos de campos en sidebar (Blanco/Celeste para contraste) */
.field-title { 
    color: #64ffda; 
    font-size: 10px; 
    font-weight: 800; 
    letter-spacing: 1.5px; 
    text-transform: uppercase; 
    margin-top: 20px; 
    margin-bottom: 8px; 
    display: block; 
    border-bottom: 1px solid rgba(100, 255, 218, 0.2); 
    padding-bottom: 4px; 
}

/* Inputs ajustados para fondo oscuro */
.stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextInput input { 
    background-color: #112240 !important; 
    color: #ccd6f6 !important; 
    border: 1px solid #233554 !important; 
    border-radius: 10px !important; 
}

/* Color del texto de las opciones del selectbox */
div[data-baseweb="select"] > div {
    color: #ccd6f6 !important;
}

label { display: none !important; }

/* Botón Principal */
.stButton>button { 
    width: 100%; 
    border-radius: 12px; 
    background: linear-gradient(90deg, #64ffda, #48cae4); 
    color: #0a192f !important; 
    font-weight: 800; 
    border: none; 
    padding: 15px; 
    transition: all 0.3s ease; 
}

/* Burbujas de Chat */
.bubble { padding: 16px 20px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; font-size: 14px; }
.user-bubble { background: #64ffda; color: #0a192f !important; margin-left: auto; border-bottom-right-radius: 2px; }
.assistant-bubble { background: #f1f5f9; border: 1px solid #e2e8f0; color: #1e293b !important; border-bottom-left-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# --- TRADUCCIONES ---
languages = {
    "Español": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESUPUESTO","risk_lab":"RIESGO","ass_lab":"TICKER (Ej: AAPL)","btn":"ANALIZAR","wait":"Procesando...","price":"Precio","target":"Predicción","shares":"Títulos","disclaimer":"Simulación 2026. Riesgo de capital."},
    "English": {"title":"InvestIA Elite","lang_lab":"LANGUAGE","cap":"BUDGET","risk_lab":"RISK","ass_lab":"TICKER (e.g. TSLA)","btn":"ANALYZE","wait":"Processing...","price":"Price","target":"Target","shares":"Shares","disclaimer":"2026 Simulation. Capital risk."},
    "Català": {"title":"InvestIA Elite","lang_lab":"IDIOMA","cap":"PRESSUPOST","risk_lab":"RISC","ass_lab":"TICKER (Ex: NVDA)","btn":"ANALITZAR","wait":"Analitzant...","price":"Preu","target":"Objectiu","shares":"Accions","disclaimer":"Simulació 2026. Risc de capital."}
}

# --- INICIALIZACIÓN ---
for key, val in [('messages', []), ('cambio', 0.0), ('analizado', False), ('ticket_act', ""), ('lang', "Español"), ('p_act', 0.0), ('p_pre', 0.0)]:
    if key not in st.session_state: st.session_state[key] = val

# --- SIDEBAR (AZUL MARINO) ---
with st.sidebar:
    t = languages[st.session_state.lang]
    st.markdown(f'<p class="field-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang))
    t = languages[st.session_state.lang]
    
    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=1.0, value=1000.0)
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"])
    
    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="AAPL").upper().strip()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Chat"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            # DESCARGA Y LIMPIEZA PROFUNDA PARA EVITAR EL TYPEERROR
            raw_data = yf.download(ticket, period="5y")
            
            if not raw_data.empty:
                # 1. Aplanar MultiIndex de columnas si existe (común en nuevas versiones de yfinance)
                if isinstance(raw_data.columns, pd.MultiIndex):
                    raw_data.columns = raw_data.columns.get_level_values(0)
                
                # 2. Resetear índice y asegurar nombres ds e y
                df_p = raw_data.reset_index()
                df_p = df_p[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                
                # 3. Limpieza de fechas y nulos
                df_p['ds'] = pd.to_datetime(df_p['ds']).dt.tz_localize(None)
                df_p = df_p.dropna()
                
                # 4. Ajuste del modelo
                m = Prophet(daily_seasonality=True).fit(df_p)
                pred = m.predict(m.make_future_dataframe(periods=30))
                
                st.session_state.p_act = float(df_p['y'].iloc[-1])
                st.session_state.p_pre = float(pred['yhat'].iloc[-1])
                st.session_state.cambio = ((st.session_state.p_pre - st.session_state.p_act) / st.session_state.p_act) * 100
                st.session_state.ticket_act = ticket
                st.session_state.analizado = True
                
                # Visualización
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{st.session_state.p_act:.2f}€")
                c2.metric(t["target"], f"{st.session_state.p_pre:.2f}€", f"{st.session_state.cambio:.2f}%")
                c3.metric(t["shares"], f"{(capital/st.session_state.p_act):.2f}")
                st.line_chart(df_p.set_index('ds')['y'])
            else:
                st.error("Error: Ticker no encontrado.")

with tab2:
    if st.session_state.analizado:
        st.info(f"Consultoría activa para {st.session_state.ticket_act}")
        # Aquí iría tu función hablar_con_ia...
    else:
        st.write("Realiza un análisis primero.")

st.markdown("---")
st.caption(f"⚠️ {t['disclaimer']}")
