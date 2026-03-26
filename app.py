import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="InvestIA Elite", page_icon="💎", layout="wide")

# --- ⚠️ CONFIGURACIÓN API ---
GROQ_API_KEY = "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" 

# --- ESTILOS CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com');
* { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background-color: #0a192f !important; border-right: 1px solid rgba(255,255,255,0.1); }
.field-title { 
    color: #64ffda; font-size: 10px; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 20px; margin-bottom: 8px;
}
.stButton>button { 
    width: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #64ffda, #48cae4);
    color: #0a192f !important; font-weight: 800; border: none;
}
</style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE IDIOMAS (Actualizado) ---
languages = {
    "Español": {
        "title":"InvestIA Elite", "lang_lab":"AJUSTES", "cap":"PRESUPUESTO", "risk_lab":"RIESGO",
        "ass_lab":"TICKER", "btn":"ANALIZAR MERCADO", "wait":"Procesando datos...", 
        "price":"Precio Actual", "target":"Predicción 30d", "shares":"Acciones posibles", 
        "analysis":"Análisis Estratégico IA", "chat_placeholder":"Pregunta lo que quieras sobre inversión..."
    },
    "English": {
        "title":"InvestIA Elite", "lang_lab":"SETTINGS", "cap":"BUDGET", "risk_lab":"RISK",
        "ass_lab":"TICKER", "btn":"ANALYZE MARKET", "wait":"Processing...", 
        "price":"Current Price", "target":"30-Day Target", "shares":"Possible Shares", 
        "analysis":"AI Strategic Analysis", "chat_placeholder":"Ask anything about investing..."
    },
    "Català": {
        "title":"InvestIA Elite", "lang_lab":"CONFIGURACIÓ", "cap":"PRESSUPOST", "risk_lab":"RISC",
        "ass_lab":"TICKER", "btn":"ANALITZAR MERCAT", "wait":"Processant dades...", 
        "price":"Preu Actual", "target":"Predicció 30d", "shares":"Accions possibles", 
        "analysis":"Anàlisi Estratègic IA", "chat_placeholder":"Pregunta el que vulguis sobre inversió..."
    }
}

# --- LÓGICA DE IA (Mejorada para Consultoría General) ---
def generar_analisis_ia(pregunta, ticket=None, p_act=None, p_fut=None, cambio=None, perfil=None, capital=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Contexto dinámico: si hay análisis previo lo incluye, si no, responde como experto general
        contexto_activo = ""
        if ticket:
            contexto_activo = f"""
            Activo analizado actualmente: {ticket}
            Precio: {p_act}€ | Predicción 30d: {p_fut}€ ({cambio:.2f}%)
            Perfil del usuario: {perfil} | Capital: {capital}€
            """

        system_prompt = f"""Eres un asesor financiero experto y estratega de mercados globales. 
        Tu objetivo es ayudar al usuario con cualquier duda sobre finanzas, trading, cripto o macroeconomía.
        {contexto_activo}
        Si el usuario pregunta algo general, responde con datos precisos y profesionalismo. 
        Si pregunta sobre el activo analizado, integra los datos proporcionados en tu respuesta.
        Sé directo, crítico y evita consejos genéricos legamente peligrosos (añade siempre que es educación financiera)."""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pregunta}
            ],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error en la IA: {e}"

# --- GESTIÓN DE SESIÓN ---
if "lang" not in st.session_state: st.session_state.lang = "Español"
if "analizado" not in st.session_state: st.session_state.analizado = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<p class="field-title">{languages[st.session_state.lang]["lang_lab"]}</p>', unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
    t = languages[st.session_state.lang]

    st.markdown(f'<p class="field-title">{t["cap"]}</p>', unsafe_allow_html=True)
    capital = st.number_input("", value=1000.0, step=100.0, label_visibility="collapsed")
    
    st.markdown(f'<p class="field-title">{t["risk_lab"]}</p>', unsafe_allow_html=True)
    perfil = st.selectbox("", ["Conservador", "Moderado", "Arriesgado"], label_visibility="collapsed")

    st.markdown(f'<p class="field-title">{t["ass_lab"]}</p>', unsafe_allow_html=True)
    ticket = st.text_input("", value="NVDA", label_visibility="collapsed").upper()

# --- INTERFAZ ---
st.title(f"💎 {t['title']}")
tab1, tab2 = st.tabs([f"📈 {t['btn']}", "💬 Consultoría Global"])

with tab1:
    if st.button(t["btn"]):
        with st.status(t["wait"]):
            data = yf.download(ticket, period="2y", interval="1d")
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                df_p = data.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)

                model = Prophet(daily_seasonality=True).fit(df_p)
                forecast = model.predict(model.make_future_dataframe(periods=30))

                p_act, p_fut = float(df_p['y'].iloc[-1]), float(forecast['yhat'].iloc[-1])
                cambio = ((p_fut - p_act) / p_act) * 100

                st.session_state.update({"p_act": p_act, "p_pre": p_fut, "cambio": cambio, "ticket_act": ticket, "analizado": True})

                # Métricas y Gráficas
                c1, c2, c3 = st.columns(3)
                c1.metric(t["price"], f"{p_act:.2f}€")
                c2.metric(t["target"], f"{p_fut:.2f}€", f"{cambio:.2f}%")
                c3.metric(t["shares"], f"{int(capital/p_act)}")

                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig, use_container_width=True)

                with st.spinner("🧠 Analizando..."):
                    inf = generar_analisis_ia(f"Haz un análisis de {ticket}", ticket, p_act, p_fut, cambio, perfil, capital)
                st.markdown(f"### {t['analysis']}")
                st.write(inf)
            else:
                st.error("Ticker no válido.")

with tab2:
    st.markdown(f"### 💬 IA Financial Advisor")
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]): st.write(chat["content"])

    if prompt_user := st.chat_input(t["chat_placeholder"]):
        st.session_state.chat_history.append({"role": "user", "content": prompt_user})
        with st.chat_message("user"): st.write(prompt_user)

        with st.chat_message("assistant"):
            # Si hay análisis previo, se lo pasamos para que tenga contexto, si no, va como consulta general
            kwargs = {
                "pregunta": prompt_user,
                "ticket": st.session_state.get("ticket_act"),
                "p_act": st.session_state.get("p_act"),
                "p_fut": st.session_state.get("p_pre"),
                "cambio": st.session_state.get("cambio"),
                "perfil": perfil,
                "capital": capital
            }
            res = generar_analisis_ia(**kwargs)
            st.write(res)
            st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()
