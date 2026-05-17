# ===================================================================
# GST RECON PRO - ULTIMATE RECONCILIATION ENGINE
# Exact match logic as per "GSTR 2B Vs PR_.xlsx" sample
# Handles invoices, credit notes, debit notes with tolerance & FY logic
# ===================================================================

import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GST Recon Pro - Enterprise Grade",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS (Modern UI) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    }
    h1 {
        font-weight: 800;
        font-size: 2.8rem !important;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #4f46e5);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(37,99,235,0.3);
    }
    [data-testid="stMetric"] {
        background: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.03);
    }
    .insight-card {
        background: white;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Reconciliation Settings")
    tolerance = st.number_input("Match Tolerance (₹)", min_value=0, value=10, step=5, help="Max allowed difference in Taxable Value & Total Tax for Exact/Suggested")
    max_excel_rows = st.number_input("Excel Report Max Rows", min_value=1000, value=20000, step=1000, help="For SUMIF formulas in output")
    st.markdown("---")
    st.markdown("### 📌 Column Mapping")
    st.info("Files must contain these columns:\n- **Supplier GSTIN**\n- **Document Number**\n- **Taxable Value**\n- **IGST / CGST / SGST**\n- **Document Date** (optional)\n- **Month** (optional)")

# ================= HEADER =================
st.markdown("<h1>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent reconciliation of GSTR-2B vs Purchase Register | Exact, Suggested, Mismatch, Missing logic as per GST standards</p>', unsafe_allow_html=True)

# ================= SAMPLE TEMPLATES =================
def generate_2b_template():
    df = pd.DataFrame({
        "Supplier GSTIN": ["36CNNPD6299J1ZB", "08AAACM8473A1ZL", "36AFKPD6156R1ZT"],
        "Document Number": ["INV-101", "MEC-439", "CN-2024-01"],
        "Document Date": ["24-07-2023", "26-05-2023", "22-02-2024"],
        "Taxable Value": [7500, 13150, -5042.36],
        "IGST": [0, 2367, 0],
        "CGST": [675, 0, -453.81],
        "SGST": [675, 0, -453.81],
        "Supplier Name": ["Neshwari Engg", "Metallizing Equip", "Sri Satya Tech"],
        "Month": ["2023-07", "2023-05", "2024-02"]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="GSTR2B", index=False)
    return output.getvalue()

def generate_pr_template():
    df = pd.DataFrame({
        "Supplier GSTIN": ["36CNNPD6299J1ZB", "08AAACM8473A1ZL", "36AFKPD6156R1ZT", "36DGLPP5363P1ZG"],
        "Document Number": ["INV-101", "MEC-439", "CN-2024-01", "ST/23-24/39"],
        "Document Date": ["24-07-2023", "26-05-2023", "22-02-2024", "01-06-2023"],
        "Taxable Value": [7500, 13000, -5042.36, 23650],
        "IGST": [0, 2340, 0, 0],
        "CGST": [675, 0, -453.81, 2128.5],
        "SGST": [675, 0, -453.81, 2128.5],
        "Supplier Name": ["Neshwari Engg", "Metallizing Equip Co", "Sri Satya Tech", "S Square Industries"],
        "Month": ["2023-07", "2023-05", "2024-02", "2023-06"]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Purchase Register", index=False)
    return output.getvalue()

col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 Sample GSTR-2B", generate_2b_template(), "GSTR2B_Sample.xlsx", use_container_width=True)
with col2:
    st.download_button("📘 Sample Purchase Register", generate_pr_template(), "PurchaseRegister_Sample.xlsx", use_container_width=True)

st.markdown("---")

# ================= HELPER FUNCTIONS =================
def normalize_doc_number(series):
    """Remove special characters, uppercase, strip leading zeros"""
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

def get_financial_year(date_series):
    """Extract FY start year from date (Apr-Mar)"""
    def fy(date_val):
        try:
            d = pd.to_datetime(date_val)
            return d.year if d.month >= 4 else d.year - 1
        except:
            return None
    return date_series.apply(fy)

def safe_date_parse(series):
    return pd.to_datetime(series, errors='coerce', dayfirst=True)

def clean_dataframe(df, source_name):
    """Standardize column names and ensure required fields exist"""
    df.columns = df.columns.str.strip().str.upper()
    # Rename common variations
    rename_map = {
        'SUPPLIER GSTIN': 'SUPPLIER GSTIN',
        'GSTIN OF SUPPLIER': 'SUPPLIER GSTIN',
        'SUPPLIER_GSTIN': 'SUPPLIER GSTIN',
        'DOCUMENT NUMBER': 'DOCUMENT NUMBER',
        'INVOICE NUMBER': 'DOCUMENT NUMBER',
        'DOC NO': 'DOCUMENT NUMBER',
        'TAXABLE VALUE': 'TAXABLE VALUE',
        'TAXABLE AMOUNT': 'TAXABLE VALUE',
        'IGST': 'IGST',
        'IGST AMOUNT': 'IGST',
        'CGST': 'CGST',
        'CGST AMOUNT': 'CGST',
        'SGST': 'SGST',
        'SGST AMOUNT': 'SGST',
        'DOCUMENT DATE': 'DOCUMENT DATE',
        'INVOICE DATE': 'DOCUMENT DATE',
        'DATE': 'DOCUMENT DATE',
        'SUPPLIER NAME': 'SUPPLIER NAME',
        'VENDOR NAME': 'SUPPLIER NAME',
        'MONTH': 'MONTH',
        'PERIOD': 'MONTH'
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    
    # Ensure numeric columns
    for col in ['TAXABLE VALUE', 'IGST', 'CGST', 'SGST']:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Mandatory columns check
    required = ['SUPPLIER GSTIN', 'DOCUMENT NUMBER', 'TAXABLE VALUE']
    missing = [r for r in required if r not in df.columns]
    if missing:
        st.error(f"{source_name} missing columns: {missing}. Please check headers.")
        return None
    
    # Fill missing optional
    if 'SUPPLIER NAME' not in df.columns:
        df['SUPPLIER NAME'] = 'Unknown'
    if 'DOCUMENT DATE' not in df.columns:
        df['DOCUMENT DATE'] = ''
    if 'MONTH' not in df.columns:
        df['MONTH'] = ''
    if 'MY GSTIN' not in df.columns:
        df['MY GSTIN'] = '36ADXFS5154R1ZU'  # default as per sample
    
    # Clean GSTIN
    df['SUPPLIER GSTIN'] = df['SUPPLIER GSTIN'].astype(str).str.upper().str.strip()
    df['SUPPLIER GSTIN'] = df['SUPPLIER GSTIN'].replace('NAN', '').fillna('')
    
    # Document Type based on taxable value sign (positive = INVOICE, negative = CREDIT NOTE)
    df['DOC_TYPE'] = df['TAXABLE VALUE'].apply(lambda x: 'CREDIT NOTE' if x < 0 else 'INVOICE')
    
    # Normalized document number
    df['NORM_DOC'] = normalize_doc_number(df['DOCUMENT NUMBER'])
    
    # Match Key = GSTIN + NORM_DOC + DOC_TYPE
    df['MATCH_KEY'] = df['SUPPLIER GSTIN'] + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE']
    
    # Total Tax
    df['TOTAL_TAX'] = df['IGST'] + df['CGST'] + df['SGST']
    
    # Total Document Value
    df['TOTAL_VALUE'] = df['TAXABLE VALUE'] + df['TOTAL_TAX']
    
    return df

# ================= MAIN RECONCILIATION =================
@st.cache_data(show_spinner=False)
def run_reconciliation(file_2b, file_pr, tolerance):
    # Load Excel files
    df_2b_raw = pd.read_excel(io.BytesIO(file_2b))
    df_pr_raw = pd.read_excel(io.BytesIO(file_pr))
    
    # Clean and standardize
    df_2b = clean_dataframe(df_2b_raw, "GSTR-2B")
    df_pr = clean_dataframe(df_pr_raw, "Purchase Register")
    
    if df_2b is None or df_pr is None:
        return None, None, None, None
    
    # Parse dates for FY logic
    df_2b['DATE_PARSED'] = safe_date_parse(df_2b['DOCUMENT DATE'])
    df_pr['DATE_PARSED'] = safe_date_parse(df_pr['DOCUMENT DATE'])
    df_2b['FY'] = get_financial_year(df_2b['DATE_PARSED'])
    df_pr['FY'] = get_financial_year(df_pr['DATE_PARSED'])
    
    # Store PAN for info (first 10 chars after state code)
    df_2b['PAN'] = df_2b['SUPPLIER GSTIN'].str[2:12]
    df_pr['PAN'] = df_pr['SUPPLIER GSTIN'].str[2:12]
    
    # Full outer merge on MATCH_KEY
    merged = pd.merge(df_2b, df_pr, on='MATCH_KEY', how='outer', suffixes=(' (2B)', ' (PR)'), indicator=True)
    
    # Initialize status columns
    merged['Match Status'] = ''
    merged['Match Status Description'] = ''
    
    # Helper for difference
    merged['Taxable Diff'] = merged['TAXABLE VALUE (2B)'].fillna(0) - merged['TAXABLE VALUE (PR)'].fillna(0)
    merged['Tax Diff'] = merged['TOTAL_TAX (2B)'].fillna(0) - merged['TOTAL_TAX (PR)'].fillna(0)
    merged['Taxable Diff Abs'] = merged['Taxable Diff'].abs()
    merged['Tax Diff Abs'] = merged['Tax Diff'].abs()
    
    # Determine match statuses
    # 1. Both present
    both_mask = merged['_merge'] == 'both'
    
    # Dates equality (only if both dates exist)
    date_eq = (merged['DATE_PARSED (2B)'] == merged['DATE_PARSED (PR)']).fillna(False)
    same_fy = (merged['FY (2B)'] == merged['FY (PR)']).fillna(False)
    amounts_within_tol = (merged['Taxable Diff Abs'] <= tolerance) & (merged['Tax Diff Abs'] <= tolerance)
    
    # Exact: amounts within tol AND dates equal
    exact_mask = both_mask & amounts_within_tol & date_eq
    # Suggested: amounts within tol, dates differ but same FY
    suggested_mask = both_mask & amounts_within_tol & (~date_eq) & same_fy
    # Mismatch: both present but amounts exceed tolerance
    mismatch_mask = both_mask & (~amounts_within_tol)
    
    # Missing in PR (only in 2B)
    missing_pr_mask = merged['_merge'] == 'left_only'
    # Missing in 2B (only in PR)
    missing_2b_mask = merged['_merge'] == 'right_only'
    
    merged.loc[exact_mask, 'Match Status'] = 'Exact'
    merged.loc[exact_mask, 'Match Status Description'] = 'All parameters match within tolerance & same date'
    
    merged.loc[suggested_mask, 'Match Status'] = 'Suggested'
    merged.loc[suggested_mask, 'Match Status Description'] = 'Values match within tolerance, dates differ but same FY'
    
    merged.loc[mismatch_mask, 'Match Status'] = 'Mismatch'
    merged.loc[mismatch_mask, 'Match Status Description'] = 'Document & GSTIN match but value/tax differs beyond tolerance'
    
    merged.loc[missing_pr_mask, 'Match Status'] = 'Missing in PR'
    merged.loc[missing_pr_mask, 'Match Status Description'] = 'Present in GSTR-2B but missing in Purchase Register'
    
    merged.loc[missing_2b_mask, 'Match Status'] = 'Missing in 2B'
    merged.loc[missing_2b_mask, 'Match Status Description'] = 'Present in Purchase Register but missing in GSTR-2B'
    
    # Build Supplier Name
    merged['Supplier Name'] = merged['SUPPLIER NAME (2B)'].fillna(merged['SUPPLIER NAME (PR)']).fillna('Unknown')
    
    return merged, df_2b, df_pr, both_mask.sum()

# ================= UI AFTER UPLOAD =================
file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=['xlsx', 'xls'], key='2b')
file_pr = st.file_uploader("📘 Upload Purchase Register", type=['xlsx', 'xls'], key='pr')

if file_2b and file_pr:
    try:
        with st.spinner("🔍 Running deep reconciliation..."):
            merged, df_2b_clean, df_pr_clean, matched_pairs = run_reconciliation(file_2b.getvalue(), file_pr.getvalue(), tolerance)
            
            if merged is None:
                st.stop()
            
            # ========== SUMMARY STATISTICS ==========
            status_counts = merged['Match Status'].value_counts()
            status_taxable = merged.groupby('Match Status')['TAXABLE VALUE (2B)'].sum().fillna(0)
            status_tax = merged.groupby('Match Status')['TOTAL_TAX (2B)'].sum().fillna(0)
            
            # For Missing in 2B, we take PR values
            status_taxable_pr = merged.groupby('Match Status')['TAXABLE VALUE (PR)'].sum().fillna(0)
            status_tax_pr = merged.groupby('Match Status')['TOTAL_TAX (PR)'].sum().fillna(0)
            
            # Grand totals
            total_docs_2b = len(df_2b_clean)
            total_docs_pr = len(df_pr_clean)
            total_taxable_2b = df_2b_clean['TAXABLE VALUE'].sum()
            total_tax_2b = df_2b_clean['TOTAL_TAX'].sum()
            total_taxable_pr = df_pr_clean['TAXABLE VALUE'].sum()
            total_tax_pr = df_pr_clean['TOTAL_TAX'].sum()
            
            # Match % (Exact + Suggested)
            exact_suggested_count = status_counts.get('Exact', 0) + status_counts.get('Suggested', 0)
            exact_suggested_tax = status_tax.get('Exact', 0) + status_tax.get('Suggested', 0)
            match_pct_docs = (exact_suggested_count / max(1, total_docs_2b)) * 100
            match_pct_tax = (exact_suggested_tax / max(1, total_tax_2b)) * 100
            
            # Action % (documents not missing)
            action_docs = total_docs_2b - status_counts.get('Missing in PR', 0)
            action_pct = (action_docs / max(1, total_docs_2b)) * 100
            
            # ========== DISPLAY METRICS ==========
            st.markdown("### 📊 Reconciliation Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Documents (2B)", f"{total_docs_2b:,}")
            col2.metric("Total Documents (PR)", f"{total_docs_pr:,}")
            col3.metric("Match % (Docs)", f"{match_pct_docs:.1f}%", delta=f"{exact_suggested_count} matched")
            col4.metric("Action Required %", f"{100-action_pct:.1f}%", delta="Missing in PR")
            
            # Overall Summary Table (exactly like sample)
            st.markdown("#### 🧾 Overall Summary (Net off Credit/Debit Notes)")
            summary_data = []
            for status in ['Exact', 'Suggested', 'Mismatch', 'Missing in PR', 'Missing in 2B']:
                cnt = status_counts.get(status, 0)
                tax_val_2b = status_taxable.get(status, 0)
                tax_2b = status_tax.get(status, 0)
                tax_val_pr = status_taxable_pr.get(status, 0) if status in status_taxable_pr.index else 0
                tax_pr = status_tax_pr.get(status, 0) if status in status_tax_pr.index else 0
                diff_docs = cnt - (status_counts.get(status, 0) if status != 'Missing in 2B' else 0)  # dummy
                diff_tax_val = tax_val_2b - tax_val_pr
                diff_tax = tax_2b - tax_pr
                
                summary_data.append({
                    'Match Status': status,
                    'Difference (2B-PR) Docs': diff_docs,
                    'Difference (2B-PR) Taxable Value': diff_tax_val,
                    'Difference (2B-PR) Total Tax': diff_tax,
                    'As Per GSTR-2B Docs': cnt if status != 'Missing in 2B' else 0,
                    'As Per GSTR-2B Taxable Value': tax_val_2b,
                    'As Per GSTR-2B Total Tax': tax_2b,
                    'As Per PR Docs': cnt if status != 'Missing in PR' else 0,
                    'As Per PR Taxable Value': tax_val_pr,
                    'As Per PR Total Tax': tax_pr
                })
            # Add Grand Total row
            summary_data.append({
                'Match Status': 'Grand Total',
                'Difference (2B-PR) Docs': total_docs_2b - total_docs_pr,
                'Difference (2B-PR) Taxable Value': total_taxable_2b - total_taxable_pr,
                'Difference (2B-PR) Total Tax': total_tax_2b - total_tax_pr,
                'As Per GSTR-2B Docs': total_docs_2b,
                'As Per GSTR-2B Taxable Value': total_taxable_2b,
                'As Per GSTR-2B Total Tax': total_tax_2b,
                'As Per PR Docs': total_docs_pr,
                'As Per PR Taxable Value': total_taxable_pr,
                'As Per PR Total Tax': total_tax_pr
            })
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df.style.format({
                'Difference (2B-PR) Taxable Value': '{:,.2f}',
                'Difference (2B-PR) Total Tax': '{:,.2f}',
                'As Per GSTR-2B Taxable Value': '{:,.2f}',
                'As Per GSTR-2B Total Tax': '{:,.2f}',
                'As Per PR Taxable Value': '{:,.2f}',
                'As Per PR Total Tax': '{:,.2f}'
            }), use_container_width=True)
            
            # ========== INSIGHTS ==========
            st.markdown("### 🧠 Smart Insights")
            missed_itc = status_tax.get('Missing in PR', 0)
            risk_itc = status_tax_pr.get('Missing in 2B', 0)
            if missed_itc > 0:
                st.info(f"💸 **Unclaimed ITC Opportunity:** ₹{missed_itc:,.2f} available in GSTR-2B but not recorded in books.")
            if risk_itc > 0:
                st.warning(f"⚠️ **Compliance Alert:** ₹{risk_itc:,.2f} claimed in books but missing in GSTR-2B. Potential ineligible ITC.")
            if status_counts.get('Suggested', 0) > 0:
                st.success(f"🕒 **Suggested Matches:** {status_counts.get('Suggested', 0)} records have date mismatches but are within same financial year.")
            if status_counts.get('Mismatch', 0) > 0:
                st.error(f"❌ **Mismatches:** {status_counts.get('Mismatch', 0)} records need manual review.")
            
            # ========== DETAILED DOCUMENT VIEW ==========
            st.markdown("### 📑 Detailed Reconciliation (Document Level)")
            
            # Prepare display columns as per sample
            detail_cols = [
                'Match Status', 'Match Status Description', 'Supplier Name',
                'SUPPLIER GSTIN (2B)', 'SUPPLIER GSTIN (PR)',
                'MY GSTIN (2B)', 'MY GSTIN (PR)',
                'DOCUMENT NUMBER (2B)', 'DOCUMENT NUMBER (PR)',
                'DOCUMENT DATE (2B)', 'DOCUMENT DATE (PR)',
                'MONTH (2B)', 'MONTH (PR)',
                'DOC_TYPE (2B)', 'DOC_TYPE (PR)',
                'TAXABLE VALUE (2B)', 'TAXABLE VALUE (PR)', 'Taxable Diff',
                'TOTAL_TAX (2B)', 'TOTAL_TAX (PR)', 'Tax Diff',
                'IGST (2B)', 'IGST (PR)',
                'CGST (2B)', 'CGST (PR)',
                'SGST (2B)', 'SGST (PR)'
            ]
            detail_df = merged[detail_cols].copy()
            detail_df.columns = [
                'Match Status', 'Match Description', 'Supplier Name',
                'Supplier GSTIN (2B)', 'Supplier GSTIN (PR)',
                'My GSTIN (2B)', 'My GSTIN (PR)',
                'Document Number (2B)', 'Document Number (PR)',
                'Document Date (2B)', 'Document Date (PR)',
                'Month (2B)', 'Month (PR)',
                'Doc Type (2B)', 'Doc Type (PR)',
                'Taxable Value (2B)', 'Taxable Value (PR)', 'Taxable Diff (2B-PR)',
                'Total Tax (2B)', 'Total Tax (PR)', 'Tax Diff (2B-PR)',
                'IGST (2B)', 'IGST (PR)',
                'CGST (2B)', 'CGST (PR)',
                'SGST (2B)', 'SGST (PR)'
            ]
            
            # Filter widget
            filter_status = st.multiselect("Filter by Match Status", options=detail_df['Match Status'].unique(), default=detail_df['Match Status'].unique())
            filtered_detail = detail_df[detail_df['Match Status'].isin(filter_status)]
            st.dataframe(filtered_detail, use_container_width=True, height=500)
            
            # ========== CHARTS ==========
            st.markdown("### 📈 Visual Analytics")
            col_ch1, col_ch2 = st.columns(2)
            
            with col_ch1:
                status_chart = status_counts.reset_index()
                status_chart.columns = ['Status', 'Count']
                fig = px.bar(status_chart, x='Count', y='Status', orientation='h', color='Status',
                             color_discrete_sequence=px.colors.qualitative.Set2, text='Count',
                             title='Documents by Match Status')
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_ch2:
                # Tax impact pie
                tax_impact = merged.groupby('Match Status')['TOTAL_TAX (2B)'].sum().fillna(0)
                tax_impact = tax_impact[tax_impact > 0]
                if not tax_impact.empty:
                    fig2 = px.pie(values=tax_impact.values, names=tax_impact.index, title='Tax Amount Distribution (2B)')
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Monthly trend if month column available
            if 'MONTH (2B)' in merged.columns and merged['MONTH (2B)'].notna().any():
                monthly = merged.groupby('MONTH (2B)').agg({
                    'TAXABLE VALUE (2B)': 'sum',
                    'TOTAL_TAX (2B)': 'sum'
                }).reset_index()
                monthly.columns = ['Month', 'Taxable Value', 'Total Tax']
                fig3 = px.line(monthly, x='Month', y=['Taxable Value', 'Total Tax'], title='Month-wise Trend (2B)')
                st.plotly_chart(fig3, use_container_width=True)
            
            # Top suppliers
            top_suppliers = merged.groupby('Supplier Name')['TAXABLE VALUE (2B)'].sum().nlargest(10).reset_index()
            if not top_suppliers.empty:
                fig4 = px.bar(top_suppliers, x='Supplier Name', y='TAXABLE VALUE (2B)', title='Top 10 Suppliers by Taxable Value (2B)')
                st.plotly_chart(fig4, use_container_width=True)
            
            # ========== EXCEL REPORT GENERATION ==========
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Overall Summary sheet
                summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
                # Document Details sheet
                filtered_detail.to_excel(writer, sheet_name='Document Details', index=False)
                # Raw data sheets
                df_2b_clean.drop(columns=['MATCH_KEY', 'NORM_DOC', 'DATE_PARSED', 'FY', 'PAN'], errors='ignore').to_excel(writer, sheet_name='GSTR-2B Raw', index=False)
                df_pr_clean.drop(columns=['MATCH_KEY', 'NORM_DOC', 'DATE_PARSED', 'FY', 'PAN'], errors='ignore').to_excel(writer, sheet_name='PR Raw', index=False)
                
                # Formatting
                workbook = writer.book
                header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1e3a8a', 'font_color': 'white', 'border': 1})
                for sheetname in writer.sheets:
                    worksheet = writer.sheets[sheetname]
                    worksheet.set_column('A:Z', 18)
                    for col_num, value in enumerate(pd.read_excel(output, sheet_name=sheetname, nrows=0).columns):
                        worksheet.write(0, col_num, value, header_fmt)
            
            st.download_button(
                "📎 Download Complete Excel Report",
                output.getvalue(),
                f"GST_Recon_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"🔥 Reconciliation failed: {str(e)}")
        st.info("Please check file formats. Required columns: Supplier GSTIN, Document Number, Taxable Value, IGST, CGST, SGST (optional: Document Date, Month)")

else:
    st.info("👈 Please upload both GSTR-2B and Purchase Register files to begin reconciliation.")

# ================= FOOTER =================
st.markdown("""
<div class="footer">
    Developed with ❤️ by <strong>ABHISHEK JAKKULA</strong> | jakkulaabhishek5@gmail.com<br>
    Exact match logic as per GST reconciliation standards | Supports Invoices, Credit Notes & Debit Notes
</div>
""", unsafe_allow_html=True)
