import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= ULTRA STYLISH CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }

    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: 0px !important;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.5);
    }

    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] {
        color: #38bdf8;
        font-weight: 800;
    }

    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 16px;
        padding: 1.5em;
        border: 1px dashed #64748b;
        transition: border 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #38bdf8;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    tolerance = st.number_input("Mismatch Tolerance (₹)", min_value=0, value=20, step=1)
    max_rows = st.number_input("Max Rows for Excel Formulas", min_value=1000, value=15000, step=1000)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#94a3b8; font-size: 0.9rem;">
        Developed by <br>
        <b style="color:#f8fafc;">ABHISHEK JAKKULA</b><br>
        jakkulaabhishek5@gmail.com
    </div>
    """, unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<h1>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered reconciliation with Smart Invoice Matching.</p>', unsafe_allow_html=True)

# ================= SAMPLE TEMPLATE =================
def generate_sample_template():
    return pd.DataFrame({
        "SUPPLIER NAME": ["TESLA CORP", "STARK INDUSTRIES", "WAYNE ENTERPRISES"],
        "SUPPLIER GSTIN": ["36CNNPD6299J1ZB", "08AAACM8473A1ZL", "27AADCB2230M1Z2"],
        "MY GSTIN": ["36ADXFS5154R1ZU", "36ADXFS5154R1ZU", "36ADXFS5154R1ZU"],
        "DOCUMENT NUMBER": ["INV-001/23", "SI/2023/045", "WE-999"],
        "DOCUMENT DATE": ["24-07-2023", "26-05-2023", "10-10-2023"],
        "TAXABLE VALUE": [7500, 13150, 50000],
        "IGST": [0, 2367, 9000],
        "CGST": [675, 0, 0],
        "SGST": [675, 0, 0]
    })

template_buffer = io.BytesIO()
generate_sample_template().to_excel(template_buffer, index=False)

col_dl, empty = st.columns([1, 3])
with col_dl:
    st.download_button(
        "📥 Get Upload Template",
        template_buffer.getvalue(),
        "GST_Template.xlsx",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ================= FILE UPLOAD =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx", "xls"])
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx", "xls"])

# ================= SMART FUZZY NORMALIZATION =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

# ================= PROCESS =================
if file_2b and file_pr:
    try:
        with st.spinner("🚀 Running Smart Reconciliation Engine..."):
            df_2b = pd.read_excel(file_2b)
            df_pr = pd.read_excel(file_pr)

            df_2b.columns = df_2b.columns.str.strip().str.upper()
            df_pr.columns = df_pr.columns.str.strip().str.upper()

            required_cols = ["SUPPLIER GSTIN", "DOCUMENT NUMBER", "TAXABLE VALUE", "IGST", "CGST", "SGST"]
            for df, name in [(df_2b, "GSTR-2B"), (df_pr, "Purchase Register")]:
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    st.error(f"Missing columns in {name}: {', '.join(missing)}")
                    st.stop()

            numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
            for col in numeric_cols:
                df_2b[col] = pd.to_numeric(df_2b[col], errors="coerce").fillna(0)
                df_pr[col] = pd.to_numeric(df_pr[col], errors="coerce").fillna(0)

            df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
            df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])

            df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["NORM_DOC"]
            df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["NORM_DOC"]

            merged = pd.merge(df_2b, df_pr, on="KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)

            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            diff = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()

            exact_invoice = merged["DOCUMENT NUMBER (2B)"].astype(str).str.upper() == merged["DOCUMENT NUMBER (PR)"].astype(str).str.upper()

            conditions = [
                (merged["_merge"] == "both") & (diff == 0) & exact_invoice,
                (merged["_merge"] == "both") & (diff == 0) & ~exact_invoice,
                (merged["_merge"] == "both") & (diff <= tolerance),
                (merged["_merge"] == "both") & (diff > tolerance),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            
            statuses = [
                "Exact Match", 
                "Fuzzy Match (Invoice Format)", 
                "Exact (Tolerance)", 
                "Value Mismatch", 
                "Missing in Books", 
                "Missing in 2B"
            ]
            
            reasons = [
                "Perfect match on all fields", 
                "Matched ignoring special chars/zeros in Invoice No.", 
                "Values within tolerance", 
                "Taxable value mismatch", 
                "Present only in GSTR-2B", 
                "Present only in Purchase Register"
            ]

            merged["Match Status"] = np.select(conditions, statuses, default="Unknown")
            merged["Match Reason"] = np.select(conditions, reasons, default="Unknown")

            supplier_2b = merged.get("SUPPLIER NAME (2B)", pd.Series(dtype='object'))
            supplier_pr = merged.get("SUPPLIER NAME (PR)", pd.Series(dtype='object'))
            merged["Supplier Name"] = supplier_2b.combine_first(supplier_pr).fillna("Unknown")

            recon_df = merged[[
                "Match Status", "Match Reason", "Supplier Name", 
                "SUPPLIER GSTIN (2B)", "SUPPLIER GSTIN (PR)", 
                "DOCUMENT NUMBER (2B)", "DOCUMENT NUMBER (PR)", 
                "TAXABLE VALUE (2B)", "TAXABLE VALUE (PR)", 
                "Total Tax (2B)", "Total Tax (PR)"
            ]].copy()

            recon_df.columns = [
                "Match Status", "Match Reason", "Supplier Name", 
                "Supplier GSTIN (2B)", "Supplier GSTIN (Books)", 
                "Invoice No (2B)", "Invoice No (Books)", 
                "Taxable (2B)", "Taxable (Books)", 
                "Total Tax (2B)", "Total Tax (Books)"
            ]

            # --- DASHBOARD & METRICS ---
            st.markdown("### 📊 Live Summary")
            counts = recon_df["Match Status"].value_counts()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(recon_df))
            m2.metric("Perfect & Fuzzy Matches", counts.get("Exact Match", 0) + counts.get("Fuzzy Match (Invoice Format)", 0))
            m3.metric("Missing in Books", counts.get("Missing in Books", 0))
            m4.metric("Missing in 2B", counts.get("Missing in 2B", 0))
            
            # --- PLOTLY CHART ---
            st.markdown("<br>", unsafe_allow_html=True)
            chart_data = counts.reset_index()
            chart_data.columns = ["Match Status", "Count"]
            
            # Define colors for the chart
            color_map = {
                "Exact Match": "#10b981",              # Green
                "Fuzzy Match (Invoice Format)": "#38bdf8", # Blue
                "Exact (Tolerance)": "#f59e0b",        # Yellow/Amber
                "Value Mismatch": "#ef4444",           # Red
                "Missing in Books": "#f97316",         # Orange
                "Missing in 2B": "#8b5cf6"             # Purple
            }

            fig = px.bar(
                chart_data, 
                x="Count", 
                y="Match Status", 
                color="Match Status",
                color_discrete_map=color_map,
                text="Count",
                orientation='h',
                title="Status Distribution"
            )

            # Style the chart to fit the dark theme
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Poppins"),
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title=""),
                yaxis=dict(title="", categoryorder="total ascending")
            )
            fig.update_traces(textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("👁️ Preview Recon Engine Output"):
                st.dataframe(recon_df.head(100), use_container_width=True)

            # --- EXCEL EXPORT ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                
                header_format = workbook.add_format({"bold": True, "bg_color": "#1e293b", "font_color": "white", "border": 1})

                recon_df.to_excel(writer, sheet_name="Reconciliation", startrow=2, index=False, header=False)
                sheet = writer.sheets["Reconciliation"]

                for col in recon_df.select_dtypes(include=np.number).columns:
                    idx = recon_df.columns.get_loc(col)
                    letter = chr(65 + idx)
                    sheet.write_formula(0, idx, f"=SUBTOTAL(9,{letter}3:{letter}{max_rows})")

                for col_num, col_name in enumerate(recon_df.columns):
                    sheet.write(1, col_num, col_name, header_format)

                sheet.set_column('A:B', 25)
                sheet.set_column('C:E', 20)
                sheet.set_column('F:K', 15)

                df_2b.drop(columns=["NORM_DOC", "KEY"], errors="ignore").to_excel(writer, sheet_name="2B Raw", index=False)
                df_pr.drop(columns=["NORM_DOC", "KEY"], errors="ignore").to_excel(writer, sheet_name="Books Raw", index=False)

            st.success("✅ Smart Reconciliation complete!")

            col_btn, empty2 = st.columns([1, 2])
            with col_btn:
                st.download_button(
                    "⚡ Download Final Excel Report",
                    output.getvalue(),
                    f"GST_Recon_Pro_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"⚠️ Engine Error: {e}")
