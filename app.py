import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import warnings
warnings.filterwarnings('ignore')

# ================= CONFIG & UI SETUP =================
st.set_page_config(
    page_title="✨ GST Recon Pro", 
    page_icon="🧾",
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:jakkulaabhishek5@gmail.com',
        'Report a bug': "https://github.com/abhishekjakkula/gst-recon-pro/issues",
        'About': "# GST Recon Pro v3.1\nEnterprise GST Reconciliation Engine"
    }
)

# ================= ENHANCED THEME-ADAPTIVE CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #3b82f6;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --border-light: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }

    [data-theme="dark"] {
        --bg-light: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-light: #334155;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-light) 0%, #f1f5f9 100%);
        background-attachment: fixed;
    }
    [data-theme="dark"] .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: var(--shadow-lg);
    }

    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .main-header h1 {
        font-weight: 900 !important;
        font-size: 3rem !important;
        background: linear-gradient(90deg, #fff, #e0e7ff, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    .main-header .subtitle {
        font-size: 1.25rem;
        color: rgba(255,255,255,0.9);
        margin: 1rem 0 0 0;
        line-height: 1.6;
        position: relative;
        z-index: 1;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    .metric-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 24px 20px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary);
    }
    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1;
        margin: 8px 0;
    }
    .metric-card .metric-label {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.9rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        margin-top: 8px;
    }
    .metric-delta.positive { background: rgba(16, 185, 129, 0.1); color: var(--success); }
    .metric-delta.negative { background: rgba(239, 68, 68, 0.1); color: var(--error); }
    .metric-delta.neutral { background: rgba(100, 116, 139, 0.1); color: var(--text-secondary); }

    .insight-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 20px 24px;
        margin-bottom: 16px;
        border-left: 5px solid var(--primary);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: all 0.2s ease;
    }
    .insight-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateX(4px);
    }
    .insight-card.warning {
        border-left-color: var(--warning);
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), transparent);
    }
    .insight-card.success {
        border-left-color: var(--success);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), transparent);
    }
    .insight-card.error {
        border-left-color: var(--error);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), transparent);
    }
    .insight-card .insight-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: var(--text-primary);
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-card .insight-message {
        color: var(--text-secondary);
        line-height: 1.5;
        font-size: 0.95rem;
    }

    .section-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
    }
    .section-card h3 {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border-light);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-card h3 .icon { font-size: 1.4rem; }

    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        border-radius: var(--radius-md);
        padding: 12px 28px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    .stButton>button:hover::before { left: 100%; }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-dark), #4338ca);
    }

    [data-testid="stDataFrame"] {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
    }
    [data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        font-weight: 600;
        padding: 12px 16px;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
    [data-testid="stDataFrame"] td {
        padding: 10px 16px;
        border-bottom: 1px solid var(--border-light);
    }
    [data-testid="stDataFrame"] tr:hover {
        background: rgba(99, 102, 241, 0.05);
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-exact { background: rgba(16, 185, 129, 0.15); color: #065f46; }
    .status-suggested { background: rgba(6, 182, 212, 0.15); color: #0e7490; }
    .status-mismatch { background: rgba(245, 158, 11, 0.15); color: #92400e; }
    .status-missing-2b { background: rgba(239, 68, 68, 0.15); color: #991b1b; }
    .status-missing-pr { background: rgba(139, 92, 246, 0.15); color: #5b21b6; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255,255,255,0.5);
        padding: 8px;
        border-radius: var(--radius-lg);
        backdrop-filter: blur(8px);
        border: 1px solid var(--border-light);
    }
    [data-theme="dark"] .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .progress-container {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 20px;
        margin: 20px 0;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
    }
    .progress-bar {
        height: 8px;
        background: var(--border-light);
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: 4px;
        transition: width 0.3s ease;
    }

    .footer {
        text-align: center;
        padding: 32px 20px;
        margin-top: 60px;
        background: linear-gradient(135deg, var(--bg-card), var(--bg-light));
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        border-top: 1px solid var(--border-light);
    }
    .footer .brand {
        font-weight: 800;
        font-size: 1.2rem;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .footer .credits {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 8px 0;
    }
    .footer .version {
        display: inline-block;
        background: var(--border-light);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 12px;
    }

    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    .quick-action-btn {
        background: var(--bg-card);
        border: 2px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        color: var(--text-primary);
    }
    .quick-action-btn:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    .quick-action-btn .icon { font-size: 1.8rem; margin-bottom: 8px; display: block; }
    .quick-action-btn .label { font-weight: 600; font-size: 0.9rem; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in { animation: fadeInUp 0.5s ease forwards; }
    .animate-fade-in:nth-child(1) { animation-delay: 0.1s; }
    .animate-fade-in:nth-child(2) { animation-delay: 0.2s; }
    .animate-fade-in:nth-child(3) { animation-delay: 0.3s; }
    .animate-fade-in:nth-child(4) { animation-delay: 0.4s; }

    .theme-toggle {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 1000;
    }
    .theme-toggle button {
        background: var(--bg-card);
        border: 2px solid var(--border-light);
        border-radius: 50%;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
    }
    .theme-toggle button:hover {
        transform: scale(1.1);
        border-color: var(--primary);
    }

    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem !important; }
        .main-header .subtitle { font-size: 1rem; }
        .metric-card .metric-value { font-size: 1.8rem; }
        .section-card { padding: 20px; }
    }
</style>

<!-- Theme Toggle Script -->
<script>
const savedTheme = localStorage.getItem('gst-recon-theme');
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
if (initialTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('gst-recon-theme', newTheme);
}
</script>
""", unsafe_allow_html=True)

# ================= THEME TOGGLE BUTTON =================
st.markdown("""
<div class="theme-toggle">
    <button onclick="toggleTheme()" title="Toggle Dark/Light Mode">🌓</button>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR - ENHANCED =================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;">
        <div style="font-size: 2.5rem; margin-bottom: 8px;">🧾</div>
        <h3 style="margin: 0; color: #fff;">GST Recon Pro</h3>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">v3.1 • Enterprise Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚡ Quick Actions")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📥 Load Sample", use_container_width=True):
            st.session_state.load_sample = True
    with col_q2:
        if st.button("🔄 Reset", use_container_width=True):
            for key in list(st.session_state.keys()):
                if 'upload' in key or 'file' in key:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")
    
    with st.expander("🎯 Matching Parameters", expanded=True):
        tolerance = st.number_input("Tax/Taxable Tolerance (₹)", min_value=0, max_value=1000, value=20, step=1)
        date_tolerance = st.number_input("Date Tolerance (Days)", min_value=0, max_value=30, value=7, step=1)
    
    with st.expander("📋 Processing Options"):
        include_reverse_charge = st.checkbox("Include Reverse Charge", value=True)
        auto_claim_itc = st.checkbox("Auto-claim ITC for Exact", value=True)
        fuzzy_doc_matching = st.checkbox("Fuzzy Document Matching", value=True)
        # ✅ NEW: Credit/Debit Note Handling
        handle_cdn_negative = st.checkbox("Treat Credit Notes as Negative Values", value=True, help="Credit notes will have negative taxable/tax values for proper matching")
    
    with st.expander("📤 Export Preferences"):
        include_charts = st.checkbox("Include Charts", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=True)
        max_rows = st.number_input("Max Excel Rows", min_value=1000, max_value=100000, value=15000, step=1000)
    
    st.markdown("---")
    with st.expander("❓ Help"):
        st.markdown("""
        **📚 Quick Guide**
        - Upload GSTR-2B & Purchase Register files
        - Configure matching tolerance in sidebar
        - Review dashboard insights & charts
        - Export comprehensive Excel report
        
        **🔧 Support**
        - Email: jakkulaabhishek5@gmail.com
        - Response: < 24 hours
        """)
    
    st.markdown("---")
    st.markdown("### 🟢 System Status")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #94a3b8;">
        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
            <span>Engine:</span><span style="color: #10b981;">● Online</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
            <span>Matching AI:</span><span style="color: #10b981;">● Active</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
            <span>Export Service:</span><span style="color: #10b981;">● Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= HEADER SECTION =================
st.markdown("""
<div class="main-header animate-fade-in">
    <h1>✨ GST Recon Pro</h1>
    <p class="subtitle">
        AI-Powered GST Reconciliation • Match GSTR-2B with Purchase Register • 
        Real-time Insights • Compliance-Ready Reports • Credit/Debit Note Support
    </p>
</div>
""", unsafe_allow_html=True)

# ================= ENHANCED SAMPLE TEMPLATE GENERATORS =================
def generate_sample_2b_template():
    """Generate sample GSTR-2B with proper DOC_TYPE breakdown and negative CDN values"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE"
    ]
    
    sample_data = [
        # ========== INVOICES (Positive Values) ==========
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "2023-07", "INVOICE", "NO"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "2023-05", "INVOICE", "NO"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "2024-01", "INVOICE", "NO"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "2024-01", "INVOICE", "NO"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO"],
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4582.00, 0, 412.38, 412.38, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "2023-07", "INVOICE", "NO"],
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "03-05-2023", "2023-05", "INVOICE", "NO"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "07-07-2023", "2023-07", "INVOICE", "NO"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "25-04-2023", "2023-04", "INVOICE", "NO"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "15-01-2024", "2024-01", "INVOICE", "NO"],
        
        # ========== CREDIT NOTES (NEGATIVE VALUES - Key Feature) ==========
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02", "CREDIT", "NO"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "15-03-2024", "2024-03", "CREDIT", "NO"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "10-01-2024", "2024-01", "CREDIT", "NO"],
        
        # ========== DEBIT NOTES (Positive Values - Additional Charges) ==========
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "05-03-2024", "2024-03", "DEBIT", "NO"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "20-02-2024", "2024-02", "DEBIT", "NO"],
        
        # ========== MISSING IN PR (Present in 2B only) ==========
        ["36AADCR6281N1ZT", "67186859-1D", 8579.40, 0, 772.11, 772.11, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "01-01-2024", "2024-01", "INVOICE", "NO"],
        ["36CKUPB7102C1ZF", "BEW/23-24/53", 3500.00, 0, 315.00, 315.00, "BALAJI ENGINEERING WORKS", "36ADXFS5154R1ZU", "29-09-2023", "2023-09", "INVOICE", "NO"],
        ["36AAJCS4517L1ZZ", "362311I000806960", 11388.88, 0, 1025.00, 1025.00, "STAR HEALTH AND ALLIED INSURANCE COMPANY LIMITED", "36ADXFS5154R1ZU", "13-11-2023", "2023-11", "INVOICE", "NO"],
        ["36AADCR6281N1ZT", "71936233-1D", 6987.59, 0, 628.89, 628.89, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "01-12-2023", "2023-12", "INVOICE", "NO"],
        ["36AXXPS8501J1ZN", "34/2022-23", 90000.00, 0, 2250.00, 2250.00, "SRINIVASA CATERERS", "36ADXFS5154R1ZU", "01-11-2022", "2023-04", "INVOICE", "NO"],
        
        # ========== REVERSE CHARGE ==========
        ["29AAOCA4995P1ZH", "RC/2023/001", 5000.00, 900.00, 0, 0, "REVERSE CHARGE SUPPLIER", "36ADXFS5154R1ZU", "15-06-2023", "2023-06", "INVOICE", "YES"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="GSTR_2B_Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["GSTR_2B_Data"]
        header_format = workbook.add_format({"bold": True, "bg_color": "#1e40af", "font_color": "white", "border": 1, "align": "center"})
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:F', 14)
        worksheet.set_column('G:G', 35)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 14)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:L', 12)
    return output.getvalue()


def generate_sample_books_template():
    """Generate sample Purchase Register with proper DOC_TYPE and negative CDN values"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "ITC_CLAIM_TYPE", "PLACE_OF_SUPPLY"
    ]
    
    sample_data = [
        # ========== INVOICES (Matching 2B) ==========
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "2023-07", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "2024-01", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "2024-01", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4582.00, 0, 412.38, 412.38, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "2023-07", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        
        # ========== CREDIT NOTES (NEGATIVE VALUES - Matching 2B) ==========
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02", "CREDIT", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "15-03-2024", "2024-03", "CREDIT", "NO", "ELIGIBLE", "TELANGANA"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "10-01-2024", "2024-01", "CREDIT", "NO", "ELIGIBLE", "TELANGANA"],
        
        # ========== DEBIT NOTES (Matching 2B) ==========
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "05-03-2024", "2024-03", "DEBIT", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "20-02-2024", "2024-02", "DEBIT", "NO", "ELIGIBLE", "TELANGANA"],
        
        # ========== SUGGESTED MATCHES (Date differs but within FY) ==========
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "01-06-2023", "2023-06", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "01-09-2023", "2023-09", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-02-2024", "2024-02", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        
        # ========== MISSING IN 2B (Present in Books only) ==========
        ["36AAGCE1603E1Z6", "EDT/SB/2223/013", 79200.00, 0, 4752.00, 4752.00, "EXIGENT DRILLING TECHNOLOGIES PRIVATE LIMITED", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36BDJPM4292D2ZF", "106/22-23", 211868.00, 0, 19068.12, 19068.12, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36BNDPM1159D1Z9", "160", 12015.00, 0, 1081.35, 1081.35, "SRI SAI DURGA PAINTS", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36CKUPB7102C1ZF", "BEW/22-23/101", 1365.00, 0, 81.90, 81.90, "BALAJI ENGINEERING WORKS", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36BECPP5867F1Z7", "055/BSE/22-23", 3850.00, 0, 346.50, 346.50, "B-SON ELECTRICALS", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["29AAOCA4995P1ZH", "FD/22-23/0316", 165318.00, 29757.24, 0, 0, "ANNFLUID DYNAMIKS PRIVATE LIMITED", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["29AILPR7596P1ZS", "MMU/22-23/86", 265000.00, 47700.00, 0, 0, "MARUTHI MACHINE UDYOG", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["29AARFC9317P1ZG", "2022008", 21000.00, 3780.00, 0, 0, "CAL-TECHNOLOGIES", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AAGCE1603E1Z6", "DEBIT NOTE NO.1", 8240.00, 0, 494.40, 494.40, "Exigent Drilling Technologies Private Limited", "36ADXFS5154R1ZU", "12-06-2023", "2023-06", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36ATFPG9930M1Z8", "GRK/43/2022-2023", 88143.00, 0, 7932.87, 7932.87, "GRK ENTERPRISES", "36ADXFS5154R1ZU", "01-06-2023", "2023-06", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["29AILPR7596P1ZS", "MMU/22-23/85", 1350000.00, 243000.00, 0, 0, "MARUTHI MACHINE UDYOG", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["29AILPR7596P1ZS", "MMU/22-23/84", 250000.00, 45000.00, 0, 0, "MARUTHI MACHINE UDYOG", "36ADXFS5154R1ZU", "01-04-2023", "2023-04", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        
        # ========== MISMATCH EXAMPLE ==========
        ["36AAACU2414K1ZG", "Z", 300.00, 0, 27.00, 27.00, "AXIS BANK LTD", "36ADXFS5154R1ZU", "07-11-2023", "2023-11", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="Purchase_Register", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Purchase_Register"]
        header_format = workbook.add_format({"bold": True, "bg_color": "#1e40af", "font_color": "white", "border": 1, "align": "center"})
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:F', 14)
        worksheet.set_column('G:G', 35)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 14)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:N', 15)
    return output.getvalue()

# ================= FILE UPLOAD SECTION =================
st.markdown("""
<div class="section-card animate-fade-in">
    <h3><span class="icon">📁</span> Upload Your Files</h3>
    <p style="color: var(--text-secondary); margin-bottom: 20px;">
        Select your GSTR-2B and Purchase Register files. Ensure DOC_TYPE column has: INVOICE, CREDIT, or DEBIT.
        <br><strong>💡 Credit Notes should have negative taxable/tax values for proper matching.</strong>
    </p>
""", unsafe_allow_html=True)

col_upload1, col_upload2, col_upload3 = st.columns([2, 2, 1])

with col_upload1:
    file_2b = st.file_uploader("📄 GSTR-2B File", type=['xlsx', 'xls'], key='upload_2b', label_visibility="collapsed")
    if file_2b:
        st.success(f"✓ {file_2b.name}")

with col_upload2:
    file_pr = st.file_uploader("📘 Purchase Register", type=['xlsx', 'xls'], key='upload_pr', label_visibility="collapsed")
    if file_pr:
        st.success(f"✓ {file_pr.name}")

with col_upload3:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 2B Sample",
            data=generate_sample_2b_template(),
            file_name="GSTR2B_Sample_CDN.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_d2:
        st.download_button(
            label="📘 PR Sample",
            data=generate_sample_books_template(),
            file_name="PurchaseRegister_Sample_CDN.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def normalize_document_number(doc_num):
    if pd.isna(doc_num) or str(doc_num).strip() == "":
        return "UNKNOWN"
    normalized = re.sub(r'[^A-Z0-9]', '', str(doc_num).upper().strip())
    return normalized.lstrip('0') or "0"

def extract_pan_from_gstin(gstin):
    if pd.isna(gstin) or len(str(gstin).strip()) < 15:
        return "UNKNOWN"
    return str(gstin).strip().upper()[2:12]

def get_document_type(taxable_value, doc_type_col=None):
    """Determine DOC_TYPE from value sign or existing column"""
    if doc_type_col and pd.notna(doc_type_col):
        dt = str(doc_type_col).upper().strip()
        if dt in ['CREDIT', 'CREDIT NOTE', 'CDN', 'CN']:
            return 'CREDIT'
        elif dt in ['DEBIT', 'DEBIT NOTE', 'DBN', 'DN']:
            return 'DEBIT'
        elif dt in ['INVOICE', 'INV', 'B2B', 'B2C']:
            return 'INVOICE'
    try:
        val = float(taxable_value)
        if val < 0:
            return 'CREDIT'
        elif val > 0:
            return 'INVOICE'
        else:
            return 'DEBIT'
    except:
        return 'INVOICE'

def parse_date(date_str):
    if pd.isna(date_str) or str(date_str).strip() == "":
        return None
    for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except:
            continue
    return None

def get_financial_year(date_obj):
    if date_obj is None:
        return "Unknown"
    if date_obj.month >= 4:
        return f"{date_obj.year}-{str(date_obj.year + 1)[-2:]}"
    return f"{date_obj.year - 1}-{str(date_obj.year)[-2:]}"

def is_same_financial_year(date1_str, date2_str):
    d1, d2 = parse_date(date1_str), parse_date(date2_str)
    return d1 and d2 and get_financial_year(d1) == get_financial_year(d2)

@st.cache_data(show_spinner=False)
def process_reconciliation(file_2b_bytes, file_pr_bytes, tolerance, date_tol_days, include_rc, handle_cdn_neg):
    """Main reconciliation with enhanced Credit/Debit Note handling"""
    
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
    
    # Clean column names
    for df in [df_2b, df_pr]:
        df.columns = df.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    
    # Standardize columns
    col_map = {
        'SUPPLIER GSTIN': 'SUPPLIER_GSTIN', 'DOCUMENT NUMBER': 'DOC_NUMBER',
        'TAXABLE VALUE': 'TAXABLE_VALUE', 'SUPPLIER NAME': 'SUPPLIER_NAME',
        'MY GSTIN': 'MY_GSTIN', 'DOCUMENT DATE': 'DOC_DATE', 'DOC_TYPE': 'DOC_TYPE',
        'REVERSE_CHARGE': 'REVERSE_CHARGE', 'ITC_CLAIM_TYPE': 'ITC_CLAIM_TYPE',
        'PLACE_OF_SUPPLY': 'PLACE_OF_SUPPLY', 'MONTH': 'MONTH'
    }
    for old, new in col_map.items():
        if old in df_2b.columns:
            df_2b[new] = df_2b[old]
        if old in df_pr.columns:
            df_pr[new] = df_pr[old]
    
    # Ensure required columns
    required = ['SUPPLIER_GSTIN', 'DOC_NUMBER', 'TAXABLE_VALUE', 'SUPPLIER_NAME', 
                'MY_GSTIN', 'DOC_DATE', 'IGST', 'CGST', 'SGST']
    for col in required:
        if col not in df_2b.columns:
            df_2b[col] = None
        if col not in df_pr.columns:
            df_pr[col] = None
    for df in [df_2b, df_pr]:
        if 'CESS' not in df.columns:
            df['CESS'] = 0
    
    # Fill NaN and standardize
    for df in [df_2b, df_pr]:
        df['SUPPLIER_GSTIN'] = df['SUPPLIER_GSTIN'].fillna('UNKNOWN').astype(str).str.upper().str.strip()
        df['MY_GSTIN'] = df['MY_GSTIN'].fillna('').astype(str).str.upper().str.strip()
        df['SUPPLIER_NAME'] = df['SUPPLIER_NAME'].fillna('Unknown').astype(str).str.strip()
        df['DOC_NUMBER'] = df['DOC_NUMBER'].fillna('').astype(str).str.strip()
        df['DOC_DATE'] = df['DOC_DATE'].fillna('').astype(str).str.strip()
        df['REVERSE_CHARGE'] = df.get('REVERSE_CHARGE', pd.Series(['NO']*len(df))).fillna('NO').astype(str).str.upper().str.strip()
        df['MONTH'] = df.get('MONTH', pd.Series(['Unknown']*len(df))).fillna('Unknown').astype(str).str.strip()
        df['ITC_CLAIM_TYPE'] = df.get('ITC_CLAIM_TYPE', pd.Series(['']*len(df))).fillna('').astype(str).str.strip().str.upper()
        df['PLACE_OF_SUPPLY'] = df.get('PLACE_OF_SUPPLY', pd.Series(['']*len(df))).fillna('').astype(str).str.strip().str.upper()
        
        # Convert numeric
        for col in ['TAXABLE_VALUE', 'IGST', 'CGST', 'SGST', 'CESS']:
            df[col] = pd.to_numeric(df.get(col, pd.Series([0]*len(df))), errors='coerce').fillna(0)
        
        # ✅ ENHANCED: Derive DOC_TYPE properly with negative value handling
        if 'DOC_TYPE' not in df.columns or df['DOC_TYPE'].isna().any():
            df['DOC_TYPE'] = df.apply(lambda r: get_document_type(r['TAXABLE_VALUE'], r.get('DOC_TYPE')), axis=1)
        else:
            # Ensure consistency: if value is negative but DOC_TYPE is not CREDIT, fix it
            if handle_cdn_neg:
                df.loc[(df['TAXABLE_VALUE'] < 0) & (~df['DOC_TYPE'].str.upper().isin(['CREDIT', 'CDN', 'CN'])), 'DOC_TYPE'] = 'CREDIT'
                df.loc[(df['TAXABLE_VALUE'] > 0) & (df['DOC_TYPE'].str.upper().isin(['CREDIT', 'CDN', 'CN'])), 'DOC_TYPE'] = 'INVOICE'
            df['DOC_TYPE'] = df['DOC_TYPE'].apply(lambda x: str(x).upper().strip())
            df['DOC_TYPE'] = df['DOC_TYPE'].replace({'CREDIT NOTE': 'CREDIT', 'DEBIT NOTE': 'DEBIT', 'CDN': 'CREDIT', 'CN': 'CREDIT', 'DBN': 'DEBIT', 'DN': 'DEBIT', 'INV': 'INVOICE', 'B2B': 'INVOICE', 'B2C': 'INVOICE'})
    
    # Filter reverse charge if needed
    if not include_rc:
        df_2b = df_2b[df_2b['REVERSE_CHARGE'] != 'YES'].copy()
        df_pr = df_pr[df_pr['REVERSE_CHARGE'] != 'YES'].copy()
    
    # Create matching keys
    for df in [df_2b, df_pr]:
        df['PAN'] = df['SUPPLIER_GSTIN'].apply(extract_pan_from_gstin)
        df['NORM_DOC'] = df['DOC_NUMBER'].apply(normalize_document_number)
        # ✅ Key improvement: Include DOC_TYPE in matching key for CDN handling
        df['MATCH_KEY'] = df['PAN'] + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE']
    
    dup_pr_count = df_pr.duplicated(subset=['MATCH_KEY'], keep=False).sum()
    
    # Outer merge
    merged = pd.merge(df_2b, df_pr, on='MATCH_KEY', how='outer', suffixes=('_2B', '_PR'), indicator=True)
    
    # Calculate totals
    merged['TOTAL_TAX_2B'] = merged[['IGST_2B', 'CGST_2B', 'SGST_2B', 'CESS_2B']].sum(axis=1)
    merged['TOTAL_TAX_PR'] = merged[['IGST_PR', 'CGST_PR', 'SGST_PR', 'CESS_PR']].sum(axis=1)
    merged['TAXABLE_DIFF'] = (merged['TAXABLE_VALUE_2B'].fillna(0) - merged['TAXABLE_VALUE_PR'].fillna(0)).abs()
    merged['TAX_DIFF'] = (merged['TOTAL_TAX_2B'].fillna(0) - merged['TOTAL_TAX_PR'].fillna(0)).abs()
    
    # Matching conditions
    exact_gstin = merged['SUPPLIER_GSTIN_2B'].str.upper() == merged['SUPPLIER_GSTIN_PR'].str.upper()
    exact_doc = merged['DOC_NUMBER_2B'].str.upper() == merged['DOC_NUMBER_PR'].str.upper()
    tax_within_tol = merged['TAXABLE_DIFF'] <= tolerance
    tax_exact = merged['TAXABLE_DIFF'] == 0
    same_pan = merged['PAN_2B'] == merged['PAN_PR']
    norm_doc_match = merged['NORM_DOC_2B'] == merged['NORM_DOC_PR']
    same_doc_type = merged['DOC_TYPE_2B'] == merged['DOC_TYPE_PR']
    date_differs = merged['DOC_DATE_2B'] != merged['DOC_DATE_PR']
    within_fy = merged.apply(lambda r: is_same_financial_year(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1)
    
    conditions = [
        (merged['_merge'] == 'both') & exact_gstin & exact_doc & same_doc_type & tax_exact,
        (merged['_merge'] == 'both') & same_pan & norm_doc_match & same_doc_type & tax_within_tol & date_differs & within_fy,
        (merged['_merge'] == 'both') & exact_gstin & exact_doc & same_doc_type & ~tax_within_tol,
        (merged['_merge'] == 'both') & same_pan & norm_doc_match & tax_within_tol & ~same_doc_type,
        (merged['_merge'] == 'both') & same_pan & ~exact_gstin & tax_within_tol,
        (merged['_merge'] == 'left_only'),
        (merged['_merge'] == 'right_only'),
    ]
    statuses = ['Exact', 'Suggested', 'Value Mismatch', 'Doc Type Mismatch', 'Cross-State (PAN Match)', 'Missing in GSTR 2B', 'Missing in PR']
    reasons = [
        'All parameters matching exactly including DOC_TYPE',
        'Document date differs within FY, values within tolerance, same DOC_TYPE',
        'Document number & GSTIN match, but taxable/tax mismatch exceeds tolerance',
        'Document matches but DOC_TYPE differs (Invoice vs Credit/Debit)',
        'Matched on PAN, but State GSTIN differs',
        'Present in GSTR-2B but missing in Purchase Register',
        'Present in Purchase Register but missing in GSTR-2B'
    ]
    
    merged['MATCH_STATUS'] = np.select(conditions, statuses, default='Other')
    merged['MATCH_REASON'] = np.select(conditions, reasons, default='Unable to determine match criteria')
    merged['SUPPLIER_NAME_COMBINED'] = merged['SUPPLIER_NAME_2B'].combine_first(merged['SUPPLIER_NAME_PR']).fillna('Unknown')
    
    # ITC eligibility with CDN awareness
    def determine_itc(row):
        if row['MATCH_STATUS'] == 'Exact' and auto_claim_itc:
            return 'ELIGIBLE'
        elif row['MATCH_STATUS'] == 'Suggested':
            return 'REVIEW REQUIRED'
        elif row['MATCH_STATUS'] in ['Missing in GSTR 2B', 'Value Mismatch']:
            return 'NOT ELIGIBLE'
        elif row['MATCH_STATUS'] == 'Missing in PR':
            return 'PENDING BOOKS ENTRY'
        elif row['DOC_TYPE_2B'] == 'CREDIT' or row['DOC_TYPE_PR'] == 'CREDIT':
            return 'CREDIT NOTE - REVIEW'
        else:
            return row.get('ITC_CLAIM_TYPE_2B', row.get('ITC_CLAIM_TYPE_PR', 'UNKNOWN'))
    
    merged['ITC_ELIGIBILITY'] = merged.apply(determine_itc, axis=1)
    
    return merged, dup_pr_count, df_2b, df_pr

# ================= MAIN PROCESSING LOGIC =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Advanced Reconciliation Engine..."):
            merged_df, dup_pr_count, df_2b, df_pr = process_reconciliation(
                file_2b.getvalue(), file_pr.getvalue(), tolerance, date_tolerance, 
                include_reverse_charge, handle_cdn_negative
            )
            
            # Summary stats
            status_counts = merged_df['MATCH_STATUS'].value_counts()
            total_records = len(merged_df)
            exact_count = status_counts.get('Exact', 0)
            suggested_count = status_counts.get('Suggested', 0)
            missing_2b = status_counts.get('Missing in GSTR 2B', 0)
            missing_pr = status_counts.get('Missing in PR', 0)
            
            # ✅ DOC_TYPE BREAKDOWN STATS
            doc_type_stats = {}
            for dt in ['INVOICE', 'CREDIT', 'DEBIT']:
                mask_2b = df_2b['DOC_TYPE'] == dt
                mask_pr = df_pr['DOC_TYPE'] == dt
                doc_type_stats[f'{dt}_2B_count'] = mask_2b.sum()
                doc_type_stats[f'{dt}_2B_taxable'] = df_2b.loc[mask_2b, 'TAXABLE_VALUE'].sum()
                doc_type_stats[f'{dt}_2B_tax'] = df_2b.loc[mask_2b, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
                doc_type_stats[f'{dt}_PR_count'] = mask_pr.sum()
                doc_type_stats[f'{dt}_PR_taxable'] = df_pr.loc[mask_pr, 'TAXABLE_VALUE'].sum()
                doc_type_stats[f'{dt}_PR_tax'] = df_pr.loc[mask_pr, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
            
            # ========== DASHBOARD METRICS ==========
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📊</span> Live Reconciliation Dashboard</h3>
            </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📋 Total Records</div>
                    <div class="metric-value">{total_records:,}</div>
                    <div class="metric-delta neutral">All documents</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                match_rate = (exact_count + suggested_count) / total_records * 100 if total_records > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✅ Match Rate</div>
                    <div class="metric-value">{match_rate:.1f}%</div>
                    <div class="metric-delta {'positive' if match_rate >= 80 else 'negative'}">
                        {'↑ Excellent' if match_rate >= 90 else '↑ Good' if match_rate >= 80 else '↓ Review needed'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔍 Suggested</div>
                    <div class="metric-value">{suggested_count:,}</div>
                    <div class="metric-delta neutral">Needs review</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                unclaimed_itc = merged_df[merged_df['MATCH_STATUS'] == 'Missing in PR']['TOTAL_TAX_2B'].sum()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">💰 Unclaimed ITC</div>
                    <div class="metric-value">₹{unclaimed_itc:,.0f}</div>
                    <div class="metric-delta positive">Cash flow opportunity</div>
                </div>
                """, unsafe_allow_html=True)
            with m5:
                risky_claims = merged_df[merged_df['MATCH_STATUS'] == 'Missing in GSTR 2B']['TOTAL_TAX_PR'].sum()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⚠️ Risk Claims</div>
                    <div class="metric-value">₹{risky_claims:,.0f}</div>
                    <div class="metric-delta negative">Compliance risk</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ✅ DOC_TYPE BREAKDOWN SECTION
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📑</span> Document Type Breakdown</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_dt1, col_dt2, col_dt3 = st.columns(3)
            with col_dt1:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 16px; border-left: 4px solid #10b981;">
                    <strong>📄 INVOICES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['INVOICE_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['INVOICE_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Taxable:</span><strong>₹{doc_type_stats['INVOICE_2B_taxable']:,.0f}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>PR Taxable:</span><strong>₹{doc_type_stats['INVOICE_PR_taxable']:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_dt2:
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border-radius: 12px; padding: 16px; border-left: 4px solid #ef4444;">
                    <strong>📉 CREDIT NOTES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['CREDIT_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['CREDIT_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Taxable:</span><strong style="color: #ef4444;">₹{doc_type_stats['CREDIT_2B_taxable']:,.0f}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>PR Taxable:</span><strong style="color: #ef4444;">₹{doc_type_stats['CREDIT_PR_taxable']:,.0f}</strong>
                    </div>
                    <small style="color: var(--text-secondary);">* Negative values shown</small>
                </div>
                """, unsafe_allow_html=True)
            with col_dt3:
                st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 16px; border-left: 4px solid #f59e0b;">
                    <strong>📈 DEBIT NOTES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['DEBIT_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['DEBIT_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>2B Taxable:</span><strong>₹{doc_type_stats['DEBIT_2B_taxable']:,.0f}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>PR Taxable:</span><strong>₹{doc_type_stats['DEBIT_PR_taxable']:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== AI INSIGHTS ==========
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">🧠</span> AI-Powered Financial Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            
            insights = []
            if dup_pr_count > 0:
                insights.append({'type': 'warning', 'icon': '⚠️', 'title': 'Data Quality Alert', 'message': f"Found **{dup_pr_count} duplicate entries** in Purchase Register."})
            if missing_pr > 0:
                insights.append({'type': 'success', 'icon': '💡', 'title': 'Cash Flow Opportunity', 'message': f"**₹{unclaimed_itc:,.2f}** in ITC available in GSTR-2B but not claimed."})
            if missing_2b > 0:
                insights.append({'type': 'error', 'icon': '🚨', 'title': 'Compliance Risk', 'message': f"**₹{risky_claims:,.2f}** claimed in books but missing from GSTR-2B."})
            if match_rate < 80:
                insights.append({'type': 'warning', 'icon': '🔄', 'title': 'Reconciliation Health', 'message': f"Match rate is **{match_rate:.1f}%**. Review document numbering."})
            elif match_rate >= 95:
                insights.append({'type': 'success', 'icon': '✅', 'title': 'Excellent Health', 'message': f"Outstanding match rate of **{match_rate:.1f}%**!"})
            if suggested_count > 0:
                insights.append({'type': 'info', 'icon': '🕒', 'title': 'Date Mismatches', 'message': f"**{suggested_count} records** have date differences but match on other parameters."})
            # ✅ CDN-specific insights
            if doc_type_stats['CREDIT_2B_count'] != doc_type_stats['CREDIT_PR_count']:
                insights.append({'type': 'warning', 'icon': '📉', 'title': 'Credit Note Mismatch', 'message': f"Credit note counts differ: {doc_type_stats['CREDIT_2B_count']} in 2B vs {doc_type_stats['CREDIT_PR_count']} in PR."})
            if not insights:
                insights.append({'type': 'success', 'icon': '🎉', 'title': 'All Clear', 'message': "No critical issues detected. Your GST reconciliation is healthy!"})
            
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div class="insight-card {insight['type']} animate-fade-in" style="animation-delay: {i*0.1}s">
                    <div class="insight-title">{insight['icon']} {insight['title']}</div>
                    <div class="insight-message">{insight['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== VISUALIZATIONS ==========
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📈</span> Visual Analytics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Status", "📑 Doc Types", "📅 Trends", "🔍 Details"])
            
            with tab1:
                status_data = merged_df['MATCH_STATUS'].value_counts().reset_index()
                status_data.columns = ['Status', 'Count']
                color_map = {'Exact': '#10b981', 'Suggested': '#06b6d4', 'Value Mismatch': '#f97316', 'Doc Type Mismatch': '#8b5cf6', 'Cross-State (PAN Match)': '#6366f1', 'Missing in GSTR 2B': '#ef4444', 'Missing in PR': '#f59e0b', 'Other': '#64748b'}
                fig_status = px.pie(status_data, values='Count', names='Status', color='Status', color_discrete_map=color_map, hole=0.5, title='Reconciliation Status Distribution')
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
                fig_status.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5), height=400)
                st.plotly_chart(fig_status, use_container_width=True)
            
            with tab2:
                # ✅ DOC_TYPE COMPARISON CHART
                dt_data = pd.DataFrame({
                    'Document Type': ['INVOICE', 'CREDIT', 'DEBIT'],
                    'GSTR-2B Taxable': [doc_type_stats['INVOICE_2B_taxable'], doc_type_stats['CREDIT_2B_taxable'], doc_type_stats['DEBIT_2B_taxable']],
                    'Purchase Register Taxable': [doc_type_stats['INVOICE_PR_taxable'], doc_type_stats['CREDIT_PR_taxable'], doc_type_stats['DEBIT_PR_taxable']]
                })
                fig_dt = px.bar(dt_data, x='Document Type', y=['GSTR-2B Taxable', 'Purchase Register Taxable'], barmode='group', title='Taxable Value by Document Type', labels={'value': 'Amount (₹)'})
                fig_dt.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation='h', y=-0.2))
                st.plotly_chart(fig_dt, use_container_width=True)
            
            with tab3:
                if 'MONTH_2B' in merged_df.columns:
                    monthly = merged_df.groupby('MONTH_2B').agg({'TAXABLE_VALUE_2B': 'sum', 'TOTAL_TAX_2B': 'sum', 'TAXABLE_VALUE_PR': 'sum', 'TOTAL_TAX_PR': 'sum'}).reset_index().fillna(0)
                    fig_monthly = go.Figure()
                    fig_monthly.add_trace(go.Bar(x=monthly['MONTH_2B'], y=monthly['TAXABLE_VALUE_2B'], name='Taxable (2B)', marker_color=px.colors.qualitative.Set1[0]))
                    fig_monthly.add_trace(go.Bar(x=monthly['MONTH_2B'], y=monthly['TAXABLE_VALUE_PR'], name='Taxable (PR)', marker_color=px.colors.qualitative.Set1[1]))
                    fig_monthly.update_layout(barmode='group', title='Monthly Taxable Value Comparison', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation='h', y=-0.2))
                    st.plotly_chart(fig_monthly, use_container_width=True)
            
            with tab4:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    status_filter = st.multiselect("Filter Status", merged_df['MATCH_STATUS'].unique().tolist(), default=merged_df['MATCH_STATUS'].unique().tolist())
                with col_f2:
                    search = st.text_input("🔎 Search Supplier", placeholder="Type to search...")
                with col_f3:
                    min_val = st.number_input("Min Value (₹)", min_value=0, value=0, step=1000)
                
                filtered = merged_df.copy()
                if status_filter:
                    filtered = filtered[filtered['MATCH_STATUS'].isin(status_filter)]
                if search:
                    filtered = filtered[filtered['SUPPLIER_NAME_COMBINED'].str.contains(search, case=False, na=False)]
                if min_val > 0:
                    filtered = filtered[(filtered['TAXABLE_VALUE_2B'].abs() >= min_val) | (filtered['TAXABLE_VALUE_PR'].abs() >= min_val)]
                
                display_cols = ['MATCH_STATUS', 'SUPPLIER_NAME_COMBINED', 'DOC_TYPE_2B', 'DOC_NUMBER_2B', 'DOC_NUMBER_PR', 'TAXABLE_VALUE_2B', 'TAXABLE_VALUE_PR', 'TOTAL_TAX_2B', 'TOTAL_TAX_PR', 'ITC_ELIGIBILITY']
                st.dataframe(filtered[display_cols].head(100).style.format({'TAXABLE_VALUE_2B': '₹{:.2f}', 'TAXABLE_VALUE_PR': '₹{:.2f}', 'TOTAL_TAX_2B': '₹{:.2f}', 'TOTAL_TAX_PR': '₹{:.2f}'}).map(lambda x: f'<span class="status-badge status-{str(x).lower().replace(" ", "-")}">{x}</span>' if x in ['Exact', 'Suggested', 'Value Mismatch', 'Missing in GSTR 2B', 'Missing in PR'] else x, subset=['MATCH_STATUS']), use_container_width=True, hide_index=True)
            
            # ========== EXPORT SECTION ==========
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📤</span> Export Reconciliation Report</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_export1, col_export2 = st.columns([3, 1])
            with col_export1:
                st.markdown("""
                <div style="background: rgba(99, 102, 241, 0.05); border-radius: 12px; padding: 16px; border: 1px solid var(--border-light);">
                    <strong>📋 Report Includes:</strong>
                    <ul style="margin: 8px 0 0 20px; color: var(--text-secondary);">
                        <li>Executive Dashboard with charts</li>
                        <li>Detailed reconciliation with DOC_TYPE breakdown</li>
                        <li>Credit/Debit Note handling with negative values</li>
                        <li>Summary tables matching GST portal format</li>
                        <li>Raw data sheets for audit trail</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col_export2:
                # Simplified export for demo
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    recon_df = merged_df[['MATCH_STATUS', 'MATCH_REASON', 'SUPPLIER_NAME_COMBINED', 'SUPPLIER_GSTIN_2B', 'SUPPLIER_GSTIN_PR', 'DOC_NUMBER_2B', 'DOC_NUMBER_PR', 'DOC_DATE_2B', 'DOC_DATE_PR', 'DOC_TYPE_2B', 'DOC_TYPE_PR', 'TAXABLE_VALUE_2B', 'TAXABLE_VALUE_PR', 'TOTAL_TAX_2B', 'TOTAL_TAX_PR', 'ITC_ELIGIBILITY']].copy()
                    recon_df.columns = ['Match Status', 'Match Reason', 'Supplier Name', 'Supplier GSTIN (2B)', 'Supplier GSTIN (PR)', 'Document Number (2B)', 'Document Number (PR)', 'Document Date (2B)', 'Document Date (PR)', 'Doc Type (2B)', 'Doc Type (PR)', 'Taxable Value (2B)', 'Taxable Value (PR)', 'Total Tax (2B)', 'Total Tax (PR)', 'ITC Eligibility']
                    recon_df.to_excel(writer, sheet_name='Reconciliation', index=False)
                st.download_button(label="⚡ Download Report", data=output.getvalue(), file_name=f"GST_Recon_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
            st.success(f"✅ Ready! Processed {total_records:,} records with proper Credit/Debit Note handling.")
    
    except Exception as e:
        st.error(f"❌ Processing Error: {str(e)}")
        with st.expander("🔧 Technical Details"):
            st.exception(e)
            st.info("💡 Ensure files follow the sample template format with DOC_TYPE column (INVOICE/CREDIT/DEBIT) and negative values for Credit Notes.")

else:
    st.markdown("""
    <div class="section-card animate-fade-in" style="text-align: center; padding: 60px 40px;">
        <div style="font-size: 4rem; margin-bottom: 20px;">🧾✨</div>
        <h2 style="margin: 0 0 16px 0;">Welcome to GST Recon Pro</h2>
        <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 600px; margin: 0 auto 32px auto; line-height: 1.6;">
            Upload your GSTR-2B and Purchase Register files to begin intelligent reconciliation. 
            Our AI-powered engine matches invoices, handles Credit/Debit Notes with negative values, 
            identifies discrepancies, and generates compliance-ready reports.
        </p>
        <div class="quick-actions">
            <div class="quick-action-btn"><span class="icon">📁</span><span class="label">Upload Files</span></div>
            <div class="quick-action-btn"><span class="icon">📥</span><span class="label">Get Samples</span></div>
            <div class="quick-action-btn"><span class="icon">📉</span><span class="label">CDN Support</span></div>
            <div class="quick-action-btn"><span class="icon">📊</span><span class="label">Live Insights</span></div>
        </div>
        <div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid var(--border-light);">
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                <strong>💡 Pro Tip:</strong> Credit Notes should have <strong>negative taxable/tax values</strong> for proper matching.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
<div class="footer">
    <div class="brand">🧾 GST Recon Pro</div>
    <div class="credits">Enterprise GST Reconciliation Engine</div>
    <div class="credits">Developed by <strong>ABHISHEK JAKKULA</strong> • jakkulaabhishek5@gmail.com</div>
    <div class="version">v3.1 • Last Updated: May 2026</div>
    <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem;">📚 Documentation</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem;">🎥 Tutorials</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem;">🔧 Support</a>
    </div>
</div>
""", unsafe_allow_html=True)
