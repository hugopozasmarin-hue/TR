st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* =========================
   GLOBAL - FINANCE TERMINAL
========================= */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, #0A0D10 0%, #05070A 100%);
    color: #E5E7EB;
}

/* Subtle grid overlay (premium trading desk feel) */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* =========================
   SIDEBAR PREMIUM
========================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070A0F 0%, #020407 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
}

.field-title {
    color: #10B981;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 18px;
    opacity: 0.9;
}

/* =========================
   INPUTS PREMIUM
========================= */
.stTextInput input,
.stNumberInput input {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 12px !important;
    background: rgba(255,255,255,0.03) !important;
    color: #E5E7EB !important;
    transition: all 0.25s ease;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border: 1px solid #10B981 !important;
    box-shadow: 0 0 0 2px rgba(16,185,129,0.15);
}

/* SELECT PREMIUM FIX */
.stSelectbox > div {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* dropdown */
div[data-baseweb="popover"] {
    background-color: #0B0F14 !important;
    border: 1px solid rgba(255,255,255,0.08);
}

/* =========================
   BUTTONS - TRADING STYLE
========================= */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #10B981 0%, #0EA5E9 100%);
    color: white;
    font-weight: 700;
    height: 52px;
    border: none;
    letter-spacing: 0.5px;
    transition: all 0.25s ease;
    box-shadow: 0 10px 25px rgba(16,185,129,0.15);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px rgba(16,185,129,0.25);
}

/* =========================
   TABS - TERMINAL STYLE
========================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 10px 18px;
    color: #9CA3AF;
    transition: 0.2s;
    border: 1px solid rgba(255,255,255,0.05);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #10B981, #0EA5E9) !important;
    color: #0A0D10 !important;
    font-weight: 700;
}

/* =========================
   METRICS - PREMIUM CARDS
========================= */
.metric-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 22px;
    backdrop-filter: blur(10px);
    transition: all 0.25s ease;
}

.metric-container:hover {
    transform: translateY(-4px);
    border-color: rgba(16,185,129,0.4);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

/* =========================
   CHARTS
========================= */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* =========================
   CHAT - FINANCE AI STYLE
========================= */
.chat-container {
    padding: 10px;
}

.bubble {
    padding: 14px 18px;
    border-radius: 14px;
    font-size: 14px;
    max-width: 75%;
    line-height: 1.4;
}

.user-bubble {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    align-self: flex-end;
}

.ai-bubble {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
}

/* =========================
   NEWS CARDS PREMIUM
========================= */
.news-card {
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.06);
    transition: all 0.2s ease;
    backdrop-filter: blur(10px);
}

.news-card:hover {
    transform: translateY(-3px);
    border-color: rgba(16,185,129,0.3);
}

/* =========================
   RECOMMENDATION BOX
========================= */
.recommendation-box {
    border-radius: 16px;
    padding: 25px;
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(14,165,233,0.05));
    border: 1px solid rgba(16,185,129,0.2);
    backdrop-filter: blur(12px);
}

/* =========================
   TYPOGRAPHY ENHANCEMENTS
========================= */
h1, h2, h3, h4 {
    letter-spacing: -0.5px;
}

/* =========================
   SCROLLBAR (premium feel)
========================= */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: rgba(16,185,129,0.4);
    border-radius: 10px;
}

::-webkit-scrollbar-track {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

