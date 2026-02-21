import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= ULTRA STYLISH CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background: #0f172a; color: #f8fafc; }
    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3rem !important; margin-bottom: 0px !important;
    }
    .subtitle { color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem; }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white;
        border: none; border-radius: 8px; padding: 10px 24px; font-weight: 600;
        transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.5); }
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] { color: #38bdf8; font-weight: 800; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .insight-box {
        background: rgba(30, 41, 59, 0.6); padding: 18px; 
        border-left: 5px solid #38bdf8; border-radius: 8px; 
        margin-bottom: 12px; font-size: 1.05rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .web-branding {
        text-align: center; margin-top: 50px; padding: 20px;
        border-top: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 1rem;
    }
    .web-branding b { color: #38bdf8; letter-spacing: 1px; }
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

# ================= SMART FUZZY NORMALIZATION =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

# ================= FILE UPLOAD =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx", "xls"])
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx", "xls"])

# ================= PROCESS =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Smart Engine & Generating Insights..."):
            df_2b = pd.read_excel(file_2b)
            df_pr = pd.read_excel(file_pr)

            df_2b.columns = df_2b.columns.str.strip().str.upper()
            df_pr.columns = df_pr.columns.str.strip().str.upper()

            # Ensure extra columns exist gracefully
            for df in [df_2b, df_pr]:
                if "MY GSTIN" not in df.columns: df["MY GSTIN"] = ""
                if "DOCUMENT DATE" not in df.columns: df["DOCUMENT DATE"] = ""

            numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
            for col in numeric_cols:
                df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
                df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

            # FUZZY LOGIC KEY
            df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
            df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])

            df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["NORM_DOC"]
            df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["NORM_DOC"]

            merged = pd.merge(df_2b, df_pr, on="KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)

            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            
            merged["Tax Difference(2B-PR)"] = merged["Total Tax (2B)"] - merged["Total Tax (PR)"]
            diff = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()

            exact_invoice = merged["DOCUMENT NUMBER (2B)"].astype(str).str.upper() == merged["DOCUMENT NUMBER (PR)"].astype(str).str.upper()

            # Assign Status
            conditions = [
                (merged["_merge"] == "both") & (diff == 0) & exact_invoice,
                (merged["_merge"] == "both") & (diff == 0) & ~exact_invoice,
                (merged["_merge"] == "both") & (diff <= tolerance),
                (merged["_merge"] == "both") & (diff > tolerance),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            
            statuses = ["Exact", "Fuzzy Match", "Exact (Tolerance)", "Value Mismatch", "Missing in PR", "Missing in 2B"]
            merged["Match Status"] = np.select(conditions, statuses, default="Unknown")

            # Assign Detailed Matching Reasons
            reasons = [
                "Exact match on all fields", 
                "Matched ignoring special chars", 
                f"Matched within ₹{tolerance} tolerance", 
                "Taxable value mismatch", 
                "Present only in GSTR-2B", 
                "Present only in Books"
            ]
            merged["Match Reason"] = np.select(conditions, reasons, default="Unknown")

            supplier_2b = merged.get("SUPPLIER NAME (2B)", pd.Series(dtype='object'))
            supplier_pr = merged.get("SUPPLIER NAME (PR)", pd.Series(dtype='object'))
            merged["Supplier Name"] = supplier_2b.combine_first(supplier_pr).fillna("Unknown")

            # --- PRECISE COLUMN ORDERING ---
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

            counts = recon_df["Match Status"].value_counts()
            
            # --- 1. WEB DASHBOARD: METRICS ---
            st.markdown("### 📊 Live Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(recon_df))
            m2.metric("Total Matches", counts.get("Exact", 0) + counts.get("Fuzzy Match", 0) + counts.get("Exact (Tolerance)", 0))
            m3.metric("Missing in Books", counts.get("Missing in PR", 0))
            m4.metric("Missing in 2B", counts.get("Missing in 2B", 0))

            # --- 2. 🤖 SMART AI INSIGHTS ---
            st.markdown("### 🧠 Automated Financial Insights")
            
            total_records = len(recon_df)
            miss_pr_pct = (counts.get("Missing in PR", 0) / total_records) * 100 if total_records else 0
            
            missed_itc = recon_df[recon_df["Match Status"] == "Missing in PR"]["Total Tax (2B)"].sum()
            risk_itc = recon_df[recon_df["Match Status"] == "Missing in 2B"]["Total Tax (PR)"].sum()

            insights = []
            if miss_pr_pct > 10:
                insights.append(f"🚨 **High Action Required:** **{miss_pr_pct:.1f}%** of records are missing in your Purchase Register. You have **₹{missed_itc:,.2f}** in unclaimed ITC.")
            elif missed_itc > 0:
                insights.append(f"💡 **Cash Flow Opportunity:** You have **₹{missed_itc:,.2f}** of ITC sitting in GSTR-2B that isn't recorded in your books. Claim this to optimize cash flow.")
                
            if risk_itc > 0:
                insights.append(f"⚠️ **Compliance Risk:** **₹{risk_itc:,.2f}** of tax is claimed in your books but missing in GSTR-2B. Follow up with these suppliers to avoid notices.")
                
            bad_statuses = ["Missing in PR", "Missing in 2B", "Value Mismatch"]
            problem_records = recon_df[recon_df["Match Status"].isin(bad_statuses)].copy()
            if not problem_records.empty:
                problem_records["Tax Variance"] = (problem_records["Total Tax (2B)"] - problem_records["Total Tax (PR)"]).abs()
                top_supplier = problem_records.groupby("Supplier Name")["Tax Variance"].sum().sort_values(ascending=False).head(1)
                if not top_supplier.empty and top_supplier.iloc[0] > 0:
                    insights.append(f"🏢 **Top Defaulter:** **{top_supplier.index[0]}** is causing the highest variance (₹{top_supplier.iloc[0]:,.2f} mismatch). Focus here first.")

            if not insights:
                insights.append("✅ **Excellent Health:** Your books are exceptionally well-reconciled with GSTR-2B. No major financial risks detected.")

            for insight in insights:
                st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

            # --- 3. PLOTLY WEB CHART ---
            st.markdown("<br>", unsafe_allow_html=True)
            chart_data = counts.reset_index()
            chart_data.columns = ["Match Status", "Count"]
            
            color_map = {
                "Exact": "#10b981", "Fuzzy Match": "#38bdf8", "Exact (Tolerance)": "#f59e0b",
                "Value Mismatch": "#ef4444", "Missing in PR": "#f97316", "Missing in 2B": "#8b5cf6"
            }

            fig = px.bar(
                chart_data, x="Count", y="Match Status", color="Match Status",
                color_discrete_map=color_map, text="Count", orientation='h', title="Status Distribution"
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Poppins"), showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title=""),
                yaxis=dict(title="", categoryorder="total ascending")
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            # --- 4. DATA PREVIEW ---
            st.markdown("#### 🔎 Filter & Preview Data")
            selected_status = st.multiselect("Filter by Match Status:", options=statuses, default=statuses)
            filtered_df = recon_df[recon_df["Match Status"].isin(selected_status)]
            st.dataframe(filtered_df.head(100), use_container_width=True)

            # --- 5. EXCEL EXPORT ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                
                # Setup Formats
                brand_format = workbook.add_format({"bold": True, "font_size": 18, "bg_color": "#0f172a", "font_color": "#38bdf8", "align": "center", "valign": "vcenter"})
                dev_format = workbook.add_format({"italic": True, "font_size": 10, "bg_color": "#0f172a", "font_color": "#94a3b8", "align": "center"})
                
                # Image-matched Color formats
                fmt_blue = workbook.add_format({"bold": True, "bg_color": "#cce5ff", "border": 1, "text_wrap": True, "align": "center"})
                fmt_grey = workbook.add_format({"bold": True, "bg_color": "#d9d9d9", "border": 1, "text_wrap": True, "align": "center"})
                fmt_red = workbook.add_format({"bold": True, "bg_color": "#e6b8b7", "border": 1, "text_wrap": True, "align": "center"})
                fmt_orange = workbook.add_format({"bold": True, "bg_color": "#fce4d6", "border": 1, "text_wrap": True, "align": "center"})
                fmt_tax_diff = workbook.add_format({"bold": True, "bg_color": "#a4c2f4", "border": 1, "text_wrap": True, "align": "center"})
                fmt_subtotal = workbook.add_format({"bold": True, "bg_color": "#f2f2f2", "border": 1, "num_format": "#,##0.00"})
                
                def get_col_format(col_name):
                    if "Status" in col_name or "Reason" in col_name: return fmt_blue
                    if "Supplier Name" in col_name: return fmt_grey
                    if "(2B)" in col_name: return fmt_red
                    if "(PR)" in col_name: return fmt_orange
                    if "Difference" in col_name: return fmt_tax_diff
                    return fmt_grey

                # A. Create Dashboard FIRST
                dash = workbook.add_worksheet("Dashboard")
                dash.hide_gridlines(2)
                
                dash.merge_range("A1:I2", "GST RECON PRO - EXECUTIVE SUMMARY", brand_format)
                dash.merge_range("A3:I3", "Developed by ABHISHEK JAKKULA | jakkulaabhishek5@gmail.com", dev_format)

                dash.write_row("B5", ["Match Status", "Record Count", "Taxable Impact (2B)"], workbook.add_format({"bold": True, "bg_color": "#1e293b", "font_color": "white", "border": 1}))
                dash.set_column('B:B', 25)
                dash.set_column('C:D', 18)

                for i, status in enumerate(statuses):
                    row = 5 + i
                    dash.write(row, 1, status)
                    dash.write_formula(row, 2, f'=COUNTIF(Reconciliation!$A$3:$A${max_rows}, "{status}")')
                    dash.write_formula(row, 3, f'=SUMIF(Reconciliation!$A$3:$A${max_rows}, "{status}", Reconciliation!$L$3:$L${max_rows})')

                pie_chart = workbook.add_chart({'type': 'doughnut'})
                pie_chart.add_series({
                    'name': 'Status Distribution',
                    'categories': f'=Dashboard!$B$6:$B$11',
                    'values': f'=Dashboard!$C$6:$C$11',
                    'data_labels': {'percentage': True}
                })
                dash.insert_chart('F5', pie_chart)

                bar_chart = workbook.add_chart({'type': 'column'})
                bar_chart.add_series({
                    'name': 'Taxable Value Impact',
                    'categories': f'=Dashboard!$B$6:$B$11',
                    'values': f'=Dashboard!$D$6:$D$11',
                    'data_labels': {'value': True}
                })
                dash.insert_chart('A14', bar_chart, {'x_scale': 1.5, 'y_scale': 1.2})

                # B. Create Reconciliation Sheet (with Subtotals)
                sheet_recon = workbook.add_worksheet("Reconciliation")
                
                # Write data starting at row 2 (Excel Row 3) to leave space for Subtotals and Headers
                recon_df.to_excel(writer, sheet_name="Reconciliation", startrow=2, index=False, header=False)
                
                # Write Subtotals (Row 0 / Excel Row 1) and Headers (Row 1 / Excel Row 2)
                for col_num, col_name in enumerate(recon_df.columns):
                    # Write Header
                    sheet_recon.write(1, col_num, col_name, get_col_format(col_name))
                    
                    # Write Subtotals for numeric columns
                    if pd.api.types.is_numeric_dtype(recon_df[col_name]):
                        col_letter = chr(65 + col_num)  # Works dynamically up to column Z
                        formula = f"=SUBTOTAL(9,{col_letter}3:{col_letter}{max_rows})"
                        sheet_recon.write_formula(0, col_num, formula, fmt_subtotal)

                # Set Column Widths
                sheet_recon.set_column('A:B', 22)
                sheet_recon.set_column('C:C', 35)
                sheet_recon.set_column('D:K', 18)
                sheet_recon.set_column('L:V', 14)

                # Add auto-filter for easy sorting
                sheet_recon.autofilter(1, 0, max_rows, len(recon_df.columns) - 1)

                # C. Create Raw Data Sheets
                df_2b.drop(columns=["NORM_DOC", "KEY"], errors="ignore").to_excel(writer, sheet_name="2B Raw", index=False)
                df_pr.drop(columns=["NORM_DOC", "KEY"], errors="ignore").to_excel(writer, sheet_name="Books Raw", index=False)

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
