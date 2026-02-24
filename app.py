import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= ENHANCED HIGH-CONTRAST UI CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
    }
    .stApp { 
        background-color: #0f172a; 
        color: #ffffff; 
    }

    /* Headings */
    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3.5rem !important; 
        margin-bottom: 5px !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .subtitle { 
        color: #cbd5e1; 
        font-size: 1.2rem; 
        margin-bottom: 2rem; 
        font-weight: 400;
    }

    /* Sidebar Contrast */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 600;
    }

    /* Metrics Cards */
    [data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* Insight Boxes - Enhanced Contrast */
    .insight-box {
        background: #1e293b;
        padding: 20px; 
        border-left: 6px solid #38bdf8; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        color: #f8fafc;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #7c3aed); 
        color: #ffffff !important;
        border: none; border-radius: 10px; padding: 12px 24px; 
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.4);
        color: #ffffff !important;
    }

    /* Dataframe Header Visibility */
    .stDataFrame {
        background-color: #1e293b;
        border-radius: 10px;
    }

    /* Footer Branding */
    .web-branding {
        text-align: center; margin-top: 60px; padding: 30px;
        border-top: 1px solid #334155; color: #94a3b8; font-size: 1.1rem;
    }
    .web-branding b { color: #38bdf8; letter-spacing: 1.5px; }

    /* File Uploader Text */
    .st-emotion-cache-1ae8k9h e1b2p2ww14 {
        color: white !important;
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
st.markdown('<p class="subtitle">Intelligent Reconciliation with High-Contrast Financial Visibility.</p>', unsafe_allow_html=True)

# ================= LOGIC FUNCTIONS (Unchanged from original logic) =================
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
    return output.getvalue()

def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

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
    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, df_2b, df_pr

# ================= MAIN APP FLOW =================
col_btn, empty_space = st.columns([1, 2])
with col_btn:
    st.download_button(
        label="📥 Download Templates",
        data=generate_sample_templates(),
        file_name="GST_Templates.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx", "xls"])
with col2:
    file_pr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx", "xls"])

if file_2b and file_pr:
    try:
        with st.spinner("🚀 Analyzing Data..."):
            merged, df_2b, df_pr = process_data_files(file_2b.getvalue(), file_pr.getvalue())

            # Math calculations
            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["TAXABLE VALUE (2B)"] = merged["TAXABLE VALUE (2B)"].fillna(0)
            merged["TAXABLE VALUE (PR)"] = merged["TAXABLE VALUE (PR)"].fillna(0)
            
            diff = (merged["TAXABLE VALUE (2B)"] - merged["TAXABLE VALUE (PR)"]).abs()
            
            # Simplified Logic for statuses
            conditions = [
                (merged["_merge"] == "both") & (diff == 0),
                (merged["_merge"] == "both") & (diff <= tolerance),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            statuses = ["Exact Match", "Within Tolerance", "Missing in Books", "Missing in 2B"]
            merged["Match Status"] = np.select(conditions, statuses, default="Mismatch")
            
            # Dashboard Metrics
            st.markdown("### 📊 Business Intelligence")
            counts = merged["Match Status"].value_counts()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(merged))
            m2.metric("Matches", counts.get("Exact Match", 0))
            m3.metric("Unclaimed ITC", f"₹{merged[merged['Match Status'] == 'Missing in Books']['Total Tax (2B)'].sum():,.0f}")
            m4.metric("Potential Risk", f"₹{merged[merged['Match Status'] == 'Missing in 2B']['Total Tax (PR)'].sum():,.0f}")

            # Insight Section
            st.markdown("### 🧠 Smart Insights")
            st.markdown(f"<div class='insight-box'>💡 <b>Action Required:</b> You have {counts.get('Missing in Books', 0)} invoices in GSTR-2B that are not in your books. Claiming these could save you tax outflow.</div>", unsafe_allow_html=True)

            # Charts
            fig = px.pie(merged, names='Match Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig, use_container_width=True)

            # Data Preview
            st.markdown("### 🔍 Data Explorer")
            st.dataframe(merged.drop(columns=['PAN_KEY', 'NORM_DOC'], errors='ignore').head(50), use_container_width=True)

            # Download Result
            output = io.BytesIO()
            merged.to_excel(output, index=False)
            st.download_button("⚡ Download Full Report", output.getvalue(), "GST_Reconciliation_Report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Error: {e}")

# ================= BRANDING =================
st.markdown("""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
