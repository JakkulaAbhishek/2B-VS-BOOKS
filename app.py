import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ================= CONFIG =================
TOLERANCE = 20
MAX_ROWS = 15000

st.set_page_config(page_title="GST Reconciliation Suite", layout="wide")

# ================= CLEAN GOOGLE STYLE UI =================
st.markdown("""
<style>
body {background-color:#f8fafc;}
h1 {color:#1a73e8;font-weight:600;}
.stButton>button {
    background:#1a73e8;
    color:white;
    border-radius:8px;
    height:40px;
}
.footer {
    margin-top:40px;
    text-align:center;
    color:#6b7280;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

st.title("GST 2B vs Books Reconciliation")

# ================= SAMPLE TEMPLATE =================
def generate_sample_template():
    sample = pd.DataFrame({
        "SUPPLIER NAME":[
            "NESHVARI ENGINEERING AND SERVICES",
            "METALLIZING EQUIPMENT COMPANY P. LTD."
        ],
        "SUPPLIER GSTIN":[
            "36CNNPD6299J1ZB",
            "08AAACM8473A1ZL"
        ],
        "MY GSTIN":[
            "36ADXFS5154R1ZU",
            "36ADXFS5154R1ZU"
        ],
        "DOCUMENT NUMBER":[
            "11/2023-24",
            "MEC-439-2023"
        ],
        "DOCUMENT DATE":[
            "24-07-2023",
            "26-05-2023"
        ],
        "TAXABLE VALUE":[7500,13150],
        "IGST":[0,2367],
        "CGST":[675,0],
        "SGST":[675,0]
    })
    return sample

template = generate_sample_template()
template_buffer = io.BytesIO()
template.to_excel(template_buffer, index=False)

st.download_button(
    "Download Sample Upload Template",
    template_buffer.getvalue(),
    "GST_Common_Template.xlsx"
)

# ================= FILE UPLOAD =================
col1, col2 = st.columns(2)

with col1:
    file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])

with col2:
    file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

# ================= PROCESS =================
if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b[col], errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr[col], errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str)+"|"+df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str)+"|"+df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(
        df_2b,
        df_pr,
        on="KEY",
        how="outer",
        suffixes=(" (2B)", " (PR)"),
        indicator=True
    )

    records = []

    for _, r in merged.iterrows():

        taxable_2b = r.get("TAXABLE VALUE (2B)",0)
        taxable_pr = r.get("TAXABLE VALUE (PR)",0)

        igst_2b = r.get("IGST (2B)",0)
        cgst_2b = r.get("CGST (2B)",0)
        sgst_2b = r.get("SGST (2B)",0)

        igst_pr = r.get("IGST (PR)",0)
        cgst_pr = r.get("CGST (PR)",0)
        sgst_pr = r.get("SGST (PR)",0)

        total_2b = igst_2b + cgst_2b + sgst_2b
        total_pr = igst_pr + cgst_pr + sgst_pr

        if r["_merge"]=="both":
            diff = abs(taxable_2b-taxable_pr)
            if diff==0:
                status="Exact"
                reason="GSTIN+Invoice+Taxable matched"
            elif diff<=TOLERANCE:
                status="Exact (Tolerance)"
                reason="Within tolerance"
            else:
                status="Value Mismatch"
                reason="Taxable mismatch"
        elif r["_merge"]=="left_only":
            status="Missing in PR"
            reason="Present only in 2B"
        else:
            status="Missing in 2B"
            reason="Present only in PR"

        supplier = r.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier):
            supplier = r.get("SUPPLIER NAME (PR)","")

        records.append({
            "Match Status":status,
            "Match Reason":reason,
            "Supplier Name":supplier,
            "Supplier GSTIN (2B)":r.get("SUPPLIER GSTIN (2B)",""),
            "Supplier GSTIN (PR)":r.get("SUPPLIER GSTIN (PR)",""),
            "Document Number (2B)":r.get("DOCUMENT NUMBER (2B)",""),
            "Document Number (PR)":r.get("DOCUMENT NUMBER (PR)",""),
            "Taxable Value (2B)":taxable_2b,
            "Taxable Value (PR)":taxable_pr,
            "Total Tax (2B)":total_2b,
            "Total Tax (PR)":total_pr
        })

    recon_df = pd.DataFrame(records)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book

        header_format = workbook.add_format({
            "bold":True,
            "bg_color":"#1a73e8",
            "font_color":"white",
            "border":1
        })

        recon_df.to_excel(writer,
                          sheet_name="Reconciliation",
                          startrow=2,
                          index=False,
                          header=False)

        sheet = writer.sheets["Reconciliation"]

        # Subtotal row
        for col in recon_df.select_dtypes(include=np.number).columns:
            idx = recon_df.columns.get_loc(col)
            col_letter = chr(65+idx)
            sheet.write_formula(
                0,
                idx,
                f"=SUBTOTAL(9,{col_letter}3:{col_letter}{MAX_ROWS})"
            )

        # Header row
        for col_num, col_name in enumerate(recon_df.columns):
            sheet.write(1, col_num, col_name, header_format)

        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Books Data", index=False)

        # Dashboard sheet
        dash = workbook.add_worksheet("Dashboard")

        dash.write_row("A1",["Status","Count"],header_format)

        statuses = ["Exact","Exact (Tolerance)",
                    "Value Mismatch","Missing in PR","Missing in 2B"]

        for i,status in enumerate(statuses):
            dash.write(1+i,0,status)
            dash.write_formula(
                1+i,1,
                f'=COUNTIF(Reconciliation!A3:A{MAX_ROWS},"{status}")'
            )

        pie = workbook.add_chart({'type':'pie'})
        pie.add_series({
            'categories': '=Dashboard!$A$2:$A$6',
            'values': '=Dashboard!$B$2:$B$6',
            'data_labels': {'percentage':True}
        })

        dash.insert_chart('D2', pie)

    st.success("Reconciliation file generated successfully")

    st.download_button(
        "Download Final Excel",
        output.getvalue(),
        f"GST_Reconciliation_{datetime.now().strftime('%Y%m%d')}.xlsx"
    )

# ================= BRANDING =================
st.markdown("""
<div class="footer">
Developed by <b>ABHISHEK JAKKULA</b><br>
Email: jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
