st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* =====================================================
   DESIGN SYSTEM - INVESTMENT TERMINAL (TOKENS)
===================================================== */
:root {
    --bg-primary: #0A0D10;
    --bg-secondary: #0E1218;
    --bg-tertiary: #111827;

    --text-primary: #E5E7EB;
    --text-secondary: #9CA3AF;

    --accent-green: #10B981;
    --accent-blue: #0EA5E9;
    --accent-gold: #FBBF24;

    --border-subtle: rgba(255,255,255,0.06);
    --border-strong: rgba(255,255,255,0.12);

    --shadow-soft: 0 10px 25px rgba(0,0,0,0.25);
    --shadow-strong: 0 20px 40px rgba(0,0,0,0.4);

    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 18px;

    --blur: blur(14px);
}

/* =====================================================
   GLOBAL LAYOUT
===================================================== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, var(--bg-secondary) 0%, var(--bg-primary) 70%);
    color: var(--text-primary);
}

/* GRID FINANCIAL OVERLAY */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 55px 55px;
    pointer-events: none;
    z-index: 0;
}

/* =====================================================
   TYPOGRAPHY SYSTEM
===================================================== */
h1, h2, h3, h4 {
    letter-spacing: -0.6px;
    font-weight: 700;
}

p {
    color: var(--text-secondary);
}

/* =====================================================
   SIDEBAR - TRADING DESK PANEL
===================================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070A0F 0%, #020407 100%);
    border-right: 1px solid var(--border-subtle);
    backdrop-filter: var(--blur);
}

[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top, rgba(16,185,129,0.08), transparent 60%);
    pointer-events: none;
}

.field-title {
    color: var(--accent-green);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 18px;
    opacity: 0.85;
}

/* =====================================================
   INPUT SYSTEM (FINTECH GRADE)
===================================================== */
.stTextInput input,
.stNumberInput input {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border-subtle) !important;
    background: rgba(255,255,255,0.03) !important;
    color: var(--text-primary) !important;
    padding: 12px !important;
    transition: all 0.25s ease;
}

.stTextInput input:hover {
    border-color: rgba(16,185,129,0.4) !important;
}

.stTextInput input:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.12);
}

/* SELECTBOX SYSTEM */
.stSelectbox > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease;
}

.stSelectbox > div:hover {
    border-color: rgba(14,165,233,0.4) !important;
}

/* POPUP DROPDOWN */
div[data-baseweb="popover"] {
    background: #0B0F14 !important;
    border: 1px solid var(--border-subtle);
    backdrop-filter: var(--blur);
}

/* =====================================================
   BUTTON SYSTEM - EXECUTION STYLE
===================================================== */
.stButton>button {
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
    color: white;
    font-weight: 700;
    height: 52px;
    border: none;
    letter-spacing: 0.6px;
    transition: all 0.25s ease;
    box-shadow: var(--shadow-soft);
    position: relative;
    overflow: hidden;
}

.stButton>button::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: translateX(-100%);
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-strong);
}

.stButton>button:hover::after {
    animation: shine 1.2s ease;
}

@keyframes shine {
    100% { transform: translateX(100%); }
}

/* =====================================================
   METRICS - FINANCIAL CARDS
===================================================== */
.metric-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 22px;
    backdrop-filter: var(--blur);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-container::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top left, rgba(16,185,129,0.08), transparent 60%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.metric-container:hover {
    transform: translateY(-4px);
    border-color: rgba(16,185,129,0.35);
}

.metric-container:hover::before {
    opacity: 1;
}

/* =====================================================
   TABS - TERMINAL STYLE
===================================================== */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    transition: 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)) !important;
    color: #0A0D10 !important;
}

/* =====================================================
   CHAT SYSTEM
===================================================== */
.bubble {
    padding: 14px 18px;
    border-radius: var(--radius-md);
    max-width: 75%;
    font-size: 14px;
    line-height: 1.45;
}

.user-bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border-subtle);
}

.ai-bubble {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
}

/* =====================================================
   NEWS CARDS SYSTEM
===================================================== */
.news-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 20px;
    margin-bottom: 15px;
    backdrop-filter: var(--blur);
    transition: all 0.25s ease;
}

.news-card:hover {
    transform: translateY(-3px);
    border-color: rgba(14,165,233,0.3);
}

/* =====================================================
   RECOMMENDATION PANEL
===================================================== */
.recommendation-box {
    border-radius: var(--radius-lg);
    padding: 25px;
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(14,165,233,0.05));
    border: 1px solid rgba(16,185,129,0.2);
    backdrop-filter: var(--blur);
}

/* =====================================================
   SCROLLBAR PREMIUM
===================================================== */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--accent-green), var(--accent-blue));
    border-radius: 10px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

/* =====================================================
   MICRO ANIMATIONS SYSTEM
===================================================== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-container,
.news-card,
.recommendation-box {
    animation: fadeIn 0.4s ease;
}
</style>
""", unsafe_allow_html=True)
