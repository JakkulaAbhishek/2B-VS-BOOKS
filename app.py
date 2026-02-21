import streamlit as st
import pandas as pd
import numpy as np
import io
import xlsxwriter

TOLERANCE = 20

st.set_page_config(page_title="GST 2B vs Books", layout="wide")
st.title("GST 2B vs Purchase Reconciliation Tool")

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

st.download_button("Download Common Template",
                   buffer.getvalue(),
                   "2B_Books_Template.xlsx")

st.divider()

file_2b = st.file_uploader("Upload GSTR-2B", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col, 0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col, 0), errors="coerce").fillna(0)

    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["PRIMARY_KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(df_2b, df_pr,
                      on="PRIMARY_KEY",
                      how="outer",
                      suffixes=(" (2B)", " (PR)"),
                      indicator=True)

    rows = []

    for _, row in merged.iterrows():

        taxable_2b = float(row.get("TAXABLE VALUE (2B)",0))
        taxable_pr = float(row.get("TAXABLE VALUE (PR)",0))

        igst_2b = float(row.get("IGST (2B)",0))
        igst_pr = float(row.get("IGST (PR)",0))

        cgst_2b = float(row.get("CGST (2B)",0))
        cgst_pr = float(row.get("CGST (PR)",0))

        sgst_2b = float(row.get("SGST (2B)",0))
        sgst_pr = float(row.get("SGST (PR)",0))

        total_tax_2b = igst_2b + cgst_2b + sgst_2b
        total_tax_pr = igst_pr + cgst_pr + sgst_pr

        if row["_merge"] == "both":
            diff = abs(taxable_2b - taxable_pr)
            if diff == 0:
                status = "Exact"
            elif diff <= TOLERANCE:
                status = "Exact (Within 20)"
            else:
                status = "Value Mismatch"
        elif row["_merge"] == "left_only":
            status = "Missing in PR"
        else:
            status = "Missing in 2B"

        supplier_name = row.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier_name) or supplier_name == "":
            supplier_name = row.get("SUPPLIER NAME (PR)", "")

        rows.append({
            "Match Status": status,
            "Supplier Name": supplier_name,
            "Supplier GSTIN (2B)": row.get("SUPPLIER GSTIN (2B)", ""),
            "Supplier GSTIN (PR)": row.get("SUPPLIER GSTIN (PR)", ""),
            "My GSTIN (2B)": row.get("MY GSTIN (2B)", ""),
            "My GSTIN (PR)": row.get("MY GSTIN (PR)", ""),
            "Document Number (2B)": row.get("DOCUMENT NUMBER (2B)", ""),
            "Document Number (PR)": row.get("DOCUMENT NUMBER (PR)", ""),
            "Taxable Value (2B)": taxable_2b,
            "Taxable Value (PR)": taxable_pr,
            "Tax Difference (2B-PR)": taxable_2b - taxable_pr,
            "Total Tax (2B)": total_tax_2b,
            "Total Tax (PR)": total_tax_pr,
            "IGST (2B)": igst_2b,
            "IGST (PR)": igst_pr,
            "CGST (2B)": cgst_2b,
            "CGST (PR)": cgst_pr,
            "SGST (2B)": sgst_2b,
            "SGST (PR)": sgst_pr
        })

    recon_df = pd.DataFrame(rows)

    st.success("Reconciliation Completed")
    st.dataframe(recon_df)

    # -------- SAFE NUMERIC AGGREGATION --------
    igst_2b_total = pd.to_numeric(recon_df["IGST (2B)"], errors="coerce").fillna(0).sum()
    igst_pr_total = pd.to_numeric(recon_df["IGST (PR)"], errors="coerce").fillna(0).sum()

    cgst_2b_total = pd.to_numeric(recon_df["CGST (2B)"], errors="coerce").fillna(0).sum()
    cgst_pr_total = pd.to_numeric(recon_df["CGST (PR)"], errors="coerce").fillna(0).sum()

    sgst_2b_total = pd.to_numeric(recon_df["SGST (2B)"], errors="coerce").fillna(0).sum()
    sgst_pr_total = pd.to_numeric(recon_df["SGST (PR)"], errors="coerce").fillna(0).sum()

    # -------- EXCEL --------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    recon_sheet = workbook.add_worksheet("Reconciliation")
    dash_sheet = workbook.add_worksheet("Dashboard")
    sheet_2b = workbook.add_worksheet("2B Data")
    sheet_pr = workbook.add_worksheet("Books Data")

    header = workbook.add_format({'bold':True,'bg_color':'#D9E1F2','border':1})

    # Write reconciliation
    for col_num, col in enumerate(recon_df.columns):
        recon_sheet.write(0,col_num,col,header)

    for r,row in enumerate(recon_df.values):
        for c,val in enumerate(row):
            recon_sheet.write(r+1,c,val)

    # Write raw sheets
    df_2b.to_excel(pd.ExcelWriter(output, engine='xlsxwriter'), sheet_name="2B Data")
    df_pr.to_excel(pd.ExcelWriter(output, engine='xlsxwriter'), sheet_name="Books Data")

    # Dashboard - Match Status Pie
    status_counts = recon_df["Match Status"].value_counts()

    dash_sheet.write_row("A1",["Status","Count"],header)

    for i,(k,v) in enumerate(status_counts.items()):
        dash_sheet.write(i+1,0,k)
        dash_sheet.write(i+1,1,v)

    pie1 = workbook.add_chart({'type':'pie'})
    pie1.add_series({
        'categories': f'=Dashboard!$A$2:$A${len(status_counts)+1}',
        'values': f'=Dashboard!$B$2:$B${len(status_counts)+1}',
        'data_labels': {'percentage':True}
    })
    dash_sheet.insert_chart('D2',pie1)

    # IGST Pie
    dash_sheet.write("A6","IGST 2B")
    dash_sheet.write("B6",igst_2b_total)
    dash_sheet.write("A7","IGST PR")
    dash_sheet.write("B7",igst_pr_total)

    pie2 = workbook.add_chart({'type':'pie'})
    pie2.add_series({
        'categories':'=Dashboard!$A$6:$A$7',
        'values':'=Dashboard!$B$6:$B$7',
        'data_labels':{'percentage':True}
    })
    dash_sheet.insert_chart('D18',pie2)

    workbook.close()

    st.download_button("Download Final Reconciliation Report",
                       output.getvalue(),
                       "GST_Reconciliation_Report.xlsx")

st.markdown("""
<hr>
<center>
Tool developed by <b>ABHISHEK JAKKULA</b><br>
GMAIL: jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
