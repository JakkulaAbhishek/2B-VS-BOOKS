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

    merged = pd.merge(
        df_2b, df_pr,
        on="PRIMARY_KEY",
        how="outer",
        suffixes=(" (2B)", " (PR)"),
        indicator=True
    )

    records = []

    for _, row in merged.iterrows():

        taxable_2b = float(row.get("TAXABLE VALUE (2B)",0) or 0)
        taxable_pr = float(row.get("TAXABLE VALUE (PR)",0) or 0)

        igst_2b = float(row.get("IGST (2B)",0) or 0)
        igst_pr = float(row.get("IGST (PR)",0) or 0)

        cgst_2b = float(row.get("CGST (2B)",0) or 0)
        cgst_pr = float(row.get("CGST (PR)",0) or 0)

        sgst_2b = float(row.get("SGST (2B)",0) or 0)
        sgst_pr = float(row.get("SGST (PR)",0) or 0)

        total_2b = igst_2b + cgst_2b + sgst_2b
        total_pr = igst_pr + cgst_pr + sgst_pr

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

        supplier = row.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier) or supplier == "":
            supplier = row.get("SUPPLIER NAME (PR)", "")

        records.append([
            str(status),
            str(supplier),
            str(row.get("SUPPLIER GSTIN (2B)","")),
            str(row.get("SUPPLIER GSTIN (PR)","")),
            str(row.get("MY GSTIN (2B)","")),
            str(row.get("MY GSTIN (PR)","")),
            str(row.get("DOCUMENT NUMBER (2B)","")),
            str(row.get("DOCUMENT NUMBER (PR)","")),
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
        "Supplier GSTIN (2B)","Supplier GSTIN (PR)",
        "My GSTIN (2B)","My GSTIN (PR)",
        "Document Number (2B)","Document Number (PR)",
        "Taxable Value (2B)","Taxable Value (PR)",
        "Tax Difference (2B-PR)",
        "Total Tax (2B)","Total Tax (PR)",
        "IGST (2B)","IGST (PR)",
        "CGST (2B)","CGST (PR)",
        "SGST (2B)","SGST (PR)"
    ]

    recon_df = pd.DataFrame(records, columns=columns)

    st.success("Reconciliation Completed")
    st.dataframe(recon_df)

    # ---------------- EXCEL EXPORT ----------------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    recon_sheet = workbook.add_worksheet("Reconciliation")
    dash_sheet = workbook.add_worksheet("Dashboard")
    sheet_2b = workbook.add_worksheet("2B Data")
    sheet_pr = workbook.add_worksheet("Books Data")

    header_format = workbook.add_format({'bold':True,'bg_color':'#D9E1F2','border':1})

    # Write Reconciliation safely
    for col_num, col in enumerate(columns):
        recon_sheet.write(0,col_num,col,header_format)

    for r,row in enumerate(records):
        for c,val in enumerate(row):
            if isinstance(val,(int,float)):
                recon_sheet.write_number(r+1,c,val)
            else:
                recon_sheet.write_string(r+1,c,str(val))

    # Write raw sheets safely
    df_2b = df_2b.fillna("")
    df_pr = df_pr.fillna("")

    for col_num, col in enumerate(df_2b.columns):
        sheet_2b.write(0,col_num,col,header_format)
    for r in range(len(df_2b)):
        for c in range(len(df_2b.columns)):
            sheet_2b.write_string(r+1,c,str(df_2b.iloc[r,c]))

    for col_num, col in enumerate(df_pr.columns):
        sheet_pr.write(0,col_num,col,header_format)
    for r in range(len(df_pr)):
        for c in range(len(df_pr.columns)):
            sheet_pr.write_string(r+1,c,str(df_pr.iloc[r,c]))

    # Dashboard Pie Chart
    status_counts = recon_df["Match Status"].value_counts()

    dash_sheet.write_row("A1",["Status","Count"],header_format)
    row_index = 1
    for k,v in status_counts.items():
        dash_sheet.write_string(row_index,0,k)
        dash_sheet.write_number(row_index,1,int(v))
        row_index += 1

    pie = workbook.add_chart({'type':'pie'})
    pie.add_series({
        'categories': f'=Dashboard!$A$2:$A${row_index}',
        'values': f'=Dashboard!$B$2:$B${row_index}',
        'data_labels': {'percentage':True}
    })
    dash_sheet.insert_chart('D2',pie)

    workbook.close()

    st.download_button(
        "Download Final Reconciliation Report",
        output.getvalue(),
        "GST_Reconciliation_Report.xlsx"
    )

st.markdown("""
<hr>
<center>
Tool developed by <b>ABHISHEK JAKKULA</b><br>
GMAIL: jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
