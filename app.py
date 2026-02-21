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
        "Taxable Value (2B)","Taxable Value (PR)",
        "Tax Difference",
        "Total Tax (2B)","Total Tax (PR)",
        "IGST (2B)","IGST (PR)",
        "CGST (2B)","CGST (PR)",
        "SGST (2B)","SGST (PR)"
    ]

    recon_df = pd.DataFrame(records, columns=columns)

    st.success("Reconciliation Completed")
    st.dataframe(recon_df)

    # ---------------- KPI TILES ----------------
    total = len(recon_df)
    exact = len(recon_df[recon_df["Match Status"].str.contains("Exact")])
    mismatch = len(recon_df[recon_df["Match Status"]=="Value Mismatch"])
    missing = len(recon_df[recon_df["Match Status"].str.contains("Missing")])

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Records", total)
    col2.metric("Exact %", f"{round((exact/total)*100,2) if total else 0}%")
    col3.metric("Mismatch %", f"{round((mismatch/total)*100,2) if total else 0}%")
    col4.metric("Missing %", f"{round((missing/total)*100,2) if total else 0}%")

    # ---------------- SAFE EXCEL EXPORT ----------------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    recon_sheet = workbook.add_worksheet("Reconciliation")
    dash_sheet = workbook.add_worksheet("Dashboard")

    header = workbook.add_format({'bold':True,'bg_color':'#D9E1F2','border':1})

    # Write reconciliation safely
    for c,col in enumerate(columns):
        recon_sheet.write(0,c,col,header)

    for r,row in enumerate(records):
        for c,val in enumerate(row):
            if isinstance(val,(int,float)):
                recon_sheet.write_number(r+1,c,val)
            else:
                recon_sheet.write_string(r+1,c,str(val))

    # Dashboard Summary
    dash_sheet.write_row("A1",["Metric","Value"],header)
    dash_sheet.write_row("A2",["Total Records", total])
    dash_sheet.write_row("A3",["Exact %", round((exact/total)*100,2) if total else 0])
    dash_sheet.write_row("A4",["Mismatch %", round((mismatch/total)*100,2) if total else 0])
    dash_sheet.write_row("A5",["Missing %", round((missing/total)*100,2) if total else 0])

    # Pie Chart
    status_counts = recon_df["Match Status"].value_counts()
    dash_sheet.write_row("A7",["Status","Count"],header)

    row_index=8
    for k,v in status_counts.items():
        dash_sheet.write_string(row_index,0,k)
        dash_sheet.write_number(row_index,1,int(v))
        row_index+=1

    pie = workbook.add_chart({'type':'pie'})
    pie.add_series({
        'categories': f'=Dashboard!$A$9:$A${row_index}',
        'values': f'=Dashboard!$B$9:$B${row_index}',
        'data_labels': {'percentage':True}
    })
    dash_sheet.insert_chart('D2',pie)

    workbook.close()

    st.download_button("Download Final Report",
                       output.getvalue(),
                       "GST_Reconciliation_Report.xlsx")
