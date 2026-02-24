import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= HIGH-VISIBILITY PROFESSIONAL CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
    }
    .stApp { 
        background-color: #ffffff; 
        color: #1e293b; 
    }

    /* Primary Heading */
    h1 {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3.5rem !important; 
        margin-bottom: 5px !important;
    }
    .subtitle { 
        color: #475569; 
        font-size: 1.2rem; 
        margin-bottom: 2rem; 
        font-weight: 500;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #cbd5e1;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #0f172a !important;
        font-weight: 600;
    }

    /* Metric Cards - High Contrast */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1e40af !important;
        font-weight: 800 !important;
    }

    /* Insight Boxes */
    .insight-box {
        background: #f8fafc;
        padding: 18px; 
        border-left: 6px solid #2563eb; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        color: #0f172a;
        font-size: 1.05rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Buttons */
    .stButton>button {
        background: #2563eb; 
        color: #ffffff !important;
        border: none; border-radius: 8px; padding: 12px 24px; 
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    /* Footer Branding - Black on White */
    .web-branding {
        text-align: center; 
        margin-top: 60px; 
        padding: 40px;
        border-top: 2px solid #e2e8f0; 
        color: #000000; 
        font-size: 1.1rem;
        background-color: #f8fafc;
    }
    .web-branding b { color: #1e40af; letter-spacing: 1px; }
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
    return output.getvalue()

col_btn, _ = st.columns([1, 2])
with col_btn:
    st.download_button("📥 Download Excel Templates", generate_sample_templates(), "GST_Templates.xlsx")

st.markdown("<br>", unsafe_allow_html=True)

# ================= LOGIC & PROCESSING =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

@st.cache_data(show_spinner=False)
def process_data_files(file_2b_bytes, file_pr_bytes):
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
    df_2b.columns = df_2b.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.replace('*', '', regex=False).str.strip().str.upper()
    
    for df in [df_2b, df_pr]:
        for col in ["MY GSTIN", "DOCUMENT DATE", "SUPPLIER GSTIN"]:
            if col not in df.columns: df[col] = ""
        df["SUPPLIER GSTIN"] = df["SUPPLIER GSTIN"].fillna("UNKNOWN").astype(str).str.upper().str.strip()
        for num_col in ["TAXABLE VALUE", "IGST", "CGST", "SGST"]:
            df[num_col] = pd.to_numeric(df.get(num_col, 0), errors="coerce").fillna(0)

    df_2b["PAN_KEY"] = df_2b["SUPPLIER GSTIN"].str[2:12] + "|" + normalize_invoice(df_2b["DOCUMENT NUMBER"])
    df_pr["PAN_KEY"] = df_pr["SUPPLIER GSTIN"].str[2:12] + "|" + normalize_invoice(df_pr["DOCUMENT NUMBER"])
    
    dup_pr = df_pr.duplicated(subset=["PAN_KEY"], keep=False).sum()
    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, dup_pr, df_2b, df_pr

# ================= UPLOAD & MAIN =================
c1, c2 = st.columns(2)
with c1:
    f2b = st.file_uploader("📄 Upload GSTR-2B Excel", type=["xlsx"])
with c2:
    fpr = st.file_uploader("📘 Upload Purchase Register", type=["xlsx"])

if f2b and fpr:
    try:
        with st.spinner("⚙️ Analyzing..."):
            merged, dup_pr_count, df_2b, df_pr = process_data_files(f2b.getvalue(), fpr.getvalue())
            
            # Reconciliation Math
            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            merged["Match Status"] = np.where(merged["_merge"] == "both", "Matched", 
                                     np.where(merged["_merge"] == "left_only", "Missing in Books", "Missing in 2B"))
            
            # --- DASHBOARD ---
            st.markdown("### 📊 Reconciliation Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(merged))
            m2.metric("Matched", (merged["_merge"] == "both").sum())
            m3.metric("Missing in Books", (merged["_merge"] == "left_only").sum())
            m4.metric("Unclaimed ITC", f"₹{merged[merged['_merge'] == 'left_only']['Total Tax (2B)'].sum():,.0f}")

            # --- INSIGHTS ---
            st.markdown("### 🧠 Smart Insights")
            missed_val = merged[merged["_merge"] == "left_only"]["Total Tax (2B)"].sum()
            if missed_val > 0:
                st.markdown(f"<div class='insight-box'>💡 <b>Action Required:</b> You have ₹{missed_val:,.2f} of unclaimed ITC in GSTR-2B not found in your books.</div>", unsafe_allow_html=True)
            if dup_pr_count > 0:
                st.markdown(f"<div class='insight-box'>⚠️ <b>Data Integrity:</b> Found {dup_pr_count} duplicate entries in your Purchase Register.</div>", unsafe_allow_html=True)

            # --- PREVIEW & DOWNLOAD ---
            st.markdown("### 🔍 Data Preview")
            st.dataframe(merged.head(100), use_container_width=True)

            output = io.BytesIO()
            merged.to_excel(output, index=False)
            st.download_button("⚡ Download Final Report", output.getvalue(), "GST_Reconciliation_Final.xlsx")

    except Exception as e:
        st.error(f"Engine Error: {e}")

# ================= BRANDING =================
st.markdown(f"""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    Contact: jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
