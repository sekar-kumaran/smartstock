import streamlit as st

def apply_theme():
    """
    Applies the SmartStock Professional Light Theme.
    Uses a clean white/blue gradient wave background, glassmorphism cards, 
    and Tailwind CSS for component-level styling.
    """
    st.markdown("""
        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <!-- Tailwind CSS CDN -->
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        
        <style>
        /* ======================================
           GLOBAL - HIDE STREAMLIT CHROME
           ====================================== */
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        [data-testid="stSidebarNav"] {display: none !important;}
        
        /* ======================================
           GLOBAL - BACKGROUND WAVE PATTERN
           ====================================== */
        .stApp {
            background: linear-gradient(135deg, #f8faff 0%, #eef2ff 30%, #e0e7ff 60%, #f0f4f8 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Animated wave overlay at top */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 320px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%233b82f6' fill-opacity='0.08' d='M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,165.3C960,149,1056,171,1152,192C1248,213,1344,235,1392,245.3L1440,256L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z'%3E%3C/path%3E%3Cpath fill='%231d4ed8' fill-opacity='0.04' d='M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,154.7C960,171,1056,181,1152,165.3C1248,149,1344,107,1392,85.3L1440,64L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z'%3E%3C/path%3E%3Cpath fill='%236366f1' fill-opacity='0.03' d='M0,64L48,80C96,96,192,128,288,128C384,128,480,96,576,85.3C672,75,768,85,864,112C960,139,1056,181,1152,181.3C1248,181,1344,139,1392,117.3L1440,96L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z'%3E%3C/path%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-size: cover;
            pointer-events: none;
            z-index: 0;
        }
        
        /* ======================================
           SIDEBAR - FROSTED GLASS
           ====================================== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(238,242,255,0.9) 100%) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
        }
        [data-testid="stSidebar"] * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* ======================================
           TYPOGRAPHY - PROFESSIONAL DARK TEXT
           ====================================== */
        * {
            font-family: 'Inter', sans-serif !important;
        }
        h1 { color: #0f172a !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
        h2 { color: #0f172a !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
        h3 { color: #1e293b !important; font-weight: 600 !important; }
        h4, h5, h6 { color: #1e293b !important; font-weight: 600 !important; }
        p, li, span, div, label { color: #334155 !important; }
        
        /* ======================================
           METRICS - GLASSMORPHISM CARDS
           ====================================== */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(99, 102, 241, 0.12) !important;
            border-radius: 16px !important;
            padding: 1.25rem 1rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -4px rgba(0, 0, 0, 0.06) !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            color: #64748b !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
        }
        
        /* ======================================
           BUTTONS - BLUE GRADIENT
           ====================================== */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.5rem !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
            transition: all 0.3s ease !important;
            font-size: 0.9rem !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
            transform: translateY(-1px) !important;
        }
        
        /* ======================================
           DATA FRAMES - FROSTED TABLE
           ====================================== */
        [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.8) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(99, 102, 241, 0.1) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04) !important;
            overflow: hidden !important;
        }
        
        /* ======================================
           INPUTS / SELECTBOXES
           ====================================== */
        .stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            color: #0f172a !important;
        }
        
        /* ======================================
           TABS
           ====================================== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            background-color: rgba(255, 255, 255, 0.5) !important;
            border-radius: 12px !important;
            padding: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px !important;
            font-weight: 600 !important;
            color: #64748b !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
            color: #2563eb !important;
        }
        
        /* ======================================
           EXPANDERS
           ====================================== */
        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.7) !important;
            border: 1px solid rgba(99, 102, 241, 0.1) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(8px) !important;
        }
        
        /* ======================================
           LAYOUT
           ====================================== */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1440px !important;
        }
        
        /* ======================================
           PLOTLY CHART CONTAINERS
           ====================================== */
        [data-testid="stPlotlyChart"] {
            background: rgba(255, 255, 255, 0.65) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(99, 102, 241, 0.08) !important;
            padding: 0.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important;
        }
        
        /* Horizontal rule */
        hr {
            border-color: rgba(99, 102, 241, 0.1) !important;
        }
        
        /* Slider styling */
        .stSlider > div > div > div > div {
            background-color: #3b82f6 !important;
        }
        
        /* Info / Warning / Success / Error boxes */
        [data-testid="stAlert"] {
            border-radius: 12px !important;
            border-left-width: 4px !important;
        }
        </style>
    """, unsafe_allow_html=True)
