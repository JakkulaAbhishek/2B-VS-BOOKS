# ===================================================================
# GST RECON PRO - Enterprise Grade Reconciliation
# Exactly matches the structure of the provided Excel samples
# ===================================================================

import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px
import re

# ================= PAGE CONFIG =================
st.set_page_config(page_title="GST Recon Pro", layout="wide")

# ================= CUSTOM CSS (clean & minimal) =================
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    h1 { font-weight: 700; color: #1e293b; }
    .stButton>button { background: #2563eb; color: white; border-radius: 8px; }
    .insight-card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; border-left: 5px solid #3b82f6; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .footer { text-align: center; margin-top: 40px; padding: 16px; font-size: 0.8rem; color: #64748b; border-top: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    tolerance = st.number_input("Match Tolerance (₹)", min_value=0, value=10, step=5)
    max_excel_rows = st.number_input("Excel Report Max Rows", min_value=1000, value=20000, step=1000)

# ================= HEADER =================
st.markdown("<h1>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown("Reconcile GSTR‑2B with Purchase Register – Exact match logic as per your sample files")

# ================= SAMPLE FILE GENERATORS (exact structure as your uploaded files) =================

def generate_sample_2b():
    """
    Generates an Excel file that EXACTLY matches the structure of your
    'GSTR 2B Vs PR_.xlsx' file:
        - Sheet: 'Overall Summary'
        - Sheet: 'Document Details (Inv CDN)'
    With all the columns shown in your sample.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # ---------- Sheet: Overall Summary ----------
        summary_data = {
            'Match Status': ['Exact', 'Manually linked', 'Manually Group linked', 'Suggested', 'Mismatch', 'Missing in GSTR 2B(at Pan Level/GSTIN )', 'Missing in PR', 'Grand Total'],
            'Difference(2B-PR) Number of Documents': [0, 0, 0, 0, 0, 13, 113, 0],
            'Difference(2B-PR) Taxable Value': [0, 0, 0, 0, 0, 2482999, 6368117.76, 0],
            'Difference(2B-PR) Total Tax': [0, 0, 0, 0, 0, 439991.52, 1263620.75, 0],
            'As Per GSTR 2B Number of Documents': [1024, 0, 0, 200, 1, 13, 0, 1238],
            'As Per GSTR 2B Taxable Value': [36526638.28, 0, 0, 13446968.37, 300, 2482999, 0, 52456905.65],
            'As Per GSTR 2B Total Tax': [6463891.27, 0, 0, 2329672.99, 54, 439991.52, 0, 9233609.78],
            'As Per Purchase Books Number of Documents': [1024, 0, 0, 200, 1, 0, 113, 1338],
            'As Per Purchase Books Taxable Value': [36526638.28, 0, 0, 13446968.37, 300, 0, 6368117.76, 56341724.41],
            'As Per Purchase Books Total Tax': [6463891.27, 0, 0, 2329672.99, 54, 0, 1263620.75, 10057239.01],
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)

        # ---------- Sheet: Document Details (Inv CDN) ----------
        # Columns exactly as in your sample (all 70+ columns)
        detail_cols = [
            'Action Errors', 'Match Status', 'Match Status Description', 'Supplier Name',
            'Supplier GSTIN (2B)', 'Supplier GSTIN (PR)', 'My GSTIN (2B)', 'My GSTIN (PR)',
            'Document Number (2B)', 'Document Number (PR)', 'Document Date (2B)', 'Document Date (PR)',
            'Total Document Value (2B)', 'Total Document Value (PR)', 'Taxable Value (2B)', 'Taxable Value (PR)',
            'Tax Difference(2B-PR)', 'Total Tax (2B)', 'Total Tax (PR)', 'IGST (2B)', 'IGST (PR)',
            'CGST (2B)', 'CGST (PR)', 'SGST (2B)', 'SGST (PR)', 'Cess (2B)', 'Cess (PR)',
            'Document Type(2B)', 'Document Type(PR)', 'Section Name 2B', 'Section Name (Pr)',
            'Return Period (2B)', 'Return Period (PR)', 'Reverse Charge (2B)', 'Reverse Charge (PR)',
            'Place of Supply (2B)', 'Place of Supply (PR)', 'Original Document Number (2B)',
            'Original Document Date (2B)', 'Reason (2B)', 'ITC Availablity(2B)', 'ITC Claim Eligibility(PR)',
            'Amendment Category', 'IGST Claimed Amount', 'CGST Claimed Amount', 'SGST Claimed Amount',
            'CESS Claimed Amount', 'GSTR1 Filing Status', 'GSTR3B Filing Status', 'Vendor GSTIN Status',
            'ITC Claim Status', 'ITC Claim Month as per 3B', 'ITC Claim Amount', 'GSTR-1/IFF/5 Filing Date',
            'GSTR-1/IFF/5 Filing Period', 'Effective date of cancellation of Supplier GSTIN',
            'Vendor Payment Status', 'Reason for Hold/Release Vendor Payment', 'Vendor Payment Remarks',
            'Is Vendor Payment status manually overwritten?', 'IRN', 'IRN generation date', 'Group Id',
            'Group Remark', 'Remarks (2B)', 'Remarks (PR)', 'Vendor Filing Frequency', 'Vendor Risk',
            'Vendor Code', 'Financial Year', 'Voucher Number', 'Out of Range (2B)', 'Out of Range (PR)',
            'Claimable ITC - CGST', 'Claimable ITC - SGST', 'Claimable ITC - IGST', 'Claimable ITC - Cess'
        ]
        
        # Create sample rows as dictionaries (ensuring all columns have a value)
        row1 = {col: '' for col in detail_cols}
        row1.update({
            'Action Errors': 'action_errors',
            'Match Status': 'Missing in PR',
            'Supplier Name': 'M/S SRI SATYA TECHNOLOGIES',
            'Supplier GSTIN (2B)': '36AFKPD6156R1ZT',
            'My GSTIN (2B)': '36ADXFS5154R1ZU',
            'Document Number (2B)': '23',
            'Document Date (2B)': '22-02-2024',
            'Total Document Value (2B)': -5950,
            'Taxable Value (2B)': -5042.36,
            'Tax Difference(2B-PR)': -907.62,
            'Total Tax (2B)': -907.62,
            'CGST (2B)': -453.81,
            'SGST (2B)': -453.81,
            'Document Type(2B)': 'CREDIT',
            'Section Name 2B': 'CDN',
            'Return Period (2B)': '02-2024',
            'Reverse Charge (2B)': 'NO',
            'Place of Supply (2B)': 'TELANGANA',
            'ITC Availablity(2B)': 'YES',
            'GSTR1 Filing Status': 'FILED',
            'GSTR3B Filing Status': 'N',
            'ITC Claim Status': 'No Action',
            'GSTR-1/IFF/5 Filing Date': '11-03-2024',
            'GSTR-1/IFF/5 Filing Period': '022024',
            'IRN': 'ed58f5e1d6b8dd60930083928a0b9396739e93be5aacf87bb2c73bd125a28c84',
            'IRN generation date': '22-02-2024',
            'Financial Year': '2023-24',
            'Out of Range (2B)': False,
            'Out of Range (PR)': False
        })
        
        row2 = {col: '' for col in detail_cols}
        row2.update({
            'Action Errors': 'action_errors',
            'Match Status': 'Exact',
            'Match Status Description': 'All parameters matching except rounding off',
            'Supplier Name': 'NESHWARI ENGINEERING AND SERVICES',
            'Supplier GSTIN (2B)': '36CNNPD6299J1ZB',
            'Supplier GSTIN (PR)': '36CNNPD6299J1ZB',
            'My GSTIN (2B)': '36ADXFS5154R1ZU',
            'My GSTIN (PR)': '36ADXFS5154R1ZU',
            'Document Number (2B)': '11/2023-24',
            'Document Number (PR)': '11/2023-24',
            'Document Date (2B)': '24-07-2023',
            'Document Date (PR)': '24-07-2023',
            'Total Document Value (2B)': 8850,
            'Total Document Value (PR)': 8850,
            'Taxable Value (2B)': 7500,
            'Taxable Value (PR)': 7500,
            'Total Tax (2B)': 1350,
            'Total Tax (PR)': 1350,
            'CGST (2B)': 675,
            'CGST (PR)': 675,
            'SGST (2B)': 675,
            'SGST (PR)': 675,
            'Document Type(2B)': 'INVOICE',
            'Document Type(PR)': 'INVOICE',
            'Section Name 2B': 'B2B',
            'Section Name (Pr)': 'B2B',
            'Return Period (2B)': '07-2023',
            'Return Period (PR)': '07-2023',
            'Reverse Charge (2B)': 'NO',
            'Reverse Charge (PR)': 'NO',
            'Place of Supply (2B)': 'TELANGANA',
            'Place of Supply (PR)': 'TELANGANA',
            'ITC Availablity(2B)': 'YES',
            'ITC Claim Eligibility(PR)': 'ELIGIBLE',
            'CGST Claimed Amount': 675,
            'SGST Claimed Amount': 675,
            'GSTR1 Filing Status': 'FILED',
            'GSTR3B Filing Status': 'N',
            'ITC Claim Status': 'Claim ITC',
            'ITC Claim Month as per 3B': '03-2024',
            'ITC Claim Amount': 1350,
            'GSTR-1/IFF/5 Filing Date': '11-08-2023',
            'GSTR-1/IFF/5 Filing Period': '072023',
            'Financial Year': '2023-24',
            'Claimable ITC - CGST': 675,
            'Claimable ITC - SGST': 675
        })
        
        sample_rows = [row1, row2]
        detail_df = pd.DataFrame(sample_rows)
        detail_df.to_excel(writer, sheet_name='Document Details (Inv CDN)', index=False)

        # Formatting
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1e3a8a', 'font_color': 'white'})
        for sheetname, df in [('Overall Summary', summary_df), ('Document Details (Inv CDN)', detail_df)]:
            worksheet = writer.sheets[sheetname]
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_fmt)
            worksheet.set_column('A:ZZ', 16)
    return output.getvalue()

def generate_sample_books():
    """
    Generates an Excel file that EXACTLY matches the structure of your
    'Sample Books and 2B.xlsx' file:
        - Sheet: 'Purchase Invoice'
        - Sheet: 'Purchase Credit Debit Note'
        - Sheet: 'Summary' (with formulas)
        - Sheet: 'State Code Definition'
        - Sheet: 'Data Validation'
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # ---------- Purchase Invoice ----------
        inv_cols = [
            'Books Month', 'Invoice Date *', 'Invoice Number *', 'Supplier Name', 'Supplier GSTIN',
            'State Place of Supply', 'Is the item a GOOD (G) or SERVICE (S)', 'Item Description',
            'HSN or SAC code', 'Item Quantity', 'Item Unit of Measurement', 'Item Taxable Value *',
            'GST Tax Rate', 'IGST Amount', 'CGST Amount', 'SGST Amount', 'CESS Amount',
            'Total Transaction Value *', 'Is Reverse Charge Applicable?', 'ITC Claim Type'
        ]
        inv_data = [
            ['2024-03-01', '2024-03-01', 'aa', 'SHRI AAIJI INDUSTRIAL', '36AASPR7710K1ZV', '', '', '', '', '', '', 2140, '', 0, 192.6, 192.6, '', 2525.2, '', ''],
            ['2024-03-01', '2024-03-01', 'bb', 'K SQUARE TECHNOLOGIES', '36AASPR7307H1ZJ', '', '', '', '', '', '', 8060, '', 0, 725.4, 725.4, '', 9510.8, '', ''],
        ]
        inv_df = pd.DataFrame(inv_data, columns=inv_cols)
        inv_df.to_excel(writer, sheet_name='Purchase Invoice', index=False)

        # ---------- Purchase Credit Debit Note ----------
        cdn_cols = [
            'Books Month', 'Credit/ Debit Note Date *', 'Credit/ Debit Note Number *',
            'Credit(C)/ Debit(D) Note Type *', 'Linked Invoice Date', 'Linked Invoice Number',
            'Supplier Name', 'Supplier GSTIN', 'State Place of Supply',
            'Is the item a GOOD (G) or SERVICE (S)', 'Item Description', 'HSN or SAC code',
            'Item Quantity', 'Item Unit of Measurement', 'Item Taxable Value *', 'GST Tax Rate',
            'IGST Amount', 'CGST Amount', 'SGST Amount', 'CESS Amount', 'Total Transaction Value *',
            'Is Reverse Charge Applicable?', 'Reason for Issuing CDN', 'ITC Claim Type'
        ]
        cdn_data = [
            ['2024-02-01', '2024-02-22', 'CN-001', 'C', '2024-02-15', 'INV-123', 'SRI SATYA TECHNOLOGIES',
             '36AFKPD6156R1ZT', 'Telangana', 'S', 'Services', '9983', 1, 'Nos', -5042.36, 18, 0, -453.81, -453.81, 0, -5950, 'N', 'Credit Note', 'Input'],
        ]
        cdn_df = pd.DataFrame(cdn_data, columns=cdn_cols)
        cdn_df.to_excel(writer, sheet_name='Purchase Credit Debit Note', index=False)

        # ---------- Summary (placeholder with correct column headers) ----------
        summary_cols = ['A','B','C','D','E','F','G','H','I','J']
        summary_data_rows = [
            ['','','','','','','','','',''],
            ['','','','','','','','','',''],
            ['','Invoice Summary','','','','','','','',''],
            ['','','Transaction Type','# Rows','Total taxable Value','IGST Amount','CGST Amount','SGST Amount','Total GST Amount','Total Transaction value'],
            ['','','B2B','=SUMPRODUCT(1*COUNTIFS(...))','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F5:G5)+...','=I5+E5'],
            ['','','B2C','=SUMPRODUCT(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F6:G6)+...','=I6+E6'],
            ['','','Total','=SUM(D5:D6)','=SUM(E5:E6)','=SUM(F5:F6)','=SUM(G5:G6)','=SUM(H5:H6)','=SUM(I5:I6)','=SUM(J5:J6)'],
            ['','','','','','','','','',''],
            ['','CDN Summary','','','','','','','',''],
            ['','Note Type','Transaction Type','# Rows','Total taxable Value','IGST Amount','CGST Amount','SGST Amount','Total GST Amount','Total Transaction value'],
            ['','Credit','B2B','=SUMPRODUCT(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F11:H11)+...','=I11+E11'],
            ['','Credit','B2C','=SUMPRODUCT(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F12:H12)+...','=I12+E12'],
            ['','Debit','B2B','=SUMPRODUCT(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F13:H13)+...','=I13+E13'],
            ['','Debit','B2C','=SUMPRODUCT(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUMIFS(...)','=SUM(F14:H14)+...','=I14+E14'],
            ['','Total','','=SUM(D11:D14)','=SUM(E11:E14)','=SUM(F11:F14)','=SUM(G11:G14)','=SUM(H11:H14)','=SUM(I11:I14)','=SUM(J11:J14)'],
        ]
        summary_df = pd.DataFrame(summary_data_rows, columns=summary_cols)
        summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)

        # ---------- State Code Definition ----------
        state_data = {
            'State': ['Telangana', 'Andhra Pradesh', 'Maharashtra'],
            'State Name': ['Telangana', 'Andhra Pradesh', 'Maharashtra'],
            '2 digit code': [36, 37, 27],
            'ISO Code': ['IN-TG', 'IN-AP', 'IN-MH'],
            'State Code': ['TG', 'AP', 'MH']
        }
        state_df = pd.DataFrame(state_data)
        state_df.to_excel(writer, sheet_name='State Code Definition', index=False)

        # ---------- Data Validation ----------
        dv_data = {
            'Item_Category': ['G', 'S', 'NA'],
            'Credit Debit': ['C', 'D', ''],
            'Reverse Charge': ['Y', 'N', ''],
            'Tax Rate': [0, 0.1, 0.25],
            'ITC Claim Type': ['Input', 'Input Service', 'Capital Good']
        }
        dv_df = pd.DataFrame(dv_data)
        dv_df.to_excel(writer, sheet_name='Data Validation', index=False)

        # Formatting
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1e3a8a', 'font_color': 'white'})
        for sheetname, df in [('Purchase Invoice', inv_df), ('Purchase Credit Debit Note', cdn_df)]:
            worksheet = writer.sheets[sheetname]
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_fmt)
            worksheet.set_column('A:Z', 18)
    return output.getvalue()

# ================= DOWNLOAD BUTTONS FOR SAMPLES =================
col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 Download Sample GSTR‑2B (exact structure)", generate_sample_2b(),
                       "GSTR2B_Sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with col2:
    st.download_button("📘 Download Sample Purchase Register (exact structure)", generate_sample_books(),
                       "PurchaseRegister_Sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")

# ================= RECONCILIATION ENGINE =================
def load_2b_data(file_bytes):
    """Reads the uploaded GSTR‑2B file (which should follow the structure of your 'Document Details (Inv CDN)' sheet)."""
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name='Document Details (Inv CDN)')
    # Map required columns
    rename_map = {
        'Supplier GSTIN (2B)': 'SUPPLIER GSTIN',
        'Document Number (2B)': 'DOCUMENT NUMBER',
        'Taxable Value (2B)': 'TAXABLE VALUE',
        'IGST (2B)': 'IGST',
        'CGST (2B)': 'CGST',
        'SGST (2B)': 'SGST',
        'Document Date (2B)': 'DOCUMENT DATE',
        'Supplier Name': 'SUPPLIER NAME',
        'Month (2B)': 'MONTH',
        'My GSTIN (2B)': 'MY GSTIN',
        'Document Type(2B)': 'DOC_TYPE',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    # Ensure numeric columns
    for col in ['TAXABLE VALUE', 'IGST', 'CGST', 'SGST']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    # Set DOC_TYPE from Taxable Value sign if not present
    if 'DOC_TYPE' not in df.columns:
        df['DOC_TYPE'] = df['TAXABLE VALUE'].apply(lambda x: 'CREDIT NOTE' if x < 0 else 'INVOICE')
    # Normalize document number
    df['NORM_DOC'] = df['DOCUMENT NUMBER'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')
    df['MATCH_KEY'] = df['SUPPLIER GSTIN'].astype(str).str.upper() + '|' + df['NORM_DOC'] + '|' + df['DOC_TYPE']
    df['TOTAL_TAX'] = df['IGST'] + df['CGST'] + df['SGST']
    return df

def load_pr_data(file_bytes):
    """Reads the Purchase Register file with sheets 'Purchase Invoice' and 'Purchase Credit Debit Note'."""
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    invoices = pd.read_excel(xl, sheet_name='Purchase Invoice')
    credit_debit = pd.read_excel(xl, sheet_name='Purchase Credit Debit Note') if 'Purchase Credit Debit Note' in xl.sheet_names else pd.DataFrame()
    
    # Standardize invoices
    inv_rename = {
        'Invoice Number *': 'DOCUMENT NUMBER',
        'Supplier GSTIN': 'SUPPLIER GSTIN',
        'Item Taxable Value *': 'TAXABLE VALUE',
        'IGST Amount': 'IGST',
        'CGST Amount': 'CGST',
        'SGST Amount': 'SGST',
        'Invoice Date *': 'DOCUMENT DATE',
        'Supplier Name': 'SUPPLIER NAME',
        'Books Month': 'MONTH',
        'Total Transaction Value *': 'TOTAL_VALUE'
    }
    invoices = invoices.rename(columns={k: v for k, v in inv_rename.items() if k in invoices.columns})
    invoices['DOC_TYPE'] = 'INVOICE'
    
    # Standardize credit/debit notes
    cdn_rename = {
        'Credit/ Debit Note Number *': 'DOCUMENT NUMBER',
        'Supplier GSTIN': 'SUPPLIER GSTIN',
        'Item Taxable Value *': 'TAXABLE VALUE',
        'IGST Amount': 'IGST',
        'CGST Amount': 'CGST',
        'SGST Amount': 'SGST',
        'Credit/ Debit Note Date *': 'DOCUMENT DATE',
        'Supplier Name': 'SUPPLIER NAME',
        'Books Month': 'MONTH',
        'Total Transaction Value *': 'TOTAL_VALUE',
        'Credit(C)/ Debit(D) Note Type *': 'NOTE_TYPE'
    }
    if not credit_debit.empty:
        credit_debit = credit_debit.rename(columns={k: v for k, v in cdn_rename.items() if k in credit_debit.columns})
        if 'NOTE_TYPE' in credit_debit.columns:
            credit_debit['DOC_TYPE'] = credit_debit['NOTE_TYPE'].apply(lambda x: 'CREDIT NOTE' if x == 'C' else 'DEBIT NOTE')
        else:
            credit_debit['DOC_TYPE'] = 'CREDIT NOTE'
        credit_debit['TAXABLE VALUE'] = credit_debit['TAXABLE VALUE'].astype(float)
        credit_debit.loc[credit_debit['DOC_TYPE'] == 'CREDIT NOTE', 'TAXABLE VALUE'] = -abs(credit_debit['TAXABLE VALUE'])
    else:
        credit_debit = pd.DataFrame(columns=invoices.columns)
    
    pr_df = pd.concat([invoices, credit_debit], ignore_index=True, sort=False)
    for col in ['IGST', 'CGST', 'SGST', 'TAXABLE VALUE']:
        if col not in pr_df.columns:
            pr_df[col] = 0
    pr_df['TOTAL_TAX'] = pr_df['IGST'] + pr_df['CGST'] + pr_df['SGST']
    pr_df['NORM_DOC'] = pr_df['DOCUMENT NUMBER'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')
    pr_df['MATCH_KEY'] = pr_df['SUPPLIER GSTIN'].astype(str).str.upper() + '|' + pr_df['NORM_DOC'] + '|' + pr_df['DOC_TYPE']
    return pr_df

def run_reconciliation(file_2b, file_pr, tolerance):
    df_2b = load_2b_data(file_2b)
    df_pr = load_pr_data(file_pr)
    
    merged = pd.merge(df_2b, df_pr, on='MATCH_KEY', how='outer', suffixes=(' (2B)', ' (PR)'), indicator=True)
    merged['Taxable Diff'] = merged['TAXABLE VALUE (2B)'].fillna(0) - merged['TAXABLE VALUE (PR)'].fillna(0)
    merged['Tax Diff'] = merged['TOTAL_TAX (2B)'].fillna(0) - merged['TOTAL_TAX (PR)'].fillna(0)
    merged['Taxable Diff Abs'] = merged['Taxable Diff'].abs()
    merged['Tax Diff Abs'] = merged['Tax Diff'].abs()
    
    both = merged['_merge'] == 'both'
    amounts_ok = (merged['Taxable Diff Abs'] <= tolerance) & (merged['Tax Diff Abs'] <= tolerance)
    exact = both & amounts_ok
    mismatch = both & (~amounts_ok)
    missing_pr = merged['_merge'] == 'left_only'
    missing_2b = merged['_merge'] == 'right_only'
    
    merged['Match Status'] = ''
    merged.loc[exact, 'Match Status'] = 'Exact'
    merged.loc[mismatch, 'Match Status'] = 'Mismatch'
    merged.loc[missing_pr, 'Match Status'] = 'Missing in PR'
    merged.loc[missing_2b, 'Match Status'] = 'Missing in 2B'
    merged['Match Status Description'] = merged['Match Status'].map({
        'Exact': 'All parameters match within tolerance',
        'Mismatch': 'Document & GSTIN match but value/tax differs',
        'Missing in PR': 'Present only in GSTR‑2B',
        'Missing in 2B': 'Present only in Purchase Register'
    }).fillna('')
    
    detail_cols = [
        'Match Status', 'Match Status Description', 'SUPPLIER NAME (2B)',
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
    detail = merged[detail_cols].copy()
    detail.columns = [
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
    return detail, df_2b, df_pr

# ================= UPLOAD & PROCESS =================
file_2b = st.file_uploader("📄 Upload GSTR‑2B Excel (must have sheet 'Document Details (Inv CDN)')", type=['xlsx', 'xls'], key='2b')
file_pr = st.file_uploader("📘 Upload Purchase Register (must have sheets 'Purchase Invoice' and 'Purchase Credit Debit Note')", type=['xlsx', 'xls'], key='pr')

if file_2b and file_pr:
    try:
        with st.spinner("Reconciling..."):
            detail_df, raw_2b, raw_pr = run_reconciliation(file_2b.getvalue(), file_pr.getvalue(), tolerance)
            
            status_counts = detail_df['Match Status'].value_counts()
            total_2b = detail_df['Taxable Value (2B)'].sum()
            total_pr = detail_df['Taxable Value (PR)'].sum()
            exact_suggested = status_counts.get('Exact', 0)
            match_pct = (exact_suggested / max(1, len(detail_df))) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", len(detail_df))
            col2.metric("Exact Matches", exact_suggested)
            col3.metric("Missing in PR", status_counts.get('Missing in PR', 0))
            col4.metric("Missing in 2B", status_counts.get('Missing in 2B', 0))
            
            st.markdown("#### Overall Summary (Net off Credit/Debit Notes)")
            summary_df = detail_df.groupby('Match Status').agg({
                'Document Number (2B)': 'count',
                'Taxable Value (2B)': 'sum',
                'Total Tax (2B)': 'sum',
                'Taxable Value (PR)': 'sum',
                'Total Tax (PR)': 'sum'
            }).reset_index()
            st.dataframe(summary_df.style.format('{:.2f}'), use_container_width=True)
            
            st.markdown("#### Document Details")
            st.dataframe(detail_df.head(100), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
                detail_df.to_excel(writer, sheet_name='Document Details', index=False)
                raw_2b.to_excel(writer, sheet_name='GSTR-2B Raw', index=False)
                raw_pr.to_excel(writer, sheet_name='PR Raw', index=False)
            st.download_button("📎 Download Excel Report", output.getvalue(),
                               f"GST_Recon_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                               use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Make sure the uploaded files follow the exact structure of the sample files.")
else:
    st.info("👈 Upload both files to start reconciliation.")

# ================= FOOTER =================
st.markdown('<div class="footer">Developed by ABHISHEK JAKKULA | jakkulaabhishek5@gmail.com</div>', unsafe_allow_html=True)
