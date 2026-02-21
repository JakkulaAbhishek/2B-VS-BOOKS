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
        df_2b[col] = pd.to_numeric(df_2b[col], errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr[col], errors="coerce").fillna(0)

    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["PRIMARY_KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(df_2b, df_pr,
                      on="PRIMARY_KEY",
                      how="outer",
                      suffixes=(" (2B)", " (PR)"),
                      indicator=True)

    rows = []

    for _, row in merged.iterrows():

        taxable_2b = row.get("TAXABLE VALUE (2B)",0)
        taxable_pr = row.get("TAXABLE VALUE (PR)",0)

        igst_2b = row.get("IGST (2B)",0)
        igst_pr = row.get("IGST (PR)",0)

        cgst_2b = row.get("CGST (2B)",0)
        cgst_pr = row.get("CGST (PR)",0)

        sgst_2b = row.get("SGST (2B)",0)
        sgst_pr = row.get("SGST (PR)",0)

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

        rows.append({
            "Match Status": status,
            "Supplier Name": row.get("SUPPLIER NAME (2B)", row.get("SUPPLIER NAME (PR)", "")),
            "Supplier GSTIN (2B)": row.get("SUPPLIER GSTIN (2B)", ""),
            "Supplier GSTIN (PR)": row.get("SUPPLIER GSTIN (PR)", ""),
            "My GSTIN (2B)": row.get("MY GSTIN (2B)", ""),
            "My GSTIN (PR)": row.get("MY GSTIN (PR)", ""),
            "Document Number (2B)": row.get("DOCUMENT NUMBER (2B)", ""),
            "Document Number (PR)": row.get("DOCUMENT NUMBER (PR)", ""),
            "Document Date (2B)": str(row.get("DOCUMENT DATE (2B)", "")),
            "Document Date (PR)": str(row.get("DOCUMENT DATE (PR)", "")),
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

    recon_df = pd.DataFrame(rows).fillna("")

    st.success("Reconciliation Completed")
    st.dataframe(recon_df)

    # ---------------- EXCEL EXPORT ----------------
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
        recon_sheet.set_column(col_num,col_num,18)

    for r,row in enumerate(recon_df.values):
        for c,val in enumerate(row):
            recon_sheet.write(r+1,c,str(val))

    # Write raw sheets
    df_2b.to_excel(pd.ExcelWriter(output, engine='xlsxwriter'), sheet_name="2B Data")

    # ---- DASHBOARD PIE CHARTS ----

    # Match Status Pie
    status_counts = recon_df["Match Status"].value_counts().reset_index()
    status_counts.columns = ["Status","Count"]

    dash_sheet.write_row("A1",["Status","Count"],header)
    for i,row in status_counts.iterrows():
        dash_sheet.write_row(i+1,0,row.values)

    pie1 = workbook.add_chart({'type':'pie'})
    pie1.add_series({
        'categories': f'=Dashboard!$A$2:$A${len(status_counts)+1}',
        'values': f'=Dashboard!$B$2:$B${len(status_counts)+1}',
        'data_labels': {'percentage':True}
    })
    dash_sheet.insert_chart('D2', pie1)

    # IGST Pie
    dash_sheet.write_row("A6",["Type","Value"],header)
    dash_sheet.write("A7","IGST 2B")
    dash_sheet.write("B7",recon_df["IGST (2B)"].sum())
    dash_sheet.write("A8","IGST PR")
    dash_sheet.write("B8",recon_df["IGST (PR)"].sum())

    pie2 = workbook.add_chart({'type':'pie'})
    pie2.add_series({
        'categories':'=Dashboard!$A$7:$A$8',
        'values':'=Dashboard!$B$7:$B$8',
        'data_labels':{'percentage':True}
    })
    dash_sheet.insert_chart('D18',pie2)

    # CGST Pie
    dash_sheet.write("A10","CGST 2B")
    dash_sheet.write("B10",recon_df["CGST (2B)"].sum())
    dash_sheet.write("A11","CGST PR")
    dash_sheet.write("B11",recon_df["CGST (PR)"].sum())

    pie3 = workbook.add_chart({'type':'pie'})
    pie3.add_series({
        'categories':'=Dashboard!$A$10:$A$11',
        'values':'=Dashboard!$B$10:$B$11',
        'data_labels':{'percentage':True}
    })
    dash_sheet.insert_chart('J2',pie3)

    # SGST Pie
    dash_sheet.write("A13","SGST 2B")
    dash_sheet.write("B13",recon_df["SGST (2B)"].sum())
    dash_sheet.write("A14","SGST PR")
    dash_sheet.write("B14",recon_df["SGST (PR)"].sum())

    pie4 = workbook.add_chart({'type':'pie'})
    pie4.add_series({
        'categories':'=Dashboard!$A$13:$A$14',
        'values':'=Dashboard!$B$13:$B$14',
        'data_labels':{'percentage':True}
    })
    dash_sheet.insert_chart('J18',pie4)

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
