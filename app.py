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
    max_rows = st.number_input("Max Rows for Excel Formulas", min_value=1000, value=15000, step=1000)

# ================= HEADER =================
st.markdown("<h1>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered reconciliation with Smart Invoice Matching & Financial Insights.</p>', unsafe_allow_html=True)

# ================= SAMPLE TEMPLATES GENERATOR (Separate Files) =================
def generate_sample_2b():
    """Generate sample GSTR-2B Excel file with positive invoice and negative credit note"""
    cols = ["SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH"]
    sample_data = [
        # Positive invoice
        ["36CNNPD6299J1ZB", "11/2023-24", 7500, 0, 675, 675, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "24-07-2023", "2023-07"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150, 2367, 0, 0, "METALLIZING EQUIPMENT", "36ADXFS5154R1ZU", "26-05-2023", "2023-05"],
        # Credit note (negative values)
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02"],
        ["36AADCR6281N1ZT", "67186859-1D", 8579.4, 0, 772.11, 772.11, "CARE HEALTH INSURANCE", "36ADXFS5154R1ZU", "01-01-2024", "2024-01"]
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
        sheet.set_column('A:J', 22)
    return output.getvalue()

def generate_sample_books():
    """Generate sample Purchase Register Excel file with matching and mismatching entries"""
    cols = ["SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST", "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE", "MONTH"]
    sample_data = [
        # Exact match with 2B invoice
        ["36CNNPD6299J1ZB", "11/2023-24", 7500, 0, 675, 675, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "24-07-2023", "2023-07"],
        # Slight mismatch in taxable value (within tolerance)
        ["08AAACM8473A1ZL", "MEC-439-2023", 13000, 2340, 0, 0, "METALLIZING EQUIPMENT CO", "36ADXFS5154R1ZU", "26-05-2023", "2023-05"],
        # Matching credit note
        ["36AFKPD6156R1ZT", "23", -5042.36, 0, -453.81, -453.81, "SRI SATYA TECHNOLOGIES", "36ADXFS5154R1ZU", "22-02-2024", "2024-02"],
        # Extra record missing in 2B
        ["27ABCDE1234F1ZR", "INV-202", 12000, 1080, 0, 0, "EXTRA IN BOOKS", "36ADXFS5154R1ZU", "10-07-2023", "2023-07"],
        # Suggested match: document date differs but within FY
        ["36DGLPP5363P1ZG", "ST/23-24/39", 23650, 0, 2128.5, 2128.5, "S SQUARE INDUSTRIES", "36ADXFS5154R1ZU", "01-06-2023", "2023-06"]
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
        sheet.set_column('A:J', 22)
    return output.getvalue()

# Provide separate download buttons for the two templates
col1_btn, col2_btn, _ = st.columns([1, 1, 1])
with col1_btn:
    st.download_button(
        label="📥 Download Sample GSTR-2B",
        data=generate_sample_2b(),
        file_name="GSTR2B_Sample.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Contains MONTH column (YYYY-MM) for period analysis"
    )
with col2_btn:
    st.download_button(
        label="📘 Download Sample Purchase Register",
        data=generate_sample_books(),
        file_name="PurchaseRegister_Sample.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Contains MONTH column (YYYY-MM) for period analysis"
    )
st.markdown("<br>", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def normalize_invoice(series):
    """Remove special characters and leading zeros for fuzzy matching"""
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

def get_doc_type(taxable):
    """Determine document type from taxable value sign"""
    if taxable < 0:
        return "CREDIT NOTE"
    else:
        return "INVOICE"

@st.cache_data(show_spinner=False)
def process_data_files(file_2b_bytes, file_pr_bytes, tolerance):
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))

    # Clean column names: remove '*', strip, uppercase
    df_2b.columns = df_2b.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.replace('*', '', regex=False).str.strip().str.upper()

    # Ensure mandatory columns exist
    for df in [df_2b, df_pr]:
        if "MY GSTIN" not in df.columns:
            df["MY GSTIN"] = ""
        if "DOCUMENT DATE" not in df.columns:
            df["DOCUMENT DATE"] = ""
        if "SUPPLIER GSTIN" not in df.columns:
            df["SUPPLIER GSTIN"] = ""
        if "MONTH" not in df.columns:
            df["MONTH"] = ""
        df["SUPPLIER GSTIN"] = df["SUPPLIER GSTIN"].fillna("UNKNOWN").astype(str).str.upper().str.strip()

    # Numeric conversion
    numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

    # Derive document type from sign of taxable value
    df_2b["DOC_TYPE"] = df_2b["TAXABLE VALUE"].apply(get_doc_type)
    df_pr["DOC_TYPE"] = df_pr["TAXABLE VALUE"].apply(get_doc_type)

    # Normalize document numbers
    df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
    df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])

    # Extract PAN from GSTIN (characters 2 to 12)
    df_2b["PAN"] = df_2b["SUPPLIER GSTIN"].str[2:12]
    df_pr["PAN"] = df_pr["SUPPLIER GSTIN"].str[2:12]

    # Matching key = PAN + normalized doc number + document type
    df_2b["PAN_KEY"] = df_2b["PAN"] + "|" + df_2b["NORM_DOC"] + "|" + df_2b["DOC_TYPE"]
    df_pr["PAN_KEY"] = df_pr["PAN"] + "|" + df_pr["NORM_DOC"] + "|" + df_pr["DOC_TYPE"]

    dup_pr_count = df_pr.duplicated(subset=["PAN_KEY"], keep=False).sum()

    # Outer merge on PAN_KEY
    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, dup_pr_count, df_2b, df_pr

# ================= FILE UPLOAD =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx", "xls"], key="2b")
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx", "xls"], key="pr")

# ================= MAIN LOGIC =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Smart Engine & Generating Insights..."):
            merged, dup_pr_count, df_2b, df_pr = process_data_files(file_2b.getvalue(), file_pr.getvalue(), tolerance)

            # Calculate totals
            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            merged["Tax Diff Abs"] = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()

            # Helper: same financial year? (Apr to Mar)
            def same_fy(date_str1, date_str2):
                try:
                    d1 = pd.to_datetime(date_str1)
                    d2 = pd.to_datetime(date_str2)
                    if pd.isna(d1) or pd.isna(d2):
                        return False
                    fy1 = d1.year if d1.month >= 4 else d1.year - 1
                    fy2 = d2.year if d2.month >= 4 else d2.year - 1
                    return fy1 == fy2
                except:
                    return False

            # Prepare conditions for match status
            exact_invoice = merged["DOCUMENT NUMBER (2B)"].astype(str).str.upper() == merged["DOCUMENT NUMBER (PR)"].astype(str).str.upper()
            exact_gstin = merged["SUPPLIER GSTIN (2B)"].astype(str).str.upper() == merged["SUPPLIER GSTIN (PR)"].astype(str).str.upper()
            tax_diff_within_tol = merged["Tax Diff Abs"] <= tolerance
            tax_diff_zero = merged["Tax Diff Abs"] == 0
            # Suggested: same PAN, doc number matches (normalized), values within tolerance, but document dates differ within FY
            norm_doc_equal = merged["NORM_DOC (2B)"] == merged["NORM_DOC (PR)"]
            same_pan = merged["PAN (2B)"] == merged["PAN (PR)"]
            dates_differ = merged["DOCUMENT DATE (2B)"] != merged["DOCUMENT DATE (PR)"]
            within_fy = merged.apply(lambda r: same_fy(r["DOCUMENT DATE (2B)"], r["DOCUMENT DATE (PR)"]), axis=1)

            conditions = [
                # Exact match
                (merged["_merge"] == "both") & exact_gstin & exact_invoice & tax_diff_zero,
                # Suggested match
                (merged["_merge"] == "both") & same_pan & norm_doc_equal & tax_diff_within_tol & dates_differ & within_fy,
                # Value mismatch (doc & GSTIN match but taxable diff > tolerance)
                (merged["_merge"] == "both") & exact_gstin & exact_invoice & (~tax_diff_within_tol),
                # Cross-state PAN match
                (merged["_merge"] == "both") & same_pan & (~exact_gstin) & tax_diff_within_tol,
                # Missing in PR
                (merged["_merge"] == "left_only"),
                # Missing in 2B
                (merged["_merge"] == "right_only")
            ]
            statuses = ["Exact", "Suggested", "Value Mismatch", "Cross-State (PAN Match)", "Missing in PR", "Missing in 2B"]
            reasons = [
                "Exact match on all fields",
                "Document date differs within FY, values within tolerance",
                "Document number & GSTIN match, but taxable value mismatch",
                "Matched on PAN, but State GSTIN differs",
                "Present only in GSTR-2B",
                "Present only in Books"
            ]
            merged["Match Status"] = np.select(conditions, statuses, default="Other")
            merged["Match Reason"] = np.select(conditions, reasons, default="Unknown")

            # Combine supplier name
            supplier_2b = merged.get("SUPPLIER NAME (2B)", pd.Series(dtype='object'))
            supplier_pr = merged.get("SUPPLIER NAME (PR)", pd.Series(dtype='object'))
            merged["Supplier Name"] = supplier_2b.combine_first(supplier_pr).fillna("Unknown")

            # Build reconciliation DataFrame
            recon_df = merged[[
                "Match Status", "Match Reason", "Supplier Name",
                "SUPPLIER GSTIN (2B)", "SUPPLIER GSTIN (PR)",
                "MY GSTIN (2B)", "MY GSTIN (PR)",
                "DOCUMENT NUMBER (2B)", "DOCUMENT NUMBER (PR)",
                "DOCUMENT DATE (2B)", "DOCUMENT DATE (PR)",
                "MONTH (2B)", "MONTH (PR)",
                "DOC_TYPE (2B)", "DOC_TYPE (PR)",
                "TAXABLE VALUE (2B)", "TAXABLE VALUE (PR)",
                "Tax Diff Abs",
                "Total Tax (2B)", "Total Tax (PR)",
                "IGST (2B)", "IGST (PR)",
                "CGST (2B)", "CGST (PR)",
                "SGST (2B)", "SGST (PR)"
            ]].copy()

            recon_df.columns = [
                "Match Status", "Match Reason", "Supplier Name",
                "Supplier GSTIN (2B)", "Supplier GSTIN (PR)",
                "My GSTIN (2B)", "My GSTIN (PR)",
                "Document Number (2B)", "Document Number (PR)",
                "Document Date (2B)", "Document Date (PR)",
                "Month (2B)", "Month (PR)",
                "Doc Type (2B)", "Doc Type (PR)",
                "Taxable Value (2B)", "Taxable Value (PR)",
                "Tax Difference Abs",
                "Total Tax (2B)", "Total Tax (PR)",
                "IGST (2B)", "IGST (PR)",
                "CGST (2B)", "CGST (PR)",
                "SGST (2B)", "SGST (PR)"
            ]

            # Fill missing month
            recon_df["Month (2B)"] = recon_df["Month (2B)"].fillna("Unknown")
            recon_df["Month (PR)"] = recon_df["Month (PR)"].fillna("Unknown")

            # Top 10 suppliers (by taxable value)
            top10_2b = recon_df.groupby("Supplier Name")[["Taxable Value (2B)", "Total Tax (2B)", "IGST (2B)", "CGST (2B)"]].sum().nlargest(10, "Taxable Value (2B)").reset_index()
            top10_pr = recon_df.groupby("Supplier Name")[["Taxable Value (PR)", "Total Tax (PR)", "IGST (PR)", "CGST (PR)"]].sum().nlargest(10, "Taxable Value (PR)").reset_index()
            counts = recon_df["Match Status"].value_counts()

            # ========== DASHBOARD METRICS ==========
            st.markdown("### 📊 Live Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(recon_df))
            total_matches = counts.get("Exact", 0) + counts.get("Suggested", 0) + counts.get("Cross-State (PAN Match)", 0)
            m2.metric("Total Matches", total_matches)
            m3.metric("Missing in Books", counts.get("Missing in PR", 0))
            m4.metric("Missing in 2B", counts.get("Missing in 2B", 0))

            # ========== SMART AI INSIGHTS ==========
            st.markdown("### 🧠 Automated Financial Insights")
            total_records = len(recon_df)
            miss_pr_pct = (counts.get("Missing in PR", 0) / total_records) * 100 if total_records else 0
            missed_itc = recon_df[recon_df["Match Status"] == "Missing in PR"]["Total Tax (2B)"].sum()
            risk_itc = recon_df[recon_df["Match Status"] == "Missing in 2B"]["Total Tax (PR)"].sum()
            suggested_count = counts.get("Suggested", 0)

            insights = []
            if dup_pr_count > 0:
                insights.append(f"⚠️ **ERP Data Warning:** Found **{dup_pr_count}** duplicate invoice entries in Purchase Register.")
            if counts.get("Cross-State (PAN Match)", 0) > 0:
                insights.append(f"🔄 **Cross-State Errors:** **{counts.get('Cross-State (PAN Match)', 0)}** invoices matched on PAN but State GSTIN differs.")
            if miss_pr_pct > 10:
                insights.append(f"🚨 **High Action Required:** **{miss_pr_pct:.1f}%** of records missing in Purchase Register. Unclaimed ITC: **₹{missed_itc:,.2f}**.")
            elif missed_itc > 0:
                insights.append(f"💡 **Cash Flow Opportunity:** Unclaimed ITC of **₹{missed_itc:,.2f}** in GSTR-2B.")
            if risk_itc > 0:
                insights.append(f"⚠️ **Compliance Risk:** **₹{risk_itc:,.2f}** tax claimed in books but missing in GSTR-2B.")
            if suggested_count > 0:
                insights.append(f"🕒 **Suggested Matches:** **{suggested_count}** records have date mismatches but are within financial year – verify if acceptable.")
            if not insights:
                insights.append("✅ **Excellent Health:** Books perfectly reconciled with GSTR-2B.")
            for insight in insights:
                st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

            # ========== MONTH-WISE CHARTS ==========
            if (recon_df["Month (2B)"] != "Unknown").any() or (recon_df["Month (PR)"] != "Unknown").any():
                st.markdown("### 📅 Month-wise Analysis")
                month_summary = recon_df.groupby("Month (2B)").agg({
                    "Taxable Value (2B)": "sum",
                    "Total Tax (2B)": "sum"
                }).reset_index().rename(columns={"Month (2B)": "Month", "Taxable Value (2B)": "Taxable Value (2B)", "Total Tax (2B)": "Total Tax (2B)"})
                month_summary2 = recon_df.groupby("Month (PR)").agg({
                    "Taxable Value (PR)": "sum",
                    "Total Tax (PR)": "sum"
                }).reset_index().rename(columns={"Month (PR)": "Month", "Taxable Value (PR)": "Taxable Value (PR)", "Total Tax (PR)": "Total Tax (PR)"})
                month_merged = pd.merge(month_summary, month_summary2, on="Month", how="outer").fillna(0)
                if not month_merged.empty:
                    fig_month = px.bar(month_merged, x="Month", y=["Taxable Value (2B)", "Taxable Value (PR)"],
                                       barmode="group", title="Taxable Value by Month")
                    st.plotly_chart(fig_month, use_container_width=True)

            # ========== STATUS DISTRIBUTION ==========
            chart_data = counts.reset_index()
            chart_data.columns = ["Match Status", "Count"]
            color_map = {
                "Exact": "#10b981", "Suggested": "#06b6d4", "Cross-State (PAN Match)": "#38bdf8",
                "Value Mismatch": "#ef4444", "Missing in PR": "#f97316", "Missing in 2B": "#8b5cf6", "Other": "#64748b"
            }
            fig = px.bar(chart_data, x="Count", y="Match Status", color="Match Status",
                         color_discrete_map=color_map, text="Count", orientation='h',
                         title="Status Distribution")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#f8fafc", family="Inter"), showlegend=False,
                              yaxis=dict(title="", categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

            # ========== TOP 10 SUPPLIERS ==========
            st.markdown("### 🏆 Top 10 Parties (Taxable, IGST & CGST Impact)")
            fig_2b = px.bar(top10_2b, x="Supplier Name", y=["Taxable Value (2B)", "IGST (2B)", "CGST (2B)"],
                            barmode="group", title="Top 10 Suppliers in 2B")
            fig_2b.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 font=dict(color="#f8fafc", family="Inter"))
            st.plotly_chart(fig_2b, use_container_width=True)

            fig_pr = px.bar(top10_pr, x="Supplier Name", y=["Taxable Value (PR)", "IGST (PR)", "CGST (PR)"],
                            barmode="group", title="Top 10 Suppliers in Books")
            fig_pr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 font=dict(color="#f8fafc", family="Inter"))
            st.plotly_chart(fig_pr, use_container_width=True)

            # ========== FILTER & PREVIEW ==========
            st.markdown("#### 🔎 Filter & Preview Data")
            selected_status = st.multiselect("Filter by Match Status:", options=statuses + ["Other"], default=statuses)
            filtered_df = recon_df[recon_df["Match Status"].isin(selected_status)]
            st.dataframe(filtered_df.head(100), use_container_width=True)

            # ========== EXCEL REPORT EXPORT ==========
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                fmt_dark_blue_white = workbook.add_format({
                    "bold": True, "bg_color": "#0052cc", "font_color": "white",
                    "border": 1, "text_wrap": True, "align": "center", "valign": "vcenter"
                })
                fmt_subtotal = workbook.add_format({"bold": True, "bg_color": "#f2f2f2", "border": 1, "num_format": "#,##0.00"})

                # --- Dashboard Sheet ---
                dash = workbook.add_worksheet("Dashboard")
                dash.hide_gridlines(2)
                dash.merge_range("A1:U2", "GST RECON PRO - EXECUTIVE SUMMARY", workbook.add_format({"bold": True, "font_size": 18, "bg_color": "#0f172a", "font_color": "#38bdf8", "align": "center"}))
                dash.merge_range("A3:U3", "Developed by ABHISHEK JAKKULA | jakkulaabhishek5@gmail.com", workbook.add_format({"italic": True, "font_size": 10, "bg_color": "#0f172a", "font_color": "#94a3b8", "align": "center"}))

                # Summary table
                dash.write_row("B5", [
                    "Match Status", "Record Count",
                    "Taxable Impact (2B)", "IGST Impact (2B)", "CGST Impact (2B)",
                    "Taxable Impact (PR)", "IGST Impact (PR)", "CGST Impact (PR)"
                ], fmt_dark_blue_white)
                dash.set_column('B:B', 25)
                dash.set_column('C:I', 18)

                for i, status in enumerate(statuses + ["Other"]):
                    row = 5 + i
                    dash.write(row, 1, status)
                    dash.write_formula(row, 2, f'=COUNTIF(Reconciliation!$A$3:$A${max_rows}, "{status}")')
                    dash.write_formula(row, 3, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$P$3:$P${max_rows})')   # Taxable Value (2B)
                    dash.write_formula(row, 4, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$U$3:$U${max_rows})')   # IGST (2B)
                    dash.write_formula(row, 5, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$W$3:$W${max_rows})')   # CGST (2B)
                    dash.write_formula(row, 6, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$Q$3:$Q${max_rows})')   # Taxable Value (PR)
                    dash.write_formula(row, 7, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$V$3:$V${max_rows})')   # IGST (PR)
                    dash.write_formula(row, 8, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$X$3:$X${max_rows})')   # CGST (PR)

                # Top 10 tables
                dash.write("K5", "Top 10 Suppliers (2B)", fmt_dark_blue_white)
                dash.write_row("K6", ["Supplier Name", "Taxable Value (2B)", "Total Tax (2B)", "IGST (2B)", "CGST (2B)"], fmt_dark_blue_white)
                for r_idx, row in top10_2b.iterrows():
                    dash.write_row(r_idx + 6, 10, [row["Supplier Name"], row["Taxable Value (2B)"], row["Total Tax (2B)"], row["IGST (2B)"], row["CGST (2B)"]])
                dash.set_column('K:K', 25)
                dash.set_column('L:O', 15)

                dash.write("Q5", "Top 10 Suppliers (Books)", fmt_dark_blue_white)
                dash.write_row("Q6", ["Supplier Name", "Taxable Value (PR)", "Total Tax (PR)", "IGST (PR)", "CGST (PR)"], fmt_dark_blue_white)
                for r_idx, row in top10_pr.iterrows():
                    dash.write_row(r_idx + 6, 16, [row["Supplier Name"], row["Taxable Value (PR)"], row["Total Tax (PR)"], row["IGST (PR)"], row["CGST (PR)"]])
                dash.set_column('Q:Q', 25)
                dash.set_column('R:U', 15)

                # Charts
                pie_chart = workbook.add_chart({'type': 'doughnut'})
                pie_chart.add_series({'name': 'Status Distribution', 'categories': '=Dashboard!$B$6:$B$12', 'values': '=Dashboard!$C$6:$C$12', 'data_labels': {'percentage': True}})
                dash.insert_chart('B14', pie_chart)

                bar_2b = workbook.add_chart({'type': 'column'})
                bar_2b.add_series({'name': 'Taxable', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$L$7:$L${6 + len(top10_2b)}'})
                bar_2b.add_series({'name': 'IGST', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$N$7:$N${6 + len(top10_2b)}'})
                bar_2b.add_series({'name': 'CGST', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$O$7:$O${6 + len(top10_2b)}'})
                bar_2b.set_title({'name': 'Top 10 Suppliers (2B)'})
                dash.insert_chart('K18', bar_2b, {'x_scale': 1.2, 'y_scale': 1.2})

                bar_pr = workbook.add_chart({'type': 'column'})
                bar_pr.add_series({'name': 'Taxable', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$R$7:$R${6 + len(top10_pr)}'})
                bar_pr.add_series({'name': 'IGST', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$T$7:$T${6 + len(top10_pr)}'})
                bar_pr.add_series({'name': 'CGST', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$U$7:$U${6 + len(top10_pr)}'})
                bar_pr.set_title({'name': 'Top 10 Suppliers (Books)'})
                dash.insert_chart('Q18', bar_pr, {'x_scale': 1.2, 'y_scale': 1.2})

                # --- Reconciliation Sheet ---
                sheet_recon = workbook.add_worksheet("Reconciliation")
                recon_df.to_excel(writer, sheet_name="Reconciliation", startrow=2, index=False, header=False)
                for col_num, col_name in enumerate(recon_df.columns):
                    sheet_recon.write(1, col_num, col_name, fmt_dark_blue_white)
                    if pd.api.types.is_numeric_dtype(recon_df[col_name]):
                        col_letter = chr(65 + col_num) if col_num < 26 else chr(65 + col_num // 26 - 1) + chr(65 + col_num % 26)
                        sheet_recon.write_formula(0, col_num, f"=SUBTOTAL(9,{col_letter}3:{col_letter}{max_rows})", fmt_subtotal)
                sheet_recon.set_column('A:B', 22)
                sheet_recon.set_column('C:C', 35)
                sheet_recon.set_column('D:M', 18)
                sheet_recon.set_column('N:Y', 14)
                sheet_recon.autofilter(1, 0, max_rows, len(recon_df.columns) - 1)

                # --- Raw Data Sheets ---
                df_2b.drop(columns=["NORM_DOC", "PAN", "PAN_KEY", "DOC_TYPE"], errors="ignore").to_excel(writer, sheet_name="2B Raw", index=False)
                df_pr.drop(columns=["NORM_DOC", "PAN", "PAN_KEY", "DOC_TYPE"], errors="ignore").to_excel(writer, sheet_name="Books Raw", index=False)

            st.success("✅ Ultimate Reconciliation Dashboard generated successfully!")

            col_btn, empty2 = st.columns([1, 2])
            with col_btn:
                st.download_button(
                    "⚡ Download Final Excel Report",
                    output.getvalue(),
                    f"GST_Recon_Ultimate_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"⚠️ Engine Error: {e}")

# ================= PROMINENT WEB BRANDING =================
st.markdown("""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
