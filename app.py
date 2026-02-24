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

    /* Let Streamlit theme control background */
    .stApp {
        background-color: transparent;
    }

    /* Header Gradient Text (works in light & dark) */
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

    /* Sidebar */
    [data-testid="stSidebar"] {
        backdrop-filter: blur(8px);
        border-right: 1px solid rgba(0,0,0,0.08);
    }

    /* Buttons */
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

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 20px;
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* Dark mode metric fix */
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

    /* Insight Box */
    .insight-box {
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 5px solid #2563eb;
        background: rgba(37, 99, 235, 0.08);
    }

    /* Dark mode insight fix */
    @media (prefers-color-scheme: dark) {
        .insight-box {
            background: rgba(37, 99, 235, 0.15);
        }
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Footer */
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

# ================= SAMPLE TEMPLATES GENERATOR =================
def generate_sample_templates():
    cols = ["SUPPLIER GSTIN*", "DOCUMENT NUMBER*", "TAXABLE VALUE*", "IGST*", "CGST*", "SGST*", "SUPPLIER NAME", "MY GSTIN", "DOCUMENT DATE"]
    sample_data = [
        ["36CNNPD6299J1ZB", "11/2023-24", 7500, 0, 675, 675, "NESHWARI ENGINEERING", "36ADXFS5154R1ZU", "24-07-2023"],
        ["08AAACM8473A1ZL", "MEC-439-2023", 13150, 2367, 0, 0, "METALLIZING EQUIPMENT", "36ADXFS5154R1ZU", "26-05-2023"]
    ]
    df_sample = pd.DataFrame(sample_data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_sample.to_excel(writer, sheet_name="2B_Template", index=False)
        df_sample.to_excel(writer, sheet_name="Books_Template", index=False)
        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#1a73e8", "font_color": "white", "border": 1})
        for sheet_name in ["2B_Template", "Books_Template"]:
            sheet = writer.sheets[sheet_name]
            for col_num, col_name in enumerate(cols):
                sheet.write(0, col_num, col_name, header_format)
            sheet.set_column('A:I', 22)
    return output.getvalue()

col_btn, empty_space = st.columns([1, 2])
with col_btn:
    st.download_button(
        label="📥 Download Sample Excel Templates",
        data=generate_sample_templates(),
        file_name="GST_Recon_Upload_Templates.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Mandatory fields are marked with an asterisk (*)"
    )
st.markdown("<br>", unsafe_allow_html=True)

# ================= SMART FUZZY NORMALIZATION =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

# ================= CACHED DATA PROCESSING (Lightning Fast) =================
@st.cache_data(show_spinner=False)
def process_data_files(file_2b_bytes, file_pr_bytes):
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))

    df_2b.columns = df_2b.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.replace('*', '', regex=False).str.strip().str.upper()

    for df in [df_2b, df_pr]:
        if "MY GSTIN" not in df.columns: df["MY GSTIN"] = ""
        if "DOCUMENT DATE" not in df.columns: df["DOCUMENT DATE"] = ""
        if "SUPPLIER GSTIN" not in df.columns: df["SUPPLIER GSTIN"] = ""
        df["SUPPLIER GSTIN"] = df["SUPPLIER GSTIN"].fillna("UNKNOWN").astype(str).str.upper().str.strip()

    numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

    df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
    df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])

    df_2b["PAN"] = df_2b["SUPPLIER GSTIN"].str[2:12]
    df_pr["PAN"] = df_pr["SUPPLIER GSTIN"].str[2:12]

    df_2b["PAN_KEY"] = df_2b["PAN"] + "|" + df_2b["NORM_DOC"]
    df_pr["PAN_KEY"] = df_pr["PAN"] + "|" + df_pr["NORM_DOC"]

    dup_pr_count = df_pr.duplicated(subset=["PAN_KEY"], keep=False).sum()

    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, dup_pr_count, df_2b, df_pr

# ================= FILE UPLOAD =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx", "xls"])
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx", "xls"])

# ================= MAIN LOGIC =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Smart Engine & Generating Insights..."):
            merged, dup_pr_count, df_2b, df_pr = process_data_files(file_2b.getvalue(), file_pr.getvalue())

            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            
            merged["Tax Difference(2B-PR)"] = merged["Total Tax (2B)"] - merged["Total Tax (PR)"]
            diff = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()

            exact_invoice = merged["DOCUMENT NUMBER (2B)"].astype(str).str.upper() == merged["DOCUMENT NUMBER (PR)"].astype(str).str.upper()
            exact_gstin = merged["SUPPLIER GSTIN (2B)"].astype(str).str.upper() == merged["SUPPLIER GSTIN (PR)"].astype(str).str.upper()

            conditions = [
                (merged["_merge"] == "both") & exact_gstin & exact_invoice & (diff == 0),
                (merged["_merge"] == "both") & exact_gstin & ~exact_invoice & (diff == 0),
                (merged["_merge"] == "both") & ~exact_gstin,
                (merged["_merge"] == "both") & exact_gstin & (diff <= tolerance),
                (merged["_merge"] == "both") & exact_gstin & (diff > tolerance),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            
            statuses = ["Exact", "Fuzzy Match", "Cross-State (PAN Match)", "Exact (Tolerance)", "Value Mismatch", "Missing in PR", "Missing in 2B"]
            merged["Match Status"] = np.select(conditions, statuses, default="Unknown")

            reasons = [
                "Exact match on all fields", 
                "Matched ignoring special chars", 
                "Matched on PAN, but State GSTIN differs",
                f"Matched within ₹{tolerance} tolerance", 
                "Taxable value mismatch", 
                "Present only in GSTR-2B", 
                "Present only in Books"
            ]
            merged["Match Reason"] = np.select(conditions, reasons, default="Unknown")

            supplier_2b = merged.get("SUPPLIER NAME (2B)", pd.Series(dtype='object'))
            supplier_pr = merged.get("SUPPLIER NAME (PR)", pd.Series(dtype='object'))
            merged["Supplier Name"] = supplier_2b.combine_first(supplier_pr).fillna("Unknown")

            recon_df = merged[[
                "Match Status", "Match Reason", "Supplier Name", 
                "SUPPLIER GSTIN (2B)", "SUPPLIER GSTIN (PR)", 
                "MY GSTIN (2B)", "MY GSTIN (PR)",
                "DOCUMENT NUMBER (2B)", "DOCUMENT NUMBER (PR)", 
                "DOCUMENT DATE (2B)", "DOCUMENT DATE (PR)",
                "TAXABLE VALUE (2B)", "TAXABLE VALUE (PR)", 
                "Tax Difference(2B-PR)",
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
                "Taxable Value (2B)", "Taxable Value (PR)", 
                "Tax Difference(2B-PR)",
                "Total Tax (2B)", "Total Tax (PR)",
                "IGST (2B)", "IGST (PR)",
                "CGST (2B)", "CGST (PR)",
                "SGST (2B)", "SGST (PR)"
            ]

            # Calculate Top 10 including IGST and CGST
            top10_2b = recon_df.groupby("Supplier Name")[["Taxable Value (2B)", "Total Tax (2B)", "IGST (2B)", "CGST (2B)"]].sum().nlargest(10, "Taxable Value (2B)").reset_index()
            top10_pr = recon_df.groupby("Supplier Name")[["Taxable Value (PR)", "Total Tax (PR)", "IGST (PR)", "CGST (PR)"]].sum().nlargest(10, "Taxable Value (PR)").reset_index()
            counts = recon_df["Match Status"].value_counts()
            
            # --- 1. WEB DASHBOARD: METRICS ---
            st.markdown("### 📊 Live Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(recon_df))
            m2.metric("Total Matches", counts.get("Exact", 0) + counts.get("Fuzzy Match", 0) + counts.get("Exact (Tolerance)", 0) + counts.get("Cross-State (PAN Match)", 0))
            m3.metric("Missing in Books", counts.get("Missing in PR", 0))
            m4.metric("Missing in 2B", counts.get("Missing in 2B", 0))

            # --- 2. 🤖 SMART AI INSIGHTS ---
            st.markdown("### 🧠 Automated Financial Insights")
            
            total_records = len(recon_df)
            miss_pr_pct = (counts.get("Missing in PR", 0) / total_records) * 100 if total_records else 0
            
            missed_itc = recon_df[recon_df["Match Status"] == "Missing in PR"]["Total Tax (2B)"].sum()
            risk_itc = recon_df[recon_df["Match Status"] == "Missing in 2B"]["Total Tax (PR)"].sum()

            insights = []
            if dup_pr_count > 0:
                insights.append(f"⚠️ **ERP Data Warning:** We found **{dup_pr_count}** duplicate invoice entries in your Purchase Register.")
            if counts.get("Cross-State (PAN Match)", 0) > 0:
                insights.append(f"🔄 **Cross-State Errors:** **{counts.get('Cross-State (PAN Match)', 0)}** invoices matched on PAN, but the State GSTIN differs.")
            if miss_pr_pct > 10:
                insights.append(f"🚨 **High Action Required:** **{miss_pr_pct:.1f}%** of records are missing in your Purchase Register. You have **₹{missed_itc:,.2f}** in unclaimed ITC.")
            elif missed_itc > 0:
                insights.append(f"💡 **Cash Flow Opportunity:** You have **₹{missed_itc:,.2f}** of unclaimed ITC sitting in GSTR-2B.")
            if risk_itc > 0:
                insights.append(f"⚠️ **Compliance Risk:** **₹{risk_itc:,.2f}** of tax is claimed in your books but missing in GSTR-2B.")

            if not insights:
                insights.append("✅ **Excellent Health:** Your books are perfectly reconciled with GSTR-2B.")

            for insight in insights:
                st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

            # --- 3. PLOTLY WEB CHARTS ---
            st.markdown("<br>", unsafe_allow_html=True)
            
            chart_data = counts.reset_index()
            chart_data.columns = ["Match Status", "Count"]
            color_map = {
                "Exact": "#10b981", "Fuzzy Match": "#38bdf8", "Cross-State (PAN Match)": "#06b6d4",
                "Exact (Tolerance)": "#f59e0b", "Value Mismatch": "#ef4444", 
                "Missing in PR": "#f97316", "Missing in 2B": "#8b5cf6"
            }
            fig = px.bar(chart_data, x="Count", y="Match Status", color="Match Status", color_discrete_map=color_map, text="Count", orientation='h', title="Status Distribution")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc", family="Poppins"), showlegend=False, yaxis=dict(title="", categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

            # Top 10 Grouped Bar Charts showing Taxable, IGST, and CGST
            st.markdown("### 🏆 Top 10 Parties (Taxable, IGST & CGST Impact)")
            fig_2b = px.bar(top10_2b, x="Supplier Name", y=["Taxable Value (2B)", "IGST (2B)", "CGST (2B)"], barmode="group", title="Top 10 Suppliers in 2B")
            fig_2b.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc", family="Poppins"), legend_title_text="Value Type")
            st.plotly_chart(fig_2b, use_container_width=True)

            fig_pr = px.bar(top10_pr, x="Supplier Name", y=["Taxable Value (PR)", "IGST (PR)", "CGST (PR)"], barmode="group", title="Top 10 Suppliers in Books")
            fig_pr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc", family="Poppins"), legend_title_text="Value Type")
            st.plotly_chart(fig_pr, use_container_width=True)

            # --- 4. DATA PREVIEW ---
            st.markdown("#### 🔎 Filter & Preview Data")
            selected_status = st.multiselect("Filter by Match Status:", options=statuses, default=statuses)
            filtered_df = recon_df[recon_df["Match Status"].isin(selected_status)]
            st.dataframe(filtered_df.head(100), use_container_width=True)

            # --- 5. EXCEL EXPORT ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                
                # Brand and Header Formats
                brand_format = workbook.add_format({"bold": True, "font_size": 18, "bg_color": "#0f172a", "font_color": "#38bdf8", "align": "center", "valign": "vcenter"})
                dev_format = workbook.add_format({"italic": True, "font_size": 10, "bg_color": "#0f172a", "font_color": "#94a3b8", "align": "center"})
                
                # Dark Blue background with White Characters for ALL headers
                fmt_dark_blue_white = workbook.add_format({
                    "bold": True, "bg_color": "#0052cc", "font_color": "white", 
                    "border": 1, "text_wrap": True, "align": "center", "valign": "vcenter"
                })
                fmt_subtotal = workbook.add_format({"bold": True, "bg_color": "#f2f2f2", "border": 1, "num_format": "#,##0.00"})

                # A. Dashboard
                dash = workbook.add_worksheet("Dashboard")
                dash.hide_gridlines(2)
                
                dash.merge_range("A1:U2", "GST RECON PRO - EXECUTIVE SUMMARY", brand_format)
                dash.merge_range("A3:U3", "Developed by ABHISHEK JAKKULA | jakkulaabhishek5@gmail.com", dev_format)

                # Summary Table with Both 2B and Books Impact side-by-side
                dash.write_row("B5", [
                    "Match Status", "Record Count", 
                    "Taxable Impact (2B)", "IGST Impact (2B)", "CGST Impact (2B)",
                    "Taxable Impact (PR)", "IGST Impact (PR)", "CGST Impact (PR)"
                ], fmt_dark_blue_white)
                dash.set_column('B:B', 25)
                dash.set_column('C:I', 18)

                for i, status in enumerate(statuses):
                    row = 5 + i
                    dash.write(row, 1, status)
                    # Record count
                    dash.write_formula(row, 2, f'=COUNTIF(Reconciliation!$A$3:$A${max_rows}, "{status}")')
                    # 2B Impact (Cols L, Q, S in Recon)
                    dash.write_formula(row, 3, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$L$3:$L${max_rows})')
                    dash.write_formula(row, 4, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$Q$3:$Q${max_rows})')
                    dash.write_formula(row, 5, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$S$3:$S${max_rows})')
                    # Books Impact (Cols M, R, T in Recon)
                    dash.write_formula(row, 6, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$M$3:$M${max_rows})')
                    dash.write_formula(row, 7, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$R$3:$R${max_rows})')
                    dash.write_formula(row, 8, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$T$3:$T${max_rows})')

                # Top 10 Tables shifted to K and Q to prevent overlapping
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

                # Status Distribution Pie Chart
                pie_chart = workbook.add_chart({'type': 'doughnut'})
                pie_chart.add_series({
                    'name': 'Status Distribution',
                    'categories': f'=Dashboard!$B$6:$B$12',
                    'values': f'=Dashboard!$C$6:$C$12',
                    'data_labels': {'percentage': True}
                })
                dash.insert_chart('B14', pie_chart)

                # Column Chart for Top 10 2B (Includes Taxable, IGST, CGST)
                bar_2b = workbook.add_chart({'type': 'column'})
                bar_2b.add_series({'name': 'Taxable', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$L$7:$L${6 + len(top10_2b)}'})
                bar_2b.add_series({'name': 'IGST', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$N$7:$N${6 + len(top10_2b)}'})
                bar_2b.add_series({'name': 'CGST', 'categories': f'=Dashboard!$K$7:$K${6 + len(top10_2b)}', 'values': f'=Dashboard!$O$7:$O${6 + len(top10_2b)}'})
                bar_2b.set_title({'name': 'Top 10 Suppliers (2B)'})
                dash.insert_chart('K18', bar_2b, {'x_scale': 1.2, 'y_scale': 1.2})

                # Column Chart for Top 10 Books (Includes Taxable, IGST, CGST)
                bar_pr = workbook.add_chart({'type': 'column'})
                bar_pr.add_series({'name': 'Taxable', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$R$7:$R${6 + len(top10_pr)}'})
                bar_pr.add_series({'name': 'IGST', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$T$7:$T${6 + len(top10_pr)}'})
                bar_pr.add_series({'name': 'CGST', 'categories': f'=Dashboard!$Q$7:$Q${6 + len(top10_pr)}', 'values': f'=Dashboard!$U$7:$U${6 + len(top10_pr)}'})
                bar_pr.set_title({'name': 'Top 10 Suppliers (Books)'})
                dash.insert_chart('Q18', bar_pr, {'x_scale': 1.2, 'y_scale': 1.2})

                # B. Reconciliation Sheet
                sheet_recon = workbook.add_worksheet("Reconciliation")
                recon_df.to_excel(writer, sheet_name="Reconciliation", startrow=2, index=False, header=False)
                
                for col_num, col_name in enumerate(recon_df.columns):
                    # Write Header using universal Dark Blue / White characters
                    sheet_recon.write(1, col_num, col_name, fmt_dark_blue_white)
                    
                    if pd.api.types.is_numeric_dtype(recon_df[col_name]):
                        col_letter = chr(65 + col_num) 
                        formula = f"=SUBTOTAL(9,{col_letter}3:{col_letter}{max_rows})"
                        sheet_recon.write_formula(0, col_num, formula, fmt_subtotal)

                sheet_recon.set_column('A:B', 22)
                sheet_recon.set_column('C:C', 35)
                sheet_recon.set_column('D:K', 18)
                sheet_recon.set_column('L:V', 14)
                sheet_recon.autofilter(1, 0, max_rows, len(recon_df.columns) - 1)

                # C. Raw Data Sheets
                df_2b.drop(columns=["NORM_DOC", "PAN", "PAN_KEY"], errors="ignore").to_excel(writer, sheet_name="2B Raw", index=False)
                df_pr.drop(columns=["NORM_DOC", "PAN", "PAN_KEY"], errors="ignore").to_excel(writer, sheet_name="Books Raw", index=False)

            st.success("✅ Ultimate Reconciliation Dashboard generated perfectly!")

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
