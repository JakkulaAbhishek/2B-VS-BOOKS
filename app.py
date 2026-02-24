import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import plotly.express as px

# ================= CONFIG & UI SETUP =================
st.set_page_config(page_title="GST Recon Pro", layout="wide", initial_sidebar_state="expanded")

# ================= REFINED UI CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

/* Global Styles */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #f8fafc; }
.stApp { background-color: #0f172a; }

/* Header Styling */
.main-title {
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 3.5rem; margin-bottom: 0px;
}
.subtitle { color: #94a3b8; font-size: 1.2rem; margin-bottom: 2rem; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }

/* Metric Cards */
[data-testid="stMetric"] {
    background: #1e293b; 
    border: 1px solid #334155;
    padding: 15px; border-radius: 12px;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 1rem !important; }
[data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 700 !important; }

/* Insight Boxes */
.insight-box {
    background: #1e293b; 
    padding: 15px;
    border-left: 4px solid #818cf8; 
    border-radius: 4px;
    margin-bottom: 10px; 
    color: #e2e8f0;
    line-height: 1.5;
}

/* Section Headers */
h2, h3 { color: #38bdf8 !important; border-bottom: 1px solid #334155; padding-bottom: 10px; }

/* Footer */
.web-branding {
    text-align: center; margin-top: 50px; padding: 20px;
    border-top: 1px solid #334155; color: #94a3b8;
}
.web-branding b { color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    tolerance = st.number_input("Mismatch Tolerance (₹)", min_value=0, value=20, step=1)
    max_rows = st.number_input("Max Rows for Excel", min_value=1000, value=15000, step=1000)

# ================= HEADER =================
st.markdown("<h1 class='main-title'>GST Recon Pro</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Smart Invoice Matching & Financial Reconciliation</p>', unsafe_allow_html=True)

# ================= TEMPLATE GENERATOR =================
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

c1, _ = st.columns([1, 2])
with c1:
    st.download_button("📥 Download Templates", generate_sample_templates(), "Templates.xlsx", "application/vnd.ms-excel")

# ================= PROCESSING LOGIC =================
def normalize_invoice(series):
    return series.astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True).str.lstrip('0')

@st.cache_data(show_spinner=False)
def process_data_files(file_2b_bytes, file_pr_bytes):
    df_2b = pd.read_excel(io.BytesIO(file_2b_bytes))
    df_pr = pd.read_excel(io.BytesIO(file_pr_bytes))
    
    for df in [df_2b, df_pr]:
        df.columns = df.columns.str.replace('*', '', regex=False).str.strip().str.upper()
        for col in ["TAXABLE VALUE", "IGST", "CGST", "SGST"]:
            df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)
        df["NORM_DOC"] = normalize_invoice(df["DOCUMENT NUMBER"])
        df["PAN_KEY"] = df["SUPPLIER GSTIN"].astype(str).str[2:12] + "|" + df["NORM_DOC"]

    dup_count = df_pr.duplicated(subset=["PAN_KEY"]).sum()
    merged = pd.merge(df_2b, df_pr, on="PAN_KEY", how="outer", suffixes=(" (2B)", " (PR)"), indicator=True)
    return merged, dup_count, df_2b, df_pr

# ================= FILE UPLOADER =================
col1, col2 = st.columns(2)
with col1:
    file_2b = st.file_uploader("📄 GSTR-2B Excel", type=["xlsx", "xls"])
with col2:
    file_pr = st.file_uploader("📘 Purchase Register", type=["xlsx", "xls"])

if file_2b and file_pr:
    try:
        merged, dup_pr_count, df_2b, df_pr = process_data_files(file_2b.getvalue(), file_pr.getvalue())
        
        # Calculation Logic
        merged["Total Tax (2B)"] = merged[["IGST (2B)", "CGST (2B)", "SGST (2B)"]].sum(axis=1)
        merged["Total Tax (PR)"] = merged[["IGST (PR)", "CGST (PR)", "SGST (PR)"]].sum(axis=1)
        diff = (merged["TAXABLE VALUE (2B)"].fillna(0) - merged["TAXABLE VALUE (PR)"].fillna(0)).abs()
        
        # Matching Logic
        cond = [
            (merged["_merge"] == "both") & (diff == 0),
            (merged["_merge"] == "both") & (diff <= tolerance),
            (merged["_merge"] == "both") & (diff > tolerance),
            (merged["_merge"] == "left_only"),
            (merged["_merge"] == "right_only")
        ]
        stats = ["Exact", "Matched (Tolerance)", "Value Mismatch", "Missing in Books", "Missing in 2B"]
        merged["Match Status"] = np.select(cond, stats, default="Fuzzy Match")
        
        # Dashboard
        st.write("---")
        st.subheader("📊 Executive Summary")
        counts = merged["Match Status"].value_counts()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Invoices", len(merged))
        m2.metric("Matched", counts.get("Exact", 0) + counts.get("Matched (Tolerance)", 0))
        m3.metric("Unclaimed ITC", f"₹{merged[merged['_merge']=='left_only']['Total Tax (2B)'].sum():,.0f}")
        m4.metric("Excess Claim", f"₹{merged[merged['_merge']=='right_only']['Total Tax (PR)'].sum():,.0f}")

        # Insights
        st.subheader("🧠 Automated Insights")
        if dup_pr_count > 0:
            st.markdown(f"<div class='insight-box'>⚠️ Found <b>{dup_pr_count}</b> duplicate entries in Purchase Register.</div>", unsafe_allow_html=True)
        if counts.get("Missing in Books", 0) > 0:
            st.markdown(f"<div class='insight-box'>💡 Unclaimed ITC: <b>{counts.get('Missing in Books')}</b> invoices are in 2B but not in your books.</div>", unsafe_allow_html=True)

        # Charts
        st.write("---")
        fig = px.pie(names=counts.index, values=counts.values, hole=0.4, title="Reconciliation Status")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)

        # Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            merged.to_excel(writer, sheet_name="Reconciliation", index=False)
        
        st.download_button("⚡ Download Full Report", output.getvalue(), "GST_Recon_Report.xlsx", use_container_width=True)

    except Exception as e:
        st.error(f"Analysis Error: {e}")

# ================= FOOTER =================
st.markdown(f"""
<div class="web-branding">
    Developed by <b>ABHISHEK JAKKULA</b><br>
    jakkulaabhishek5@gmail.com | {datetime.now().year}
</div>
""", unsafe_allow_html=True)
