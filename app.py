import streamlit as st
import pandas as pd
import numpy as np
import io
import xlsxwriter

# ---------------- CONFIG ----------------
TOLERANCE = 20
st.set_page_config(page_title="GST 2B vs Books Reconciliation", layout="wide")

# ---------------- PROFESSIONAL UI ----------------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
.block-container {
    padding-top: 2rem;
}
h1 {
    color: #0a1f44;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 GST 2B vs Purchase Register Reconciliation")
st.caption("Enterprise Reconciliation Engine")

# ---------------- TEMPLATE ----------------
def create_template():
    return pd.DataFrame({
        "SUPPLIER NAME": [],
        "SUPPLIER GSTIN": [],
        "MY GSTIN": [],
        "DOCUMENT NUMBER": [],
        "DOCUMENT DATE": [],
        "TAXABLE VALUE": [],
        "IGST": [],
        "CGST": [],
        "SGST": []
    })

template = create_template()
buf = io.BytesIO()
template.to_excel(buf, index=False)

st.download_button("⬇ Download Standard Template",
                   buf.getvalue(),
                   "2B_Books_Template.xlsx")

st.divider()

file_2b = st.file_uploader("Upload GSTR-2B", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register", type=["xlsx"])

# ---------------- PROCESS ----------------
if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(df_2b, df_pr,
                      on="KEY",
                      how="outer",
                      suffixes=(" (2B)", " (PR)"),
                      indicator=True)

    records = []

    for _, row in merged.iterrows():

        taxable_2b = float(row.get("TAXABLE VALUE (2B)", 0))
        taxable_pr = float(row.get("TAXABLE VALUE (PR)", 0))

        igst_2b = float(row.get("IGST (2B)", 0))
        igst_pr = float(row.get("IGST (PR)", 0))

        cgst_2b = float(row.get("CGST (2B)", 0))
        cgst_pr = float(row.get("CGST (PR)", 0))

        sgst_2b = float(row.get("SGST (2B)", 0))
        sgst_pr = float(row.get("SGST (PR)", 0))

        total_2b = igst_2b + cgst_2b + sgst_2b
        total_pr = igst_pr + cgst_pr + sgst_pr

        if row["_merge"] == "both":
            diff = abs(taxable_2b - taxable_pr)
            if diff == 0:
                status = "Exact"
            elif diff <= TOLERANCE:
                status = "Exact (Tolerance)"
            else:
                status = "Value Mismatch"
        elif row["_merge"] == "left_only":
            status = "Missing in PR"
        else:
            status = "Missing in 2B"

        supplier = row.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier) or supplier == "":
            supplier = row.get("SUPPLIER NAME (PR)", "")

        records.append([
            status,
            supplier,
            taxable_2b,
            taxable_pr,
            taxable_2b - taxable_pr,
            total_2b,
            total_pr,
            igst_2b,
            igst_pr,
            cgst_2b,
            cgst_pr,
            sgst_2b,
            sgst_pr
        ])

    columns = [
        "Match Status","Supplier Name",
        "Taxable (2B)","Taxable (PR)",
        "Difference",
        "Total Tax (2B)","Total Tax (PR)",
        "IGST (2B)","IGST (PR)",
        "CGST (2B)","CGST (PR)",
        "SGST (2B)","SGST (PR)"
    ]

    recon_df = pd.DataFrame(records, columns=columns)

    # ---------------- KPI TILES ----------------
    total = len(recon_df)
    exact = len(recon_df[recon_df["Match Status"].str.contains("Exact")])
    mismatch = len(recon_df[recon_df["Match Status"]=="Value Mismatch"])
    missing = len(recon_df[recon_df["Match Status"].str.contains("Missing")])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Records", total)
    c2.metric("Exact %", f"{round((exact/total)*100,2) if total else 0}%")
    c3.metric("Mismatch %", f"{round((mismatch/total)*100,2) if total else 0}%")
    c4.metric("Missing %", f"{round((missing/total)*100,2) if total else 0}%")

    st.dataframe(recon_df, use_container_width=True)

    # ---------------- EXCEL EXPORT ----------------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    recon_sheet = workbook.add_worksheet("Reconciliation")
    header_format = workbook.add_format({
        'bold': True,
        'font_color': 'white',
        'bg_color': '#1f4e79',
        'border':1
    })

    number_format = workbook.add_format({'num_format':'#,##0.00'})

    # Write header
    for col, name in enumerate(columns):
        recon_sheet.write(0, col, name, header_format)

    # Write data safely
    for r in range(len(recon_df)):
        for c in range(len(columns)):
            val = recon_df.iloc[r,c]
            if isinstance(val,(int,float)):
                recon_sheet.write(r+1,c,float(val),number_format)
            else:
                recon_sheet.write(r+1,c,str(val))

    # Auto column width
    for i, col in enumerate(columns):
        width = max(recon_df[col].astype(str).map(len).max(), len(col)) + 2
        recon_sheet.set_column(i, i, width)

    workbook.close()

    st.download_button("⬇ Download Big-4 Styled Report",
                       output.getvalue(),
                       "GST_Reconciliation_Report.xlsx")

st.markdown("""
<hr>
<center>
<b>Developed by ABHISHEK JAKKULA</b><br>
jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
