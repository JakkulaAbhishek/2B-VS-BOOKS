# ============================================================================
# ✨ GST Recon Pro v6.0 - Enterprise GST Reconciliation Engine
# ============================================================================
# Author: Abhishek Jakkula
# Email: jakkulaabhishek5@gmail.com
# Version: 6.0.3 (Error-Free • Enhanced UI • Modern Design)
# Last Updated: May 2026
# License: Proprietary - Enterprise Edition
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
from urllib.parse import quote

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

# ==================== ULTRA-MODERN HIGH-VISIBILITY CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        /* High-Visibility Color Palette - Light Theme */
        --primary: #4f46e5;
        --primary-hover: #4338ca;
        --primary-light: #e0e7ff;
        --primary-text: #3730a3;
        
        --secondary: #7c3aed;
        --secondary-hover: #6d28d9;
        --secondary-light: #ede9fe;
        --secondary-text: #5b21b6;
        
        --accent: #0891b2;
        --accent-light: #cffafe;
        --accent-text: #155e75;
        
        --success: #059669;
        --success-light: #d1fae5;
        --success-text: #065f46;
        
        --warning: #d97706;
        --warning-light: #fef3c7;
        --warning-text: #92400e;
        
        --error: #dc2626;
        --error-light: #fee2e2;
        --error-text: #991b1b;
        
        --info: #2563eb;
        --info-light: #dbeafe;
        --info-text: #1e40af;
        
        /* Background & Text - High Contrast */
        --bg-primary: #f1f5f9;
        --bg-secondary: #ffffff;
        --bg-tertiary: #e2e8f0;
        --bg-card: #ffffff;
        --bg-hover: #f8fafc;
        --bg-selected: #e0e7ff;
        
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-tertiary: #475569;
        --text-muted: #64748b;
        --text-inverse: #ffffff;
        
        --border-color: #cbd5e1;
        --border-hover: #94a3b8;
        --border-focus: var(--primary);
        
        /* Shadows - Enhanced Depth */
        --shadow-xs: 0 1px 2px 0 rgb(15 23 42 / 0.05);
        --shadow-sm: 0 1px 3px 0 rgb(15 23 42 / 0.1), 0 1px 2px -1px rgb(15 23 42 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(15 23 42 / 0.1), 0 2px 4px -2px rgb(15 23 42 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(15 23 42 / 0.1), 0 4px 6px -4px rgb(15 23 42 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(15 23 42 / 0.15), 0 8px 10px -6px rgb(15 23 42 / 0.15);
        --shadow-2xl: 0 25px 50px -12px rgb(15 23 42 / 0.25);
        
        /* Border Radius */
        --radius-xs: 4px;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-2xl: 24px;
        --radius-full: 9999px;
        
        /* Transitions */
        --transition-fast: 150ms ease;
        --transition-normal: 250ms ease;
        --transition-slow: 350ms ease;
        
        /* Focus Ring */
        --focus-ring: 0 0 0 3px rgba(79, 70, 229, 0.5);
    }

    [data-theme="dark"] {
        /* High-Visibility Color Palette - Dark Theme */
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-card: #1e293b;
        --bg-hover: #334155;
        --bg-selected: #312e81;
        
        --text-primary: #f8fafc;
        --text-secondary: #e2e8f0;
        --text-tertiary: #cbd5e1;
        --text-muted: #94a3b8;
        --text-inverse: #0f172a;
        
        --border-color: #475569;
        --border-hover: #64748b;
        
        --primary-light: #312e81;
        --secondary-light: #4c1d95;
        --accent-light: #164e63;
        --success-light: #064e3b;
        --warning-light: #78350f;
        --error-light: #7f1d1d;
        --info-light: #1e3a8a;
        
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4);
    }

    /* Base Styles - High Readability */
    * { box-sizing: border-box; }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-primary);
        scroll-behavior: smooth;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        line-height: 1.6;
    }

    body {
        background: var(--bg-primary);
        background-image: 
            radial-gradient(at 40% 20%, rgba(79, 70, 229, 0.06) 0px, transparent 50%),
            radial-gradient(at 80% 0%, rgba(124, 58, 237, 0.06) 0px, transparent 50%),
            radial-gradient(at 0% 50%, rgba(8, 145, 178, 0.06) 0px, transparent 50%);
        background-attachment: fixed;
        min-height: 100vh;
    }

    .stApp {
        background: transparent !important;
    }

    /* Sidebar - High Contrast */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border-right: 2px solid var(--border-color);
        box-shadow: var(--shadow-lg);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }

    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: var(--text-primary);
        font-weight: 700;
    }

    /* Main Header - High Visibility */
    .main-header {
        text-align: center;
        padding: 2.5rem 2rem;
        margin: 1rem 0 2rem 0;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border-radius: var(--radius-2xl);
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(ellipse at center, rgba(255,255,255,0.15) 0%, transparent 60%);
        animation: pulse 10s ease-in-out infinite;
        pointer-events: none;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.08); }
    }

    .main-header h1 {
        font-weight: 800 !important;
        font-size: 2.8rem !important;
        color: white !important;
        margin: 0 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        position: relative;
        z-index: 2;
        letter-spacing: -0.02em;
    }

    .main-header .subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.95);
        margin: 1rem 0 0 0;
        line-height: 1.7;
        position: relative;
        z-index: 2;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        font-weight: 400;
    }

    .main-header .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: var(--radius-full);
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Metric Cards - High Contrast */
    .metric-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 20px 18px;
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: var(--transition-normal);
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
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
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary);
    }

    .metric-card .metric-icon {
        font-size: 1.6rem;
        margin-bottom: 6px;
        display: block;
    }

    .metric-card .metric-label {
        font-size: 0.8rem;
        color: var(--text-tertiary);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
    }

    .metric-card .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 4px 0;
    }

    .metric-card .metric-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 4px;
        font-weight: 500;
    }

    .metric-card .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: var(--radius-full);
        margin-top: 8px;
        align-self: flex-start;
    }

    .metric-delta.positive { 
        background: var(--success-light); 
        color: var(--success-text);
        border: 1px solid var(--success);
    }
    .metric-delta.negative { 
        background: var(--error-light); 
        color: var(--error-text);
        border: 1px solid var(--error);
    }
    .metric-delta.neutral { 
        background: var(--bg-tertiary); 
        color: var(--text-tertiary);
        border: 1px solid var(--border-color);
    }
    .metric-delta.warning { 
        background: var(--warning-light); 
        color: var(--warning-text);
        border: 1px solid var(--warning);
    }

    /* Section Cards - Clear Hierarchy */
    .section-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-md);
        border: 2px solid var(--border-color);
        transition: var(--transition-normal);
    }

    .section-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }

    .section-card h3 {
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 16px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.2rem;
    }

    .section-card h3 .icon { 
        font-size: 1.3rem; 
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: var(--primary-light);
        border-radius: var(--radius-md);
        color: var(--primary-text);
        font-weight: 700;
    }

    /* Modern Buttons - High Visibility */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-hover));
        color: white !important;
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 700;
        border: 2px solid transparent;
        transition: var(--transition-normal);
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }

    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s ease;
    }

    .stButton>button:hover::before { 
        left: 100%; 
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-hover), var(--secondary-hover));
        border-color: rgba(255, 255, 255, 0.3);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* DataFrames - High Readability */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 2px solid var(--border-color);
        background: var(--bg-card);
    }

    [data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        font-weight: 700;
        padding: 14px 16px;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.6px;
        border: none;
        white-space: nowrap;
    }

    [data-testid="stDataFrame"] td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    [data-testid="stDataFrame"] tr:hover {
        background: var(--bg-hover);
    }

    [data-testid="stDataFrame"] tr:last-child td {
        border-bottom: none;
    }

    /* Status Badges - Clear Visual Hierarchy */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 12px;
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        border: 1px solid;
    }

    .status-exact { 
        background: var(--success-light); 
        color: var(--success-text);
        border-color: var(--success);
    }
    .status-suggested { 
        background: var(--accent-light); 
        color: var(--accent-text);
        border-color: var(--accent);
    }
    .status-mismatch { 
        background: var(--warning-light); 
        color: var(--warning-text);
        border-color: var(--warning);
    }
    .status-missing-2b { 
        background: var(--error-light); 
        color: var(--error-text);
        border-color: var(--error);
    }
    .status-missing-pr { 
        background: var(--info-light); 
        color: var(--info-text);
        border-color: var(--info);
    }

    /* Tabs - High Contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--bg-tertiary);
        padding: 5px;
        border-radius: var(--radius-lg);
        border: 2px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 10px 20px;
        font-weight: 700;
        transition: var(--transition-fast);
        color: var(--text-tertiary);
        font-size: 0.9rem;
        border: 2px solid transparent !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
        border-color: var(--border-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
        border-color: transparent !important;
    }

    /* Insight Cards - Clear Messaging */
    .insight-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        margin-bottom: 14px;
        border-left: 5px solid var(--primary);
        box-shadow: var(--shadow-sm);
        border: 2px solid var(--border-color);
        transition: var(--transition-normal);
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }

    .insight-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateX(3px);
        border-color: var(--primary);
    }

    .insight-card .insight-icon {
        font-size: 1.4rem;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .insight-card .insight-content {
        flex: 1;
    }

    .insight-card .insight-title {
        font-weight: 700;
        font-size: 1rem;
        color: var(--text-primary);
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .insight-card .insight-message {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .insight-card.warning {
        border-left-color: var(--warning);
        background: linear-gradient(135deg, rgba(217, 119, 6, 0.05), transparent);
    }
    .insight-card.success {
        border-left-color: var(--success);
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.05), transparent);
    }
    .insight-card.error {
        border-left-color: var(--error);
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.05), transparent);
    }
    .insight-card.info {
        border-left-color: var(--info);
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), transparent);
    }

    /* Match Status Cards */
    .match-status-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 18px;
        border: 2px solid var(--border-color);
        border-left: 5px solid var(--primary);
        box-shadow: var(--shadow-sm);
        transition: var(--transition-normal);
        margin-bottom: 12px;
    }

    .match-status-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: var(--primary);
    }

    .match-status-card.exact { border-left-color: var(--success); }
    .match-status-card.suggested { border-left-color: var(--accent); }
    .match-status-card.mismatch { border-left-color: var(--warning); }
    .match-status-card.missing-2b { border-left-color: var(--error); }
    .match-status-card.missing-pr { border-left-color: var(--info); }

    .match-status-card .status-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }

    .match-status-card .status-name {
        font-weight: 700;
        font-size: 1rem;
        color: var(--text-primary);
    }

    .match-status-card .status-count {
        background: var(--bg-tertiary);
        padding: 4px 12px;
        border-radius: var(--radius-full);
        font-weight: 800;
        font-size: 0.9rem;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }

    .match-status-card .status-details {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.5;
        font-weight: 500;
    }

    .match-status-card .status-link {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        color: var(--primary);
        font-weight: 700;
        font-size: 0.85rem;
        margin-top: 8px;
        text-decoration: none;
        transition: var(--transition-fast);
    }

    .match-status-card .status-link:hover {
        color: var(--primary-hover);
        text-decoration: underline;
    }

    /* Party Cards */
    .party-card {
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: 14px;
        border: 2px solid var(--border-color);
        margin: 6px 0;
        transition: var(--transition-fast);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
    }

    .party-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-sm);
        background: var(--bg-hover);
    }

    .party-info {
        flex: 1;
    }

    .party-name {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 3px;
        font-size: 0.95rem;
    }

    .party-gstin {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    .party-stats {
        text-align: right;
    }

    .party-value {
        font-weight: 800;
        color: var(--text-primary);
        font-size: 1.05rem;
    }

    .party-label {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    /* Theme Toggle */
    .theme-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }

    .theme-toggle button {
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-full);
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: var(--shadow-lg);
        transition: var(--transition-normal);
        color: var(--text-primary);
        font-weight: 700;
    }

    .theme-toggle button:hover {
        transform: scale(1.1) rotate(15deg);
        border-color: var(--primary);
        background: var(--primary-light);
        color: var(--primary-text);
    }

    /* Footer - Clear Branding */
    .footer {
        text-align: center;
        padding: 36px 24px;
        margin-top: 50px;
        background: linear-gradient(135deg, var(--bg-card), var(--bg-tertiary));
        border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
        border-top: 2px solid var(--border-color);
        position: relative;
    }

    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    }

    .footer .brand {
        font-weight: 800;
        font-size: 1.3rem;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .footer .credits {
        color: var(--text-tertiary);
        font-size: 0.9rem;
        margin: 3px 0;
        font-weight: 500;
    }

    .footer .version {
        display: inline-block;
        background: var(--bg-tertiary);
        padding: 5px 16px;
        border-radius: var(--radius-full);
        font-size: 0.8rem;
        color: var(--text-tertiary);
        margin-top: 14px;
        border: 1px solid var(--border-color);
        font-weight: 600;
    }

    .footer a {
        color: var(--text-secondary);
        text-decoration: none;
        transition: var(--transition-fast);
        padding: 4px 8px;
        border-radius: var(--radius-sm);
        font-weight: 500;
    }

    .footer a:hover {
        color: var(--primary);
        background: var(--primary-light);
    }

    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin: 20px 0;
    }

    .quick-action-btn {
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 18px 14px;
        text-align: center;
        cursor: pointer;
        transition: var(--transition-normal);
        text-decoration: none;
        color: var(--text-primary);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        font-weight: 600;
    }

    .quick-action-btn:hover {
        border-color: var(--primary);
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.05), rgba(124, 58, 237, 0.05));
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }

    .quick-action-btn .icon { 
        font-size: 1.8rem; 
        display: block;
        transition: var(--transition-fast);
    }

    .quick-action-btn:hover .icon {
        transform: scale(1.1);
    }

    .quick-action-btn .label { 
        font-weight: 700; 
        font-size: 0.85rem; 
    }

    /* Document Type Badges */
    .doc-type-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 700;
        margin: 2px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        border: 1px solid;
    }

    .doc-type-invoice { 
        background: var(--success-light); 
        color: var(--success-text);
        border-color: var(--success);
    }
    .doc-type-credit { 
        background: var(--error-light); 
        color: var(--error-text);
        border-color: var(--error);
    }
    .doc-type-debit { 
        background: var(--warning-light); 
        color: var(--warning-text);
        border-color: var(--warning);
    }

    /* DataFrame Row Styling */
    .df-exact { 
        color: var(--success-text) !important; 
        background-color: rgba(5, 150, 105, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-suggested { 
        color: var(--accent-text) !important; 
        background-color: rgba(8, 145, 178, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-value-mismatch { 
        color: var(--warning-text) !important; 
        background-color: rgba(217, 119, 6, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-doc-type-mismatch { 
        color: var(--secondary-text) !important; 
        background-color: rgba(124, 58, 237, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-cross-state { 
        color: var(--primary-text) !important; 
        background-color: rgba(79, 70, 229, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-missing-2b { 
        color: var(--error-text) !important; 
        background-color: rgba(220, 38, 38, 0.1) !important; 
        font-weight: 700 !important; 
    }
    .df-missing-pr { 
        color: var(--info-text) !important; 
        background-color: rgba(37, 99, 235, 0.1) !important; 
        font-weight: 700 !important; 
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .animate-fade-in { 
        animation: fadeInUp 0.45s ease forwards; 
        opacity: 0;
    }
    
    .animate-fade-in:nth-child(1) { animation-delay: 0.08s; }
    .animate-fade-in:nth-child(2) { animation-delay: 0.12s; }
    .animate-fade-in:nth-child(3) { animation-delay: 0.16s; }
    .animate-fade-in:nth-child(4) { animation-delay: 0.2s; }
    .animate-fade-in:nth-child(5) { animation-delay: 0.24s; }

    .animate-fade {
        animation: fadeIn 0.35s ease forwards;
    }

    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    .loading { 
        animation: pulse 1.3s ease-in-out infinite; 
    }

    /* Toast Notifications */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 13px 20px;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        animation: slideIn 0.28s ease;
        max-width: 400px;
        display: flex;
        align-items: center;
        gap: 10px;
        border: 2px solid var(--border-color);
        font-weight: 600;
    }

    .toast.success { 
        background: var(--bg-card); 
        border-left: 5px solid var(--success);
        color: var(--text-primary);
    }
    .toast.error { 
        background: var(--bg-card); 
        border-left: 5px solid var(--error);
        color: var(--text-primary);
    }
    .toast.warning { 
        background: var(--bg-card); 
        border-left: 5px solid var(--warning);
        color: var(--text-primary);
    }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* Form Elements - High Visibility */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: var(--radius-md);
        border: 2px solid var(--border-color);
        transition: var(--transition-fast);
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-weight: 500;
        padding: 10px 14px;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary);
        box-shadow: var(--focus-ring);
        outline: none;
    }

    /* Checkbox & Radio */
    .stCheckbox label,
    .stRadio label {
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.95rem;
    }

    /* Slider */
    .stSlider > div > div > div {
        background: var(--primary) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        border: 2px solid var(--border-color);
        font-weight: 700;
        padding: 11px 15px;
        transition: var(--transition-fast);
        font-size: 0.95rem;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-hover);
        border-color: var(--primary);
    }

    /* Chart Containers */
    .chart-container {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 18px;
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        margin: 14px 0;
    }

    /* Status Legend */
    .status-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 14px;
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        margin: 14px 0;
        border: 1px solid var(--border-color);
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .legend-dot {
        width: 11px;
        height: 11px;
        border-radius: var(--radius-full);
        display: inline-block;
        border: 1px solid var(--border-color);
    }

    /* Formula Display */
    .formula-box {
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        padding: 10px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 6px 0;
        border-left: 3px solid var(--accent);
        overflow-x: auto;
        border: 1px solid var(--border-color);
        font-weight: 500;
    }

    /* Responsive Design */
    @media (max-width: 1200px) {
        .main-header h1 { font-size: 2.3rem !important; }
        .metric-card .metric-value { font-size: 1.7rem; }
    }

    @media (max-width: 992px) {
        .main-header { padding: 2rem 1.5rem; }
        .main-header h1 { font-size: 2rem !important; }
        .main-header .subtitle { font-size: 1rem; }
        .metric-card { padding: 18px 16px; }
        .metric-card .metric-value { font-size: 1.6rem; }
        .section-card { padding: 20px; }
        .quick-actions { grid-template-columns: repeat(2, 1fr); }
    }

    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.8rem !important; }
        .metric-card .metric-value { font-size: 1.5rem; }
        .quick-actions { grid-template-columns: 1fr; }
        .section-card { padding: 18px; }
        .footer { padding: 28px 16px; }
        .stTabs [data-baseweb="tab"] { padding: 9px 16px; font-size: 0.85rem; }
    }

    @media (max-width: 480px) {
        .main-header h1 { font-size: 1.6rem !important; }
        .metric-card .metric-value { font-size: 1.4rem; }
        .party-card { flex-direction: column; text-align: center; }
        .party-stats { text-align: center; }
    }

    /* Print Styles */
    @media print {
        .theme-toggle, .stButton, .footer, .quick-actions { display: none !important; }
        .main-header, .section-card { box-shadow: none !important; border: 2px solid #666 !important; }
        body { background: white !important; }
        .metric-card, .insight-card { break-inside: avoid; }
    }

    /* Accessibility - Focus States */
    *:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
    }

    /* High Contrast Mode Support */
    @media (prefers-contrast: high) {
        :root {
            --border-color: #000;
            --text-secondary: #000;
            --text-tertiary: #333;
        }
        [data-theme="dark"] {
            --border-color: #fff;
            --text-secondary: #fff;
            --text-tertiary: #ddd;
        }
    }
</style>

<!-- Theme Toggle Script -->
<script>
// Initialize theme on load
const savedTheme = localStorage.getItem('gst-recon-theme');
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

if (initialTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}

// Theme toggle function
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('gst-recon-theme', newTheme);
    
    if (window.Streamlit && window.Streamlit.setComponentValue) {
        window.Streamlit.setComponentValue(newTheme);
    }
}

// Keyboard shortcut: Ctrl+T to toggle theme
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        toggleTheme();
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add loading state to buttons
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON' && e.target.closest('.stButton')) {
        e.target.classList.add('loading');
        setTimeout(() => e.target.classList.remove('loading'), 2000);
    }
});
</script>
""", unsafe_allow_html=True)

# ==================== THEME TOGGLE BUTTON ====================
st.markdown("""
<div class="theme-toggle">
    <button onclick="toggleTheme()" title="Toggle Dark/Light Mode (Ctrl+T)" aria-label="Toggle theme">🌓</button>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR - HIGH VISIBILITY ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 24px 0; border-bottom: 2px solid var(--border-color); margin-bottom: 20px;">
        <div style="font-size: 3rem; margin-bottom: 6px; display: inline-flex; align-items: center; justify-content: center; width: 72px; height: 72px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: var(--radius-lg); color: white; box-shadow: var(--shadow-lg); font-weight: 700;">🧾</div>
        <h3 style="margin: 12px 0 3px 0; color: var(--text-primary); font-size: 1.4rem; font-weight: 800;">GST Recon Pro</h3>
        <p style="margin: 0; color: var(--text-tertiary); font-size: 0.9rem; font-weight: 500;">v6.0.3 • Enterprise</p>
        <div style="margin-top: 10px;">
            <span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; background: var(--success-light); color: var(--success-text); border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 700; border: 1px solid var(--success);">✅ Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚡ Quick Actions")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📥 Load Sample", use_container_width=True, key="btn_load_sample", help="Download sample templates"):
            st.session_state.load_sample = True
            st.rerun()
    with col_q2:
        if st.button("🔄 Reset", use_container_width=True, key="btn_reset", help="Clear session and start fresh"):
            keys_to_clear = [k for k in st.session_state.keys() if 'upload' in k or 'file' in k or 'processed' in k or 'load_sample' in k]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Session reset!")
            time.sleep(0.6)
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")
    
    with st.expander("🎯 Matching Parameters", expanded=True):
        tolerance = st.number_input("Tax/Taxable Tolerance (₹)", min_value=0, max_value=100000, value=20, step=1, 
                                   help="Maximum allowed difference in taxable/tax values for matching", key="param_tolerance")
        date_tolerance = st.number_input("Date Tolerance (Days)", min_value=0, max_value=365, value=7, step=1, 
                                        help="Maximum date difference for suggested matches", key="param_date_tol")
        fuzzy_threshold = st.slider("Fuzzy Name Match Threshold (%)", min_value=70, max_value=100, value=85, step=5,
                                   help="Similarity percentage for fuzzy supplier name matching", key="param_fuzzy")
    
    with st.expander("📋 Processing Options"):
        include_reverse_charge = st.checkbox("Include Reverse Charge", value=True, key="opt_reverse_charge")
        auto_claim_itc = st.checkbox("Auto-claim ITC for Exact Matches", value=True, key="opt_auto_claim")
        fuzzy_doc_matching = st.checkbox("Enable Fuzzy Document Matching", value=True, key="opt_fuzzy_doc")
        handle_cdn_negative = st.checkbox("Treat Credit Notes as Negative Values", value=True, 
                                         help="Credit notes will have negative taxable/tax values",
                                         key="opt_cdn_neg")
        validate_gstin = st.checkbox("Validate GSTIN Format", value=True, key="opt_validate_gstin")
        strict_financial_year = st.checkbox("Strict Financial Year Matching", value=False,
                                           help="Only match documents within same financial year",
                                           key="opt_strict_fy")
    
    with st.expander("📤 Export Preferences"):
        include_charts = st.checkbox("Include Charts in Report", value=True, key="exp_charts")
        include_raw_data = st.checkbox("Include Raw Data Sheets", value=True, key="exp_raw")
        max_rows = st.number_input("Max Excel Rows", min_value=1000, max_value=500000, value=50000, step=1000, key="exp_max_rows")
        add_dropdown_validation = st.checkbox("Add DOC_TYPE Dropdown in Excel", value=True,
                                             help="Add data validation dropdown for DOC_TYPE column",
                                             key="exp_dropdown")
        export_format = st.selectbox("Primary Export Format", ["Excel (.xlsx)", "CSV (.csv)", "Both"], index=0, key="exp_format")
        include_subtotals = st.checkbox("Include Subtotals in Export", value=False,
                                       help="Add subtotal rows for each match status",
                                       key="exp_subtotals")
    
    st.markdown("---")
    with st.expander("❓ Help & Documentation"):
        st.markdown("""
        **📚 Quick Start**
        1. Upload GSTR-2B & Purchase Register (Excel)
        2. Configure matching tolerance
        3. Review dashboard & charts
        4. Export reconciliation report
        
        **🔧 Supported Formats**
        - DOC_TYPE: INVOICE, CREDIT, DEBIT
        - Month: JANUARY-25, FEBRUARY-25
        - Dates: DD-MM-YYYY, YYYY-MM-DD
        - Values: Credit Notes = NEGATIVE
        
        **🎯 Matching Logic**
        - Exact: GSTIN + Doc No + Type + Values match
        - Suggested: PAN + Normalized Doc + Values close
        - Value Mismatch: Same doc, different amounts
        - Missing: Present in one file only
        
        **💡 Pro Tips**
        • Credit Notes: Use negative values
        • Standardize document numbering
        • Review "Suggested" matches manually
        • Use fuzzy matching for name variations
        
        **🔐 Support**
        - Email: jakkulaabhishek5@gmail.com
        - Response: < 24 hours (Business Days)
        """)
    
    st.markdown("---")
    st.markdown("### 🟢 System Status")
    
    health_status = "✅ Operational"
    health_color = "#059669"
    
    try:
        pd_version = pd.__version__
        import plotly
        plotly_version = plotly.__version__
    except Exception as e:
        health_status = "⚠️ Check Dependencies"
        health_color = "#d97706"
        logger.warning(f"System health check: {e}")
    
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: var(--text-tertiary); font-weight: 500;">
        <div style="display: flex; justify-content: space-between; margin: 7px 0; padding: 3px 0; border-bottom: 1px dashed var(--border-color);">
            <span>Engine:</span><span style="color: {health_color}; font-weight: 700;">● {health_status}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 7px 0; padding: 3px 0; border-bottom: 1px dashed var(--border-color);">
            <span>Matching AI:</span><span style="color: #059669; font-weight: 700;">● Active</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 7px 0; padding: 3px 0; border-bottom: 1px dashed var(--border-color);">
            <span>Export:</span><span style="color: #059669; font-weight: 700;">● Ready</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 7px 0; padding: 3px 0;">
            <span>Pandas:</span><span>{pd_version}</span>
        </div>
        <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-color);">
            <small style="color: var(--text-muted);">Session: {hash(str(datetime.now())) % 10000:04d}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== HEADER SECTION ====================
st.markdown("""
<div class="main-header animate-fade-in">
    <h1>✨ GST Recon Pro v6.0</h1>
    <p class="subtitle">
        AI-Powered GST Reconciliation • Match GSTR-2B with Purchase Register • 
        Real-time Insights • Compliance Reports • Credit/Debit Note Support • 
        Enterprise Security • Professional Export • Error-Free Processing
    </p>
    <div class="badge">🚀 Enhanced UI • High Visibility • Modern Design</div>
</div>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def get_month_format(month_str: str) -> str:
    """Convert month string to standardized format like JANUARY-25"""
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
        logger.warning(f"Month format failed for '{month_str}': {e}")
        return str(month_str).upper().strip() or "Unknown"


def normalize_document_number(doc_num: str) -> str:
    """Normalize document number for matching"""
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
    """Determine DOC_TYPE from value sign or existing column"""
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
    """Simple fuzzy matching for supplier names"""
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
    """Returns proper CSS property string for pandas Styler"""
    if pd.isna(status_value):
        return ''
    
    status_lower = str(status_value).lower().strip()
    
    css_map = {
        'exact': 'color: #065f46; background-color: rgba(5, 150, 105, 0.12); font-weight: 700;',
        'suggested': 'color: #155e75; background-color: rgba(8, 145, 178, 0.12); font-weight: 700;',
        'value mismatch': 'color: #92400e; background-color: rgba(217, 119, 6, 0.12); font-weight: 700;',
        'doc type mismatch': 'color: #5b21b6; background-color: rgba(124, 58, 237, 0.12); font-weight: 700;',
        'cross-state (pan match)': 'color: #3730a3; background-color: rgba(79, 70, 229, 0.12); font-weight: 700;',
        'missing in gstr 2b': 'color: #991b1b; background-color: rgba(220, 38, 38, 0.12); font-weight: 700;',
        'missing in pr': 'color: #1e40af; background-color: rgba(37, 99, 235, 0.12); font-weight: 700;',
        'other': 'color: #475569; background-color: rgba(100, 116, 139, 0.08); font-weight: 600;',
    }
    
    return css_map.get(status_lower, '')


def format_currency(value: float) -> str:
    """Format currency with Indian numbering system"""
    if pd.isna(value):
        return "₹0"
    try:
        val = float(value)
        if abs(val) >= 10000000:
            return f"₹{val/10000000:.2f} Cr"
        elif abs(val) >= 100000:
            return f"₹{val/100000:.2f} L"
        elif abs(val) >= 1000:
            return f"₹{val/1000:.2f} K"
        else:
            return f"₹{val:,.2f}"
    except:
        return f"₹{value}"


# ==================== SAMPLE TEMPLATE GENERATORS ====================

def generate_sample_2b_template() -> bytes:
    """Generate sample GSTR-2B with proper DOC_TYPE and negative CDN values"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "SECTION_NAME"
    ]
    
    sample_data = [
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "24-07-2023", "JULY-23", "INVOICE", "NO", "B2B"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT CO", "36ADXFS5154R1ZU", "26-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS", "36ADXFS5154R1ZU", "02-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "FEBRUARY-24", "CREDIT", "NO", "CDN"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE", "36ADXFS5154R1ZU", "15-03-2024", "MARCH-24", "CREDIT", "NO", "CDN"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT CO", "36ADXFS5154R1ZU", "10-01-2024", "JANUARY-24", "CREDIT", "NO", "CDN"],
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "05-03-2024", "MARCH-24", "DEBIT", "NO", "B2B"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS", "36ADXFS5154R1ZU", "20-02-2024", "FEBRUARY-24", "DEBIT", "NO", "B2B"],
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "03-05-2023", "MAY-23", "INVOICE", "NO", "B2B"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "07-07-2023", "JULY-23", "INVOICE", "NO", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "25-04-2023", "APRIL-23", "INVOICE", "NO", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "15-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36AADCR6281N1ZT", "67186859-1D", 8579.40, 0, 772.11, 772.11, "CARE HEALTH INSURANCE", "36ADXFS5154R1ZU", "01-01-2024", "JANUARY-24", "INVOICE", "NO", "B2B"],
        ["36CKUPB7102C1ZF", "BEW/23-24/53", 3500.00, 0, 315.00, 315.00, "BALAJI ENGINEERING WORKS", "36ADXFS5154R1ZU", "29-09-2023", "SEPTEMBER-23", "INVOICE", "NO", "B2B"],
        ["36AAJCS4517L1ZZ", "362311I000806960", 11388.88, 0, 1025.00, 1025.00, "STAR HEALTH INSURANCE", "36ADXFS5154R1ZU", "13-11-2023", "NOVEMBER-23", "INVOICE", "NO", "B2B"],
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
    """Generate sample Purchase Register with proper DOC_TYPE"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "ITC_CLAIM_TYPE", "PLACE_OF_SUPPLY", "SECTION_NAME"
    ]
    
    sample_data = [
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "24-07-2023", "JULY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT CO", "36ADXFS5154R1ZU", "26-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "JANUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS", "36ADXFS5154R1ZU", "02-01-2024", "JANUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "FEBRUARY-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        ["36AADCR6281N1ZT", "CN-2024-001", -2500.00, 0, -225.00, -225.00, "CARE HEALTH INSURANCE", "36ADXFS5154R1ZU", "15-03-2024", "MARCH-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        ["08AAACM8473A1ZL", "CN-MEC-001", -1500.00, -270.00, 0, 0, "METALLIZING EQUIPMENT CO", "36ADXFS5154R1ZU", "10-01-2024", "JANUARY-24", "CREDIT", "NO", "ELIGIBLE", "TELANGANA", "CDN"],
        ["36CNNPD6299J1ZB", "DN-2024-001", 1200.00, 0, 108.00, 108.00, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "05-03-2024", "MARCH-24", "DEBIT", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AAFCS6791L1ZN", "DN-SDR-002", 3500.00, 0, 315.00, 315.00, "SAI DEEPA ROCK DRILLS", "36ADXFS5154R1ZU", "20-02-2024", "FEBRUARY-24", "DEBIT", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "01-06-2023", "JUNE-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "01-09-2023", "SEPTEMBER-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-05-2023", "MAY-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-02-2024", "FEBRUARY-24", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36AAGCE1603E1Z6", "EDT/SB/2223/013", 79200.00, 0, 4752.00, 4752.00, "EXIGENT DRILLING TECH", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BDJPM4292D2ZF", "106/22-23", 211868.00, 0, 19068.12, 19068.12, "SANJAY MANDAL CONTRACTOR", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
        ["36BNDPM1159D1Z9", "160", 12015.00, 0, 1081.35, 1081.35, "SRI SAI DURGA PAINTS", "36ADXFS5154R1ZU", "01-04-2023", "APRIL-23", "INVOICE", "NO", "ELIGIBLE", "TELANGANA", "B2B"],
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
    <p style="color: var(--text-secondary); margin-bottom: 20px; line-height: 1.6; font-weight: 500;">
        Select your GSTR-2B and Purchase Register files. Ensure DOC_TYPE has: INVOICE, CREDIT, or DEBIT.
        <br><strong style="color: var(--text-primary);">💡 Credit Notes: Use negative taxable/tax values</strong>
        <br><strong style="color: var(--text-primary);">📅 Month format: JANUARY-25, FEBRUARY-25</strong>
        <br><strong style="color: var(--text-primary);">✅ GSTIN: 15 characters (e.g., 36AADCR6281N1ZT)</strong>
    </p>
""", unsafe_allow_html=True)

col_upload1, col_upload2, col_upload3 = st.columns([2, 2, 1])

with col_upload1:
    file_2b = st.file_uploader("📄 GSTR-2B File", type=['xlsx', 'xls'], key='upload_2b', label_visibility="collapsed", help="Upload GSTR-2B Excel file")
    if file_2b:
        st.success(f"✓ {file_2b.name}")
        st.session_state.file_2b_hash = generate_file_hash(file_2b.getvalue())

with col_upload2:
    file_pr = st.file_uploader("📘 Purchase Register", type=['xlsx', 'xls'], key='upload_pr', label_visibility="collapsed", help="Upload Purchase Register Excel file")
    if file_pr:
        st.success(f"✓ {file_pr.name}")
        st.session_state.file_pr_hash = generate_file_hash(file_pr.getvalue())

with col_upload3:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 2B Sample",
            data=generate_sample_2b_template(),
            file_name="GSTR2B_Sample_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_2b_sample",
            help="Download sample GSTR-2B template"
        )
    with col_d2:
        st.download_button(
            label="📘 PR Sample",
            data=generate_sample_books_template(),
            file_name="PurchaseRegister_Sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_pr_sample",
            help="Download sample Purchase Register"
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
    """Main reconciliation engine with enhanced Credit/Debit Note handling"""
    start_time = time.time()
    logger.info("Starting reconciliation process")
    
    try:
        # Load data
        df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
        df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
        logger.info(f"Loaded {len(df_2b)} from 2B, {len(df_pr)} from PR")
        
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
                    logger.warning(f"Found {invalid_count} invalid GSTINs")
        
        # Filter reverse charge if needed
        if not include_rc:
            df_2b = df_2b[df_2b['REVERSE_CHARGE'] != 'YES'].copy()
            df_pr = df_pr[df_pr['REVERSE_CHARGE'] != 'YES'].copy()
            logger.info("Filtered reverse charge entries")
        
        # Create matching keys
        for df in [df_2b, df_pr]:
            df['PAN'] = df['SUPPLIER_GSTIN'].apply(extract_pan_from_gstin)
            df['NORM_DOC'] = df['DOC_NUMBER'].apply(normalize_document_number)
            df['MATCH_KEY'] = df['PAN'] + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE']
        
        # Check for duplicates in PR
        dup_pr_count = df_pr.duplicated(subset=['MATCH_KEY'], keep=False).sum()
        if dup_pr_count > 0:
            logger.warning(f"Found {dup_pr_count} duplicate MATCH_KEY in PR")
        
        # Perform outer merge
        merged = pd.merge(df_2b, df_pr, on='MATCH_KEY', how='outer', suffixes=('_2B', '_PR'), indicator=True)
        logger.info(f"Merged: {len(merged)} records")
        
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
        
        # Calculate date difference
        merged['DATE_DIFF_DAYS'] = merged.apply(
            lambda r: calculate_date_difference(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1
        )
        within_date_tol = merged['DATE_DIFF_DAYS'].notna() & (merged['DATE_DIFF_DAYS'] <= date_tol_days)
        
        # Financial year check
        if strict_fy:
            within_fy = merged.apply(lambda r: is_same_financial_year(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1)
        else:
            within_fy = pd.Series([True] * len(merged))
        
        # Fuzzy name matching
        if fuzzy_threshold < 100:
            merged['NAME_FUZZY_MATCH'] = merged.apply(
                lambda r: fuzzy_match_names(r['SUPPLIER_NAME_2B'], r['SUPPLIER_NAME_PR'], fuzzy_threshold), axis=1
            )
        else:
            merged['NAME_FUZZY_MATCH'] = pd.Series([True] * len(merged))
        
        # Define matching logic
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
            'All parameters matching exactly',
            'Date differs within tolerance, values close, same DOC_TYPE',
            'Document matches but amounts differ beyond tolerance',
            'Document matches but DOC_TYPE differs',
            'Matched on PAN, but State GSTIN differs',
            'Present in Purchase Register but missing in GSTR-2B',
            'Present in GSTR-2B but missing in Purchase Register'
        ]
        
        merged['MATCH_STATUS'] = np.select(conditions, statuses, default='Other')
        merged['MATCH_REASON'] = np.select(conditions, reasons, default='Unable to determine')
        merged['SUPPLIER_NAME_COMBINED'] = merged['SUPPLIER_NAME_2B'].combine_first(merged['SUPPLIER_NAME_PR']).fillna('Unknown')
        
        # ITC eligibility
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
        
        # Calculate stats
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
        }
        
        logger.info(f"Reconciliation completed in {processing_time:.2f}s")
        return merged, dup_pr_count, df_2b, df_pr, stats
        
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}", exc_info=True)
        raise

# ==================== ENHANCED EXCEL EXPORT (ERROR-FREE) ====================
def create_enhanced_excel_export(
    merged_df: pd.DataFrame,
    df_2b: pd.DataFrame,
    df_pr: pd.DataFrame,
    stats: Dict,
    include_charts: bool = True,
    include_raw_data: bool = True,
    add_dropdown: bool = True,
    include_subtotals: bool = False
) -> bytes:
    """
    Create enhanced Excel export - ERROR-FREE xlsxwriter API usage
    - NO subtotal formulas in Reconciliation sheet
    - Enhanced Summary with match status, charts, top 10 parties
    - Hyperlinks and formulas for easy navigation
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats - Using CORRECT xlsxwriter API
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#1e40af', 'font_color': 'white', 
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
            'font_size': 10
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00', 'border': 1, 'align': 'right'
        })
        
        text_format = workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'top'
        })
        
        link_format = workbook.add_format({
            'font_color': 'blue', 'underline': 1, 'border': 1
        })
        
        # Status formats - Using set_bold() NOT set_font_weight()
        status_formats = {
            'Exact': workbook.add_format({'bg_color': '#d1fae5', 'font_color': '#065f46', 'border': 1, 'bold': True}),
            'Suggested': workbook.add_format({'bg_color': '#cffafe', 'font_color': '#0e7490', 'border': 1, 'bold': True}),
            'Value Mismatch': workbook.add_format({'bg_color': '#fef3c7', 'font_color': '#92400e', 'border': 1, 'bold': True}),
            'Doc Type Mismatch': workbook.add_format({'bg_color': '#ede9fe', 'font_color': '#7c3aed', 'border': 1, 'bold': True}),
            'Cross-State (PAN Match)': workbook.add_format({'bg_color': '#e0e7ff', 'font_color': '#4f46e5', 'border': 1, 'bold': True}),
            'Missing in GSTR 2B': workbook.add_format({'bg_color': '#fee2e2', 'font_color': '#991b1b', 'border': 1, 'bold': True}),
            'Missing in PR': workbook.add_format({'bg_color': '#dbeafe', 'font_color': '#1e40af', 'border': 1, 'bold': True}),
        }
        
        title_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'bg_color': '#f1f5f9', 'border': 1, 'align': 'center'
        })
        
        # ==================== RECONCILIATION SHEET ====================
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
            'SECTION_NAME_2B', 'SECTION_NAME_PR',
            'ITC_ELIGIBILITY'
        ]].copy()
        
        recon_df.columns = [
            'Match Status', 'Match Reason', 'Supplier Name',
            'Supplier GSTIN (2B)', 'Supplier GSTIN (PR)', 'My GSTIN (2B)', 'My GSTIN (PR)',
            'Document Number (2B)', 'Document Number (PR)', 'Document Date (2B)', 'Document Date (PR)',
            'Total Value (2B)', 'Total Value (PR)',
            'Taxable (2B)', 'Taxable (PR)',
            'Taxable Diff', 'Total Tax (2B)', 'Total Tax (PR)',
            'IGST (2B)', 'IGST (PR)', 'CGST (2B)', 'CGST (PR)', 'SGST (2B)', 'SGST (PR)',
            'CESS (2B)', 'CESS (PR)',
            'Doc Type (2B)', 'Doc Type (PR)',
            'Section (2B)', 'Section (PR)',
            'ITC Eligibility'
        ]
        
        # Write reconciliation data - NO SUBTOTALS
        start_row = 3
        recon_df.to_excel(writer, sheet_name='Reconciliation', index=False, startrow=start_row)
        
        worksheet = writer.sheets['Reconciliation']
        
        # Write headers
        worksheet.merge_range(0, 0, 0, len(recon_df.columns)-1, 'GST Reconciliation Report', title_format)
        worksheet.write(1, 0, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', text_format)
        worksheet.write(2, 0, f'Total Records: {len(recon_df)}', text_format)
        
        # Write column headers
        for col_num, col_name in enumerate(recon_df.columns):
            worksheet.write(start_row, col_num, col_name, header_format)
        
        # Apply formatting to data rows
        for row_num in range(start_row + 1, len(recon_df) + start_row + 1):
            status = recon_df.iloc[row_num - start_row - 1]['Match Status']
            if status in status_formats:
                for col in range(len(recon_df.columns)):
                    worksheet.set_row(row_num - 1, None, status_formats[status])
            
            # Apply number formatting
            for col_num in range(12, 26):
                if col_num < len(recon_df.columns):
                    try:
                        val = recon_df.iloc[row_num - start_row - 1, col_num]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            worksheet.write_number(row_num, col_num, val, number_format)
                    except (ValueError, TypeError, IndexError):
                        pass
        
        # Add DOC_TYPE dropdown validation
        if add_dropdown:
            doc_type_2b_col = None
            doc_type_pr_col = None
            for idx, col in enumerate(recon_df.columns):
                if col == 'Doc Type (2B)':
                    doc_type_2b_col = idx
                elif col == 'Doc Type (PR)':
                    doc_type_pr_col = idx
            
            if doc_type_2b_col is not None:
                worksheet.data_validation(start_row + 1, doc_type_2b_col, start_row + len(recon_df), doc_type_2b_col, 
                                        {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
            if doc_type_pr_col is not None:
                worksheet.data_validation(start_row + 1, doc_type_pr_col, start_row + len(recon_df), doc_type_pr_col, 
                                        {'validate': 'list', 'source': ['INVOICE', 'CREDIT', 'DEBIT']})
        
        # Set column widths
        col_widths = [18, 45, 35, 20, 20, 20, 20, 22, 22, 14, 14, 18, 18, 16, 16, 14, 16, 16, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 18]
        for idx, width in enumerate(col_widths):
            if idx < len(recon_df.columns):
                worksheet.set_column(idx, idx, width)
        
        worksheet.freeze_panes(start_row + 1, 0)
        
        # ==================== ENHANCED SUMMARY SHEET ====================
        summary_ws = workbook.add_worksheet('Summary')
        
        summary_ws.merge_range('A1:F1', '📊 GST Reconciliation Summary Dashboard', title_format)
        summary_ws.write('A2', f'Report Generated: {datetime.now().strftime("%d-%b-%Y %I:%M %p")}', text_format)
        summary_ws.write('A3', f'Processing Time: {stats.get("processing_time_sec", 0):.2f} seconds', text_format)
        
        row_idx = 5
        
        # Key Metrics
        summary_ws.merge_range(f'A{row_idx}:C{row_idx}', '🔑 Key Metrics', header_format)
        row_idx += 1
        
        metrics = [
            ('Total Records Processed', stats.get('merged_records', 0)),
            ('Exact Matches', stats.get('exact_matches', 0)),
            ('Suggested Matches', stats.get('suggested_matches', 0)),
            ('Value Mismatches', stats.get('value_mismatches', 0)),
            ('Missing in GSTR-2B', stats.get('missing_in_2b', 0)),
            ('Missing in PR', stats.get('missing_in_pr', 0)),
        ]
        
        for label, value in metrics:
            summary_ws.write(f'A{row_idx}', label, text_format)
            summary_ws.write(f'C{row_idx}', value, number_format)
            row_idx += 1
        
        # Match Status Breakdown with Formulas & Links
        summary_ws.merge_range(f'A{row_idx}:F{row_idx}', '📋 Match Status Details (Click to View)', header_format)
        row_idx += 1
        
        headers = ['Status', 'Count', 'Formula', 'Taxable (2B)', 'Taxable (PR)', 'Quick Link']
        for col, header in enumerate(headers):
            summary_ws.write(row_idx, col, header, header_format)
        row_idx += 1
        
        status_breakdown = merged_df['MATCH_STATUS'].value_counts()
        status_values = {}
        
        for status in ['Exact', 'Suggested', 'Value Mismatch', 'Doc Type Mismatch', 'Cross-State (PAN Match)', 'Missing in GSTR 2B', 'Missing in PR']:
            mask = merged_df['MATCH_STATUS'] == status
            count = mask.sum()
            taxable_2b = merged_df.loc[mask, 'TAXABLE_VALUE_2B'].sum()
            taxable_pr = merged_df.loc[mask, 'TAXABLE_VALUE_PR'].sum()
            status_values[status] = {'count': count, 'taxable_2b': taxable_2b, 'taxable_pr': taxable_pr}
            
            summary_ws.write(row_idx, 0, status, text_format)
            summary_ws.write(row_idx, 1, count, number_format)
            summary_ws.write_formula(row_idx, 2, f'=COUNTIF(Reconciliation!A:A, "{status}")', number_format)
            summary_ws.write(row_idx, 3, taxable_2b, number_format)
            summary_ws.write(row_idx, 4, taxable_pr, number_format)
            summary_ws.write_url(row_idx, 5, f"internal:'Reconciliation'!A1", string='View', format=link_format)
            
            row_idx += 1
        
        # Document Type Breakdown
        summary_ws.merge_range(f'A{row_idx}:E{row_idx}', '📑 Document Type Analysis', header_format)
        row_idx += 1
        
        dt_headers = ['Doc Type', 'Count (2B)', 'Taxable (2B)', 'Count (PR)', 'Taxable (PR)']
        for col, header in enumerate(dt_headers):
            summary_ws.write(row_idx, col, header, header_format)
        row_idx += 1
        
        for doc_type in ['INVOICE', 'CREDIT', 'DEBIT']:
            count_2b = (df_2b['DOC_TYPE'] == doc_type).sum()
            taxable_2b = df_2b.loc[df_2b['DOC_TYPE'] == doc_type, 'TAXABLE_VALUE'].sum()
            count_pr = (df_pr['DOC_TYPE'] == doc_type).sum()
            taxable_pr = df_pr.loc[df_pr['DOC_TYPE'] == doc_type, 'TAXABLE_VALUE'].sum()
            
            summary_ws.write(row_idx, 0, doc_type, text_format)
            summary_ws.write(row_idx, 1, count_2b, number_format)
            summary_ws.write(row_idx, 2, taxable_2b, number_format)
            summary_ws.write(row_idx, 3, count_pr, number_format)
            summary_ws.write(row_idx, 4, taxable_pr, number_format)
            row_idx += 1
        
        # Top 10 Parties from GSTR-2B
        summary_ws.merge_range(f'A{row_idx}:D{row_idx}', '🏆 Top 10 Suppliers (GSTR-2B)', header_format)
        row_idx += 1
        
        top_10_2b = df_2b.groupby('SUPPLIER_NAME')['TAXABLE_VALUE'].sum().nlargest(10).reset_index()
        top_10_2b.columns = ['Supplier Name', 'Total Taxable Value']
        
        summary_ws.write(row_idx, 0, 'Rank', header_format)
        summary_ws.write(row_idx, 1, 'Supplier Name', header_format)
        summary_ws.write(row_idx, 2, 'Total Taxable (₹)', header_format)
        summary_ws.write(row_idx, 3, 'Link', header_format)
        row_idx += 1
        
        for rank, (_, row) in enumerate(top_10_2b.iterrows(), 1):
            summary_ws.write(row_idx, 0, rank, number_format)
            summary_ws.write(row_idx, 1, row['Supplier Name'], text_format)
            summary_ws.write(row_idx, 2, row['Total Taxable Value'], number_format)
            summary_ws.write_url(row_idx, 3, f"internal:'Reconciliation'!A1", string='View Records', format=link_format)
            row_idx += 1
        
        row_idx += 2
        
        # Top 10 Parties from Purchase Register
        summary_ws.merge_range(f'A{row_idx}:D{row_idx}', '🏆 Top 10 Suppliers (Purchase Register)', header_format)
        row_idx += 1
        
        top_10_pr = df_pr.groupby('SUPPLIER_NAME')['TAXABLE_VALUE'].sum().nlargest(10).reset_index()
        top_10_pr.columns = ['Supplier Name', 'Total Taxable Value']
        
        summary_ws.write(row_idx, 0, 'Rank', header_format)
        summary_ws.write(row_idx, 1, 'Supplier Name', header_format)
        summary_ws.write(row_idx, 2, 'Total Taxable (₹)', header_format)
        summary_ws.write(row_idx, 3, 'Link', header_format)
        row_idx += 1
        
        for rank, (_, row) in enumerate(top_10_pr.iterrows(), 1):
            summary_ws.write(row_idx, 0, rank, number_format)
            summary_ws.write(row_idx, 1, row['Supplier Name'], text_format)
            summary_ws.write(row_idx, 2, row['Total Taxable Value'], number_format)
            summary_ws.write_url(row_idx, 3, f"internal:'Reconciliation'!A1", string='View Records', format=link_format)
            row_idx += 1
        
        # Formulas Reference
        row_idx += 2
        summary_ws.merge_range(f'A{row_idx}:C{row_idx}', '📐 Formula Reference', header_format)
        row_idx += 1
        
        formulas = [
            ('Exact Match Count', '=COUNTIF(Reconciliation!A:A, "Exact")', 'Counts exact matches'),
            ('Suggested Match Count', '=COUNTIF(Reconciliation!A:A, "Suggested")', 'Counts suggested matches'),
            ('Missing in 2B', '=COUNTIF(Reconciliation!A:A, "Missing in GSTR 2B")', 'Records in PR not in 2B'),
            ('Missing in PR', '=COUNTIF(Reconciliation!A:A, "Missing in PR")', 'Records in 2B not in PR'),
            ('Match Rate %', '=(B7+B8)/B6*100', 'Percentage of matched records'),
            ('Total Taxable (2B)', '=SUM(Reconciliation!O:O)', 'Sum of taxable from GSTR-2B'),
            ('Total Taxable (PR)', '=SUM(Reconciliation!P:P)', 'Sum of taxable from Purchase Register'),
        ]
        
        for formula_name, formula, description in formulas:
            summary_ws.write(row_idx, 0, formula_name, text_format)
            summary_ws.write(row_idx, 1, formula, text_format)
            summary_ws.write(row_idx, 2, description, text_format)
            row_idx += 1
        
        # Set column widths for Summary
        summary_ws.set_column('A:A', 35)
        summary_ws.set_column('B:B', 15)
        summary_ws.set_column('C:C', 45)
        summary_ws.set_column('D:D', 20)
        summary_ws.set_column('E:E', 20)
        summary_ws.set_column('F:F', 15)
        
        # ==================== CHARTS SHEET ====================
        if include_charts:
            charts_ws = workbook.add_worksheet('Charts')
            charts_ws.write('A1', '📈 Visual Analytics', title_format)
            
            # Match Status Chart Data
            chart_data = []
            for status in ['Exact', 'Suggested', 'Value Mismatch', 'Missing in GSTR 2B', 'Missing in PR']:
                chart_data.append([status, status_values.get(status, {}).get('count', 0)])
            
            charts_ws.write('A3', 'Match Status', header_format)
            charts_ws.write('B3', 'Count', header_format)
            
            for idx, (status, count) in enumerate(chart_data, start=4):
                charts_ws.write(f'A{idx}', status, text_format)
                charts_ws.write(f'B{idx}', count, number_format)
            
            # Create chart
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Match Status Distribution',
                'categories': '=Charts!$A$4:$A$8',
                'values': '=Charts!$B$4:$B$8',
                'data_labels': {'value': True},
            })
            chart.set_title({'name': 'Reconciliation Status Distribution'})
            chart.set_x_axis({'name': 'Match Status'})
            chart.set_y_axis({'name': 'Number of Records'})
            charts_ws.insert_chart('D3', chart, {'x_scale': 1.5, 'y_scale': 1.5})
            
            # Top 10 Parties Chart
            charts_ws.write('A20', 'Top 10 Suppliers (GSTR-2B)', header_format)
            
            for idx, (_, row) in enumerate(top_10_2b.head(10).iterrows(), start=21):
                charts_ws.write(f'A{idx}', row['Supplier Name'][:30], text_format)
                charts_ws.write(f'B{idx}', row['Total Taxable Value'], number_format)
            
            chart2 = workbook.add_chart({'type': 'bar'})
            chart2.add_series({
                'name': 'Taxable Value',
                'categories': '=Charts!$A$21:$A$30',
                'values': '=Charts!$B$21:$B$30',
                'data_labels': {'value': True, 'position': 'end'},
            })
            chart2.set_title({'name': 'Top 10 Suppliers by Taxable Value (GSTR-2B)'})
            chart2.set_x_axis({'name': 'Taxable Value (₹)'})
            chart2.set_y_axis({'name': 'Supplier'})
            charts_ws.insert_chart('D20', chart2, {'x_scale': 1.5, 'y_scale': 1.5})
        
        # ==================== RAW DATA SHEETS ====================
        if include_raw_data:
            df_2b.to_excel(writer, sheet_name='Raw_GSTR2B', index=False)
            df_pr.to_excel(writer, sheet_name='Raw_PurchaseRegister', index=False)
            
            for sheet_name in ['Raw_GSTR2B', 'Raw_PurchaseRegister']:
                ws = writer.sheets[sheet_name]
                ws.set_column('A:Z', 15)
                ws.freeze_panes(1, 0)
    
    return output.getvalue()


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
            
            # DOC_TYPE BREAKDOWN
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
            
            # Financial metrics
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
                    <span class="metric-icon">📋</span>
                    <div class="metric-label">Total Records</div>
                    <div class="metric-value">{total_records:,}</div>
                    <div class="metric-subtitle">All documents processed</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                delta_class = 'positive' if match_rate >= 80 else 'warning' if match_rate >= 60 else 'negative'
                delta_text = '✓ Excellent' if match_rate >= 90 else '✓ Good' if match_rate >= 80 else '⚠ Review'
                st.markdown(f"""
                <div class="metric-card">
                    <span class="metric-icon">✅</span>
                    <div class="metric-label">Match Rate</div>
                    <div class="metric-value">{match_rate:.1f}%</div>
                    <div class="metric-delta {delta_class}">{delta_text}</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <span class="metric-icon">🔍</span>
                    <div class="metric-label">Suggested</div>
                    <div class="metric-value">{suggested_count:,}</div>
                    <div class="metric-subtitle">Needs manual review</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <span class="metric-icon">💰</span>
                    <div class="metric-label">Unclaimed ITC</div>
                    <div class="metric-value">{format_currency(unclaimed_itc)}</div>
                    <div class="metric-delta positive">Cash flow opportunity</div>
                </div>
                """, unsafe_allow_html=True)
            with m5:
                st.markdown(f"""
                <div class="metric-card">
                    <span class="metric-icon">⚠️</span>
                    <div class="metric-label">Risk Claims</div>
                    <div class="metric-value">{format_currency(risky_claims)}</div>
                    <div class="metric-delta negative">Compliance risk</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== MATCH STATUS SUMMARY ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📋</span> Match Status Breakdown</h3>
                <p style="color: var(--text-secondary); margin-bottom: 18px; font-weight: 500;">
                    Detailed breakdown with direct links to filtered views.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            status_cards = [
                {'status': 'Exact', 'count': exact_count, 'desc': 'Perfect matches - GSTIN, Doc No, Type & Values identical', 'color': 'exact', 'icon': '✅', 'link': 'View Exact Matches →'},
                {'status': 'Suggested', 'count': suggested_count, 'desc': 'Potential matches - Date differs within tolerance, values close', 'color': 'suggested', 'icon': '🔍', 'link': 'Review Suggested →'},
                {'status': 'Value Mismatch', 'count': int(status_counts.get('Value Mismatch', 0)), 'desc': 'Same document but taxable/tax amounts differ beyond tolerance', 'color': 'mismatch', 'icon': '⚠️', 'link': 'Check Mismatches →'},
                {'status': 'Missing in PR', 'count': missing_pr, 'desc': 'Present in GSTR-2B but not recorded in Purchase Register', 'color': 'missing-pr', 'icon': '📥', 'link': 'Add to Books →'},
                {'status': 'Missing in GSTR 2B', 'count': missing_2b, 'desc': 'Claimed in books but not appearing in GSTR-2B', 'color': 'missing-2b', 'icon': '🔎', 'link': 'Verify Claims →'},
            ]
            
            cols = st.columns(len(status_cards))
            for idx, card in enumerate(status_cards):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="match-status-card {card['color']}">
                        <div class="status-header">
                            <span class="status-name">{card['icon']} {card['status']}</span>
                            <span class="status-count">{card['count']:,}</span>
                        </div>
                        <div class="status-details">{card['desc']}</div>
                        <div class="status-link">🔗 {card['link']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ==================== TOP 10 PARTIES ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">🏆</span> Top 10 Suppliers Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("#### 📊 Top 10 from GSTR-2B")
                top_10_2b = df_2b.groupby('SUPPLIER_NAME')['TAXABLE_VALUE'].sum().nlargest(10).reset_index()
                top_10_2b.columns = ['Supplier', 'Taxable Value']
                
                for idx, row in top_10_2b.iterrows():
                    st.markdown(f"""
                    <div class="party-card">
                        <div class="party-info">
                            <div class="party-name">#{idx+1} {row['Supplier'][:40]}{'...' if len(row['Supplier'])>40 else ''}</div>
                        </div>
                        <div class="party-stats">
                            <div class="party-value">{format_currency(row['Taxable Value'])}</div>
                            <div class="party-label">Taxable</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_top2:
                st.markdown("#### 📊 Top 10 from Purchase Register")
                top_10_pr = df_pr.groupby('SUPPLIER_NAME')['TAXABLE_VALUE'].sum().nlargest(10).reset_index()
                top_10_pr.columns = ['Supplier', 'Taxable Value']
                
                for idx, row in top_10_pr.iterrows():
                    st.markdown(f"""
                    <div class="party-card">
                        <div class="party-info">
                            <div class="party-name">#{idx+1} {row['Supplier'][:40]}{'...' if len(row['Supplier'])>40 else ''}</div>
                        </div>
                        <div class="party-stats">
                            <div class="party-value">{format_currency(row['Taxable Value'])}</div>
                            <div class="party-label">Taxable</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ==================== CHARTS ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📈</span> Visual Analytics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Status", "📑 Doc Types", "🏆 Top Parties", "🔍 Details"])
            
            with tab1:
                status_data = merged_df['MATCH_STATUS'].value_counts().reset_index()
                status_data.columns = ['Status', 'Count']
                color_map = {
                    'Exact': '#10b981', 'Suggested': '#06b6d4', 'Value Mismatch': '#f97316', 
                    'Doc Type Mismatch': '#8b5cf6', 'Cross-State (PAN Match)': '#6366f1', 
                    'Missing in GSTR 2B': '#ef4444', 'Missing in PR': '#3b82f6', 'Other': '#64748b'
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
                    'GSTR-2B Taxable': [doc_type_stats['INVOICE_2B_taxable'], doc_type_stats['CREDIT_2B_taxable'], doc_type_stats['DEBIT_2B_taxable']],
                    'Purchase Register Taxable': [doc_type_stats['INVOICE_PR_taxable'], doc_type_stats['CREDIT_PR_taxable'], doc_type_stats['DEBIT_PR_taxable']]
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
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("##### Top 10 Suppliers - GSTR-2B")
                    fig_top2b = px.bar(
                        top_10_2b.head(10), x='Taxable Value', y='Supplier',
                        orientation='h', title='Top 10 by Taxable Value (2B)',
                        color='Taxable Value', color_continuous_scale='Blues'
                    )
                    fig_top2b.update_layout(height=400, margin=dict(t=40, b=40, l=20, r=20))
                    st.plotly_chart(fig_top2b, use_container_width=True)
                
                with col_chart2:
                    st.markdown("##### Top 10 Suppliers - Purchase Register")
                    fig_toppr = px.bar(
                        top_10_pr.head(10), x='Taxable Value', y='Supplier',
                        orientation='h', title='Top 10 by Taxable Value (PR)',
                        color='Taxable Value', color_continuous_scale='Greens'
                    )
                    fig_toppr.update_layout(height=400, margin=dict(t=40, b=40, l=20, r=20))
                    st.plotly_chart(fig_toppr, use_container_width=True)
            
            with tab4:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    status_filter = st.multiselect("Filter Status", merged_df['MATCH_STATUS'].unique().tolist(), default=merged_df['MATCH_STATUS'].unique().tolist(), key="status_filter_multiselect")
                with col_f2:
                    search = st.text_input("🔎 Search Supplier", placeholder="Type to search...", key="supplier_search")
                with col_f3:
                    min_val = st.number_input("Min Value (₹)", min_value=0, value=0, step=1000, key="min_value_filter")
                
                filtered = merged_df.copy()
                if status_filter:
                    filtered = filtered[filtered['MATCH_STATUS'].isin(status_filter)]
                if search:
                    filtered = filtered[filtered['SUPPLIER_NAME_COMBINED'].str.contains(search, case=False, na=False)]
                if min_val > 0:
                    filtered = filtered[(filtered['TAXABLE_VALUE_2B'].abs() >= min_val) | (filtered['TAXABLE_VALUE_PR'].abs() >= min_val)]
                
                display_cols = ['MATCH_STATUS', 'SUPPLIER_NAME_COMBINED', 'DOC_TYPE_2B', 'DOC_NUMBER_2B', 'DOC_NUMBER_PR', 'TAXABLE_VALUE_2B', 'TAXABLE_VALUE_PR', 'TOTAL_TAX_2B', 'TOTAL_TAX_PR', 'ITC_ELIGIBILITY']
                
                def apply_status_styling(val):
                    return get_status_css_class(val)
                
                styled_df = filtered[display_cols].head(100).style.format({
                    'TAXABLE_VALUE_2B': '₹{:.2f}', 'TAXABLE_VALUE_PR': '₹{:.2f}', 
                    'TOTAL_TAX_2B': '₹{:.2f}', 'TOTAL_TAX_PR': '₹{:.2f}'
                }).map(apply_status_styling, subset=['MATCH_STATUS'])
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
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
                insights.append({'type': 'success', 'icon': '💡', 'title': 'Cash Flow Opportunity', 'message': f"**{format_currency(unclaimed_itc)}** in ITC available in GSTR-2B but not claimed. Consider claiming."})
            if missing_2b > 0:
                insights.append({'type': 'error', 'icon': '🚨', 'title': 'Compliance Risk', 'message': f"**{format_currency(risky_claims)}** claimed in books but missing from GSTR-2B. May lead to ITC reversal."})
            if match_rate < 80:
                insights.append({'type': 'warning', 'icon': '🔄', 'title': 'Reconciliation Health', 'message': f"Match rate is **{match_rate:.1f}%**. Review document numbering and date formats."})
            elif match_rate >= 95:
                insights.append({'type': 'success', 'icon': '✅', 'title': 'Excellent Health', 'message': f"Outstanding match rate of **{match_rate:.1f}%**! GST compliance is excellent."})
            if suggested_count > 0:
                insights.append({'type': 'info', 'icon': '🕒', 'title': 'Date Mismatches', 'message': f"**{suggested_count} records** have date differences within tolerance. Review for accurate reporting."})
            if not insights:
                insights.append({'type': 'success', 'icon': '🎉', 'title': 'All Clear', 'message': "No critical issues detected. GST reconciliation is healthy!"})
            
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div class="insight-card {insight['type']} animate-fade-in" style="animation-delay: {i*0.1}s">
                    <span class="insight-icon">{insight['icon']}</span>
                    <div class="insight-content">
                        <div class="insight-title">{insight['title']}</div>
                        <div class="insight-message">{insight['message']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== EXPORT SECTION ====================
            st.markdown("""
            <div class="section-card animate-fade-in">
                <h3><span class="icon">📤</span> Export Enhanced Report</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_export1, col_export2 = st.columns([3, 1])
            with col_export1:
                st.markdown("""
                <div style="background: rgba(79, 70, 229, 0.05); border-radius: 12px; padding: 18px; border: 2px solid var(--border-color);">
                    <strong>📋 Enhanced Report Includes:</strong>
                    <ul style="margin: 8px 0 0 20px; color: var(--text-secondary); line-height: 1.7; font-weight: 500;">
                        <li>✅ <strong>Reconciliation Sheet</strong> - All columns, NO subtotal formulas</li>
                        <li>📊 <strong>Enhanced Summary</strong> with match status, formulas, hyperlinks</li>
                        <li>🏆 <strong>Top 10 Parties</strong> from 2B & PR with clickable links</li>
                        <li>📈 <strong>Charts Sheet</strong> - Visual analytics (if enabled)</li>
                        <li>📑 <strong>Raw Data Sheets</strong> - Complete audit trail</li>
                        <li>🔽 <strong>DOC_TYPE dropdown</strong> validation</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col_export2:
                excel_output = create_enhanced_excel_export(
                    merged_df, df_2b, df_pr, stats,
                    include_charts=include_charts,
                    include_raw_data=include_raw_data,
                    add_dropdown=add_dropdown_validation,
                    include_subtotals=False
                )
                
                st.download_button(
                    label="⚡ Download Enhanced Excel", 
                    data=excel_output, 
                    file_name=f"GST_Recon_Enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    use_container_width=True,
                    key="btn_download_excel_enhanced",
                    help="Download comprehensive report with enhanced summary"
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
            
            st.success(f"✅ Ready! Processed {total_records:,} records in {stats['processing_time_sec']}s with enhanced export.")
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        st.error(f"❌ Processing Error: {str(e)}")
        with st.expander("🔧 Technical Details"):
            st.exception(e)
            st.info("""
            💡 **Troubleshooting:**
            - Ensure files follow sample template format
            - DOC_TYPE: INVOICE, CREDIT, or DEBIT
            - Credit Notes: Use negative values
            - GSTIN: Valid 15-character format
            - Dates: DD-MM-YYYY, YYYY-MM-DD, or DD/MM/YYYY
            """)

else:
    st.markdown("""
    <div class="section-card animate-fade-in" style="text-align: center; padding: 56px 40px;">
        <div style="font-size: 4rem; margin-bottom: 20px; display: inline-flex; align-items: center; justify-content: center; width: 110px; height: 110px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: var(--radius-xl); color: white; box-shadow: var(--shadow-2xl); font-weight: 700;">🧾✨</div>
        <h2 style="margin: 0 0 16px 0; font-size: 1.9rem; font-weight: 800;">Welcome to GST Recon Pro v6.0</h2>
        <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 680px; margin: 0 auto 32px auto; line-height: 1.7; font-weight: 500;">
            Upload your GSTR-2B and Purchase Register files to begin intelligent reconciliation. 
            AI-powered matching, Credit/Debit Note support, compliance reports, enterprise security.
        </p>
        <div class="quick-actions">
            <div class="quick-action-btn"><span class="icon">📁</span><span class="label">Upload Files</span></div>
            <div class="quick-action-btn"><span class="icon">📥</span><span class="label">Get Samples</span></div>
            <div class="quick-action-btn"><span class="icon">📉</span><span class="label">CDN Support</span></div>
            <div class="quick-action-btn"><span class="icon">📊</span><span class="label">Live Insights</span></div>
        </div>
        <div style="margin-top: 40px; padding-top: 24px; border-top: 2px solid var(--border-color);">
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; font-weight: 500;">
                <strong>💡 Pro Tips:</strong><br>
                • Credit Notes: <strong>negative taxable/tax values</strong><br>
                • DOC_TYPE: INVOICE / CREDIT / DEBIT<br>
                • Month: <strong>JANUARY-25, FEBRUARY-25</strong><br>
                • GSTIN: 15 characters (e.g., 36AADCR6281N1ZT)<br>
                • Press <strong>Ctrl+T</strong> to toggle theme
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
    <div class="version">v6.0.3 • Error-Free • Enhanced UI • May 2026</div>
    <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;">📚 Documentation</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;">🎥 Tutorials</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;">🔧 Support</a>
        <a href="#" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;">🐛 Report Bug</a>
    </div>
    <div style="margin-top: 14px; font-size: 0.8rem; color: var(--text-tertiary); font-weight: 500;">
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
        const exportBtn = document.querySelector('button[title*="Download"]');
        if (exportBtn) exportBtn.click();
    }
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const exportBtn = document.querySelector('button[kind="primary"]');
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
    st.info("📥 Sample templates downloaded. Please upload to begin reconciliation.")
    st.session_state.load_sample = False

# ==================== ERROR HANDLING ====================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    st.error(f"💥 Unexpected Error: {exc_value}")
    st.info("Please refresh or contact support if issue persists.")

sys.excepthook = global_exception_handler

# ==================== PERFORMANCE MONITORING ====================
if 'page_load_start' not in st.session_state:
    st.session_state.page_load_start = time.time()
else:
    load_time = time.time() - st.session_state.page_load_start
    if load_time > 5:
        logger.warning(f"Page load time: {load_time:.2f}s")

# ==================== END OF APPLICATION ====================
