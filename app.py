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
    page_title="GST Recon Pro", 
    page_icon="🧾",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ================= COMPREHENSIVE THEME-ADAPTIVE CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    h1 {
        font-weight: 800 !important;
        font-size: 2.8rem !important;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    h2 {
        font-weight: 700 !important;
        color: #1e293b;
        border-left: 4px solid #2563eb;
        padding-left: 12px;
        margin: 2rem 0 1rem 0;
    }

    h3 {
        font-weight: 600 !important;
        color: #334155;
    }

    .subtitle {
        font-size: 1.15rem;
        color: #64748b;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white !important;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5);
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 22px 18px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }

    [data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 2rem;
        color: #1e293b;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 500;
    }

    .insight-box {
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 16px;
        border-left: 5px solid #2563eb;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(37, 99, 235, 0.03));
        border: 1px solid rgba(37, 99, 235, 0.15);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .insight-box.warning {
        border-left-color: #f97316;
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.08), rgba(249, 115, 22, 0.03));
        border-color: rgba(249, 115, 22, 0.15);
    }

    .insight-box.success {
        border-left-color: #10b981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03));
        border-color: rgba(16, 185, 129, 0.15);
    }

    .insight-box.error {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.03));
        border-color: rgba(239, 68, 68, 0.15);
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.6);
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(8px);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .web-branding {
        text-align: center;
        margin-top: 60px;
        padding: 28px 20px;
        border-top: 1px solid rgba(226, 232, 240, 0.8);
        background: rgba(255, 255, 255, 0.7);
        border-radius: 16px 16px 0 0;
        font-size: 0.95rem;
        color: #64748b;
    }

    .web-branding b {
        color: #2563eb;
        letter-spacing: 0.5px;
        font-weight: 700;
    }

    .section-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.8);
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-exact { background: #dcfce7; color: #166534; }
    .status-suggested { background: #cffafe; color: #0e7490; }
    .status-mismatch { background: #fee2e2; color: #991b1b; }
    .status-missing-2b { background: #ede9fe; color: #5b21b6; }
    .status-missing-pr { background: #ffedd5; color: #9a3412; }

    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        [data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(255,255,255,0.1);
        }
        [data-testid="stMetricValue"] {
            color: #f1f5f9;
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8;
        }
        .insight-box {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(37, 99, 235, 0.08));
            border-color: rgba(37, 99, 235, 0.3);
        }
        .section-card {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(255,255,255,0.1);
        }
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR CONFIGURATION =================
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")
    st.markdown("---")
    
    # Tolerance Settings
    st.markdown("#### 🎯 Matching Tolerance")
    tolerance = st.number_input(
        "Tax/Taxable Value Tolerance (₹)", 
        min_value=0, 
        max_value=1000, 
        value=20, 
        step=1,
        help="Maximum allowed difference for fuzzy matching"
    )
    
    date_tolerance = st.number_input(
        "Date Tolerance (Days)", 
        min_value=0, 
        max_value=30, 
        value=7, 
        step=1,
        help="Maximum date difference for suggested matches"
    )
    
    st.markdown("---")
    
    # Processing Settings
    st.markdown("#### ⚡ Processing Options")
    max_rows = st.number_input(
        "Max Rows for Excel Formulas", 
        min_value=1000, 
        max_value=100000, 
        value=15000, 
        step=1000
    )
    
    include_reverse_charge = st.checkbox(
        "Include Reverse Charge Transactions", 
        value=True
    )
    
    auto_claim_itc = st.checkbox(
        "Auto-mark ITC Eligible for Exact Matches", 
        value=True
    )
    
    st.markdown("---")
    
    # Export Settings
    st.markdown("#### 📤 Export Settings")
    include_charts = st.checkbox("Include Charts in Excel", value=True)
    include_raw_data = st.checkbox("Include Raw Data Sheets", value=True)
    
    st.markdown("---")
    st.info("💡 **Pro Tip:** Use sample templates below to understand the expected file format.")

# ================= HEADER SECTION =================
st.markdown("<h1>🧾 GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Enterprise-grade GST reconciliation engine with AI-powered invoice matching, financial insights, and compliance reporting. Seamlessly reconcile GSTR-2B with your Purchase Register.</p>', unsafe_allow_html=True)

# ================= SAMPLE TEMPLATE GENERATORS =================
def generate_sample_2b_template():
    """Generate sample GSTR-2B Excel file matching the expected input format"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE"
    ]
    
    sample_data = [
        # Exact matches - Invoices
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "2023-07", "INVOICE", "NO"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "2023-05", "INVOICE", "NO"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "2024-01", "INVOICE", "NO"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "2024-01", "INVOICE", "NO"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO"],
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4582.00, 0, 412.38, 412.38, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "2023-07", "INVOICE", "NO"],
        
        # Suggested matches - Date differs but within FY
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "03-05-2023", "2023-05", "INVOICE", "NO"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "07-07-2023", "2023-07", "INVOICE", "NO"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "25-04-2023", "2023-04", "INVOICE", "NO"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "15-01-2024", "2024-01", "INVOICE", "NO"],
        
        # Credit Notes (negative values)
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02", "CREDIT", "NO"],
        
        # Missing in PR (present in 2B only)
        ["36AADCR6281N1ZT", "67186859-1D", 8579.40, 0, 772.11, 772.11, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "01-01-2024", "2024-01", "INVOICE", "NO"],
        ["36CKUPB7102C1ZF", "BEW/23-24/53", 3500.00, 0, 315.00, 315.00, "BALAJI ENGINEERING WORKS", "36ADXFS5154R1ZU", "29-09-2023", "2023-09", "INVOICE", "NO"],
        ["36AAJCS4517L1ZZ", "362311I000806960", 11388.88, 0, 1025.00, 1025.00, "STAR HEALTH AND ALLIED INSURANCE COMPANY LIMITED", "36ADXFS5154R1ZU", "13-11-2023", "2023-11", "INVOICE", "NO"],
        ["36AADCR6281N1ZT", "71936233-1D", 6987.59, 0, 628.89, 628.89, "CARE HEALTH INSURANCE LIMITED", "36ADXFS5154R1ZU", "01-12-2023", "2023-12", "INVOICE", "NO"],
        ["36AXXPS8501J1ZN", "34/2022-23", 90000.00, 0, 2250.00, 2250.00, "SRINIVASA CATERERS", "36ADXFS5154R1ZU", "01-11-2022", "2023-04", "INVOICE", "NO"],
        
        # Reverse Charge
        ["29AAOCA4995P1ZH", "RC/2023/001", 5000.00, 900.00, 0, 0, "REVERSE CHARGE SUPPLIER", "36ADXFS5154R1ZU", "15-06-2023", "2023-06", "INVOICE", "YES"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="GSTR_2B_Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["GSTR_2B_Data"]
        
        # Header formatting
        header_format = workbook.add_format({
            "bold": True, "bg_color": "#1e40af", "font_color": "white",
            "border": 1, "align": "center", "valign": "vcenter"
        })
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        
        # Column widths
        worksheet.set_column('A:A', 20)  # SUPPLIER GSTIN
        worksheet.set_column('B:B', 22)  # DOCUMENT NUMBER
        worksheet.set_column('C:F', 14)  # Tax values
        worksheet.set_column('G:G', 35)  # SUPPLIER NAME
        worksheet.set_column('H:H', 20)  # MY GSTIN
        worksheet.set_column('I:I', 14)  # DOCUMENT DATE
        worksheet.set_column('J:J', 10)  # MONTH
        worksheet.set_column('K:L', 12)  # DOC_TYPE, REVERSE_CHARGE
        
    return output.getvalue()


def generate_sample_books_template():
    """Generate sample Purchase Register Excel file matching expected input format"""
    cols = [
        "SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", 
        "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOC_TYPE", "REVERSE_CHARGE",
        "ITC_CLAIM_TYPE", "PLACE_OF_SUPPLY"
    ]
    
    sample_data = [
        # Exact matches with 2B
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "2023-07", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0, 0, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "2024-01", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "2024-01", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36BDJPM4292D2ZF", "11/23-24", 153026.00, 0, 13772.34, 13772.34, "SANJAY MANDAL LABOUR CONTRACTOR", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36AGIPG4790K1Z0", "GST-23-24/157", 4582.00, 0, 412.38, 412.38, "S K ENGINEERS", "36ADXFS5154R1ZU", "06-07-2023", "2023-07", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        
        # Suggested matches - Date differs but within FY
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650.00, 0, 2128.50, 2128.50, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "01-06-2023", "2023-06", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["36ADXFS5161J1ZB", "INV/23-24/0092", 2470.00, 0, 222.30, 222.30, "SD WoT", "36ADXFS5154R1ZU", "01-09-2023", "2023-09", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["27AIXPL7527J1ZF", "VT/23-24/045", 14700.00, 2646.00, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-05-2023", "2023-05", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        ["27AIXPL7527J1ZF", "VT/23-24/312", 31290.00, 5632.20, 0, 0, "VICTORY TOOLS", "36ADXFS5154R1ZU", "01-02-2024", "2024-02", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
        
        # Credit Notes
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02", "CREDIT", "NO", "ELIGIBLE", "TELANGANA"],
        
        # Missing in 2B (present in Books only)
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
        
        # Mismatch example
        ["36AAACU2414K1ZG", "Z", 300.00, 0, 27.00, 27.00, "AXIS BANK LTD", "36ADXFS5154R1ZU", "07-11-2023", "2023-11", "INVOICE", "NO", "ELIGIBLE", "TELANGANA"],
    ]
    
    df_sample = pd.DataFrame(sample_data, columns=cols)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="Purchase_Register", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Purchase_Register"]
        
        # Header formatting
        header_format = workbook.add_format({
            "bold": True, "bg_color": "#1e40af", "font_color": "white",
            "border": 1, "align": "center", "valign": "vcenter"
        })
        for col_num, col_name in enumerate(cols):
            worksheet.write(0, col_num, col_name, header_format)
        
        # Column widths
        worksheet.set_column('A:A', 20)  # SUPPLIER GSTIN
        worksheet.set_column('B:B', 22)  # DOCUMENT NUMBER
        worksheet.set_column('C:F', 14)  # Tax values
        worksheet.set_column('G:G', 35)  # SUPPLIER NAME
        worksheet.set_column('H:H', 20)  # MY GSTIN
        worksheet.set_column('I:I', 14)  # DOCUMENT DATE
        worksheet.set_column('J:J', 10)  # MONTH
        worksheet.set_column('K:N', 15)  # DOC_TYPE, REVERSE_CHARGE, ITC_CLAIM_TYPE, PLACE_OF_SUPPLY
        
    return output.getvalue()


# Download buttons for sample templates
st.markdown("### 📥 Download Sample Templates")
col_t1, col_t2, col_t3 = st.columns([1, 1, 3])

with col_t1:
    st.download_button(
        label="📄 GSTR-2B Sample",
        data=generate_sample_2b_template(),
        file_name="GSTR2B_Sample_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Sample GSTR-2B format with required columns"
    )

with col_t2:
    st.download_button(
        label="📘 Purchase Register Sample",
        data=generate_sample_books_template(),
        file_name="PurchaseRegister_Sample_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Sample Purchase Register format with required columns"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================

def normalize_document_number(doc_num):
    """Normalize document number for fuzzy matching"""
    if pd.isna(doc_num) or str(doc_num).strip() == "":
        return "UNKNOWN"
    # Remove special characters, convert to uppercase, remove leading zeros
    normalized = re.sub(r'[^A-Z0-9]', '', str(doc_num).upper().strip())
    normalized = normalized.lstrip('0') or "0"
    return normalized


def extract_pan_from_gstin(gstin):
    """Extract PAN from GSTIN (characters 3-12, 0-indexed: 2:12)"""
    if pd.isna(gstin) or len(str(gstin).strip()) < 15:
        return "UNKNOWN"
    gstin_str = str(gstin).strip().upper()
    return gstin_str[2:12]


def get_document_type(taxable_value):
    """Determine document type based on taxable value sign"""
    try:
        val = float(taxable_value)
        if val < 0:
            return "CREDIT"
        elif val > 0:
            return "INVOICE"
        else:
            return "DEBIT"
    except:
        return "INVOICE"


def parse_date(date_str):
    """Parse date string to datetime object"""
    if pd.isna(date_str) or str(date_str).strip() == "":
        return None
    try:
        # Try common date formats
        for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except:
                continue
        return None
    except:
        return None


def get_financial_year(date_obj):
    """Get financial year string (e.g., '2023-24') from date"""
    if date_obj is None:
        return "Unknown"
    # FY starts April 1
    if date_obj.month >= 4:
        return f"{date_obj.year}-{str(date_obj.year + 1)[-2:]}"
    else:
        return f"{date_obj.year - 1}-{str(date_obj.year)[-2:]}"


def is_same_financial_year(date1_str, date2_str):
    """Check if two dates fall in the same financial year"""
    d1 = parse_date(date1_str)
    d2 = parse_date(date2_str)
    if d1 is None or d2 is None:
        return False
    return get_financial_year(d1) == get_financial_year(d2)


def calculate_total_tax(row, prefix=""):
    """Calculate total tax from IGST, CGST, SGST, Cess columns"""
    cols = [f"{prefix}IGST", f"{prefix}CGST", f"{prefix}SGST", f"{prefix}CESS"]
    total = 0
    for col in cols:
        if col in row and pd.notna(row[col]):
            try:
                total += float(row[col])
            except:
                pass
    return total


@st.cache_data(show_spinner="🔄 Processing reconciliation engine...")
def process_reconciliation(file_2b_bytes, file_pr_bytes, tolerance, date_tol_days, include_rc):
    """Main reconciliation processing function"""
    
    # Load data
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
    
    # Clean column names
    df_2b.columns = df_2b.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    
    # Standardize column names to match expected format
    column_mapping = {
        'SUPPLIER GSTIN': 'SUPPLIER_GSTIN',
        'DOCUMENT NUMBER': 'DOC_NUMBER',
        'TAXABLE VALUE': 'TAXABLE_VALUE',
        'SUPPLIER NAME': 'SUPPLIER_NAME',
        'MY GSTIN': 'MY_GSTIN',
        'DOCUMENT DATE': 'DOC_DATE',
        'DOC_TYPE': 'DOC_TYPE',
        'REVERSE_CHARGE': 'REVERSE_CHARGE',
        'ITC_CLAIM_TYPE': 'ITC_CLAIM_TYPE',
        'PLACE_OF_SUPPLY': 'PLACE_OF_SUPPLY',
        'MONTH': 'MONTH',
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df_2b.columns:
            df_2b[new_col] = df_2b[old_col]
        if old_col in df_pr.columns:
            df_pr[new_col] = df_pr[old_col]
    
    # Ensure required columns exist
    required_cols = ['SUPPLIER_GSTIN', 'DOC_NUMBER', 'TAXABLE_VALUE', 'SUPPLIER_NAME', 
                     'MY_GSTIN', 'DOC_DATE', 'IGST', 'CGST', 'SGST']
    
    for col in required_cols:
        if col not in df_2b.columns:
            df_2b[col] = None
        if col not in df_pr.columns:
            df_pr[col] = None
    
    # Add CESS column if missing
    if 'CESS' not in df_2b.columns:
        df_2b['CESS'] = 0
    if 'CESS' not in df_pr.columns:
        df_pr['CESS'] = 0
    
    # Fill NaN values
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
        
        # Convert numeric columns
        for col in ['TAXABLE_VALUE', 'IGST', 'CGST', 'SGST', 'CESS']:
            df[col] = pd.to_numeric(df.get(col, pd.Series([0]*len(df))), errors='coerce').fillna(0)
        
        # Derive DOC_TYPE if not present
        if 'DOC_TYPE' not in df.columns or df['DOC_TYPE'].isna().any():
            df['DOC_TYPE'] = df['TAXABLE_VALUE'].apply(get_document_type)
    
    # Filter reverse charge if not included
    if not include_rc:
        df_2b = df_2b[df_2b['REVERSE_CHARGE'] != 'YES'].copy()
        df_pr = df_pr[df_pr['REVERSE_CHARGE'] != 'YES'].copy()
    
    # Create normalized keys for matching
    for df in [df_2b, df_pr]:
        df['PAN'] = df['SUPPLIER_GSTIN'].apply(extract_pan_from_gstin)
        df['NORM_DOC'] = df['DOC_NUMBER'].apply(normalize_document_number)
        df['DOC_TYPE_STD'] = df['DOC_TYPE'].apply(lambda x: str(x).upper().strip())
        # Matching key: PAN + Normalized Doc Number + Doc Type
        df['MATCH_KEY'] = df['PAN'] + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE_STD']
    
    # Count duplicates in PR
    dup_pr_count = df_pr.duplicated(subset=['MATCH_KEY'], keep=False).sum()
    
    # Perform outer merge on MATCH_KEY
    merged = pd.merge(
        df_2b, df_pr, 
        on='MATCH_KEY', 
        how='outer', 
        suffixes=('_2B', '_PR'),
        indicator=True
    )
    
    # Calculate derived fields
    merged['TOTAL_TAX_2B'] = merged[['IGST_2B', 'CGST_2B', 'SGST_2B', 'CESS_2B']].sum(axis=1)
    merged['TOTAL_TAX_PR'] = merged[['IGST_PR', 'CGST_PR', 'SGST_PR', 'CESS_PR']].sum(axis=1)
    merged['TAXABLE_DIFF'] = (merged['TAXABLE_VALUE_2B'].fillna(0) - merged['TAXABLE_VALUE_PR'].fillna(0)).abs()
    merged['TAX_DIFF'] = (merged['TOTAL_TAX_2B'].fillna(0) - merged['TOTAL_TAX_PR'].fillna(0)).abs()
    
    # Prepare matching conditions
    exact_gstin = merged['SUPPLIER_GSTIN_2B'].str.upper() == merged['SUPPLIER_GSTIN_PR'].str.upper()
    exact_doc = merged['DOC_NUMBER_2B'].str.upper() == merged['DOC_NUMBER_PR'].str.upper()
    tax_within_tol = merged['TAXABLE_DIFF'] <= tolerance
    tax_exact = merged['TAXABLE_DIFF'] == 0
    same_pan = merged['PAN_2B'] == merged['PAN_PR']
    norm_doc_match = merged['NORM_DOC_2B'] == merged['NORM_DOC_PR']
    date_differs = merged['DOC_DATE_2B'] != merged['DOC_DATE_PR']
    within_fy = merged.apply(lambda r: is_same_financial_year(r['DOC_DATE_2B'], r['DOC_DATE_PR']), axis=1)
    
    # Define match status conditions
    conditions = [
        # Exact: Both present, GSTIN match, Doc number match, values exact
        (merged['_merge'] == 'both') & exact_gstin & exact_doc & tax_exact,
        
        # Suggested: Same PAN, normalized doc match, values within tolerance, date differs but same FY
        (merged['_merge'] == 'both') & same_pan & norm_doc_match & tax_within_tol & date_differs & within_fy,
        
        # Value Mismatch: Doc & GSTIN match but values differ beyond tolerance
        (merged['_merge'] == 'both') & exact_gstin & exact_doc & ~tax_within_tol,
        
        # Cross-State PAN Match: Same PAN but different state GSTIN
        (merged['_merge'] == 'both') & same_pan & ~exact_gstin & tax_within_tol,
        
        # Missing in PR: Present in 2B only
        (merged['_merge'] == 'left_only'),
        
        # Missing in 2B: Present in PR only
        (merged['_merge'] == 'right_only'),
    ]
    
    statuses = [
        'Exact', 
        'Suggested', 
        'Value Mismatch', 
        'Cross-State (PAN Match)', 
        'Missing in GSTR 2B', 
        'Missing in PR'
    ]
    
    reasons = [
        'All parameters matching exactly',
        'Document date differs within FY, values within tolerance threshold',
        'Document number & GSTIN match, but taxable value/tax mismatch exceeds tolerance',
        'Matched on PAN, but State GSTIN differs (cross-state transaction)',
        'Present in GSTR-2B but missing in Purchase Register',
        'Present in Purchase Register but missing in GSTR-2B'
    ]
    
    merged['MATCH_STATUS'] = np.select(conditions, statuses, default='Other')
    merged['MATCH_REASON'] = np.select(conditions, reasons, default='Unable to determine match criteria')
    
    # Combine supplier names
    merged['SUPPLIER_NAME_COMBINED'] = merged['SUPPLIER_NAME_2B'].combine_first(merged['SUPPLIER_NAME_PR']).fillna('Unknown')
    
    # Determine ITC eligibility
    def determine_itc_eligibility(row):
        if row['MATCH_STATUS'] == 'Exact' and auto_claim_itc:
            return 'ELIGIBLE'
        elif row['MATCH_STATUS'] == 'Suggested':
            return 'REVIEW REQUIRED'
        elif row['MATCH_STATUS'] in ['Missing in GSTR 2B', 'Value Mismatch']:
            return 'NOT ELIGIBLE'
        elif row['MATCH_STATUS'] == 'Missing in PR':
            return 'PENDING BOOKS ENTRY'
        else:
            return row.get('ITC_CLAIM_TYPE_2B', row.get('ITC_CLAIM_TYPE_PR', 'UNKNOWN'))
    
    merged['ITC_ELIGIBILITY'] = merged.apply(determine_itc_eligibility, axis=1)
    
    return merged, dup_pr_count, df_2b, df_pr


def generate_summary_statistics(merged_df, df_2b, df_pr):
    """Generate summary statistics matching the sample output format"""
    
    # Overall Summary
    summary = {}
    
    # Count by match status
    status_counts = merged_df['MATCH_STATUS'].value_counts()
    
    # Calculate totals for each category
    for status in ['Exact', 'Suggested', 'Value Mismatch', 'Cross-State (PAN Match)', 'Missing in GSTR 2B', 'Missing in PR']:
        mask = merged_df['MATCH_STATUS'] == status
        
        # 2B values
        if status == 'Missing in PR':
            # Only count 2B side
            summary[f'{status}_2B_docs'] = merged_df.loc[mask, 'DOC_NUMBER_2B'].notna().sum()
            summary[f'{status}_2B_taxable'] = merged_df.loc[mask, 'TAXABLE_VALUE_2B'].sum()
            summary[f'{status}_2B_tax'] = merged_df.loc[mask, 'TOTAL_TAX_2B'].sum()
            summary[f'{status}_PR_docs'] = 0
            summary[f'{status}_PR_taxable'] = 0
            summary[f'{status}_PR_tax'] = 0
        elif status == 'Missing in GSTR 2B':
            # Only count PR side
            summary[f'{status}_2B_docs'] = 0
            summary[f'{status}_2B_taxable'] = 0
            summary[f'{status}_2B_tax'] = 0
            summary[f'{status}_PR_docs'] = merged_df.loc[mask, 'DOC_NUMBER_PR'].notna().sum()
            summary[f'{status}_PR_taxable'] = merged_df.loc[mask, 'TAXABLE_VALUE_PR'].sum()
            summary[f'{status}_PR_tax'] = merged_df.loc[mask, 'TOTAL_TAX_PR'].sum()
        else:
            # Both sides
            summary[f'{status}_2B_docs'] = merged_df.loc[mask, 'DOC_NUMBER_2B'].notna().sum()
            summary[f'{status}_2B_taxable'] = merged_df.loc[mask, 'TAXABLE_VALUE_2B'].sum()
            summary[f'{status}_2B_tax'] = merged_df.loc[mask, 'TOTAL_TAX_2B'].sum()
            summary[f'{status}_PR_docs'] = merged_df.loc[mask, 'DOC_NUMBER_PR'].notna().sum()
            summary[f'{status}_PR_taxable'] = merged_df.loc[mask, 'TAXABLE_VALUE_PR'].sum()
            summary[f'{status}_PR_tax'] = merged_df.loc[mask, 'TOTAL_TAX_PR'].sum()
        
        # Calculate match % and action %
        if summary[f'{status}_2B_docs'] > 0 and summary[f'{status}_PR_docs'] > 0:
            summary[f'{status}_doc_match_pct'] = 100.0
            summary[f'{status}_tax_match_pct'] = min(100, (1 - summary[f'{status}_2B_tax'] / max(1, summary[f'{status}_PR_tax'])) * 100) if summary[f'{status}_PR_tax'] != 0 else 100
            summary[f'{status}_action_pct'] = 100 if status == 'Exact' else (0 if status in ['Missing in GSTR 2B', 'Missing in PR'] else 50)
        elif status == 'Missing in PR':
            summary[f'{status}_doc_match_pct'] = 0
            summary[f'{status}_tax_match_pct'] = 0
            summary[f'{status}_action_pct'] = 0
        elif status == 'Missing in GSTR 2B':
            summary[f'{status}_doc_match_pct'] = 0
            summary[f'{status}_tax_match_pct'] = 0
            summary[f'{status}_action_pct'] = 0
        else:
            summary[f'{status}_doc_match_pct'] = 0
            summary[f'{status}_tax_match_pct'] = 0
            summary[f'{status}_action_pct'] = 0
    
    # Grand totals
    summary['grand_total_2B_docs'] = df_2b.shape[0]
    summary['grand_total_2B_taxable'] = df_2b['TAXABLE_VALUE'].sum()
    summary['grand_total_2B_tax'] = (df_2b['IGST'] + df_2b['CGST'] + df_2b['SGST'] + df_2b['CESS']).sum()
    summary['grand_total_PR_docs'] = df_pr.shape[0]
    summary['grand_total_PR_taxable'] = df_pr['TAXABLE_VALUE'].sum()
    summary['grand_total_PR_tax'] = (df_pr['IGST'] + df_pr['CGST'] + df_pr['SGST'] + df_pr['CESS']).sum()
    
    # GSTR-2B Summary by document type
    gstr2b_summary = {}
    
    # Non-reverse charge
    df_2b_non_rc = df_2b[df_2b['REVERSE_CHARGE'] != 'YES'] if 'REVERSE_CHARGE' in df_2b.columns else df_2b
    
    for doc_type in ['INVOICE', 'CREDIT', 'DEBIT']:
        mask = df_2b_non_rc['DOC_TYPE'].str.upper() == doc_type
        gstr2b_summary[f'2B_non_rc_{doc_type}_docs'] = mask.sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_taxable'] = df_2b_non_rc.loc[mask, 'TAXABLE_VALUE'].sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_tax'] = df_2b_non_rc.loc[mask, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_igst'] = df_2b_non_rc.loc[mask, 'IGST'].sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_cgst'] = df_2b_non_rc.loc[mask, 'CGST'].sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_sgst'] = df_2b_non_rc.loc[mask, 'SGST'].sum()
        gstr2b_summary[f'2B_non_rc_{doc_type}_cess'] = df_2b_non_rc.loc[mask, 'CESS'].sum()
    
    # Reverse charge
    df_2b_rc = df_2b[df_2b['REVERSE_CHARGE'] == 'YES'] if 'REVERSE_CHARGE' in df_2b.columns else pd.DataFrame(columns=df_2b.columns)
    
    for doc_type in ['INVOICE', 'CREDIT', 'DEBIT']:
        mask = df_2b_rc['DOC_TYPE'].str.upper() == doc_type
        gstr2b_summary[f'2B_rc_{doc_type}_docs'] = mask.sum()
        gstr2b_summary[f'2B_rc_{doc_type}_taxable'] = df_2b_rc.loc[mask, 'TAXABLE_VALUE'].sum()
        gstr2b_summary[f'2B_rc_{doc_type}_tax'] = df_2b_rc.loc[mask, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
        gstr2b_summary[f'2B_rc_{doc_type}_igst'] = df_2b_rc.loc[mask, 'IGST'].sum()
        gstr2b_summary[f'2B_rc_{doc_type}_cgst'] = df_2b_rc.loc[mask, 'CGST'].sum()
        gstr2b_summary[f'2B_rc_{doc_type}_sgst'] = df_2b_rc.loc[mask, 'SGST'].sum()
        gstr2b_summary[f'2B_rc_{doc_type}_cess'] = df_2b_rc.loc[mask, 'CESS'].sum()
    
    # IMPG/IMPGSEZ (placeholder - typically empty for domestic)
    gstr2b_summary['2B_impg_docs'] = 0
    gstr2b_summary['2B_impg_taxable'] = 0
    gstr2b_summary['2B_impg_tax'] = 0
    gstr2b_summary['2B_impg_igst'] = 0
    gstr2b_summary['2B_impg_cess'] = 0
    
    # Purchase Books Summary
    pr_summary = {}
    
    # Non-reverse charge
    df_pr_non_rc = df_pr[df_pr['REVERSE_CHARGE'] != 'YES'] if 'REVERSE_CHARGE' in df_pr.columns else df_pr
    
    for doc_type in ['INVOICE', 'CREDIT', 'DEBIT']:
        mask = df_pr_non_rc['DOC_TYPE'].str.upper() == doc_type
        pr_summary[f'PR_non_rc_{doc_type}_docs'] = mask.sum()
        pr_summary[f'PR_non_rc_{doc_type}_taxable'] = df_pr_non_rc.loc[mask, 'TAXABLE_VALUE'].sum()
        pr_summary[f'PR_non_rc_{doc_type}_tax'] = df_pr_non_rc.loc[mask, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
        pr_summary[f'PR_non_rc_{doc_type}_igst'] = df_pr_non_rc.loc[mask, 'IGST'].sum()
        pr_summary[f'PR_non_rc_{doc_type}_cgst'] = df_pr_non_rc.loc[mask, 'CGST'].sum()
        pr_summary[f'PR_non_rc_{doc_type}_sgst'] = df_pr_non_rc.loc[mask, 'SGST'].sum()
        pr_summary[f'PR_non_rc_{doc_type}_cess'] = df_pr_non_rc.loc[mask, 'CESS'].sum()
    
    # Reverse charge
    df_pr_rc = df_pr[df_pr['REVERSE_CHARGE'] == 'YES'] if 'REVERSE_CHARGE' in df_pr.columns else pd.DataFrame(columns=df_pr.columns)
    
    for doc_type in ['INVOICE', 'CREDIT', 'DEBIT']:
        mask = df_pr_rc['DOC_TYPE'].str.upper() == doc_type
        pr_summary[f'PR_rc_{doc_type}_docs'] = mask.sum()
        pr_summary[f'PR_rc_{doc_type}_taxable'] = df_pr_rc.loc[mask, 'TAXABLE_VALUE'].sum()
        pr_summary[f'PR_rc_{doc_type}_tax'] = df_pr_rc.loc[mask, ['IGST', 'CGST', 'SGST', 'CESS']].sum().sum()
        pr_summary[f'PR_rc_{doc_type}_igst'] = df_pr_rc.loc[mask, 'IGST'].sum()
        pr_summary[f'PR_rc_{doc_type}_cgst'] = df_pr_rc.loc[mask, 'CGST'].sum()
        pr_summary[f'PR_rc_{doc_type}_sgst'] = df_pr_rc.loc[mask, 'SGST'].sum()
        pr_summary[f'PR_rc_{doc_type}_cess'] = df_pr_rc.loc[mask, 'CESS'].sum()
    
    # IMPG/IMPGSEZ
    pr_summary['PR_impg_docs'] = 0
    pr_summary['PR_impg_taxable'] = 0
    pr_summary['PR_impg_tax'] = 0
    pr_summary['PR_impg_igst'] = 0
    pr_summary['PR_impg_cess'] = 0
    
    return summary, gstr2b_summary, pr_summary


def create_reconciliation_dataframe(merged_df):
    """Create the detailed reconciliation dataframe matching sample output format"""
    
    # Select and rename columns to match sample output
    recon_cols = {
        'MATCH_STATUS': 'Match Status',
        'MATCH_REASON': 'Match Status Description',
        'SUPPLIER_NAME_COMBINED': 'Supplier Name',
        'SUPPLIER_GSTIN_2B': 'Supplier GSTIN (2B)',
        'SUPPLIER_GSTIN_PR': 'Supplier GSTIN (PR)',
        'MY_GSTIN_2B': 'My GSTIN (2B)',
        'MY_GSTIN_PR': 'My GSTIN (PR)',
        'DOC_NUMBER_2B': 'Document Number (2B)',
        'DOC_NUMBER_PR': 'Document Number (PR)',
        'DOC_DATE_2B': 'Document Date (2B)',
        'DOC_DATE_PR': 'Document Date (PR)',
        'TAXABLE_VALUE_2B': 'Taxable Value (2B)',
        'TAXABLE_VALUE_PR': 'Taxable Value (PR)',
        'TAXABLE_DIFF': 'Tax Difference(2B-PR)',
        'TOTAL_TAX_2B': 'Total Tax (2B)',
        'TOTAL_TAX_PR': 'Total Tax (PR)',
        'IGST_2B': 'IGST (2B)',
        'IGST_PR': 'IGST (PR)',
        'CGST_2B': 'CGST (2B)',
        'CGST_PR': 'CGST (PR)',
        'SGST_2B': 'SGST (2B)',
        'SGST_PR': 'SGST (PR)',
        'CESS_2B': 'Cess (2B)',
        'CESS_PR': 'Cess (PR)',
        'DOC_TYPE_2B': 'Document Type(2B)',
        'DOC_TYPE_PR': 'Document Type(PR)',
        'MONTH_2B': 'Return Period (2B)',
        'MONTH_PR': 'Return Period (PR)',
        'REVERSE_CHARGE_2B': 'Reverse Charge (2B)',
        'REVERSE_CHARGE_PR': 'Reverse Charge (PR)',
        'PLACE_OF_SUPPLY_2B': 'Place of Supply (2B)',
        'PLACE_OF_SUPPLY_PR': 'Place of Supply (PR)',
        'ITC_ELIGIBILITY': 'ITC Claim Eligibility(PR)',
    }
    
    recon_df = merged_df[list(recon_cols.keys())].copy()
    recon_df.columns = list(recon_cols.values())
    
    # Add additional columns from sample
    recon_df['Section Name 2B'] = recon_df['Match Status'].apply(lambda x: 'B2B' if x in ['Exact', 'Suggested', 'Value Mismatch'] else '')
    recon_df['Section Name (Pr)'] = recon_df['Section Name 2B']
    recon_df['Original Document Number (2B)'] = recon_df['Document Number (2B)']
    recon_df['Original Document Date (2B)'] = recon_df['Document Date (2B)']
    recon_df['Reason (2B)'] = ''
    recon_df['ITC Availablity(2B)'] = 'YES'
    recon_df['Amendment Category'] = ''
    recon_df['IGST Claimed Amount'] = recon_df['IGST (2B)'].fillna(0)
    recon_df['CGST Claimed Amount'] = recon_df['CGST (2B)'].fillna(0)
    recon_df['SGST Claimed Amount'] = recon_df['SGST (2B)'].fillna(0)
    recon_df['CESS Claimed Amount'] = recon_df['Cess (2B)'].fillna(0)
    recon_df['GSTR1 Filing Status'] = 'FILED'
    recon_df['GSTR3B Filing Status'] = 'N'
    recon_df['Vendor GSTIN Status'] = ''
    recon_df['ITC Claim Status'] = recon_df['ITC Claim Eligibility(PR)'].apply(lambda x: 'Claim ITC' if x == 'ELIGIBLE' else 'No Action')
    recon_df['ITC Claim Month as per 3B'] = '03-2024'
    recon_df['ITC Claim Amount'] = recon_df['Total Tax (2B)'].fillna(0)
    recon_df['GSTR-1/IFF/5 Filing Date'] = ''
    recon_df['GSTR-1/IFF/5 Filing Period'] = recon_df['Return Period (2B)']
    recon_df['Effective date of cancellation of Supplier GSTIN'] = ''
    recon_df['Vendor Payment Status'] = ''
    recon_df['Reason for Hold/Release Vendor Payment'] = ''
    recon_df['Vendor Payment Remarks'] = ''
    recon_df['Is Vendor Payment status manually overwritten?'] = ''
    recon_df['IRN'] = ''
    recon_df['IRN generation date'] = ''
    recon_df['Group Id'] = ''
    recon_df['Group Remark'] = ''
    recon_df['Remarks (2B)'] = ''
    recon_df['Remarks (PR)'] = ''
    recon_df['Vendor Filing Frequency'] = ''
    recon_df['Vendor Risk'] = ''
    recon_df['Vendor Code'] = ''
    recon_df['Financial Year'] = '2023-24'
    recon_df['Voucher Number'] = ''
    recon_df['Out of Range (2B)'] = 'false'
    recon_df['Out of Range (PR)'] = 'false'
    recon_df['Claimable ITC - CGST'] = recon_df['CGST (2B)'].fillna(0)
    recon_df['Claimable ITC - SGST'] = recon_df['SGST (2B)'].fillna(0)
    recon_df['Claimable ITC - IGST'] = recon_df['IGST (2B)'].fillna(0)
    recon_df['Claimable ITC - Cess'] = recon_df['Cess (2B)'].fillna(0)
    
    return recon_df


def generate_excel_report(merged_df, recon_df, summary, gstr2b_summary, pr_summary, 
                          df_2b, df_pr, dup_pr_count, include_charts=True, include_raw=True, max_rows=15000):
    """Generate comprehensive Excel report matching sample output format"""
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats
        fmt_header = workbook.add_format({
            'bold': True, 'bg_color': '#1e40af', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
        })
        fmt_subheader = workbook.add_format({
            'bold': True, 'bg_color': '#3b82f6', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        fmt_data = workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True
        })
        fmt_numeric = workbook.add_format({
            'border': 1, 'align': 'right', 'valign': 'top', 'num_format': '#,##0.00'
        })
        fmt_numeric_int = workbook.add_format({
            'border': 1, 'align': 'right', 'valign': 'top', 'num_format': '#,##0'
        })
        fmt_pct = workbook.add_format({
            'border': 1, 'align': 'right', 'valign': 'top', 'num_format': '0.00%'
        })
        fmt_status_exact = workbook.add_format({
            'border': 1, 'bg_color': '#dcfce7', 'font_color': '#166534', 'align': 'center'
        })
        fmt_status_suggested = workbook.add_format({
            'border': 1, 'bg_color': '#cffafe', 'font_color': '#0e7490', 'align': 'center'
        })
        fmt_status_missing = workbook.add_format({
            'border': 1, 'bg_color': '#ffedd5', 'font_color': '#9a3412', 'align': 'center'
        })
        fmt_status_error = workbook.add_format({
            'border': 1, 'bg_color': '#fee2e2', 'font_color': '#991b1b', 'align': 'center'
        })
        fmt_total = workbook.add_format({
            'bold': True, 'bg_color': '#f1f5f9', 'border': 2, 'align': 'right', 
            'valign': 'top', 'num_format': '#,##0.00'
        })
        
        # ============ SHEET 1: Overall Summary ============
        sheet_summary = workbook.add_worksheet('Overall Summary')
        sheet_summary.hide_gridlines(2)
        
        # Title
        sheet_summary.merge_range('A1:C1', 'PAN GSTR - 2B Vs PR', fmt_header)
        sheet_summary.write('A3', 'Business name', fmt_data)
        sheet_summary.write('B3', 'SUPRATEC', fmt_data)
        sheet_summary.write('A4', 'PAN', fmt_data)
        sheet_summary.write('B4', 'ADXFS5154R', fmt_data)
        sheet_summary.write('A5', 'Return Period(2B)', fmt_data)
        sheet_summary.write('B5', '042023 - 032024', fmt_data)
        sheet_summary.write('A6', 'Return Period(PR)', fmt_data)
        sheet_summary.write('B6', '042023 - 032024', fmt_data)
        sheet_summary.write('A7', 'Fiscal Year (2B)', fmt_data)
        sheet_summary.write('B7', '-', fmt_data)
        sheet_summary.write('A8', 'Fiscal Year (PR)', fmt_data)
        sheet_summary.write('B8', '-', fmt_data)
        sheet_summary.write('A10', '* Values are calculated on basis of net off Credit and Debit notes', fmt_data)
        
        # Section A: Overall Summary Table
        sheet_summary.merge_range('A12:O12', 'A : Overall Summary', fmt_subheader)
        
        # Headers
        headers_2b = ['Number of Documents', 'Taxable Value', 'Total Tax']
        headers_pr = ['Number of Documents', 'Taxable Value', 'Total Tax']
        
        sheet_summary.write('A14', 'MATCH STATUS', fmt_header)
        sheet_summary.merge_range('B14:D14', 'Difference(2B-PR)', fmt_header)
        sheet_summary.merge_range('E14:G14', 'As Per GSTR 2B', fmt_header)
        sheet_summary.merge_range('H14:J14', 'As Per Purchase Books', fmt_header)
        sheet_summary.merge_range('K14:L14', 'Match %', fmt_header)
        sheet_summary.write('M14', 'Action %', fmt_header)
        
        sheet_summary.write_row('A15', ['MATCH STATUS'] + headers_2b + headers_pr + ['Document Count', 'Tax Amount', 'Action %'], fmt_subheader)
        
        # Data rows
        statuses_order = ['Exact', 'Manually linked', 'Manually Group linked', 'Suggested', 
                         'Mismatch', 'Missing in GSTR 2B', 'Missing in PR', 'Grand Total']
        
        row = 16
        for status in statuses_order:
            if status == 'Grand Total':
                sheet_summary.write(row, 0, status, fmt_total)
                sheet_summary.write(row, 1, summary.get('grand_total_PR_docs', 0) - summary.get('grand_total_2B_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 2, summary.get('grand_total_PR_taxable', 0) - summary.get('grand_total_2B_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 3, summary.get('grand_total_PR_tax', 0) - summary.get('grand_total_2B_tax', 0), fmt_numeric)
                sheet_summary.write(row, 4, summary.get('grand_total_2B_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 5, summary.get('grand_total_2B_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 6, summary.get('grand_total_2B_tax', 0), fmt_numeric)
                sheet_summary.write(row, 7, summary.get('grand_total_PR_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 8, summary.get('grand_total_PR_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 9, summary.get('grand_total_PR_tax', 0), fmt_numeric)
            else:
                sheet_summary.write(row, 0, status, fmt_data)
                
                # Difference columns (simplified)
                diff_docs = summary.get(f'{status}_PR_docs', 0) - summary.get(f'{status}_2B_docs', 0)
                diff_taxable = summary.get(f'{status}_PR_taxable', 0) - summary.get(f'{status}_2B_taxable', 0)
                diff_tax = summary.get(f'{status}_PR_tax', 0) - summary.get(f'{status}_2B_tax', 0)
                sheet_summary.write(row, 1, diff_docs if status not in ['Missing in GSTR 2B', 'Missing in PR'] else summary.get(f'{status}_PR_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 2, diff_taxable if status not in ['Missing in GSTR 2B', 'Missing in PR'] else summary.get(f'{status}_PR_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 3, diff_tax if status not in ['Missing in GSTR 2B', 'Missing in PR'] else summary.get(f'{status}_PR_tax', 0), fmt_numeric)
                
                # 2B columns
                sheet_summary.write(row, 4, summary.get(f'{status}_2B_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 5, summary.get(f'{status}_2B_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 6, summary.get(f'{status}_2B_tax', 0), fmt_numeric)
                
                # PR columns
                sheet_summary.write(row, 7, summary.get(f'{status}_PR_docs', 0), fmt_numeric_int)
                sheet_summary.write(row, 8, summary.get(f'{status}_PR_taxable', 0), fmt_numeric)
                sheet_summary.write(row, 9, summary.get(f'{status}_PR_tax', 0), fmt_numeric)
                
                # Match % columns
                sheet_summary.write(row, 10, summary.get(f'{status}_doc_match_pct', 0)/100, fmt_pct)
                sheet_summary.write(row, 11, summary.get(f'{status}_tax_match_pct', 0)/100, fmt_pct)
                
                # Action %
                sheet_summary.write(row, 12, summary.get(f'{status}_action_pct', 0)/100, fmt_pct)
            
            row += 1
        
        # Section B: GSTR-2B Summary
        sheet_summary.merge_range('A28:C28', 'B:  GSTR -2B Summary', fmt_subheader)
        
        # Documents (Other than Reverse Charge)
        sheet_summary.write('A30', 'Documents (Other than Reverse Charge)', fmt_subheader)
        doc_headers = ['Document Type', 'Number of Documents', 'Taxable Value', 'Tax Amount', 'IGST', 'CGST', 'SGST', 'Cess', 'Total Value']
        sheet_summary.write_row('A31', doc_headers, fmt_header)
        
        row = 32
        for doc_type in ['Invoices', 'Credit Notes', 'Debit Notes', 'Total ( Invoices+Debit notes- Credit notes)']:
            key = doc_type.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').upper()
            if key == 'TOTAL_INVOICES_DEBIT_NOTES_CREDIT_NOTES':
                key = 'INVOICE'  # Use invoice totals for total row calculation
            
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, gstr2b_summary.get(f'2B_non_rc_{key}_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, gstr2b_summary.get(f'2B_non_rc_{key}_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, gstr2b_summary.get(f'2B_non_rc_{key}_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, gstr2b_summary.get(f'2B_non_rc_{key}_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, gstr2b_summary.get(f'2B_non_rc_{key}_cgst', 0), fmt_numeric)
            sheet_summary.write(row, 6, gstr2b_summary.get(f'2B_non_rc_{key}_sgst', 0), fmt_numeric)
            sheet_summary.write(row, 7, gstr2b_summary.get(f'2B_non_rc_{key}_cess', 0), fmt_numeric)
            # Total Value = Taxable + Tax
            total_val = gstr2b_summary.get(f'2B_non_rc_{key}_taxable', 0) + gstr2b_summary.get(f'2B_non_rc_{key}_tax', 0)
            sheet_summary.write(row, 8, total_val, fmt_numeric)
            row += 1
        
        # Documents (Reverse Charge)
        sheet_summary.write('A40', 'Documents (Reverse Charge)', fmt_subheader)
        sheet_summary.write_row('A41', doc_headers, fmt_header)
        
        row = 42
        for doc_type in ['Invoices', 'Credit Notes', 'Debit Notes', 'Total ( Invoices+Debit notes- Credit notes)']:
            key = doc_type.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').upper()
            if key == 'TOTAL_INVOICES_DEBIT_NOTES_CREDIT_NOTES':
                key = 'INVOICE'
            
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, gstr2b_summary.get(f'2B_rc_{key}_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, gstr2b_summary.get(f'2B_rc_{key}_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, gstr2b_summary.get(f'2B_rc_{key}_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, gstr2b_summary.get(f'2B_rc_{key}_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, gstr2b_summary.get(f'2B_rc_{key}_cgst', 0), fmt_numeric)
            sheet_summary.write(row, 6, gstr2b_summary.get(f'2B_rc_{key}_sgst', 0), fmt_numeric)
            sheet_summary.write(row, 7, gstr2b_summary.get(f'2B_rc_{key}_cess', 0), fmt_numeric)
            total_val = gstr2b_summary.get(f'2B_rc_{key}_taxable', 0) + gstr2b_summary.get(f'2B_rc_{key}_tax', 0)
            sheet_summary.write(row, 8, total_val, fmt_numeric)
            row += 1
        
        # IMPG/IMPGSEZ
        sheet_summary.write('A50', 'IMPG/ IMPGSEZ', fmt_subheader)
        impg_headers = ['Document Type', 'Number of Documents', 'Taxable Value', 'Tax Amount', 'IGST', 'Cess', 'Total Value']
        sheet_summary.write_row('A51', impg_headers, fmt_header)
        
        row = 52
        for doc_type in ['IMPG', 'IMPGSEZ', 'Total']:
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, gstr2b_summary.get('2B_impg_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, gstr2b_summary.get('2B_impg_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, gstr2b_summary.get('2B_impg_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, gstr2b_summary.get('2B_impg_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, gstr2b_summary.get('2B_impg_cess', 0), fmt_numeric)
            total_val = gstr2b_summary.get('2B_impg_taxable', 0) + gstr2b_summary.get('2B_impg_tax', 0)
            sheet_summary.write(row, 6, total_val, fmt_numeric)
            row += 1
        
        # Section C: Summary as per Purchase Books
        sheet_summary.merge_range('A60:C60', 'C : Summary as per Purchase Books', fmt_subheader)
        
        # Documents (Other than Reverse Charge)
        sheet_summary.write('A62', 'Documents (Other than Reverse charge)', fmt_subheader)
        sheet_summary.write_row('A63', doc_headers, fmt_header)
        
        row = 64
        for doc_type in ['Invoices', 'Credit Notes', 'Debit Notes', 'Total ( Invoices+Debit notes- Credit notes)']:
            key = doc_type.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').upper()
            if key == 'TOTAL_INVOICES_DEBIT_NOTES_CREDIT_NOTES':
                key = 'INVOICE'
            
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, pr_summary.get(f'PR_non_rc_{key}_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, pr_summary.get(f'PR_non_rc_{key}_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, pr_summary.get(f'PR_non_rc_{key}_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, pr_summary.get(f'PR_non_rc_{key}_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, pr_summary.get(f'PR_non_rc_{key}_cgst', 0), fmt_numeric)
            sheet_summary.write(row, 6, pr_summary.get(f'PR_non_rc_{key}_sgst', 0), fmt_numeric)
            sheet_summary.write(row, 7, pr_summary.get(f'PR_non_rc_{key}_cess', 0), fmt_numeric)
            total_val = pr_summary.get(f'PR_non_rc_{key}_taxable', 0) + pr_summary.get(f'PR_non_rc_{key}_tax', 0)
            sheet_summary.write(row, 8, total_val, fmt_numeric)
            row += 1
        
        # Documents (Reverse Charge)
        sheet_summary.write('A72', 'Documents( Reverse charge)', fmt_subheader)
        sheet_summary.write_row('A73', doc_headers, fmt_header)
        
        row = 74
        for doc_type in ['Invoices', 'Credit Notes', 'Debit Notes', 'Total ( Invoices+Debit notes- Credit notes)']:
            key = doc_type.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').upper()
            if key == 'TOTAL_INVOICES_DEBIT_NOTES_CREDIT_NOTES':
                key = 'INVOICE'
            
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, pr_summary.get(f'PR_rc_{key}_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, pr_summary.get(f'PR_rc_{key}_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, pr_summary.get(f'PR_rc_{key}_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, pr_summary.get(f'PR_rc_{key}_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, pr_summary.get(f'PR_rc_{key}_cgst', 0), fmt_numeric)
            sheet_summary.write(row, 6, pr_summary.get(f'PR_rc_{key}_sgst', 0), fmt_numeric)
            sheet_summary.write(row, 7, pr_summary.get(f'PR_rc_{key}_cess', 0), fmt_numeric)
            total_val = pr_summary.get(f'PR_rc_{key}_taxable', 0) + pr_summary.get(f'PR_rc_{key}_tax', 0)
            sheet_summary.write(row, 8, total_val, fmt_numeric)
            row += 1
        
        # IMPG/IMPGSEZ
        sheet_summary.write('A82', 'IMPG/ IMPGSEZ', fmt_subheader)
        sheet_summary.write_row('A83', impg_headers, fmt_header)
        
        row = 84
        for doc_type in ['IMPG', 'IMPGSEZ', 'Total']:
            sheet_summary.write(row, 0, doc_type, fmt_data)
            sheet_summary.write(row, 1, pr_summary.get('PR_impg_docs', 0), fmt_numeric_int)
            sheet_summary.write(row, 2, pr_summary.get('PR_impg_taxable', 0), fmt_numeric)
            sheet_summary.write(row, 3, pr_summary.get('PR_impg_tax', 0), fmt_numeric)
            sheet_summary.write(row, 4, pr_summary.get('PR_impg_igst', 0), fmt_numeric)
            sheet_summary.write(row, 5, pr_summary.get('PR_impg_cess', 0), fmt_numeric)
            total_val = pr_summary.get('PR_impg_taxable', 0) + pr_summary.get('PR_impg_tax', 0)
            sheet_summary.write(row, 6, total_val, fmt_numeric)
            row += 1
        
        # Set column widths
        sheet_summary.set_column('A:A', 45)
        sheet_summary.set_column('B:C', 25)
        sheet_summary.set_column('D:O', 16)
        
        # ============ SHEET 2: Document Details ============
        sheet_details = workbook.add_worksheet('Document Details (Inv CDN)')
        
        # Write headers
        for col, (col_name, col_key) in enumerate(recon_df.columns.items()):
            sheet_details.write(0, col, col_name, fmt_header)
        
        # Write data with conditional formatting
        for row_idx, row_data in enumerate(recon_df.itertuples(index=False), start=1):
            status = row_data._asdict().get('Match Status', '')
            row_format = fmt_data
            
            if status == 'Exact':
                row_format = fmt_status_exact
            elif status == 'Suggested':
                row_format = fmt_status_suggested
            elif status in ['Missing in GSTR 2B', 'Missing in PR']:
                row_format = fmt_status_missing
            elif status in ['Value Mismatch', 'Mismatch']:
                row_format = fmt_status_error
            
            for col_idx, value in enumerate(row_data):
                if pd.isna(value):
                    sheet_details.write(row_idx, col_idx, '', row_format)
                elif isinstance(value, (int, float, np.number)):
                    if col_name in ['Tax Difference(2B-PR)', 'Taxable Value (2B)', 'Taxable Value (PR)', 
                                   'Total Tax (2B)', 'Total Tax (PR)', 'IGST (2B)', 'IGST (PR)',
                                   'CGST (2B)', 'CGST (PR)', 'SGST (2B)', 'SGST (PR)', 'Cess (2B)', 'Cess (PR)']:
                        sheet_details.write(row_idx, col_idx, float(value), fmt_numeric)
                    else:
                        sheet_details.write(row_idx, col_idx, int(value) if float(value).is_integer() else float(value), fmt_numeric)
                else:
                    sheet_details.write(row_idx, col_idx, str(value), row_format)
        
        # Auto-filter
        sheet_details.autofilter(0, 0, len(recon_df), len(recon_df.columns) - 1)
        
        # Set column widths (key columns wider)
        col_widths = {
            'Match Status': 18, 'Match Status Description': 50, 'Supplier Name': 35,
            'Supplier GSTIN (2B)': 22, 'Supplier GSTIN (PR)': 22,
            'Document Number (2B)': 25, 'Document Number (PR)': 25,
            'Document Date (2B)': 15, 'Document Date (PR)': 15,
            'Taxable Value (2B)': 16, 'Taxable Value (PR)': 16,
            'Total Tax (2B)': 14, 'Total Tax (PR)': 14,
            'Tax Difference(2B-PR)': 18, 'ITC Claim Eligibility(PR)': 20,
        }
        for col_idx, col_name in enumerate(recon_df.columns):
            width = col_widths.get(col_name, 14)
            sheet_details.set_column(col_idx, col_idx, width)
        
        # ============ SHEET 3: Raw 2B Data ============
        if include_raw:
            df_2b_export = df_2b.copy()
            # Remove internal columns
            for col in ['PAN', 'NORM_DOC', 'MATCH_KEY', 'DOC_TYPE_STD']:
                if col in df_2b_export.columns:
                    df_2b_export.drop(columns=[col], inplace=True, errors='ignore')
            df_2b_export.to_excel(writer, sheet_name='2B Raw Data', index=False)
            sheet_2b = writer.sheets['2B Raw Data']
            sheet_2b.set_column('A:Z', 18)
        
        # ============ SHEET 4: Raw PR Data ============
        if include_raw:
            df_pr_export = df_pr.copy()
            for col in ['PAN', 'NORM_DOC', 'MATCH_KEY', 'DOC_TYPE_STD']:
                if col in df_pr_export.columns:
                    df_pr_export.drop(columns=[col], inplace=True, errors='ignore')
            df_pr_export.to_excel(writer, sheet_name='PR Raw Data', index=False)
            sheet_pr = writer.sheets['PR Raw Data']
            sheet_pr.set_column('A:Z', 18)
        
        # ============ SHEET 5: Dashboard (if charts enabled) ============
        if include_charts:
            sheet_dash = workbook.add_worksheet('Dashboard')
            
            # Title
            sheet_dash.merge_range('A1:F1', 'GST Recon Pro - Executive Dashboard', 
                                  workbook.add_format({'bold': True, 'font_size': 16, 'bg_color': '#1e40af', 'font_color': 'white', 'align': 'center'}))
            
            # Key Metrics
            metrics = [
                ('Total Records', len(recon_df)),
                ('Exact Matches', (merged_df['MATCH_STATUS'] == 'Exact').sum()),
                ('Suggested Matches', (merged_df['MATCH_STATUS'] == 'Suggested').sum()),
                ('Missing in 2B', (merged_df['MATCH_STATUS'] == 'Missing in GSTR 2B').sum()),
                ('Missing in PR', (merged_df['MATCH_STATUS'] == 'Missing in PR').sum()),
                ('Unclaimed ITC (₹)', merged_df[merged_df['MATCH_STATUS'] == 'Missing in PR']['TOTAL_TAX_2B'].sum()),
            ]
            
            for i, (label, value) in enumerate(metrics):
                sheet_dash.write(3 + i, 0, label, fmt_data)
                if isinstance(value, (int, float)):
                    sheet_dash.write(3 + i, 1, value, fmt_numeric_int if isinstance(value, int) else fmt_numeric)
                else:
                    sheet_dash.write(3 + i, 1, str(value), fmt_data)
            
            # Status Distribution Chart
            status_counts = merged_df['MATCH_STATUS'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            if len(status_counts) > 0:
                chart = workbook.add_chart({'type': 'pie'})
                chart.add_series({
                    'name': 'Match Status Distribution',
                    'categories': ['Dashboard', 1, len(status_counts), 0],
                    'values': ['Dashboard', 1, len(status_counts), 1],
                    'data_labels': {'percentage': True, 'category': True},
                })
                chart.set_title({'name': 'Reconciliation Status Distribution'})
                sheet_dash.insert_chart('A15', chart)
            
            sheet_dash.set_column('A:A', 25)
            sheet_dash.set_column('B:B', 18)
    
    return output.getvalue()


# ================= FILE UPLOAD SECTION =================
st.markdown("### 📁 Upload Your Files")
col_upload1, col_upload2 = st.columns(2)

with col_upload1:
    file_2b = st.file_uploader(
        "📄 Upload GSTR-2B File", 
        type=['xlsx', 'xls'],
        key='upload_2b',
        help="Excel file with GSTR-2B data. Required columns: SUPPLIER GSTIN, DOCUMENT NUMBER, TAXABLE VALUE, IGST, CGST, SGST, SUPPLIER NAME, MY GSTIN, DOCUMENT DATE"
    )

with col_upload2:
    file_pr = st.file_uploader(
        "📘 Upload Purchase Register", 
        type=['xlsx', 'xls'],
        key='upload_pr',
        help="Excel file with Purchase Register data. Required columns: SUPPLIER GSTIN, DOCUMENT NUMBER, TAXABLE VALUE, IGST, CGST, SGST, SUPPLIER NAME, MY GSTIN, DOCUMENT DATE"
    )

# ================= MAIN PROCESSING LOGIC =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Advanced Reconciliation Engine..."):
            
            # Process files
            merged_df, dup_pr_count, df_2b, df_pr = process_reconciliation(
                file_2b.getvalue(), 
                file_pr.getvalue(), 
                tolerance, 
                date_tolerance, 
                include_reverse_charge
            )
            
            # Generate summaries
            summary, gstr2b_summary, pr_summary = generate_summary_statistics(merged_df, df_2b, df_pr)
            
            # Create reconciliation dataframe
            recon_df = create_reconciliation_dataframe(merged_df)
            
            # ========== DASHBOARD METRICS ==========
            st.markdown("### 📊 Live Reconciliation Summary")
            m1, m2, m3, m4, m5 = st.columns(5)
            
            total_records = len(recon_df)
            exact_count = (merged_df['MATCH_STATUS'] == 'Exact').sum()
            suggested_count = (merged_df['MATCH_STATUS'] == 'Suggested').sum()
            missing_2b_count = (merged_df['MATCH_STATUS'] == 'Missing in GSTR 2B').sum()
            missing_pr_count = (merged_df['MATCH_STATUS'] == 'Missing in PR').sum()
            
            m1.metric("📋 Total Records", f"{total_records:,}")
            m2.metric("✅ Exact Matches", f"{exact_count:,}", 
                     delta=f"{(exact_count/total_records*100):.1f}%" if total_records > 0 else "0%")
            m3.metric("🔍 Suggested", f"{suggested_count:,}")
            m4.metric("⚠️ Missing in 2B", f"{missing_2b_count:,}", delta_color="inverse")
            m5.metric("📥 Missing in PR", f"{missing_pr_count:,}", delta_color="inverse")
            
            # ========== AI-POWERED INSIGHTS ==========
            st.markdown("### 🧠 Automated Financial Insights")
            
            insights = []
            
            # Calculate key metrics
            total_2b_tax = df_2b['TAXABLE_VALUE'].sum()
            total_pr_tax = df_pr['TAXABLE_VALUE'].sum()
            unclaimed_itc = merged_df[merged_df['MATCH_STATUS'] == 'Missing in PR']['TOTAL_TAX_2B'].sum()
            risky_claims = merged_df[merged_df['MATCH_STATUS'] == 'Missing in GSTR 2B']['TOTAL_TAX_PR'].sum()
            match_rate = (exact_count + suggested_count) / total_records * 100 if total_records > 0 else 0
            
            if dup_pr_count > 0:
                insights.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Data Quality Alert',
                    'message': f"Found **{dup_pr_count} duplicate entries** in Purchase Register. Review for potential double-claiming of ITC."
                })
            
            if missing_pr_count > 0:
                insights.append({
                    'type': 'success',
                    'icon': '💡',
                    'title': 'Cash Flow Opportunity',
                    'message': f"**₹{unclaimed_itc:,.2f}** in Input Tax Credit available in GSTR-2B but not claimed in books. Consider updating Purchase Register."
                })
            
            if missing_2b_count > 0:
                insights.append({
                    'type': 'error',
                    'icon': '🚨',
                    'title': 'Compliance Risk',
                    'message': f"**₹{risky_claims:,.2f}** in ITC claimed in books but missing from GSTR-2B. Verify supplier filings to avoid ITC reversal."
                })
            
            if match_rate < 80:
                insights.append({
                    'type': 'warning',
                    'icon': '🔄',
                    'title': 'Reconciliation Health',
                    'message': f"Match rate is **{match_rate:.1f}%**. Consider reviewing document numbering conventions and date formats for better matching."
                })
            elif match_rate >= 95:
                insights.append({
                    'type': 'success',
                    'icon': '✅',
                    'title': 'Excellent Health',
                    'message': f"Outstanding match rate of **{match_rate:.1f}%**! Your books are well-aligned with GSTR-2B."
                })
            
            if suggested_count > 0:
                insights.append({
                    'type': 'warning',
                    'icon': '🕒',
                    'title': 'Date Mismatches Detected',
                    'message': f"**{suggested_count} records** have document date differences but match on other parameters. Review if these are acceptable variations."
                })
            
            # Display insights
            for insight in insights:
                css_class = f"insight-box {insight['type']}"
                st.markdown(f"""
                <div class='{css_class}'>
                    <strong>{insight['icon']} {insight['title']}:</strong> {insight['message']}
                </div>
                """, unsafe_allow_html=True)
            
            if not insights:
                st.markdown("<div class='insight-box success'><strong>✅ All Clear:</strong> No critical issues detected. Your GST reconciliation is healthy!</div>", unsafe_allow_html=True)
            
            # ========== VISUALIZATIONS ==========
            st.markdown("### 📈 Visual Analytics")
            
            tab1, tab2, tab3 = st.tabs(["📊 Status Distribution", "📅 Monthly Trends", "🏆 Top Suppliers"])
            
            with tab1:
                # Status distribution chart
                status_data = merged_df['MATCH_STATUS'].value_counts().reset_index()
                status_data.columns = ['Status', 'Count']
                
                color_map = {
                    'Exact': '#10b981',
                    'Suggested': '#06b6d4', 
                    'Value Mismatch': '#f97316',
                    'Cross-State (PAN Match)': '#8b5cf6',
                    'Missing in GSTR 2B': '#ef4444',
                    'Missing in PR': '#f59e0b',
                    'Other': '#64748b'
                }
                
                fig_status = px.bar(
                    status_data, 
                    x='Count', 
                    y='Status', 
                    color='Status',
                    color_discrete_map=color_map,
                    orientation='h',
                    title='Reconciliation Status Distribution',
                    text='Count'
                )
                fig_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with tab2:
                # Monthly analysis
                if 'MONTH_2B' in merged_df.columns and merged_df['MONTH_2B'].notna().any():
                    monthly_2b = merged_df.groupby('MONTH_2B').agg({
                        'TAXABLE_VALUE_2B': 'sum',
                        'TOTAL_TAX_2B': 'sum'
                    }).reset_index()
                    monthly_2b.columns = ['Month', 'Taxable Value (2B)', 'Total Tax (2B)']
                    
                    monthly_pr = merged_df.groupby('MONTH_PR').agg({
                        'TAXABLE_VALUE_PR': 'sum',
                        'TOTAL_TAX_PR': 'sum'
                    }).reset_index()
                    monthly_pr.columns = ['Month', 'Taxable Value (PR)', 'Total Tax (PR)']
                    
                    # Merge monthly data
                    monthly_combined = pd.merge(
                        monthly_2b, monthly_pr, 
                        on='Month', 
                        how='outer',
                        suffixes=('_2B', '_PR')
                    ).fillna(0)
                    
                    if not monthly_combined.empty:
                        fig_monthly = px.bar(
                            monthly_combined,
                            x='Month',
                            y=['Taxable Value (2B)', 'Taxable Value (PR)'],
                            barmode='group',
                            title='Taxable Value Comparison by Month',
                            labels={'value': 'Amount (₹)', 'Month': 'Period'}
                        )
                        fig_monthly.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=400
                        )
                        st.plotly_chart(fig_monthly, use_container_width=True)
            
            with tab3:
                # Top suppliers analysis
                top_suppliers_2b = recon_df.groupby('Supplier Name').agg({
                    'Taxable Value (2B)': 'sum',
                    'Total Tax (2B)': 'sum',
                    'IGST (2B)': 'sum',
                    'CGST (2B)': 'sum'
                }).nlargest(10, 'Taxable Value (2B)').reset_index()
                
                top_suppliers_pr = recon_df.groupby('Supplier Name').agg({
                    'Taxable Value (PR)': 'sum',
                    'Total Tax (PR)': 'sum',
                    'IGST (PR)': 'sum',
                    'CGST (PR)': 'sum'
                }).nlargest(10, 'Taxable Value (PR)').reset_index()
                
                col_top1, col_top2 = st.columns(2)
                
                with col_top1:
                    fig_top_2b = px.bar(
                        top_suppliers_2b,
                        x='Supplier Name',
                        y=['Taxable Value (2B)', 'IGST (2B)', 'CGST (2B)'],
                        barmode='group',
                        title='Top 10 Suppliers by GSTR-2B Value',
                        labels={'value': 'Amount (₹)'}
                    )
                    fig_top_2b.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_tickangle=-45,
                        height=400
                    )
                    st.plotly_chart(fig_top_2b, use_container_width=True)
                
                with col_top2:
                    fig_top_pr = px.bar(
                        top_suppliers_pr,
                        x='Supplier Name',
                        y=['Taxable Value (PR)', 'IGST (PR)', 'CGST (PR)'],
                        barmode='group',
                        title='Top 10 Suppliers by Purchase Register Value',
                        labels={'value': 'Amount (₹)'}
                    )
                    fig_top_pr.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_tickangle=-45,
                        height=400
                    )
                    st.plotly_chart(fig_top_pr, use_container_width=True)
            
            # ========== DATA EXPLORER ==========
            st.markdown("### 🔍 Detailed Reconciliation Data")
            
            # Filters
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                status_filter = st.multiselect(
                    "Filter by Match Status",
                    options=merged_df['MATCH_STATUS'].unique().tolist(),
                    default=merged_df['MATCH_STATUS'].unique().tolist()[:3]
                )
            with col_f2:
                search_supplier = st.text_input("🔎 Search Supplier", placeholder="Enter supplier name...")
            with col_f3:
                min_taxable = st.number_input("Min Taxable Value (₹)", min_value=0, value=0, step=1000)
            
            # Apply filters
            filtered_df = recon_df.copy()
            if status_filter:
                filtered_df = filtered_df[filtered_df['Match Status'].isin(status_filter)]
            if search_supplier:
                filtered_df = filtered_df[filtered_df['Supplier Name'].str.contains(search_supplier, case=False, na=False)]
            if min_taxable > 0:
                filtered_df = filtered_df[
                    (filtered_df['Taxable Value (2B)'].abs() >= min_taxable) | 
                    (filtered_df['Taxable Value (PR)'].abs() >= min_taxable)
                ]
            
            # Display filtered data
            st.dataframe(
                filtered_df.head(100),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Match Status": st.column_config.SelectboxColumn(
                        "Match Status",
                        options=["Exact", "Suggested", "Value Mismatch", "Missing in GSTR 2B", "Missing in PR"],
                        width="medium"
                    ),
                    "Taxable Value (2B)": st.column_config.NumberColumn("Taxable Value (2B)", format="₹%.2f"),
                    "Taxable Value (PR)": st.column_config.NumberColumn("Taxable Value (PR)", format="₹%.2f"),
                    "Total Tax (2B)": st.column_config.NumberColumn("Total Tax (2B)", format="₹%.2f"),
                    "Total Tax (PR)": st.column_config.NumberColumn("Total Tax (PR)", format="₹%.2f"),
                }
            )
            
            st.caption(f"Showing first 100 of {len(filtered_df):,} filtered records. Use filters above to narrow results.")
            
            # ========== EXCEL EXPORT ==========
            st.markdown("### 📤 Export Reconciliation Report")
            
            with st.spinner("📊 Generating comprehensive Excel report..."):
                excel_bytes = generate_excel_report(
                    merged_df, recon_df, summary, gstr2b_summary, pr_summary,
                    df_2b, df_pr, dup_pr_count,
                    include_charts=include_charts,
                    include_raw=include_raw_data,
                    max_rows=max_rows
                )
            
            col_dl1, col_dl2 = st.columns([1, 3])
            with col_dl1:
                st.download_button(
                    label="⚡ Download Full Report",
                    data=excel_bytes,
                    file_name=f"GST_Recon_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            st.success(f"✅ Report generated successfully! Contains {len(recon_df):,} reconciled records across {len(merged_df['MATCH_STATUS'].unique())} match categories.")
            
            # ========== TECHNICAL DETAILS (Collapsible) ==========
            with st.expander("🔧 Technical Details & Matching Logic"):
                st.markdown("""
                #### Matching Algorithm
                1. **Exact Match**: Same Supplier GSTIN + Document Number + Document Type + Exact Taxable/Tax Values
                2. **Suggested Match**: Same PAN + Normalized Document Number + Values within tolerance + Date differs but same FY
                3. **Value Mismatch**: GSTIN & Document match but taxable/tax difference exceeds tolerance threshold
                4. **Cross-State PAN Match**: Same PAN but different state GSTIN codes (inter-state transactions)
                5. **Missing in GSTR 2B**: Record exists in Purchase Register but not in GSTR-2B
                6. **Missing in PR**: Record exists in GSTR-2B but not in Purchase Register
                
                #### Key Processing Steps
                - Document numbers normalized (special chars removed, case-insensitive, leading zeros stripped)
                - PAN extracted from GSTIN (characters 3-12) for cross-state matching
                - Financial year calculated (April-March) for date-based suggested matching
                - Tax calculations: Total Tax = IGST + CGST + SGST + Cess
                - ITC eligibility auto-determined based on match status and configuration
                
                #### Configuration Applied
                - Tax/Taxable Tolerance: ₹{tolerance}
                - Date Tolerance: {date_tol_days} days within same FY
                - Reverse Charge Included: {include_rc}
                - Auto-claim ITC for Exact Matches: {auto_claim}
                """.format(
                    tolerance=tolerance,
                    date_tol_days=date_tolerance,
                    include_rc=include_reverse_charge,
                    auto_claim=auto_claim_itc
                ))
                
                st.code(f"""
# Sample matching key generation:
# MATCH_KEY = PAN + "|" + NORMALIZED_DOC + "|" + DOC_TYPE
# Example: "ADXFS5154R|11202324|INVOICE"

# Tolerance check:
# abs(TAXABLE_2B - TAXABLE_PR) <= {tolerance}

# Financial year check:
# FY = year if month >= 4 else year-1
# Same FY: FY_2B == FY_PR
                """, language="python")
    
    except Exception as e:
        st.error(f"❌ Processing Error: {str(e)}")
        st.exception(e)
        st.info("💡 Please ensure your files follow the sample template format with required columns.")

else:
    # Show welcome message when no files uploaded
    st.markdown("""
    <div class="section-card" style="text-align: center; padding: 40px;">
        <h3>👋 Welcome to GST Recon Pro</h3>
        <p style="color: #64748b; margin: 20px 0;">
            Upload your GSTR-2B and Purchase Register files to begin intelligent reconciliation.
            Our AI-powered engine will match invoices, identify discrepancies, and generate 
            compliance-ready reports.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 30px;">
            <div style="background: #f1f5f9; padding: 20px; border-radius: 12px; min-width: 200px;">
                <strong>🎯 Smart Matching</strong><br>
                <small>AI-powered invoice reconciliation with fuzzy matching</small>
            </div>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 12px; min-width: 200px;">
                <strong>📊 Live Insights</strong><br>
                <small>Real-time financial analytics and compliance alerts</small>
            </div>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 12px; min-width: 200px;">
                <strong>📤 Excel Export</strong><br>
                <small>Professional reports matching GST portal format</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
<div class="web-branding">
    <strong>🧾 GST Recon Pro</strong><br>
    Enterprise GST Reconciliation Engine<br>
    Developed by <b>ABHISHEK JAKKULA</b> | jakkulaabhishek5@gmail.com<br>
    <small>Version 2.0 • Last Updated: May 2026</small>
</div>
""", unsafe_allow_html=True)

# ================= HIDDEN INSTRUCTIONS FOR USER =================
with st.expander("ℹ️ How to Use This Application"):
    st.markdown("""
    ### Quick Start Guide
    
    1. **Download Sample Templates** (top of sidebar) to understand required file format
    2. **Prepare Your Files**:
       - GSTR-2B: Export from GST portal with columns: SUPPLIER GSTIN, DOCUMENT NUMBER, TAXABLE VALUE, IGST, CGST, SGST, SUPPLIER NAME, MY GSTIN, DOCUMENT DATE
       - Purchase Register: Your ERP export with same columns + optional: REVERSE_CHARGE, ITC_CLAIM_TYPE, PLACE_OF_SUPPLY
    3. **Configure Settings** (sidebar):
       - Adjust tolerance values based on your rounding practices
       - Enable/disable reverse charge processing
       - Set Excel export preferences
    4. **Upload Files** and click process
    5. **Review Dashboard**:
       - Check match rates and financial insights
       - Filter and explore detailed reconciliation data
       - Download comprehensive Excel report
    
    ### Understanding Match Statuses
    
    | Status | Description | Action Required |
    |--------|-------------|----------------|
    | ✅ Exact | Perfect match on all key fields | None - ITC auto-claimed |
    | 🔍 Suggested | Match on PAN+Doc, date differs within FY | Review date discrepancy |
    | ⚠️ Value Mismatch | Doc matches but values differ beyond tolerance | Investigate value difference |
    | 🔄 Cross-State | Same PAN, different state GSTIN | Verify inter-state transaction |
    | ❌ Missing in 2B | In books but not in GSTR-2B | Follow up with supplier |
    | 📥 Missing in PR | In GSTR-2B but not in books | Update Purchase Register |
    
    ### Pro Tips
    
    - Use consistent document numbering across systems for better matching
    - Ensure GSTINs are validated before upload
    - Review "Suggested" matches monthly to refine matching rules
    - Export reports before month-end for GSTR-3B filing
    
    ### Support
    
    For technical issues or feature requests, contact: jakkulaabhishek5@gmail.com
    """)
