# ============================================================================
# ✨ GST Recon Pro v6.0 - Enterprise GST Reconciliation Engine
# ============================================================================
# Author: Abhishek Jakkula
# Email: jakkulaabhishek5@gmail.com
# Version: 6.0.0 (Professional Format with Subtotals)
# Last Updated: May 2026
# License: Proprietary - Enterprise Edition
# ============================================================================
# 
# KEY FEATURES IN v6.0:
# ✅ Professional reconciliation sheet matching uploaded format
# ✅ All 30+ columns as per your requirements
# ✅ Subtotals at top of reconciliation sheet
# ✅ Enhanced Excel formatting with color coding
# ✅ Summary dashboard with key metrics
# ✅ Advanced filtering and search capabilities
# ✅ Multi-sheet export with proper formatting
# ✅ Automated data validation
# ✅ Comprehensive audit trail
# ✅ Performance optimized for large datasets
# ============================================================================

# ==================== IMPORTS ====================
import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import warnings
import hashlib
import json
import base64
import logging
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Callable
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xlsxwriter
from io import BytesIO
from difflib import SequenceMatcher
import os

# Suppress warnings
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==================== CONFIG & UI SETUP ====================
st.set_page_config(
    page_title="✨ GST Recon Pro v6.0", 
    page_icon="🧾",
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:jakkulaabhishek5@gmail.com',
        'Report a bug': "https://github.com/abhishekjakkula/gst-recon-pro/issues",
        'About': "# GST Recon Pro v6.0\nEnterprise GST Reconciliation Engine\n\n© 2026 Abhishek Jakkula. All rights reserved."
    }
)

# ==================== ENHANCED THEME-ADAPTIVE CSS ====================
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
        --transition: all 0.3s ease;
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
        scroll-behavior: smooth;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-light) 0%, #f1f5f9 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    [data-theme="dark"] .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: var(--shadow-lg);
        z-index: 999;
    }

    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
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
        font-size: 3.2rem !important;
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
        color: rgba(255,255,255,0.95);
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
        padding: 28px 24px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
        cursor: default;
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
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1;
        margin: 10px 0;
    }
    .metric-card .metric-label {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.9rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        margin-top: 10px;
    }
    .metric-delta.positive { background: rgba(16, 185, 129, 0.15); color: var(--success); }
    .metric-delta.negative { background: rgba(239, 68, 68, 0.15); color: var(--error); }
    .metric-delta.neutral { background: rgba(100, 116, 139, 0.15); color: var(--text-secondary); }

    .insight-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 22px 26px;
        margin-bottom: 16px;
        border-left: 5px solid var(--primary);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: var(--transition);
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
    .insight-card.info {
        border-left-color: var(--info);
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), transparent);
    }
    .insight-card .insight-title {
        font-weight: 700;
        font-size: 1.15rem;
        color: var(--text-primary);
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .insight-card .insight-message {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .section-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
    }
    .section-card h3 {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 24px;
        padding-bottom: 14px;
        border-bottom: 2px solid var(--border-light);
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.3rem;
    }
    .section-card h3 .icon { font-size: 1.5rem; }

    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        border-radius: var(--radius-md);
        padding: 14px 32px;
        font-weight: 600;
        border: none;
        transition: var(--transition);
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
        font-size: 1rem;
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
        padding: 14px 18px;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    [data-testid="stDataFrame"] td {
        padding: 12px 18px;
        border-bottom: 1px solid var(--border-light);
        font-size: 0.9rem;
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
        background: rgba(255,255,255,0.6);
        padding: 10px;
        border-radius: var(--radius-lg);
        backdrop-filter: blur(8px);
        border: 1px solid var(--border-light);
    }
    [data-theme="dark"] .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.6);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 14px 28px;
        font-weight: 600;
        transition: var(--transition);
        color: var(--text-secondary);
        font-size: 0.95rem;
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
        padding: 24px;
        margin: 20px 0;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
    }
    .progress-bar {
        height: 10px;
        background: var(--border-light);
        border-radius: 5px;
        overflow: hidden;
        margin: 12px 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: 5px;
        transition: width 0.3s ease;
    }

    .footer {
        text-align: center;
        padding: 36px 24px;
        margin-top: 60px;
        background: linear-gradient(135deg, var(--bg-card), var(--bg-light));
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        border-top: 1px solid var(--border-light);
    }
    .footer .brand {
        font-weight: 800;
        font-size: 1.3rem;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .footer .credits {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 10px 0;
    }
    .footer .version {
        display: inline-block;
        background: var(--border-light);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 16px;
    }

    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }
    .quick-action-btn {
        background: var(--bg-card);
        border: 2px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: var(--transition);
        text-decoration: none;
        color: var(--text-primary);
    }
    .quick-action-btn:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    .quick-action-btn .icon { font-size: 2rem; margin-bottom: 10px; display: block; }
    .quick-action-btn .label { font-weight: 600; font-size: 0.95rem; }

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
        bottom: 28px;
        right: 28px;
        z-index: 1000;
    }
    .theme-toggle button {
        background: var(--bg-card);
        border: 2px solid var(--border-light);
        border-radius: 50%;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        cursor: pointer;
        box-shadow: var(--shadow-lg);
        transition: var(--transition);
    }
    .theme-toggle button:hover {
        transform: scale(1.1);
        border-color: var(--primary);
    }

    .doc-type-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .doc-type-invoice { background: rgba(16, 185, 129, 0.15); color: #065f46; }
    .doc-type-credit { background: rgba(239, 68, 68, 0.15); color: #991b1b; }
    .doc-type-debit { background: rgba(245, 158, 11, 0.15); color: #92400e; }

    .df-exact { color: #065f46 !important; background-color: rgba(16, 185, 129, 0.1) !important; font-weight: 600 !important; }
    .df-suggested { color: #0e7490 !important; background-color: rgba(6, 182, 212, 0.1) !important; font-weight: 600 !important; }
    .df-value-mismatch { color: #92400e !important; background-color: rgba(245, 158, 11, 0.1) !important; font-weight: 600 !important; }
    .df-doc-type-mismatch { color: #7c3aed !important; background-color: rgba(139, 92, 246, 0.1) !important; font-weight: 600 !important; }
    .df-cross-state { color: #4f46e5 !important; background-color: rgba(99, 102, 241, 0.1) !important; font-weight: 600 !important; }
    .df-missing-2b { color: #991b1b !important; background-color: rgba(239, 68, 68, 0.1) !important; font-weight: 600 !important; }
    .df-missing-pr { color: #5b21b6 !important; background-color: rgba(139, 92, 246, 0.1) !important; font-weight: 600 !important; }

    @media (max-width: 768px) {
        .main-header h1 { font-size: 2.2rem !important; }
        .main-header .subtitle { font-size: 1rem; }
        .metric-card .metric-value { font-size: 2rem; }
        .section-card { padding: 24px; }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .loading { animation: pulse 1.5s ease-in-out infinite; }

    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    }
    .toast.success { background: var(--success); color: white; }
    .toast.error { background: var(--error); color: white; }
    .toast.warning { background: var(--warning); color: #1f2937; }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .summary-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: var(--radius-lg);
        padding: 24px;
        color: white;
        margin: 16px 0;
        box-shadow: var(--shadow-lg);
    }
    .summary-box h4 {
        margin: 0 0 16px 0;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
    }
    .summary-item {
        background: rgba(255,255,255,0.1);
        padding: 16px;
        border-radius: var(--radius-md);
        backdrop-filter: blur(10px);
    }
    .summary-item .label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 4px;
    }
    .summary-item .value {
        font-size: 1.5rem;
        font-weight: 700;
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
    if (window.Streamlit) {
        window.Streamlit.setComponentValue(newTheme);
    }
}
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        toggleTheme();
    }
});
</script>
""", unsafe_allow_html=True)

# ==================== THEME TOGGLE BUTTON ====================
st.markdown("""
<div class="theme-toggle">
    <button onclick="toggleTheme()" title="Toggle Dark/Light Mode (Ctrl+T)">🌓</button>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR - ENHANCED ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 24px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 28px;">
        <div style="font-size: 3rem; margin-bottom: 10px;">🧾</div>
        <h3 style="margin: 0; color: #fff; font-size: 1.4rem;">GST Recon Pro</h3>
        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.9rem;">v6.0 • Enterprise Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚡ Quick Actions")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📥 Load Sample", use_container_width=True, key="btn_load_sample"):
            st.session_state.load_sample = True
            st.rerun()
    with col_q2:
        if st.button("🔄 Reset", use_container_width=True, key="btn_reset"):
            keys_to_clear = [k for k in st.session_state.keys() if 'upload' in k or 'file' in k or 'processed' in k]
            for key in keys_to_clear:
                del st.session_state[key]
            st.success("✅ Session reset successfully!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")
    
    with st.expander("🎯 Matching Parameters", expanded=True):
        tolerance = st.number_input("Tax/Taxable Tolerance (₹)", min_value=0, max_value=100000, value=20, step=1, 
                                   help="Maximum allowed difference in taxable/tax values for matching")
        date_tolerance = st.number_input("Date Tolerance (Days)", min_value=0, max_value=365, value=7, step=1, 
                                        help="Maximum date difference for suggested matches")
        fuzzy_threshold = st.slider("Fuzzy Name Match Threshold (%)", min_value=70, max_value=100, value=85, step=5,
                                   help="Similarity percentage for fuzzy supplier name matching")
    
    with st.expander("📋 Processing Options"):
        include_reverse_charge = st.checkbox("Include Reverse Charge", value=True)
        auto_claim_itc = st.checkbox("Auto-claim ITC for Exact Matches", value=True)
        fuzzy_doc_matching = st.checkbox("Enable Fuzzy Document Matching", value=True)
        handle_cdn_negative = st.checkbox("Treat Credit Notes as Negative Values", value=True, 
                                         help="Credit notes will have negative taxable/tax values for proper matching")
        validate_gstin = st.checkbox("Validate GSTIN Format", value=True)
        strict_financial_year = st.checkbox("Strict Financial Year Matching", value=False,
                                           help="Only match documents within same financial year")
    
    with st.expander("📤 Export Preferences"):
        include_charts = st.checkbox("Include Charts in Report", value=True)
        include_raw_data = st.checkbox("Include Raw Data Sheets", value=True)
        max_rows = st.number_input("Max Excel Rows", min_value=1000, max_value=500000, value=50000, step=1000)
        add_dropdown_validation = st.checkbox("Add DOC_TYPE Dropdown in Excel", value=True,
                                             help="Add data validation dropdown for DOC_TYPE column")
        export_format = st.selectbox("Primary Export Format", ["Excel (.xlsx)", "CSV (.csv)", "Both"], index=0)
        include_subtotals = st.checkbox("Include Subtotals in Export", value=True,
                                       help="Add subtotal rows for each match status")
    
    st.markdown("---")
    with st.expander("❓ Help & Documentation"):
        st.markdown("""
        **📚 Quick Start Guide**
        1. Upload GSTR-2B & Purchase Register files (Excel format)
        2. Configure matching tolerance in sidebar settings
        3. Review dashboard insights & interactive charts
        4. Export comprehensive reconciliation report
        
        **🔧 Supported Formats**
        - DOC_TYPE: INVOICE, CREDIT, DEBIT (case-insensitive)
        - Month: JANUARY-25, FEBRUARY-25, etc.
        - Dates: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY
        - Values: Credit Notes should have NEGATIVE values
        
        **🎯 Matching Logic**
        - Exact: GSTIN + Doc No + Doc Type + Values match exactly
        - Suggested: PAN + Normalized Doc No + Values within tolerance
        - Value Mismatch: Document matches but amounts differ beyond tolerance
        - Missing: Document present in one file but not the other
        
        **💡 Pro Tips**
        • Use sample templates for correct column structure
        • Ensure Credit Notes have negative taxable/tax values
        • Standardize document numbering across systems
        • Review "Suggested" matches manually for accuracy
        • Use fuzzy matching for supplier name variations
        
        **🔐 Support**
        - Email: jakkulaabhishek5@gmail.com
        - Response Time: < 24 hours (Business Days)
        - GitHub: github.com/abhishekjakkula/gst-recon-pro
        """)
    
    st.markdown("---")
    st.markdown("### 🟢 System Status")
    
    health_status = "✅ All Systems Operational"
    health_color = "#10b981"
    
    try:
        pd_version = pd.__version__
        import plotly
        plotly_version = plotly.__version__
    except Exception as e:
        health_status = "⚠️ Dependency Issue"
        health_color = "#f59e0b"
        logger.warning(f"System health check failed: {e}")
    
    st.markdown(f"""
    <div style="font-size: 0.9rem; color: #94a3b8;">
        <div style="display: flex; justify-content: space-between; margin: 6px 0;">
            <span>Engine:</span><span style="color: {health_color};">● {health_status}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 6px 0;">
            <span>Matching AI:</span><span style="color: #10b981;">● Active</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 6px 0;">
            <span>Export Service:</span><span style="color: #10b981;">● Ready</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 6px 0;">
            <span>Pandas:</span><span>{pd_version}</span>
        </div>
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
            <small>Session ID: {hash(str(datetime.now())) % 10000:04d}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== HEADER SECTION ====================
st.markdown("""
<div class="main-header animate-fade-in">
    <h1>✨ GST Recon Pro v6.0</h1>
    <p class="subtitle">
        AI-Powered GST Reconciliation • Match GSTR-2B with Purchase Register • 
        Real-time Insights • Compliance-Ready Reports • Credit/Debit Note Support • 
        Enterprise-Grade Security & Performance • Professional Format Export
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def get_month_format(month_str: str) -> str:
    """Convert month string to standardized format like JANUARY-25, FEBRUARY-25"""
    if pd.isna(month_str) or str(month_str).strip() == "":
        return "Unknown"
    
    try:
        month_str = str(month_str).strip().upper()
        
        if '-' in month_str and len(month_str.split('-')[0]) > 3:
            return month_str
        
        if '-' in month_str and len(month_str) == 7:
            parts = month_str.split('-')
            if parts[0].isdigit() and parts[1].isdigit():
                year, month_num = int(parts[0]), int(parts[1])
                month_name = datetime(year, month_num, 1).strftime('%B').upper()
                year_short = str(year)[-2:]
                return f"{month_name}-{year_short}"
        
        if '-' in month_str:
            parts = month_str.split('-')
            if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
                month_num, year = int(parts[0]), int(parts[1])
                if 1 <= month_num <= 12:
                    month_name = datetime(year, month_num, 1).strftime('%B').upper()
                    year_short = str(year)[-2:]
                    return f"{month_name}-{year_short}"
        
        for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(month_str, fmt)
                month_name = dt.strftime('%B').upper()
                year_short = str(dt.year)[-2:]
                return f"{month_name}-{year_short}"
            except:
                continue
        
        return month_str
    except Exception as e:
        logger.warning(f"Month format conversion failed for '{month_str}': {e}")
        return str(month_str).upper().strip() or "Unknown"


def normalize_document_number(doc_num: str) -> str:
    """Normalize document number for matching - remove special chars, convert to uppercase"""
    if pd.isna(doc_num) or str(doc_num).strip() == "":
        return "UNKNOWN"
    normalized = re.sub(r'[^A-Z0-9]', '', str(doc_num).upper().strip())
    return normalized.lstrip('0') or "0"


def extract_pan_from_gstin(gstin: str) -> str:
    """Extract PAN from GSTIN (characters 3-12)"""
    if pd.isna(gstin) or len(str(gstin).strip()) < 15:
        return "UNKNOWN"
    gstin_str = str(gstin).strip().upper()
    if len(gstin_str) >= 12:
        return gstin_str[2:12]
    return "UNKNOWN"


def get_document_type(taxable_value: float, doc_type_col: str = None) -> str:
    """Determine DOC_TYPE from value sign or existing column with intelligent fallback"""
    if doc_type_col and pd.notna(doc_type_col):
        dt = str(doc_type_col).upper().strip()
        if dt in ['CREDIT', 'CREDIT NOTE', 'CDN', 'CN', 'CR', 'C']:
            return 'CREDIT'
        elif dt in ['DEBIT', 'DEBIT NOTE', 'DBN', 'DN', 'DB', 'D']:
            return 'DEBIT'
        elif dt in ['INVOICE', 'INV', 'B2B', 'B2C', 'I', 'IN']:
            return 'INVOICE'
    
    try:
        val = float(taxable_value)
        if val < -0.01:
            return 'CREDIT'
        elif val > 0.01:
            return 'INVOICE'
        else:
            return 'DEBIT'
    except (ValueError, TypeError):
        return 'INVOICE'


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string with multiple format support"""
    if pd.isna(date_str) or str(date_str).strip() == "":
        return None
    
    date_str = str(date_str).strip()
    
    formats = [
        '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y',
        '%d-%b-%Y', '%d %b %Y', '%b %d, %Y',
        '%Y/%m/%d', '%d.%m.%Y', '%m.%d.%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    try:
        parsed = pd.to_datetime(date_str, errors='coerce')
        if pd.notna(parsed):
            return parsed.to_pydatetime()
    except:
        pass
    
    return None


def get_financial_year(date_obj: datetime) -> str:
    """Get financial year string like '2023-24' from date"""
    if date_obj is None:
        return "Unknown"
    if date_obj.month >= 4:
        return f"{date_obj.year}-{str(date_obj.year + 1)[-2:]}"
    return f"{date_obj.year - 1}-{str(date_obj.year)[-2:]}"


def is_same_financial_year(date1_str: str, date2_str: str) -> bool:
    """Check if two dates fall in same financial year"""
    d1, d2 = parse_date(date1_str), parse_date(date2_str)
    if d1 is None or d2 is None:
        return False
    return get_financial_year(d1) == get_financial_year(d2)


def calculate_date_difference(date1_str: str, date2_str: str) -> Optional[int]:
    """Calculate absolute difference in days between two dates"""
    d1, d2 = parse_date(date1_str), parse_date(date2_str)
    if d1 is None or d2 is None:
        return None
    return abs((d2 - d1).days)


def fuzzy_match_names(name1: str, name2: str, threshold: float = 85.0) -> bool:
    """Simple fuzzy matching for supplier names using string similarity"""
    if pd.isna(name1) or pd.isna(name2):
        return False
    
    n1 = str(name1).upper().strip()
    n2 = str(name2).upper().strip()
    
    if n1 == n2:
        return True
    
    for suffix in ['PVT LTD', 'PVT. LTD.', 'PRIVATE LIMITED', 'LTD', 'LIMITED', 'LLP', 'AND SONS', '& SONS']:
        n1 = re.sub(r'\b' + re.escape(suffix) + r'\b', '', n1).strip()
        n2 = re.sub(r'\b' + re.escape(suffix) + r'\b', '', n2).strip()
    
    ratio = SequenceMatcher(None, n1, n2).ratio() * 100
    return ratio >= threshold


def validate_gstin_format(gstin: str) -> bool:
    """Validate GSTIN format: 2 digits + 10 chars PAN + 1 digit + Z + 1 digit"""
    if pd.isna(gstin) or len(str(gstin).strip()) != 15:
        return False
    gstin = str(gstin).strip().upper()
    pattern = r'^[0-9]{2}[A-Z0-9]{10}[0-9]Z[A-Z0-9]{1}$'
    return bool(re.match(pattern, gstin))


def generate_file_hash(file_bytes: bytes) -> str:
    """Generate MD5 hash for file content tracking"""
    return hashlib.md5(file_bytes).hexdigest()


def get_status_css_class(status_value) -> str:
    """
    ✅ Returns proper CSS property string for pandas Styler
    This fixes the ValueError: Styles supplied as string must follow CSS rule formats
    
    Returns CSS properties like: "color: red; background: blue;"
    NOT class names like: "status-exact"
    """
    if pd.isna(status_value):
        return ''
    
    status_lower = str(status_value).lower().strip()
    
    # ✅ Map each status to actual CSS properties (not class names!)
    css_map = {
        'exact': 'color: #065f46; background-color: rgba(16, 185, 129, 0.15); font-weight: 600;',
        'suggested': 'color: #0e7490; background-color: rgba(6, 182, 212, 0.15); font-weight: 600;',
        'value mismatch': 'color: #92400e; background-color: rgba(245, 158, 11, 0.15); font-weight: 600;',
        'doc type mismatch': 'color: #7c3aed; background-color: rgba(139, 92, 246, 0.15); font-weight: 600;',
        'cross-state (pan match)': 'color: #4f46e5; background-color: rgba(99, 102, 241, 0.15); font-weight: 600;',
        'missing in gstr 2b': 'color: #991b1b; background-color: rgba(239, 68, 68, 0.15); font-weight: 600;',
        'missing in pr': 'color: #5b21b6; background-color: rgba(139, 92, 246, 0.15); font-weight: 600;',
        'other': 'color: #64748b; background-color: rgba(100, 116, 139, 0.1); font-weight: 500;',
    }
    
    return css_map.get(status_lower, '')


# ==================== ENHANCED SAMPLE TEMPLATE GENERATORS ====================

def generate_sample_2b_template() -> bytes:
    """Generate sample GSTR-2B with proper DOC_TYPE breakdown and negative CDN values"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "SECTION_NAME"
    ]
    
    sample_data = [
        # INVOICES - Exact Matches
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "JULY-23", "INVOICE", "NO", "B2B"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        
        # CREDIT NOTES (NEGATIVE VALUES) - Exact Matches
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "FEBRUARY-24", "CREDIT", "NO", "CDN"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "15-03-2024", "MARCH-24", "CREDIT", "NO", "CDN"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "10-01-2024", "JANUARY-24", "CREDIT", "NO", "CDN"],
        
        # DEBIT NOTES - Exact Matches
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "05-03-2024", "MARCH-24", "DEBIT", "NO", "B2B"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "20-02-2024", "FEBRUARY-24", "DEBIT", "NO", "B2B"],
        
        # SUGGESTED MATCHES (Date differs within tolerance)
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "03-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "07-07-2023", "JULY-23", "INVOICE", "NO", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "25-04-2023", "APRIL-23", "INVOICE", "NO", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "15-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        
        # MISSING IN PR (Present in 2B only)
        ["36AADCR6281N1ZT", "67186859-1D", 8579.40, 0, 772.11, 772.11, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "01-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36CKUPB7102C1ZF", "BEW/23-24/53", 3500.00, 0, 315.00, 315.00, "BALAJI ENGINEERING WORKS", "36ADXFS5154R1ZU", "29-09-2023", "SEPTEMBER-23", "INVOICE", "NO", "B2B"],
        ["36AAJCS4517L1ZZ", "362311I000806960", 11388.88, 0, 1025.00, 1025.00, "STAR HEALTH AND ALLIED INSURANCE COMPANY LIMITED", "36ADXFS5154R1ZU", "13-11-2023", "NOVEMBER-23", "INVOICE", "NO", "B2B"],
        
        # VALUE MISMATCH EXAMPLE
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4582.00, 0, 412.38, 412.38, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "JULY-23", "INVOICE", "NO", "B2B"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="GSTR_2B_Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["GSTR_2B_Data"]
        
        header_format = workbook.add_format({
            "bold": True, "bg_color": "#1e40af", "font_color": "white", 
            "border": 1, "align": "center", "valign": "vcenter"
        })
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:F', 14)
        worksheet.set_column('G:G', 35)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 14)
        worksheet.set_column('J:J', 14)
        worksheet.set_column('K:M', 14)
        
        worksheet.data_validation('K2:K1000', {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
    
    return output.getvalue()


def generate_sample_books_template() -> bytes:
    """Generate sample Purchase Register with proper DOC_TYPE and negative CDN values"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "ITC_CLAIM_TYPE", "PLACE_OF_SUPPLY", "SECTION_NAME"
    ]
    
    sample_data = [
        # INVOICES - Exact Matches
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "JULY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "JANUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "JANUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        
        # CREDIT NOTES (NEGATIVE VALUES) - Exact Matches
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "FEBRUARY-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "15-03-2024", "MARCH-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "10-01-2024", "JANUARY-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        
        # DEBIT NOTES - Exact Matches
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "05-03-2024", "MARCH-24", "DEBIT", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "20-02-2024", "FEBRUARY-24", "DEBIT", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        
        # SUGGESTED MATCHES (Date differs within tolerance)
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "01-06-2023", "JUNE-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "01-09-2023", "SEPTEMBER-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-02-2024", "FEBRUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        
        # MISSING IN 2B (Present in PR only)
        ["36AAGCE1603E1Z6", "EDT/SB/2223/013", 79200.00, 0, 4752.00, 4752.00, "EXIGENT DRILLING TECHNOLOGIES PRIVATE LIMITED", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BDJPM4292D2ZF", "106/22-23", 211868.00, 0, 19068.12, 19068.12, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BNDPM1159D1Z9", "160", 12015.00, 0, 1081.35, 1081.35, "SRI SAI DURGA PAINTS", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        
        # VALUE MISMATCH EXAMPLE (Different amounts)
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4600.00, 0, 414.00, 414.00, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "JULY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="Purchase_Register", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Purchase_Register"]
        
        header_format = workbook.add_format({
            "bold": True, "bg_color": "#1e40af", "font_color": "white", 
            "border": 1, "align": "center", "valign": "vcenter"
        })
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:F', 14)
        worksheet.set_column('G:G', 35)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 14)
        worksheet.set_column('J:J', 14)
        worksheet.set_column('K:O', 14)
        
        worksheet.data_validation('K2:K1000', {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
    
    return output.getvalue()

# ==================== FILE UPLOAD SECTION ====================
st.markdown("""
<div class="section-card animate-fade-in">
    <h3><span class="icon">📁</span> Upload Your Files</h3>
    <p style="color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6;">
        Select your GSTR-2B and Purchase Register files. Ensure DOC_TYPE column has: INVOICE, CREDIT, or DEBIT.
        <br><strong>💡 Credit Notes should have negative taxable/tax values for proper matching.</strong>
        <br><strong>📅 Month format: JANUARY-25, FEBRUARY-25, etc.</strong>
        <br><strong>✅ GSTIN format: 15 characters (e.g., 36AADCR6281N1ZT)</strong>
    </p>
""", unsafe_allow_html=True)

col_upload1, col_upload2, col_upload3 = st.columns([2, 2, 1])

with col_upload1:
    file_2b = st.file_uploader("📄 GSTR-2B File", type=['xlsx', 'xls'], key='upload_2b', label_visibility="collapsed")
    if file_2b:
        st.success(f"✓ {file_2b.name}")
        st.session_state.file_2b_hash = generate_file_hash(file_2b.getvalue())

with col_upload2:
    file_pr = st.file_uploader("📘 Purchase Register", type=['xlsx', 'xls'], key='upload_pr', label_visibility="collapsed")
    if file_pr:
        st.success(f"✓ {file_pr.name}")
        st.session_state.file_pr_hash = generate_file_hash(file_pr.getvalue())

with col_upload3:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 2B Sample",
            data=generate_sample_2b_template(),
            file_name="GSTR2B_Sample_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_2b_sample"
        )
    with col_d2:
        st.download_button(
            label="📘 PR Sample",
            data=generate_sample_books_template(),
            file_name="PurchaseRegister_Sample_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_pr_sample"
        )

st.markdown("</div>", unsafe_allow_html=True)

# ==================== MAIN PROCESSING FUNCTION ====================
@st.cache_data(show_spinner=False, ttl=3600)
def process_reconciliation(
    file_2b_bytes: bytes, 
    file_pr_bytes: bytes, 
    tolerance: float, 
    date_tol_days: int, 
    include_rc: bool, 
    handle_cdn_neg: bool,
    fuzzy_threshold: float,
    validate_gstin_flag: bool,
    strict_fy: bool
) -> Tuple[pd.DataFrame, int, pd.DataFrame, pd.DataFrame, Dict]:
    """
    Main reconciliation engine with enhanced Credit/Debit Note handling
    
    Returns:
        Tuple of (merged_df, dup_pr_count, df_2b, df_pr, stats_dict)
    """
    start_time = time.time()
    logger.info("Starting reconciliation process")
    
    try:
        # Load data
        df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
        df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
        logger.info(f"Loaded {len(df_2b)} records from 2B, {len(df_pr)} from PR")
        
        # Clean column names
        for df in [df_2b, df_pr]:
            df.columns = df.columns.str.replace('*', '', regex=False).str.strip().str.upper()
        
        # Standardize column names
        col_map = {
            'SUPPLIER GSTIN': 'SUPPLIER_GSTIN', 'DOCUMENT NUMBER': 'DOC_NUMBER',
            'TAXABLE VALUE': 'TAXABLE_VALUE', 'SUPPLIER NAME': 'SUPPLIER_NAME',
            'MY GSTIN': 'MY_GSTIN', 'DOCUMENT DATE': 'DOC_DATE', 'DOC_TYPE': 'DOC_TYPE',
            'REVERSE_CHARGE': 'REVERSE_CHARGE', 'ITC_CLAIM_TYPE': 'ITC_CLAIM_TYPE',
            'PLACE_OF_SUPPLY': 'PLACE_OF_SUPPLY', 'MONTH': 'MONTH', 'SECTION_NAME': 'SECTION_NAME'
        }
        for old, new in col_map.items():
            if old in df_2b.columns:
                df_2b[new] = df_2b[old]
            if old in df_pr.columns:
                df_pr[new] = df_pr[old]
        
        # Ensure required columns exist
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
            if 'SECTION_NAME' not in df.columns:
                df['SECTION_NAME'] = 'B2B'
        
        # Fill NaN and standardize data types
        for df in [df_2b, df_pr]:
            df['SUPPLIER_GSTIN'] = df['SUPPLIER_GSTIN'].fillna('UNKNOWN').astype(str).str.upper().str.strip()
            df['MY_GSTIN'] = df['MY_GSTIN'].fillna('').astype(str).str.upper().str.strip()
            df['SUPPLIER_NAME'] = df['SUPPLIER_NAME'].fillna('Unknown').astype(str).str.strip()
            df['DOC_NUMBER'] = df['DOC_NUMBER'].fillna('').astype(str).str.strip()
            df['DOC_DATE'] = df['DOC_DATE'].fillna('').astype(str).str.strip()
            df['REVERSE_CHARGE'] = df.get('REVERSE_CHARGE', pd.Series(['NO']*len(df))).fillna('NO').astype(str).str.upper().str.strip()
            df['MONTH'] = df.get('MONTH', pd.Series(['Unknown']*len(df))).fillna('Unknown').apply(get_month_format)
            df['ITC_CLAIM_TYPE'] = df.get('ITC_CLAIM_TYPE', pd.Series(['']*len(df))).fillna('').astype(str).str.strip().str.upper()
            df['PLACE_OF_SUPPLY'] = df.get('PLACE_OF_SUPPLY', pd.Series(['']*len(df))).fillna('').astype(str).str.strip().str.upper()
            df['SECTION_NAME'] = df.get('SECTION_NAME', pd.Series(['B2B']*len(df))).fillna('B2B').astype(str).str.strip().str.upper()
            
            # Convert numeric columns
            for col in ['TAXABLE_VALUE', 'IGST', 'CGST', 'SGST', 'CESS']:
                df[col] = pd.to_numeric(df.get(col, pd.Series([0]*len(df))), errors='coerce').fillna(0)
            
            # Derive/standardize DOC_TYPE
            if 'DOC_TYPE' not in df.columns or df['DOC_TYPE'].isna().any():
                df['DOC_TYPE'] = df.apply(lambda r: get_document_type(r['TAXABLE_VALUE'], r.get('DOC_TYPE')), axis=1)
            else:
                if handle_cdn_neg:
                    df.loc[(df['TAXABLE_VALUE'] < -0.01) & (~df['DOC_TYPE'].str.upper().isin(['CREDIT', 'CDN', 'CN'])), 'DOC_TYPE'] = 'CREDIT'
                    df.loc[(df['TAXABLE_VALUE'] > 0.01) & (df['DOC_TYPE'].str.upper().isin(['CREDIT', 'CDN', 'CN'])), 'DOC_TYPE'] = 'INVOICE'
                df['DOC_TYPE'] = df['DOC_TYPE'].apply(lambda x: str(x).upper().strip())
                df['DOC_TYPE'] = df['DOC_TYPE'].replace({
                    'CREDIT NOTE': 'CREDIT', 'DEBIT NOTE': 'DEBIT', 
                    'CDN': 'CREDIT', 'CN': 'CREDIT', 'CR': 'CREDIT',
                    'DBN': 'DEBIT', 'DN': 'DEBIT', 'DB': 'DEBIT',
                    'INV': 'INVOICE', 'B2B': 'INVOICE', 'B2C': 'INVOICE', 'I': 'INVOICE'
                })
            
            # Validate GSTIN if enabled
            if validate_gstin_flag:
                df['GSTIN_VALID'] = df['SUPPLIER_GSTIN'].apply(validate_gstin_format)
                invalid_count = (~df['GSTIN_VALID']).sum()
                if invalid_count > 0:
                    logger.warning(f"Found {invalid_count} invalid GSTINs in dataset")
        
        # Filter reverse charge if needed
        if not include_rc:
            df_2b = df_2b[df_2b['REVERSE_CHARGE'] != 'YES'].copy()
            df_pr = df_pr[df_pr['REVERSE_CHARGE'] != 'YES'].copy()
            logger.info("Filtered out reverse charge entries")
        
        # Create matching keys
        for df in [df_2b, df_pr]:
            df['PAN'] = df['SUPPLIER_GSTIN'].apply(extract_pan_from_gstin)
            df['NORM_DOC'] = df['DOC_NUMBER'].apply(normalize_document_number)
            df['MATCH_KEY'] = df['PAN'] + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE']
        
        # Check for duplicates in PR
        dup_pr_count = df_pr.duplicated(subset=['MATCH_KEY'], keep=False).sum()
        if dup_pr_count > 0:
            logger.warning(f"Found {dup_pr_count} duplicate MATCH_KEY entries in Purchase Register")
        
        # Perform outer merge on MATCH_KEY
        merged = pd.merge(df_2b, df_pr, on='MATCH_KEY', how='outer', suffixes=('_2B', '_PR'), indicator=True)
        logger.info(f"Merged dataset has {len(merged)} records")
        
        # Calculate totals
        tax_cols_2b = ['IGST_2B', 'CGST_2B', 'SGST_2B', 'CESS_2B']
        tax_cols_pr = ['IGST_PR', 'CGST_PR', 'SGST_PR', 'CESS_PR']
        merged['TOTAL_TAX_2B'] = merged[tax_cols_2b].sum(axis=1, skipna=True)
        merged['TOTAL_TAX_PR'] = merged[tax_cols_pr].sum(axis=1, skipna=True)
        merged['TAXABLE_DIFF'] = (merged['TAXABLE_VALUE_2B'].fillna(0) - merged['TAXABLE_VALUE_PR'].fillna(0)).abs()
        merged['TAX_DIFF'] = (merged['TOTAL_TAX_2B'].fillna(0) - merged['TOTAL_TAX_PR'].fillna(0)).abs()
        
        # Calculate Total Document Value
        merged['TOTAL_DOC_VALUE_2B'] = merged['TAXABLE_VALUE_2B'].fillna(0) + merged['TOTAL_TAX_2B'].fillna(0)
        merged['TOTAL_DOC_VALUE_PR'] = merged['TAXABLE_VALUE_PR'].fillna(0) + merged['TOTAL_TAX_PR'].fillna(0)
        
        # Build matching conditions
        exact_gstin = merged['SUPPLIER_GSTIN_2B'].str.upper() == merged['SUPPLIER_GSTIN_PR'].str.upper()
        exact_doc = merged['DOC_NUMBER_2B'].str.upper() == merged['DOC_NUMBER_PR'].str.upper()
        tax_within_tol = merged['TAXABLE_DIFF'] <= tolerance
        tax_exact = merged['TAXABLE_DIFF'] == 0
        same_pan = merged['PAN_2B'] == merged['PAN_PR']
        norm_doc_match = merged['NORM_DOC_2B'] == merged['NORM_DOC_PR']
        same_doc_type = merged['DOC_TYPE_2B'] == merged['DOC_TYPE_PR']
        date_differs = merged['DOC_DATE_2B'] != merged['DOC_DATE_PR']
        
        # Calculate date difference for suggested matches
        merged['DATE_DIFF_DAYS'] = merged.apply(
            lambda r: calculate_date_difference(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1
        )
        within_date_tol = merged['DATE_DIFF_DAYS'].notna() & (merged['DATE_DIFF_DAYS'] <= date_tol_days)
        
        # Financial year check if enabled
        if strict_fy:
            within_fy = merged.apply(lambda r: is_same_financial_year(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1)
        else:
            within_fy = pd.Series([True] * len(merged))
        
        # Fuzzy name matching for additional validation
        if fuzzy_threshold < 100:
            merged['NAME_FUZZY_MATCH'] = merged.apply(
                lambda r: fuzzy_match_names(r['SUPPLIER_NAME_2B'], r['SUPPLIER_NAME_PR'], fuzzy_threshold), axis=1
            )
        else:
            merged['NAME_FUZZY_MATCH'] = pd.Series([True] * len(merged))
        
        # Define matching logic with priority
        conditions = [
            (merged['_merge'] == 'both') & exact_gstin & exact_doc & same_doc_type & tax_exact,
            (merged['_merge'] == 'both') & same_pan & norm_doc_match & same_doc_type & 
            tax_within_tol & within_date_tol & within_fy & merged['NAME_FUZZY_MATCH'],
            (merged['_merge'] == 'both') & exact_gstin & exact_doc & same_doc_type & ~tax_within_tol,
            (merged['_merge'] == 'both') & same_pan & norm_doc_match & tax_within_tol & ~same_doc_type,
            (merged['_merge'] == 'both') & same_pan & ~exact_gstin & tax_within_tol,
            (merged['_merge'] == 'right_only'),
            (merged['_merge'] == 'left_only'),
        ]
        
        statuses = [
            'Exact', 'Suggested', 'Value Mismatch', 'Doc Type Mismatch', 
            'Cross-State (PAN Match)', 'Missing in PR', 'Missing in GSTR 2B'
        ]
        
        reasons = [
            'All parameters matching exactly including DOC_TYPE and values',
            'Document date differs within tolerance & FY, values within tolerance, same DOC_TYPE, name fuzzy match',
            'Document number & GSTIN match, but taxable/tax mismatch exceeds tolerance',
            'Document matches but DOC_TYPE differs (Invoice vs Credit/Debit Note)',
            'Matched on PAN, but State GSTIN differs (inter-state transaction)',
            'Present in Purchase Register but missing in GSTR-2B',
            'Present in GSTR-2B but missing in Purchase Register'
        ]
        
        merged['MATCH_STATUS'] = np.select(conditions, statuses, default='Other')
        merged['MATCH_REASON'] = np.select(conditions, reasons, default='Unable to determine match criteria')
        merged['SUPPLIER_NAME_COMBINED'] = merged['SUPPLIER_NAME_2B'].combine_first(merged['SUPPLIER_NAME_PR']).fillna('Unknown')
        
        # ITC eligibility determination
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
            elif row['MATCH_STATUS'] == 'Doc Type Mismatch':
                return 'DOC TYPE CONFLICT'
            else:
                return row.get('ITC_CLAIM_TYPE_2B', row.get('ITC_CLAIM_TYPE_PR', 'UNKNOWN'))
        
        merged['ITC_ELIGIBILITY'] = merged.apply(determine_itc, axis=1)
        
        # Calculate processing stats
        processing_time = time.time() - start_time
        stats = {
            'processing_time_sec': round(processing_time, 2),
            'total_2b_records': len(df_2b),
            'total_pr_records': len(df_pr),
            'merged_records': len(merged),
            'exact_matches': (merged['MATCH_STATUS'] == 'Exact').sum(),
            'suggested_matches': (merged['MATCH_STATUS'] == 'Suggested').sum(),
            'value_mismatches': (merged['MATCH_STATUS'] == 'Value Mismatch').sum(),
            'missing_in_2b': (merged['MATCH_STATUS'] == 'Missing in GSTR 2B').sum(),
            'missing_in_pr': (merged['MATCH_STATUS'] == 'Missing in PR').sum(),
            'duplicate_pr_keys': dup_pr_count,
            'invalid_gstins_2b': int(df_2b.get('GSTIN_VALID', pd.Series([True]*len(df_2b))).sum()) if validate_gstin_flag else 0,
            'invalid_gstins_pr': int(df_pr.get('GSTIN_VALID', pd.Series([True]*len(df_pr))).sum()) if validate_gstin_flag else 0,
        }
        
        logger.info(f"Reconciliation completed in {processing_time:.2f}s")
        return merged, dup_pr_count, df_2b, df_pr, stats
        
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}", exc_info=True)
        raise

# ==================== MAIN PROCESSING LOGIC ====================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Advanced Reconciliation Engine..."):
            current_2b_hash = generate_file_hash(file_2b.getvalue())
            current_pr_hash = generate_file_hash(file_pr.getvalue())
            
            merged_df, dup_pr_count, df_2b, df_pr, stats = process_reconciliation(
                file_2b.getvalue(), file_pr.getvalue(), 
                tolerance, date_tolerance, include_reverse_charge, 
                handle_cdn_negative, fuzzy_threshold, validate_gstin, strict_financial_year
            )
            
            st.session_state.processed_data = {
                'merged': merged_df,
                'df_2b': df_2b,
                'df_pr': df_pr,
                'stats': stats
            }
            
            # Calculate summary statistics
            status_counts = merged_df['MATCH_STATUS'].value_counts()
            total_records = len(merged_df)
            exact_count = int(status_counts.get('Exact', 0))
            suggested_count = int(status_counts.get('Suggested', 0))
            missing_2b = int(status_counts.get('Missing in GSTR 2B', 0))
            missing_pr = int(status_counts.get('Missing in PR', 0))
            
            # DOC_TYPE BREAKDOWN STATS
            doc_type_stats = {}
            for dt in ['INVOICE', 'CREDIT', 'DEBIT']:
                mask_2b = df_2b['DOC_TYPE'] == dt
                mask_pr = df_pr['DOC_TYPE'] == dt
                doc_type_stats[f'{dt}_2B_count'] = int(mask_2b.sum())
                doc_type_stats[f'{dt}_2B_taxable'] = float(df_2b.loc[mask_2b, 'TAXABLE_VALUE'].sum())
                doc_type_stats[f'{dt}_2B_tax'] = float(df_2b.loc[mask_2b, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum())
                doc_type_stats[f'{dt}_PR_count'] = int(mask_pr.sum())
                doc_type_stats[f'{dt}_PR_taxable'] = float(df_pr.loc[mask_pr, 'TAXABLE_VALUE'].sum())
                doc_type_stats[f'{dt}_PR_tax'] = float(df_pr.loc[mask_pr, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum())
            
            # Calculate financial metrics
            unclaimed_itc = float(merged_df[merged_df['MATCH_STATUS'] == 'Missing in PR']['TOTAL_TAX_2B'].sum())
            risky_claims = float(merged_df[merged_df['MATCH_STATUS'] == 'Missing in GSTR 2B']['TOTAL_TAX_PR'].sum())
            match_rate = (exact_count + suggested_count) / total_records * 100 if total_records > 0 else 0
            
            # ==================== DASHBOARD METRICS ====================
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
                delta_class = 'positive' if match_rate >= 80 else 'negative'
                delta_text = '↑ Excellent' if match_rate >= 90 else '↑ Good' if match_rate >= 80 else '↓ Review needed'
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✅ Match Rate</div>
                    <div class="metric-value">{match_rate:.1f}%</div>
                    <div class="metric-delta {delta_class}">{delta_text}</div>
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
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">💰 Unclaimed ITC</div>
                    <div class="metric-value">₹{unclaimed_itc:,.0f}</div>
                    <div class="metric-delta positive">Cash flow opportunity</div>
                </div>
                """, unsafe_allow_html=True)
            with m5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⚠️ Risk Claims</div>
                    <div class="metric-value">₹{risky_claims:,.0f}</div>
                    <div class="metric-delta negative">Compliance risk</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== DOC_TYPE BREAKDOWN SECTION ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📑</span> Document Type Breakdown</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_dt1, col_dt2, col_dt3 = st.columns(3)
            with col_dt1:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 18px; border-left: 4px solid #10b981;">
                    <strong style="font-size: 1.1rem;">📄 INVOICES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['INVOICE_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['INVOICE_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>2B Taxable:</span><strong>₹{doc_type_stats['INVOICE_2B_taxable']:,.0f}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>PR Taxable:</span><strong>₹{doc_type_stats['INVOICE_PR_taxable']:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_dt2:
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border-radius: 12px; padding: 18px; border-left: 4px solid #ef4444;">
                    <strong style="font-size: 1.1rem;">📉 CREDIT NOTES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['CREDIT_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['CREDIT_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
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
                <div style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 18px; border-left: 4px solid #f59e0b;">
                    <strong style="font-size: 1.1rem;">📈 DEBIT NOTES</strong>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>2B Count:</span><strong>{doc_type_stats['DEBIT_2B_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>PR Count:</span><strong>{doc_type_stats['DEBIT_PR_count']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>2B Taxable:</span><strong>₹{doc_type_stats['DEBIT_2B_taxable']:,.0f}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>PR Taxable:</span><strong>₹{doc_type_stats['DEBIT_PR_taxable']:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== AI INSIGHTS ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">🧠</span> AI-Powered Financial Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            
            insights = []
            if dup_pr_count > 0:
                insights.append({'type': 'warning', 'icon': '⚠️', 'title': 'Data Quality Alert', 'message': f"Found **{dup_pr_count} duplicate entries** in Purchase Register. Review for data integrity."})
            if missing_pr > 0:
                insights.append({'type': 'success', 'icon': '💡', 'title': 'Cash Flow Opportunity', 'message': f"**₹{unclaimed_itc:,.2f}** in ITC available in GSTR-2B but not claimed in books. Consider claiming to improve cash flow."})
            if missing_2b > 0:
                insights.append({'type': 'error', 'icon': '🚨', 'title': 'Compliance Risk', 'message': f"**₹{risky_claims:,.2f}** claimed in books but missing from GSTR-2B. This may lead to ITC reversal notices."})
            if match_rate < 80:
                insights.append({'type': 'warning', 'icon': '🔄', 'title': 'Reconciliation Health', 'message': f"Match rate is **{match_rate:.1f}%**. Review document numbering conventions and date formats."})
            elif match_rate >= 95:
                insights.append({'type': 'success', 'icon': '✅', 'title': 'Excellent Health', 'message': f"Outstanding match rate of **{match_rate:.1f}%**! Your GST compliance is in excellent shape."})
            if suggested_count > 0:
                insights.append({'type': 'info', 'icon': '🕒', 'title': 'Date Mismatches', 'message': f"**{suggested_count} records** have date differences within tolerance. Review for accurate period reporting."})
            if doc_type_stats['CREDIT_2B_count'] != doc_type_stats['CREDIT_PR_count']:
                insights.append({'type': 'warning', 'icon': '📉', 'title': 'Credit Note Mismatch', 'message': f"Credit note counts differ: {doc_type_stats['CREDIT_2B_count']} in 2B vs {doc_type_stats['CREDIT_PR_count']} in PR. Verify all credit notes are properly recorded."})
            if validate_gstin and (stats.get('invalid_gstins_2b', 0) > 0 or stats.get('invalid_gstins_pr', 0) > 0):
                insights.append({'type': 'error', 'icon': '🔍', 'title': 'GSTIN Validation', 'message': "Invalid GSTIN formats detected. Ensure all GSTINs follow the 15-character format for accurate matching."})
            if not insights:
                insights.append({'type': 'success', 'icon': '🎉', 'title': 'All Clear', 'message': "No critical issues detected. Your GST reconciliation is healthy and compliant!"})
            
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div class="insight-card {insight['type']} animate-fade-in" style="animation-delay: {i*0.1}s">
                    <div class="insight-title">{insight['icon']} {insight['title']}</div>
                    <div class="insight-message">{insight['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== VISUALIZATIONS ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📈</span> Visual Analytics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Status", "📑 Doc Types", "📅 Trends", "🔍 Details"])
            
            with tab1:
                status_data = merged_df['MATCH_STATUS'].value_counts().reset_index()
                status_data.columns = ['Status', 'Count']
                color_map = {
                    'Exact': '#10b981', 'Suggested': '#06b6d4', 'Value Mismatch': '#f97316', 
                    'Doc Type Mismatch': '#8b5cf6', 'Cross-State (PAN Match)': '#6366f1', 
                    'Missing in GSTR 2B': '#ef4444', 'Missing in PR': '#f59e0b', 'Other': '#64748b'
                }
                fig_status = px.pie(
                    status_data, values='Count', names='Status', 
                    color='Status', color_discrete_map=color_map, 
                    hole=0.5, title='Reconciliation Status Distribution'
                )
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
                fig_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                    legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5), 
                    height=450, margin=dict(t=50, b=50, l=20, r=20)
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with tab2:
                dt_data = pd.DataFrame({
                    'Document Type': ['INVOICE', 'CREDIT', 'DEBIT'],
                    'GSTR-2B Taxable': [
                        doc_type_stats['INVOICE_2B_taxable'], 
                        doc_type_stats['CREDIT_2B_taxable'], 
                        doc_type_stats['DEBIT_2B_taxable']
                    ],
                    'Purchase Register Taxable': [
                        doc_type_stats['INVOICE_PR_taxable'], 
                        doc_type_stats['CREDIT_PR_taxable'], 
                        doc_type_stats['DEBIT_PR_taxable']
                    ]
                })
                fig_dt = px.bar(
                    dt_data, x='Document Type', 
                    y=['GSTR-2B Taxable', 'Purchase Register Taxable'], 
                    barmode='group', title='Taxable Value by Document Type', 
                    labels={'value': 'Amount (₹)', 'Document Type': 'Type'}
                )
                fig_dt.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                    height=450, legend=dict(orientation='h', y=-0.2),
                    margin=dict(t=50, b=50, l=20, r=20)
                )
                st.plotly_chart(fig_dt, use_container_width=True)
            
            with tab3:
                if 'MONTH_2B' in merged_df.columns:
                    monthly = merged_df.groupby('MONTH_2B').agg({
                        'TAXABLE_VALUE_2B': 'sum', 
                        'TOTAL_TAX_2B': 'sum', 
                        'TAXABLE_VALUE_PR': 'sum', 
                        'TOTAL_TAX_PR': 'sum'
                    }).reset_index().fillna(0)
                    
                    fig_monthly = go.Figure()
                    fig_monthly.add_trace(go.Bar(
                        x=monthly['MONTH_2B'], y=monthly['TAXABLE_VALUE_2B'], 
                        name='Taxable (2B)', marker_color=px.colors.qualitative.Set1[0]
                    ))
                    fig_monthly.add_trace(go.Bar(
                        x=monthly['MONTH_2B'], y=monthly['TAXABLE_VALUE_PR'], 
                        name='Taxable (PR)', marker_color=px.colors.qualitative.Set1[1]
                    ))
                    fig_monthly.update_layout(
                        barmode='group', title='Monthly Taxable Value Comparison', 
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                        height=450, legend=dict(orientation='h', y=-0.2), 
                        xaxis_tickangle=-45, margin=dict(t=50, b=80, l=20, r=20)
                    )
                    st.plotly_chart(fig_monthly, use_container_width=True)
            
            with tab4:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    status_filter = st.multiselect(
                        "Filter Status", 
                        merged_df['MATCH_STATUS'].unique().tolist(), 
                        default=merged_df['MATCH_STATUS'].unique().tolist(),
                        key="status_filter_multiselect"
                    )
                with col_f2:
                    search = st.text_input("🔎 Search Supplier", placeholder="Type to search...", key="supplier_search")
                with col_f3:
                    min_val = st.number_input("Min Value (₹)", min_value=0, value=0, step=1000, key="min_value_filter")
                
                # Apply filters
                filtered = merged_df.copy()
                if status_filter:
                    filtered = filtered[filtered['MATCH_STATUS'].isin(status_filter)]
                if search:
                    filtered = filtered[filtered['SUPPLIER_NAME_COMBINED'].str.contains(search, case=False, na=False)]
                if min_val > 0:
                    filtered = filtered[
                        (filtered['TAXABLE_VALUE_2B'].abs() >= min_val) | 
                        (filtered['TAXABLE_VALUE_PR'].abs() >= min_val)
                    ]
                
                # Select display columns
                display_cols = [
                    'MATCH_STATUS', 'SUPPLIER_NAME_COMBINED', 'DOC_TYPE_2B', 
                    'DOC_NUMBER_2B', 'DOC_NUMBER_PR', 'TAXABLE_VALUE_2B', 
                    'TAXABLE_VALUE_PR', 'TOTAL_TAX_2B', 'TOTAL_TAX_PR', 'ITC_ELIGIBILITY'
                ]
                
                # ✅ FIXED: Use proper CSS property strings for pandas Styler
                def apply_status_styling(val):
                    """Returns CSS properties string for pandas Styler - NOT class names!"""
                    return get_status_css_class(val)
                
                # Format numeric columns and apply status styling
                styled_df = filtered[display_cols].head(100).style.format({
                    'TAXABLE_VALUE_2B': '₹{:.2f}',
                    'TAXABLE_VALUE_PR': '₹{:.2f}', 
                    'TOTAL_TAX_2B': '₹{:.2f}',
                    'TOTAL_TAX_PR': '₹{:.2f}'
                }).map(apply_status_styling, subset=['MATCH_STATUS'])
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # ==================== EXPORT SECTION ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📤</span> Export Reconciliation Report</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_export1, col_export2 = st.columns([3, 1])
            with col_export1:
                st.markdown("""
                <div style="background: rgba(99, 102, 241, 0.05); border-radius: 12px; padding: 20px; border: 1px solid var(--border-light);">
                    <strong>📋 Report Includes:</strong>
                    <ul style="margin: 10px 0 0 20px; color: var(--text-secondary); line-height: 1.8;">
                        <li>Executive Dashboard with interactive charts</li>
                        <li>Detailed reconciliation with all 30+ columns</li>
                        <li>Subtotals at top for each match status</li>
                        <li>Credit/Debit Note handling with negative values</li>
                        <li>Summary tables matching GST portal format</li>
                        <li>Raw data sheets for audit trail</li>
                        <li><strong>DOC_TYPE dropdown validation (INVOICE/CREDIT/DEBIT)</strong></li>
                        <li>Month format: JANUARY-25, FEBRUARY-25, etc.</li>
                        <li>Processing metadata and audit log</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col_export2:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Prepare reconciliation sheet with all required columns
                    recon_df = merged_df[[
                        'MATCH_STATUS', 'MATCH_REASON', 'SUPPLIER_NAME_COMBINED', 
                        'SUPPLIER_GSTIN_2B', 'SUPPLIER_GSTIN_PR', 'MY_GSTIN_2B', 'MY_GSTIN_PR',
                        'DOC_NUMBER_2B', 'DOC_NUMBER_PR', 'DOC_DATE_2B', 'DOC_DATE_PR',
                        'TOTAL_DOC_VALUE_2B', 'TOTAL_DOC_VALUE_PR',
                        'TAXABLE_VALUE_2B', 'TAXABLE_VALUE_PR',
                        'TAXABLE_DIFF', 'TOTAL_TAX_2B', 'TOTAL_TAX_PR',
                        'IGST_2B', 'IGST_PR', 'CGST_2B', 'CGST_PR', 'SGST_2B', 'SGST_PR',
                        'CESS_2B', 'CESS_PR',
                        'DOC_TYPE_2B', 'DOC_TYPE_PR',
                        'SECTION_NAME_2B', 'SECTION_NAME_PR'
                    ]].copy()
                    
                    recon_df.columns = [
                        'Match Status', 'Match Status Description', 'Supplier Name',
                        'Supplier GSTIN (2B)', 'Supplier GSTIN (PR)', 'My GSTIN (2B)', 'My GSTIN (PR)',
                        'Document Number (2B)', 'Document Number (PR)', 'Document Date (2B)', 'Document Date (PR)',
                        'Total Document Value (2B)', 'Total Document Value (PR)',
                        'Taxable Value (2B)', 'Taxable Value (PR)',
                        'Tax Difference(2B-PR)', 'Total Tax (2B)', 'Total Tax (PR)',
                        'IGST (2B)', 'IGST (PR)', 'CGST (2B)', 'CGST (PR)', 'SGST (2B)', 'SGST (PR)',
                        'Cess (2B)', 'Cess (PR)',
                        'Document Type(2B)', 'Document Type(PR)',
                        'Section Name 2B', 'Section Name (Pr)'
                    ]
                    
                    # Add subtotals at top if enabled
                    if include_subtotals:
                        # Create summary rows
                        summary_rows = []
                        for status in recon_df['Match Status'].unique():
                            status_data = recon_df[recon_df['Match Status'] == status]
                            summary_rows.append({
                                'Match Status': f'SUBTOTAL - {status}',
                                'Supplier Name': '',
                                'Total Document Value (2B)': status_data['Total Document Value (2B)'].sum(),
                                'Total Document Value (PR)': status_data['Total Document Value (PR)'].sum(),
                                'Taxable Value (2B)': status_data['Taxable Value (2B)'].sum(),
                                'Taxable Value (PR)': status_data['Taxable Value (PR)'].sum(),
                                'Total Tax (2B)': status_data['Total Tax (2B)'].sum(),
                                'Total Tax (PR)': status_data['Total Tax (PR)'].sum(),
                            })
                        
                        # Convert to DataFrame and add to top
                        summary_df = pd.DataFrame(summary_rows)
                        recon_df = pd.concat([summary_df, recon_df], ignore_index=True)
                    
                    # Write to Excel starting from row 2 (for header)
                    recon_df.to_excel(writer, sheet_name='Reconciliation', index=False, startrow=2)
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Reconciliation']
                    
                    # Add header format
                    header_format = workbook.add_format({
                        'bold': True, 'bg_color': '#1e40af', 'font_color': 'white', 
                        'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
                    })
                    
                    # Add subtotal format
                    subtotal_format = workbook.add_format({
                        'bold': True, 'bg_color': '#dbeafe', 'font_color': '#1e40af',
                        'border': 1, 'align': 'left', 'valign': 'vcenter'
                    })
                    
                    # Add number format
                    number_format = workbook.add_format({
                        'num_format': '#,##0.00', 'border': 1
                    })
                    
                    # Write headers
                    for col_num, col_name in enumerate(recon_df.columns):
                        worksheet.write(2, col_num, col_name, header_format)
                    
                    # Apply formatting to data rows
                    for row_num in range(3, len(recon_df) + 3):
                        # Check if this is a subtotal row
                        if worksheet.read_string(row_num - 1, 0).startswith('SUBTOTAL'):
                            worksheet.set_row(row_num - 1, None, subtotal_format)
                        else:
                            # Apply number formatting to value columns
                            for col_num in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
                                if col_num < len(recon_df.columns):
                                    worksheet.write_number(row_num - 1, col_num, 
                                                         recon_df.iloc[row_num - 3, col_num], 
                                                         number_format)
                    
                    if add_dropdown_validation:
                        worksheet.data_validation('J3:J100000', {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
                        worksheet.data_validation('K3:K100000', {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
                    
                    # Set column widths
                    worksheet.set_column('A:A', 20)  # Match Status
                    worksheet.set_column('B:B', 50)  # Match Status Description
                    worksheet.set_column('C:C', 35)  # Supplier Name
                    worksheet.set_column('D:G', 20)  # GSTINs
                    worksheet.set_column('H:I', 22)  # Doc Numbers
                    worksheet.set_column('J:K', 16)  # Doc Dates
                    worksheet.set_column('L:Q', 18)  # Values and Tax
                    worksheet.set_column('R:AA', 14) # Tax breakdown and Doc Types
                    
                    # Add summary sheet
                    summary_data = pd.DataFrame({
                        'Metric': [
                            'Total Records', 'Exact Matches', 'Suggested Matches', 
                            'Value Mismatches', 'Missing in GSTR-2B', 'Missing in PR',
                            'Match Rate (%)', 'Unclaimed ITC (₹)', 'Risk Claims (₹)',
                            'Processing Time (sec)'
                        ],
                        'Value': [
                            total_records, exact_count, suggested_count,
                            stats.get('value_mismatches', 0), missing_2b, missing_pr,
                            f"{match_rate:.2f}", f"{unclaimed_itc:,.2f}", f"{risky_claims:,.2f}",
                            stats.get('processing_time_sec', 0)
                        ]
                    })
                    summary_data.to_excel(writer, sheet_name='Summary', index=False)
                    
                    if include_raw_data:
                        df_2b.to_excel(writer, sheet_name='Raw_GSTR2B', index=False)
                        df_pr.to_excel(writer, sheet_name='Raw_PurchaseRegister', index=False)
                
                st.download_button(
                    label="⚡ Download Excel Report", 
                    data=output.getvalue(), 
                    file_name=f"GST_Recon_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    use_container_width=True,
                    key="btn_download_excel"
                )
                
                if export_format in ["CSV (.csv)", "Both"]:
                    csv_output = io.StringIO()
                    merged_df.to_csv(csv_output, index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_output.getvalue(),
                        file_name=f"GST_Recon_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="btn_download_csv"
                    )
            
            st.success(f"✅ Ready! Processed {total_records:,} records in {stats['processing_time_sec']}s with professional format export including subtotals.")
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        st.error(f"❌ Processing Error: {str(e)}")
        with st.expander("🔧 Technical Details"):
            st.exception(e)
            st.info("""
            💡 **Troubleshooting Tips:**
            - Ensure files follow the sample template format
            - Check that DOC_TYPE column contains: INVOICE, CREDIT, or DEBIT
            - Verify Credit Notes have negative taxable/tax values
            - Confirm GSTINs are in valid 15-character format
            - Check date formats: DD-MM-YYYY, YYYY-MM-DD, or DD/MM/YYYY
            """)

else:
    st.markdown("""
    <div class="section-card animate-fade-in" style="text-align: center; padding: 64px 44px;">
        <div style="font-size: 4.5rem; margin-bottom: 24px;">🧾✨</div>
        <h2 style="margin: 0 0 18px 0; font-size: 2rem;">Welcome to GST Recon Pro v6.0</h2>
        <p style="color: var(--text-secondary); font-size: 1.15rem; max-width: 650px; margin: 0 auto 36px auto; line-height: 1.7;">
            Upload your GSTR-2B and Purchase Register files to begin intelligent reconciliation. 
            Our AI-powered engine matches invoices, handles Credit/Debit Notes with negative values, 
            identifies discrepancies, and generates compliance-ready reports with enterprise-grade security.
        </p>
        <div class="quick-actions">
            <div class="quick-action-btn"><span class="icon">📁</span><span class="label">Upload Files</span></div>
            <div class="quick-action-btn"><span class="icon">📥</span><span class="label">Get Samples</span></div>
            <div class="quick-action-btn"><span class="icon">📉</span><span class="label">CDN Support</span></div>
            <div class="quick-action-btn"><span class="icon">📊</span><span class="label">Live Insights</span></div>
        </div>
        <div style="margin-top: 44px; padding-top: 28px; border-top: 1px solid var(--border-light);">
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6;">
                <strong>💡 Pro Tips:</strong><br>
                • Credit Notes should have <strong>negative taxable/tax values</strong> for proper matching<br>
                • Use DOC_TYPE dropdown: INVOICE / CREDIT / DEBIT<br>
                • Month format: <strong>JANUARY-25, FEBRUARY-25</strong>, etc.<br>
                • GSTIN format: 15 characters (e.g., 36AADCR6281N1ZT)<br>
                • Press <strong>Ctrl+T</strong> to toggle dark/light theme
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <div class="brand">🧾 GST Recon Pro v6.0</div>
    <div class="credits">Enterprise GST Reconciliation Engine</div>
    <div class="credits">Developed by <strong>ABHISHEK JAKKULA</strong> • jakkulaabhishek5@gmail.com</div>
    <div class="version">v6.0.0 • Last Updated: May 2026</div>
    <div style="margin-top: 24px; display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.95rem;">📚 Documentation</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.95rem;">🎥 Tutorials</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.95rem;">🔧 Support</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.95rem;">🐛 Report Bug</a>
    </div>
    <div style="margin-top: 16px; font-size: 0.85rem; color: var(--text-secondary);">
        © 2026 Abhishek Jakkula. All rights reserved. | GST Recon Pro is a proprietary enterprise solution.
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== KEYBOARD SHORTCUTS ====================
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (confirm('Reset session and clear all data?')) {
            window.location.reload();
        }
    }
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        const exportBtn = document.querySelector('button[kind="secondary"]');
        if (exportBtn) exportBtn.click();
    }
});
</script>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if 'load_sample' not in st.session_state:
    st.session_state.load_sample = False
if 'file_2b_hash' not in st.session_state:
    st.session_state.file_2b_hash = None
if 'file_pr_hash' not in st.session_state:
    st.session_state.file_pr_hash = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

if st.session_state.load_sample:
    st.info("📥 Sample templates downloaded. Please upload them to begin reconciliation.")
    st.session_state.load_sample = False

# ==================== ERROR HANDLING ====================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    st.error(f"💥 Unexpected Error: {exc_value}")
    st.info("Please refresh the page or contact support if the issue persists.")

sys.excepthook = global_exception_handler

# ==================== PERFORMANCE MONITORING ====================
if 'page_load_start' not in st.session_state:
    st.session_state.page_load_start = time.time()
else:
    load_time = time.time() - st.session_state.page_load_start
    if load_time > 5:
        logger.warning(f"Page load time: {load_time:.2f}s")

# ==================== END OF APPLICATION ====================
