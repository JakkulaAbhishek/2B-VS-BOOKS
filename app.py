import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= CLEAN THEME-ADAPTIVE UI =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: transparent;
    }

    h1 {
        font-weight: 800;
        font-size: 3rem !important;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px !important;
    }

    .subtitle {
        font-size: 1.1rem;
        opacity: 0.8;
        margin-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        backdrop-filter: blur(8px);
        border-right: 1px solid rgba(0,0,0,0.08);
    }

    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 20px;
        border: 1px solid rgba(0,0,0,0.05);
    }

    @media (prefers-color-scheme: dark) {
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
        }
    }

    [data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 1.8rem;
    }

    .insight-box {
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 5px solid #2563eb;
        background: rgba(37, 99, 235, 0.08);
    }

    @media (prefers-color-scheme: dark) {
        .insight-box {
            background: rgba(37, 99, 235, 0.15);
        }
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .web-branding {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid rgba(0,0,0,0.08);
        font-size: 0.95rem;
        opacity: 0.8;
    }

    .web-branding b {
        color: #2563eb;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    tolerance = st.number_input("Mismatch Tolerance (₹)", min_value=0, value=20, step=1)
    max_rows = st.number_input("Max Rows for Excel Formulas", min_value=1000, value=30000, step=1000)
    st.markdown("---")
    business_name = st.text_input("Business Name", value="SUPRATEC")
    pan_number = st.text_input("PAN Identification", value="ADXFS5154R")

# ================= HEADER =================
st.markdown("<h1>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered reconciliation with Smart Invoice Matching & Financial Insights.</p>', unsafe_allow_html=True)

# ================= SAMPLE TEMPLATES GENERATOR =================
def generate_sample_2b():
    cols = ["SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOCUMENT TYPE"]
    sample_data = [
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0.00, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "07-2023", "INVOICE"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0.00, 0.00, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "05-2023", "INVOICE"],
        ["36AFKPD6156R1ZT", "23", -5042.36, 0.00, -453.81, -453.81, "M/S SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "02-2024", "CREDIT"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0.00, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "01-2024", "INVOICE"]
    ]
    df_sample = pd.DataFrame(sample_data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="2B_Data", index=False)
        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#1a73e8", "font_color": "white", "border": 1})
        sheet = writer.sheets["2B_Data"]
        for col_num, col_name in enumerate(cols):
            sheet.write(0, col_num, col_name, header_format)
        sheet.set_column('A:K', 22)
    return output.getvalue()

def generate_sample_books():
    cols = ["SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH", "DOCUMENT TYPE"]
    sample_data = [
        ["36CNNPD6299J1ZB", "11/2023-24", 7500.00, 0.00, 675.00, 675.00, "NESHWARI ENGINEERING AND SERVICES", "36ADXFS5154R1ZU", "24-07-2023", "07-2023", "INVOICE"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150.00, 2367.00, 0.00, 0.00, "METALLIZING EQUIPMENT COMPANY P. LTD.", "36ADXFS5154R1ZU", "26-05-2023", "05-2023", "INVOICE"],
        ["36ADUPV8726H1ZM", "ET/LSR/2324/1616", 390.00, 0.00, 35.10, 35.10, "M/S EXCELANT TECHNOLOGIES", "36ADXFS5154R1ZU", "20-01-2024", "01-2024", "INVOICE"],
        ["36AAFCS6791L1ZN", "23-24/4406", 123500.00, 0.00, 11115.00, 11115.00, "SAI DEEPA ROCK DRILLS PVT LTD", "36ADXFS5154R1ZU", "02-01-2024", "01-2024", "INVOICE"]
    ]
    df_sample = pd.DataFrame(sample_data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="Books_Data", index=False)
        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#1a73e8", "font_color": "white", "border": 1})
        sheet = writer.sheets["Books_Data"]
        for col_num, col_name in enumerate(cols):
            sheet.write(0, col_num, col_name, header_format)
        sheet.set_column('A:K', 22)
    return output.getvalue()

col1_btn, col2_btn, _ = st.columns([1, 1, 1])
with col1_btn:
    st.download_button(label="📥 Download Sample GSTR-2B", data=generate_sample_2b(), file_name="GSTR2B_Production_Sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with col2_btn:
    st.download_button(label="📘 Download Sample Purchase Register", data=generate_sample_books(), file_name="PurchaseRegister_Production_Sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.markdown("<br>", unsafe_allow_html=True)

# ================= HELPER MATCHING LOGIC =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

def clean_doc_type(val):
    val_str = str(val).upper().strip()
    if "CREDIT" in val_str or "CDN" in val_str:
        return "CREDIT"
    elif "DEBIT" in val_str:
        return "DEBIT"
    return "INVOICE"

@st.cache_data(show_spinner=False)
def process_data_files(file_2b_bytes, file_pr_bytes):
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))

    df_2b.columns = df_2b.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.replace('*', '', regex=False).str.strip().str.upper()

    # Re-align dynamic structural requirements
    for df in [df_2b, df_pr]:
        if "MY GSTIN" not in df.columns: df["MY GSTIN"] = ""
        if "DOCUMENT DATE" not in df.columns: df["DOCUMENT DATE"] = ""
        if "SUPPLIER GSTIN" not in df.columns: df["SUPPLIER GSTIN"] = "UNKNOWN"
        if "MONTH" not in df.columns: df["MONTH"] = ""
        if "DOCUMENT TYPE" not in df.columns: df["DOCUMENT TYPE"] = "INVOICE"
        
        df["SUPPLIER GSTIN"] = df["SUPPLIER GSTIN"].fillna("UNKNOWN").astype(str).str.upper().str.strip()
        df["DOCUMENT NUMBER"] = df["DOCUMENT NUMBER"].fillna("").astype(str).str.strip()

    numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

    df_2b["DOC_TYPE_CLEAN"] = df_2b["DOCUMENT TYPE"].apply(clean_doc_type)
    df_pr["DOC_TYPE_CLEAN"] = df_pr["DOCUMENT TYPE"].apply(clean_doc_type)

    df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
    df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])

    df_2b["PAN"] = df_2b["SUPPLIER GSTIN"].str[2:12].fillna("")
    df_pr["PAN"] = df_pr["SUPPLIER GSTIN"].str[2:12].fillna("")

    # Composite indexing layout matrix key
    df_2b["MATCH_KEY"] = df_2b["PAN"] + "|" + df_2b["NORM_DOC"] + "|" + df_2b["DOC_TYPE_CLEAN"]
    df_pr["MATCH_KEY"] = df_pr["PAN"] + "|" + df_pr["NORM_DOC"] + "|" + df_pr["DOC_TYPE_CLEAN"]

    dup_pr_count = df_pr.duplicated(subset=["MATCH_KEY"], keep=False).sum()
    merged = pd.merge(df_2b, df_pr, on="MATCH_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, dup_pr_count, df_2b, df_pr

# ================= UPLOAD ZONE =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Matrix Excel", type=["xlsx", "xls"], key="pro_2b")
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Ledger Excel", type=["xlsx", "xls"], key="pro_pr")

if file_2b and file_pr:
    try:
        with st.spinner("🚀 Synchronizing Datasets & Generating Excel Layout..."):
            merged, dup_pr_count, df_2b, df_pr = process_data_files(file_2b.getvalue(), file_pr.getvalue())

            # Tax Computation
            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            merged["Tax Diff Abs"] = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()

            # Conditions matching standard audit classifications
            exact_invoice = merged["DOCUMENT NUMBER (2B)"].astype(str).str.upper().str.strip() == merged["DOCUMENT NUMBER (PR)"].astype(str).str.upper().str.strip()
            exact_gstin = merged["SUPPLIER GSTIN (2B)"].astype(str).str.upper().str.strip() == merged["SUPPLIER GSTIN (PR)"].astype(str).str.upper().str.strip()
            tax_diff_within_tol = merged["Tax Diff Abs"] <= tolerance

            conditions = [
                (merged["_merge"] == "both") & exact_gstin & exact_invoice & (merged["Tax Diff Abs"] <= 1.0),
                (merged["_merge"] == "both") & tax_diff_within_tol & (~exact_invoice | ~exact_gstin),
                (merged["_merge"] == "both") & (~tax_diff_within_tol),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            statuses = ["Exact", "Suggested", "Mismatch", "Missing in PR", "Missing in 2B"]
            reasons = [
                "All parameters matching except rounding off in tax & taxable value",
                "Document date or format variant within compliance threshold",
                "Taxable value or total tax parameters outside threshold limit",
                "Present exclusively in GSTR-2B ledger",
                "Present exclusively in Purchase Register ledger"
            ]

            merged["Match Status"] = np.select(conditions, statuses, default="Mismatch")
            merged["Match Status Description"] = np.select(conditions, reasons, default="Verification Required")

            supplier_2b = merged.get("SUPPLIER NAME (2B)", pd.Series(dtype='object'))
            supplier_pr = merged.get("SUPPLIER NAME (PR)", pd.Series(dtype='object'))
            merged["Supplier Name"] = supplier_2b.combine_first(supplier_pr).fillna("UNKNOWN VENDOR")

            # Building final layout to match production architecture
            recon_df = pd.DataFrame({
                "Action Errors": "action_errors",
                "Match Status": merged["Match Status"],
                "Match Status Description": merged["Match Status Description"],
                "Supplier Name": merged["Supplier Name"],
                "Supplier GSTIN (2B)": merged["SUPPLIER GSTIN (2B)"],
                "Supplier GSTIN (PR)": merged["SUPPLIER GSTIN (PR)"],
                "My GSTIN (2B)": merged["MY GSTIN (2B)"],
                "My GSTIN (PR)": merged["MY GSTIN (PR)"],
                "Document Number (2B)": merged["DOCUMENT NUMBER (2B)"],
                "Document Number (PR)": merged["DOCUMENT NUMBER (PR)"],
                "Document Date (2B)": merged["DOCUMENT DATE (2B)"],
                "Document Date (PR)": merged["DOCUMENT DATE (PR)"],
                "Total Document Value (2B)": merged["TAXABLE VALUE (2B)"] + merged["Total Tax (2B)"],
                "Total Document Value (PR)": merged["TAXABLE VALUE (PR)"] + merged["Total Tax (PR)"],
                "Taxable Value (2B)": merged["TAXABLE VALUE (2B)"],
                "Taxable Value (PR)": merged["TAXABLE VALUE (PR)"],
                "Tax Difference(2B-PR)": merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"],
                "Total Tax (2B)": merged["Total Tax (2B)"],
                "Total Tax (PR)": merged["Total Tax (PR)"],
                "IGST (2B)": merged["IGST (2B)"],
                "IGST (PR)": merged["IGST (PR)"],
                "CGST (2B)": merged["CGST (2B)"],
                "CGST (PR)": merged["CGST (PR)"],
                "SGST (2B)": merged["SGST (2B)"],
                "SGST (PR)": merged["SGST (PR)"],
                "Cess (2B)": merged.get("CESS (2B)", 0),
                "Cess (PR)": merged.get("CESS (PR)", 0),
                "Document Type(2B)": merged["DOC_TYPE_CLEAN (2B)"],
                "Document Type(PR)": merged["DOC_TYPE_CLEAN (PR)"],
                "Section Name 2B": "B2B",
                "Section Name (Pr)": "B2B",
                "Return Period (2B)": merged["MONTH (2B)"].fillna(""),
                "Return Period (PR)": merged["MONTH (PR)"].fillna(""),
                "Financial Year": "2023-24"
            })

            counts = recon_df["Match Status"].value_counts()

            # ========== DASHBOARD METRICS ==========
            st.markdown("### 📊 Live Matrix Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Processed Documents", len(recon_df))
            m2.metric("Reconciled Matches", counts.get("Exact", 0) + counts.get("Suggested", 0))
            m3.metric("Missing in Purchase Register", counts.get("Missing in PR", 0))
            m4.metric("Missing in GSTR-2B", counts.get("Missing in 2B", 0))

            # ========== SMART FINANCIAL INSIGHTS ==========
            st.markdown("### 🧠 Automated Financial Insights")
            missed_itc = recon_df[recon_df["Match Status"] == "Missing in PR"]["Total Tax (2B)"].sum()
            risk_itc = recon_df[recon_df["Match Status"] == "Missing in 2B"]["Total Tax (PR)"].sum()
            
            insights = []
            if dup_pr_count > 0:
                insights.append(f"⚠️ **Duplicate Alert:** Found **{dup_pr_count}** multi-entry rows within book listings.")
            if missed_itc > 0:
                insights.append(f"💡 **Unclaimed Advantage:** Unclaimed ITC detected in GSTR-2B totaling **₹{missed_itc:,.2f}**.")
            if risk_itc > 0:
                insights.append(f"🚨 **Compliance Risk:** Book ledger claims **₹{risk_itc:,.2f}** missing from GSTR-2B records.")
            if not insights:
                insights.append("✅ **Optimal Reconciliation Status:** System data corresponds completely with GSTR-2B logs.")
            
            for insight in insights:
                st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

            # ========== VISUAL INSIGHT CHARTS ==========
            chart_data = counts.reset_index()
            chart_data.columns = ["Match Status", "Count"]
            fig = px.bar(chart_data, x="Count", y="Match Status", color="Match Status", orientation='h', title="Status Distribution Analysis")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            # ========== FILTER & PREVIEW GRID ==========
            st.markdown("#### 🔎 Filter & Preview Matrix Data")
            selected_status = st.multiselect("Active Classifications Filter:", options=statuses, default=statuses)
            filtered_df = recon_df[recon_df["Match Status"].isin(selected_status)]
            st.dataframe(filtered_df.head(200), use_container_width=True)

            # ========== PRODUCTION ENGINE EXCEL REPORT EXPORT ==========
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                
                # Format Styles
                fmt_title = workbook.add_format({"bold": True, "font_size": 16, "bg_color": "#0f172a", "font_color": "#38bdf8", "align": "center", "valign": "vcenter"})
                fmt_subtitle = workbook.add_format({"italic": True, "font_size": 10, "bg_color": "#0f172a", "font_color": "#94a3b8", "align": "center"})
                fmt_th = workbook.add_format({"bold": True, "bg_color": "#1e3a8a", "font_color": "white", "border": 1, "align": "center", "valign": "vcenter", "text_wrap": True})
                fmt_subtotal = workbook.add_format({"bold": True, "bg_color": "#f1f5f9", "border": 1, "num_format": "#,##0.00"})
                fmt_cell = workbook.add_format({"border": 1})
                fmt_num = workbook.add_format({"border": 1, "num_format": "#,##0.00"})

                # --- SHEET A: OVERALL SUMMARY ---
                summary_sheet = workbook.add_worksheet("Overall Summary")
                summary_sheet.hide_gridlines(2)
                
                # Replicating header blocks from the source architecture
                summary_sheet.merge_range("A1:M1", "PAN GSTR - 2B Vs PR", workbook.add_format({"bold": True, "font_size": 12}))
                summary_sheet.write("A2", "Business name"); summary_sheet.write("B2", business_name)
                summary_sheet.write("A3", "PAN"); summary_sheet.write("B3", pan_number)
                summary_sheet.write("A4", "Return Period(2B)"); summary_sheet.write("B4", "042023 - 032024")
                summary_sheet.write("A5", "Return Period(PR)"); summary_sheet.write("B5", "042023 - 032024")
                summary_sheet.write("A6", "Fiscal Year (2B)"); summary_sheet.write("B6", "2023-24")
                summary_sheet.write("A7", "Fiscal Year (PR)"); summary_sheet.write("B7", "2023-24")
                
                summary_sheet.write("A9", "* Values are calculated on basis of net off Credit and Debit notes", workbook.add_format({"italic": True, "font_color": "red"}))
                summary_sheet.write("A11", "A : Overall Summary", workbook.add_format({"bold": True, "font_size": 11}))
                
                # Matrix Grid Headers
                summary_sheet.merge_range("A12:A13", "MATCH STATUS", fmt_th)
                summary_sheet.merge_range("B12:D12", "Difference(2B-PR)", fmt_th)
                summary_sheet.merge_range("E12:G12", "As Per GSTR 2B", fmt_th)
                summary_sheet.merge_range("H12:J12", "As Per Purchase Books", fmt_th)
                summary_sheet.merge_range("K12:L12", "Match %", fmt_th)
                summary_sheet.write("M12", "Action %", fmt_th)
                
                sub_headers = [
                    "Number of Documents", "Taxable Value", "Total Tax",
                    "Number of Documents", "Taxable Value", "Total Tax",
                    "Number of Documents", "Taxable Value", "Total Tax",
                    "Document Count", "Tax Amount", ""
                ]
                summary_sheet.write_row("B13", sub_headers, fmt_th)
                summary_sheet.set_column('A:A', 25)
                summary_sheet.set_column('B:M', 16)

                # Dynamic reference formulas tracking Sheet B
                for idx, status in enumerate(statuses):
                    row_num = 14 + idx
                    summary_sheet.write(row_num, 0, status, fmt_cell)
                    
                    # Difference formulas
                    summary_sheet.write_formula(row_num, 1, f'=E{row_num+1}-H{row_num+1}', fmt_num)
                    summary_sheet.write_formula(row_num, 2, f'=F{row_num+1}-I{row_num+1}', fmt_num)
                    summary_sheet.write_formula(row_num, 3, f'=G{row_num+1}-J{row_num+1}', fmt_num)
                    
                    # COUNTIF and SUMIF metrics linking to "Document Details (Inv CDN)" sheet
                    summary_sheet.write_formula(row_num, 4, f'=COUNTIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}")', fmt_cell)
                    summary_sheet.write_formula(row_num, 5, f'=SUMIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}", \'Document Details (Inv CDN)\'!$O$3:$O${max_rows})', fmt_num)
                    summary_sheet.write_formula(row_num, 6, f'=SUMIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}", \'Document Details (Inv CDN)\'!$R$3:$R${max_rows})', fmt_num)
                    
                    summary_sheet.write_formula(row_num, 7, f'=COUNTIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}")', fmt_cell)
                    summary_sheet.write_formula(row_num, 8, f'=SUMIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}", \'Document Details (Inv CDN)\'!$P$3:$P${max_rows})', fmt_num)
                    summary_sheet.write_formula(row_num, 9, f'=SUMIF(\'Document Details (Inv CDN)\'!$B$3:$B${max_rows}, "{status}", \'Document Details (Inv CDN)\'!$S$3:$S${max_rows})', fmt_num)
                    
                    # Match metrics
                    summary_sheet.write_formula(row_num, 10, f'=IF(E{row_num+1}>0,(H{row_num+1}/E{row_num+1})*100,0)', fmt_num)
                    summary_sheet.write_formula(row_num, 11, f'=IF(F{row_num+1}>0,(I{row_num+1}/F{row_num+1})*100,0)', fmt_num)
                    summary_sheet.write_formula(row_num, 12, "100", fmt_num)

                # --- SHEET B: DOCUMENT DETAILS (INV CDN) ---
                details_sheet = workbook.add_worksheet("Document Details (Inv CDN)")
                details_sheet.merge_range("A1:AH1", "GST RECON PRO - LINE ITEM TRANSCRIPT", fmt_title)
                details_sheet.merge_range("A2:AH2", "Developed by ABHISHEK JAKKULA | Source: System Matrix Engine", fmt_subtitle)
                
                recon_df.to_excel(writer, sheet_name="Document Details (Inv CDN)", startrow=2, index=False, header=False)
                
                # Write tabular columns and configure the aggregation summary row
                for col_num, col_name in enumerate(recon_df.columns):
                    details_sheet.write(1, col_num, col_name, fmt_th)
                    if pd.api.types.is_numeric_dtype(recon_df[col_name]):
                        col_letter = chr(65 + col_num) if col_num < 26 else chr(65 + col_num // 26 - 1) + chr(65 + col_num % 26)
                        details_sheet.write_formula(0, col_num, f"=SUBTOTAL(9,{col_letter}4:{col_letter}{max_rows})", fmt_subtotal)
                
                details_sheet.set_column('A:C', 22)
                details_sheet.set_column('D:D', 32)
                details_sheet.set_column('E:AH', 16)
                details_sheet.autofilter(1, 0, max_rows, len(recon_df.columns) - 1)

            st.success("✅ Ultimate Audit Report Package generated successfully!")

            col_btn, _ = st.columns([1, 2])
            with col_btn:
                st.download_button(
                    "⚡ Download Final Excel Report Package",
                    output.getvalue(),
                    f"GSTR_2B_Vs_PR_Final_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"⚠️ Production Engine Execution Fault: {e}")

# ================= PROMINENT WEB BRANDING =================
st.markdown("""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
