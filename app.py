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
    .metric-card { background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .chat-bubble { padding: 16px 22px; border-radius: 20px; max-width: 80%; font-size: 0.95rem; line-height: 1.6; box-shadow: 0 3px 10px rgba(0,0,0,0.04); margin-bottom: 15px; position: relative; }
    .ai-bubble { background: #FFFFFF; color: #1E293B; border: 1px solid #E2E8F0; border-left: 5px solid #007BFF; margin-right: auto; }
    .user-bubble { background: #0A192F; color: #FFFFFF; margin-left: auto; border-bottom-right-radius: 4px; }
    .chat-label { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; display: block; }
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


def generar_analisis_ia(lang, ticket, p_act, p_fut, cambio, perfil, capital, pregunta=None):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        idioma = "ENGLISH" if lang == "English" else "ESPAÑOL"
        prompt = f"Senior Analyst. Ticker: {ticket}. Price: {p_act}. Pred: {p_fut}. Risk: {perfil}. Lang: {idioma}. Q: {pregunta if pregunta else 'General report.'}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return res.choices[0].message.content
    except: return "Error IA"

if "lang" not in st.session_state: st.session_state.lang = "Español"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_data" not in st.session_state: st.session_state.last_data = None

t = languages[st.session_state.lang]

with st.sidebar:
    st.markdown(f'<p class="sb-title">{t["lang_lab"]}</p>', unsafe_allow_html=True)
    lang_sel = st.selectbox("", list(languages.keys()), index=list(languages.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if lang_sel != st.session_state.lang: st.session_state.lang = lang_sel; st.rerun()
    capital = st.number_input(t["cap"], value=1000.0, step=100.0)
    perfil = st.selectbox(t["risk_lab"], t["risk_options"])
    ticket = st.text_input(t["ass_lab"], value="NVDA").upper()
    btn_exec = st.button(t["btn"])

st.markdown(f"<h1 style='text-align:center; color:#0A192F; font-weight:800;'>{t['title']}</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs([f"📊 {t['btn']}", f"🤖 Chat IA", f"📰 {t['news_tab']}"])

with tab1:
    if btn_exec:
        with st.spinner(t["wait"]):
            df = yf.download(ticket, period="2y", interval="1d")
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
                df_p['ds'] = df_p['ds'].dt.tz_localize(None)
                m = Prophet(daily_seasonality=True).fit(df_p)
                future = m.make_future_dataframe(periods=30); forecast = m.predict(future)
                p_act, p_fut = df['Close'].iloc[-1], forecast['yhat'].iloc[-1]
                cambio = ((p_fut - p_act) / p_act) * 100
                st.session_state.last_data = {"ticket": ticket, "p_act": p_act, "p_fut": p_fut, "cambio": cambio}

                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="metric-card"><small>{t["price"]}</small><h2>{p_act:,.2f}€</h2></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-card"><small>{t["target"]}</small><h2 style="color:{"#10B981" if cambio > 0 else "#EF4444"}">{p_fut:,.2f}€</h2></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-card"><small>{t["shares"]}</small><h2>{ (capital / p_act) :,.4f}</h2></div>', unsafe_allow_html=True)

                st.markdown(f"#### {t['chart_v']}")
                fig_v = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market")])
                fig_v.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig_v, use_container_width=True)

                st.markdown(f"#### {t['chart_l']}")
                fig_l = go.Figure(); fig_l.add_trace(go.Scatter(x=df_p['ds'], y=df_p['y'], name="Hist")); fig_l.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Pred", line=dict(dash='dot')))
                fig_l.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig_l, use_container_width=True)

                st.markdown(f"### 🛡️ {t['analysis_title']}")
                st.info(generar_analisis_ia(st.session_state.lang, ticket, p_act, p_fut, cambio, perfil, capital))

with tab2:
    if st.session_state.last_data:
        for msg in st.session_state.chat_history:
            bubble = "user-bubble" if msg["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {bubble}"><span class="chat-label">{msg["role"].upper()}</span>{msg["content"]}</div>', unsafe_allow_html=True)
        pregunta = st.chat_input(t["chat_placeholder"])
        if pregunta:
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            ld = st.session_state.last_data
            res = generar_analisis_ia(st.session_state.lang, ld["ticket"], ld["p_act"], ld["p_fut"], ld["cambio"], perfil, capital, pregunta)
            st.session_state.chat_history.append({"role": "assistant", "content": res}); st.rerun()
    else: st.info("Analiza un activo primero.")

with tab3:
    url = "https://www.eleconomista.es" if st.session_state.lang == "Español" else "https://rss.nytimes.com"
    feed = feedparser.parse(url)
    for entry in feed.entries[:8]:
        st.markdown(f'<div style="background:white; padding:15px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:10px;"><h4>{entry.title}</h4><a href="{entry.link}" target="_blank">{t["read_more"]}</a></div>', unsafe_allow_html=True)

# --- 📰 NOTICIAS ---
with tab3:
    st.markdown("<h3 style='color:#0A192F;'>🌎</h3>", unsafe_allow_html=True)

    categoria = st.selectbox(
        ":",
        ["Global", "EEUU", "Europa", "Cripto"]
    )

    noticias = obtener_noticias(categoria)
# Cambia el título estático por la variable:
with tab3:
    st.subheader(t["news_sub"])

    for noticia in noticias:
        st.markdown(f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #E5E7EB;
            padding:20px;
            border-radius:12px;
            margin-bottom:15px;
            box-shadow:0 2px 6px rgba(0,0,0,0.05);
        ">
            <h4 style='margin-bottom:10px; color:#0A192F;'>{noticia['titulo']}</h4>
            <p style='font-size:12px; color:#6B7280;'>{noticia['fecha']}</p>
            <p style='color:#374151;'>{noticia['resumen']}...</p>
            <a href="{noticia['link']}" target="_blank" style="
                color:#3B82F6;
                font-weight:600;
                text-decoration:none;
            ">Leer más →</a>
        </div>
        """, unsafe_allow_html=True)

        # 🔥 BOTÓN IA (BIEN INDENTADO)
        if st.button("🧠 Resumir con IA", key=noticia['link']):
            resumen_ia = generar_analisis_ia(
                st.session_state.lang,
                "",
                0,
                0,
                0,
                perfil,
                capital,
                f"Resume esta noticia en 3 líneas claras: {noticia['titulo']} {noticia['resumen']}"
            )
            st.info(resumen_ia)

    # --- 📰 NOTICIAS ECONÓMICAS ---
def obtener_noticias(categoria="Global"):
    fuentes = {
        "Global": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "EEUU": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "Europa": "https://www.ft.com/rss/home/europe",
        "Cripto": "https://cointelegraph.com/rss"
    }

    url = fuentes.get(categoria, fuentes["Global"])
    feed = feedparser.parse(url)

    noticias = []
    for entry in feed.entries[:10]:
        noticias.append({
            "titulo": entry.title,
            "link": entry.link,
            "fecha": entry.get("published", "Sin fecha"),
            "resumen": entry.get("summary", "")[:200]
        })

    return noticias
