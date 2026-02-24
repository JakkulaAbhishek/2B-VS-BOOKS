import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= HIGH-CONTRAST LIGHT UI CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    /* Global Styles - Light Theme */
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
    }
    .stApp { 
        background-color: #ffffff; 
        color: #1e293b; 
    }

    /* Headings - Dark & Professional */
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

    /* Sidebar - Light Gray Contrast */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #1e293b !important;
        font-weight: 600;
    }

    /* Metrics Cards - High Visibility */
    [data-testid="stMetric"] {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1e40af !important;
        font-weight: 800 !important;
    }

    /* Insight Boxes - Professional Blue */
    .insight-box {
        background: #eff6ff;
        padding: 20px; 
        border-left: 6px solid #2563eb; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        color: #1e3a8a;
        font-size: 1.1rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Buttons - Solid Blue */
    .stButton>button {
        background: #2563eb; 
        color: #ffffff !important;
        border: none; border-radius: 10px; padding: 12px 24px; 
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        color: #ffffff !important;
    }

    /* Dataframe Visibility */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }

    /* Branding - Black text on White */
    .web-branding {
        text-align: center; margin-top: 60px; padding: 30px;
        border-top: 1px solid #e2e8f0; 
        color: #000000; 
        font-size: 1.1rem;
        background-color: #ffffff;
    }
    .web-branding b { color: #2563eb; letter-spacing: 1.5px; }

    /* File Uploader Correction */
    [data-testid="stFileUploader"] {
        color: #000000 !important;
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
st.markdown('<p class="subtitle">Clean, High-Contrast Reconciliation for Financial Professionals.</p>', unsafe_allow_html=True)

# ================= LOGIC FUNCTIONS =================
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
        for col in ["MY GSTIN", "DOCUMENT DATE", "SUPPLIER GSTIN"]:
            if col not in df.columns: df[col] = ""
        df["SUPPLIER GSTIN"] = df["SUPPLIER GSTIN"].fillna("UNKNOWN").astype(str).str.upper().str.strip()
    
    numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)
    
    df_2b["NORM_DOC"] = normalize_invoice(df_2b["DOCUMENT NUMBER"])
    df_pr["NORM_DOC"] = normalize_invoice(df_pr["DOCUMENT NUMBER"])
    df_2b["PAN_KEY"] = df_2b["SUPPLIER GSTIN"].str[2:12] + "|" + df_2b["NORM_DOC"]
    df_pr["PAN_KEY"] = df_pr["SUPPLIER GSTIN"].str[2:12] + "|" + df_pr["NORM_DOC"]
    
    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged

# ================= MAIN APP FLOW =================
col_btn, empty_space = st.columns([1, 2])
with col_btn:
    st.download_button(
        label="📥 Download Excel Templates",
        data=generate_sample_templates(),
        file_name="GST_Templates.xlsx"
    )

st.markdown("<br>", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    file_2b = st.file_uploader("📄 Step 1: Upload GSTR-2B", type=["xlsx", "xls"])
with u2:
    file_pr = st.file_uploader("📘 Step 2: Upload Books", type=["xlsx", "xls"])

if file_2b and file_pr:
    try:
        with st.spinner("⚙️ Processing..."):
            merged = process_data_files(file_2b.getvalue(), file_pr.getvalue())

            # Math & Status
            merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
            merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
            diff = (merged["TAXABLE VALUE (2B)"].fillna(0) - merged["TAXABLE VALUE (PR)"].fillna(0)).abs()
            
            conditions = [
                (merged["_merge"] == "both") & (diff == 0),
                (merged["_merge"] == "both") & (diff <= tolerance),
                (merged["_merge"] == "left_only"),
                (merged["_merge"] == "right_only")
            ]
            statuses = ["Exact Match", "Within Tolerance", "Missing in Books", "Missing in 2B"]
            merged["Match Status"] = np.select(conditions, statuses, default="Mismatch")
            
            # Dashboard
            st.markdown("### 📊 Reconciliation Summary")
            counts = merged["Match Status"].value_counts()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", len(merged))
            m2.metric("Matches Found", counts.get("Exact Match", 0))
            m3.metric("Books Missing", counts.get("Missing in Books", 0))
            m4.metric("Unclaimed ITC (2B)", f"₹{merged[merged['Match Status'] == 'Missing in Books']['Total Tax (2B)'].sum():,.0f}")

            # Insights
            st.markdown(f"<div class='insight-box'>💡 <b>Action Item:</b> Found {counts.get('Missing in Books', 0)} invoices in your 2B data that are not recorded in your Purchase Register. Verify these to maximize your ITC claim.</div>", unsafe_allow_html=True)

            # Charts
            fig = px.pie(merged, names='Match Status', hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font=dict(color="black"))
            st.plotly_chart(fig, use_container_width=True)

            # Data Preview
            st.markdown("### 🔍 Filtered Data Preview")
            st.dataframe(merged.drop(columns=['PAN_KEY', 'NORM_DOC'], errors='ignore').head(100), use_container_width=True)

            # Download Result
            output = io.BytesIO()
            merged.to_excel(output, index=False)
            st.download_button("⚡ Download Final Reconciliation Report", output.getvalue(), "GST_Recon_Report.xlsx")

    except Exception as e:
        st.error(f"Error: {e}")

# ================= BRANDING =================
st.markdown("""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    <b>Email:</b> jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
