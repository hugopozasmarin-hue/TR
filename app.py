st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* =========================
   BASE FIX (STREAMLIT SAFE)
========================= */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0A0D10;
    color: #E5E7EB;
}

/* =========================
   SIDEBAR
========================= */
[data-testid="stSidebar"] {
    background: #070A0F;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.field-title {
    color: #10B981;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* =========================
   INPUTS
========================= */
.stTextInput input,
.stNumberInput input {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(255,255,255,0.03) !important;
    color: #E5E7EB !important;
    padding: 10px !important;
}

/* =========================
   BUTTONS
========================= */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #10B981, #0EA5E9);
    color: white;
    font-weight: 700;
    height: 52px;
    border: none;
    transition: 0.2s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
}

/* =========================
   TABS
========================= */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
}

.stTabs [aria-selected="true"] {
    background: #10B981 !important;
    color: #0A0D10 !important;
}

/* =========================
   METRICS
========================= */
.metric-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
}

/* =========================
   CHARTS
========================= */
.stPlotlyChart {
    border-radius: 12px;
}

/* =========================
   CHAT
========================= */
.user-bubble {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
}

.ai-bubble {
    background: rgba(16,185,129,0.08);
    border-radius: 12px;
}

/* =========================
   NEWS
========================= */
.news-card {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.06);
}

/* =========================
   RECOMMENDATION
========================= */
.recommendation-box {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 16px;
    padding: 20px;
}

/* =========================
   HOVER EFFECTS
========================= */
.stButton>button:hover,
.metric-container:hover,
.news-card:hover {
    transition: all 0.2s ease;
}

/* =========================
   SCROLLBAR
========================= */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: #10B981;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
