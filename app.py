st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* --- GLOBAL --- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
    color: #111827;
}

/* --- SIDEBAR PRO --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A192F 0%, #020617 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

.field-title {
    color: #64FFDA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 18px;
}

/* --- INPUTS --- */
.stTextInput input, .stNumberInput input, .stSelectbox div {
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    padding: 10px;
}

/* --- BOTONES PREMIUM --- */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #0A192F, #1E3A8A);
    color: white;
    font-weight: 600;
    height: 50px;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px rgba(0,0,0,0.12);
}

/* --- TABS MODERNAS --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: #F1F5F9;
    border-radius: 10px;
    padding: 10px 18px;
    transition: 0.2s;
}

.stTabs [aria-selected="true"] {
    background: #0A192F !important;
    color: white !important;
}

/* --- METRICS PRO --- */
.metric-container {
    background: white;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    transition: 0.2s;
}

.metric-container:hover {
    transform: translateY(-4px);
}

/* --- CHARTS --- */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
}

/* --- CHAT --- */
.chat-container {
    padding: 10px;
}

.bubble {
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 14px;
    max-width: 75%;
}

.user-bubble {
    background: #F1F5F9;
    align-self: flex-end;
}

.ai-bubble {
    background: #EEF2FF;
    border-left: 4px solid #3B82F6;
}

/* --- NEWS CARDS --- */
.news-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
    transition: 0.2s;
    border: 1px solid #E5E7EB;
}

.news-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
}

/* --- RECOMMENDATION BOX --- */
.recommendation-box {
    border-radius: 16px;
    padding: 25px;
    background: linear-gradient(135deg, #F8FAFC, #FFFFFF);
    border: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)
