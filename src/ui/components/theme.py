import streamlit as st

def apply_apple_theme():
    """
    Applies a custom CSS theme inspired by Apple's design language to the Streamlit app.
    Features: System fonts, soft rounded corners, glassmorphism, refined buttons, and minimal spacing.
    """
    custom_css = """
    <style>
    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
    }
    
    .stApp {
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
    }

    /* Hide generic Streamlit UI elements for a cleaner look */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
        letter-spacing: -0.015em !important;
        color: #1D1D1F !important;
    }
    
    h1 {
        font-size: 40px !important;
        margin-bottom: 0.5rem !important;
    }

    /* Cards / Containers styling using glassmorphism */
    .st-emotion-cache-1wivap2, .css-1r6slb0, .css-1v0mbdj {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04) !important;
        padding: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #0071E3 !important;
        color: white !important;
        border: none !important;
        border-radius: 980px !important; /* Fully rounded like Apple CTAs */
        padding: 12px 24px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        letter-spacing: -0.01em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 113, 227, 0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #0077ED !important;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3) !important;
    }
    
    /* Download Buttons */
    .stDownloadButton > button {
        background-color: rgba(0, 0, 0, 0.05) !important;
        color: #1D1D1F !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 980px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: rgba(0, 0, 0, 0.08) !important;
        color: #1D1D1F !important;
        border-color: rgba(0, 0, 0, 0.2) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 0 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #86868B !important;
        border-radius: 0 !important;
        background-color: transparent !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        color: #1D1D1F !important;
        border-bottom: 2px solid #1D1D1F !important;
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.7) !important;
        border: 2px dashed rgba(0, 0, 0, 0.1) !important;
        border-radius: 18px !important;
        padding: 30px !important;
        transition: all 0.2s ease !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #0071E3 !important;
        background: rgba(0, 113, 227, 0.02) !important;
    }

    /* Metrics Panels */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 500 !important;
        color: #86868B !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.02em !important;
    }
    
    [data-testid="stMetricValue"] {
        font-weight: 600 !important;
        color: #1D1D1F !important;
        font-size: 28px !important;
    }
    
    /* Alerts and Warnings */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #0071E3 !important;
        border-radius: 10px !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
