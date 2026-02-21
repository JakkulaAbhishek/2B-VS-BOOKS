import streamlit as st
import pandas as pd
import numpy as np
import io

TOLERANCE = 20

st.set_page_config(page_title="GST 2B vs Books Reconciliation", layout="wide")

st.title("📊 GST 2B vs Purchase Register Reconciliation Engine")
st.caption("Professional Reconciliation System")

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
buffer = io.BytesIO()
template.to_excel(buffer, index=False)

st.download_button("⬇ Download Standard Template",
                   buffer.getvalue(),
                   "2B_Books_Template.xlsx")

st.divider()

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col,0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col,0), errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(df_2b, df_pr,
                      on="KEY",
                      how="outer",
                      suffixes=(" (2B)", " (PR)"),
                      indicator=True)

    records = []

    for _, row in merged.iterrows():

        taxable_2b = row.get("TAXABLE VALUE (2B)",0)
        taxable_pr = row.get("TAXABLE VALUE (PR)",0)

        igst_2b = row.get("IGST (2B)",0)
        igst_pr = row.get("IGST (PR)",0)

        cgst_2b = row.get("CGST (2B)",0)
        cgst_pr = row.get("CGST (PR)",0)

        sgst_2b = row.get("SGST (2B)",0)
        sgst_pr = row.get("SGST (PR)",0)

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

        records.append({
            "Match Status": status,
            "Supplier Name": supplier,
            "Taxable (2B)": taxable_2b,
            "Taxable (PR)": taxable_pr,
            "Difference": taxable_2b - taxable_pr,
            "Total Tax (2B)": total_2b,
            "Total Tax (PR)": total_pr,
            "IGST (2B)": igst_2b,
            "IGST (PR)": igst_pr,
            "CGST (2B)": cgst_2b,
            "CGST (PR)": cgst_pr,
            "SGST (2B)": sgst_2b,
            "SGST (PR)": sgst_pr
        })

    recon_df = pd.DataFrame(records)

    # ---------------- KPI DASHBOARD ----------------
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

    # ---------------- SAFE EXCEL EXPORT ----------------
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        recon_df.to_excel(writer, sheet_name="Reconciliation", index=False)
        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Purchase Data", index=False)

        workbook = writer.book
        recon_sheet = writer.sheets["Reconciliation"]

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1f4e79',
            'font_color': 'white'
        })

        for col_num, value in enumerate(recon_df.columns.values):
            recon_sheet.write(0, col_num, value, header_format)

        # Auto column width
        for i, col in enumerate(recon_df.columns):
            column_len = max(recon_df[col].astype(str).map(len).max(), len(col))
            recon_sheet.set_column(i, i, column_len + 2)

    st.download_button("⬇ Download Final Professional Report",
                       output.getvalue(),
                       "GST_Reconciliation_Report.xlsx")

st.markdown("""
<hr>
<center>
<b>Developed by ABHISHEK JAKKULA</b><br>
jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
